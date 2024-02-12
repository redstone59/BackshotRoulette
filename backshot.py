from roulette import *
from transposition_tables import *

INF = 1000000

def convert_move_list(move_list: list[ValidMoves]):
    resultant = []
    for move in move_list:
        match move:
            case ValidMoves.USE_BEER:
                resultant += ["beer"]
            case ValidMoves.USE_CIGARETTES:
                resultant += ["cigarettes"]
            case ValidMoves.USE_HAND_SAW:
                resultant += ["saw"]
            case ValidMoves.USE_HANDCUFFS:
                resultant += ["handcuff"]
            case ValidMoves.USE_MAGNIFYING_GLASS:
                resultant += ["glass"]
            case ValidMoves.SHOOT_DEALER:
                resultant += ["dealer"]
            case ValidMoves.SHOOT_PLAYER:
                resultant += ["player"]
    return resultant

def hand_saw_bonus(state: BuckshotRouletteMove):
    if state.is_players_turn and Items.HAND_SAW in state.dealer_items and state.player_health > 2:
        return 150
    
    elif (not state.is_players_turn) and Items.HAND_SAW in state.player_items and state.dealer_health > 2:
        return 150
    
    return 0

def is_redundant_move(move: ValidMoves, state: BuckshotRouletteMove):
    """
    Returns True if `move` doesn't make sense for the given `state`. (e.g. smoking cigarettes at max health)

    Args:
        move (ValidMoves): The move to be made
        state (BuckshotRouletteMove): The state the game is currently in.

    Returns:
        bool: True if move is redundant, False if not.
    """
    match move:
        case ValidMoves.SHOOT_DEALER:
            if state.is_players_turn and state.current_shell == "blank": return True
        
        case ValidMoves.SHOOT_PLAYER:
            if (not state.is_players_turn) and state.current_shell == "blank": return True
        
        case ValidMoves.USE_CIGARETTES:
            if state.is_players_turn and state.player_health == state.max_health:
                return True
            elif (not state.is_players_turn) and state.dealer_health == state.max_health:
                return True
        
        case ValidMoves.USE_HAND_SAW:
            if state.live_shells == 0: return True
            if state.is_players_turn and state.dealer_health == 1: return True
            elif (not state.is_players_turn) and state.player_health == 1: return True
        
        case ValidMoves.USE_HANDCUFFS:
            if state.handcuffed == True: return True
        
        case ValidMoves.USE_MAGNIFYING_GLASS:
            if state.current_shell != None: return True
            if state.live_shells == 0 or state.blank_shells == 0: return True
    
    return False

def item_bonus(items: list):
    bonus = 0
    
    for item in items:
        match item:
            case Items.BEER:
                bonus += 10
            case Items.CIGARETTES:
                bonus += 30
            case Items.HANDCUFFS:
                bonus += 50
            case Items.HAND_SAW:
                bonus += 60
            case Items.MAGNIFYING_GLASS:
                bonus += 90
    
    return bonus

def item_usage_bonus(move: ValidMoves, state: BuckshotRouletteMove):
    match move:
        case ValidMoves.USE_BEER:
            chance_live_loaded = Fraction(state.live_shells, state.live_shells + state.blank_shells)
            if state.current_shell == None and chance_live_loaded < 0.5: return 250
            return 0
        
        case ValidMoves.USE_CIGARETTES:
            health_difference = state.max_health
            health_difference -= state.player_health if state.is_players_turn else state.dealer_health
            return 150 * health_difference
        
        case ValidMoves.USE_HAND_SAW:
            if state.current_shell == "live": return 250
            chance_live_loaded = Fraction(state.live_shells, state.live_shells + state.blank_shells)
            if chance_live_loaded > 0.5: return 100
        
        case ValidMoves.USE_HANDCUFFS:
            if state.live_shells + state.blank_shells == 2: return 250
        
        case ValidMoves.USE_MAGNIFYING_GLASS:
            return 250
    
    return 0

def known_shell_bonus(move: ValidMoves, state: BuckshotRouletteMove):
    bonus = 0
    
    if state.current_shell == "live":
        bonus += 200 * (1 if state.is_players_turn else -1)
        if state.is_players_turn and move != ValidMoves.SHOOT_DEALER: return -INF
        elif (not state.is_players_turn) and move != ValidMoves.SHOOT_PLAYER: return INF
    
    elif state.current_shell == "blank":
        bonus += 100 * (1 if state.is_players_turn else -1)
        if state.is_players_turn and move != ValidMoves.SHOOT_PLAYER: return -INF
        elif (not state.is_players_turn) and move != ValidMoves.SHOOT_DEALER: return INF
    
    elif state.current_shell == None:
        chance_live_loaded = Fraction(state.live_shells, state.live_shells + state.blank_shells)
        
        if state.is_players_turn and move != ValidMoves.SHOOT_DEALER: chance_live_loaded *= -1
        elif (not state.is_players_turn) and move != ValidMoves.SHOOT_PLAYER: chance_live_loaded *= -1
        
        bonus += chance_live_loaded * 100
    
    return bonus

def low_health_penalty(state: BuckshotRouletteMove):
    if state.is_players_turn and state.player_health == 1:
        return 100
    if (not state.is_players_turn) and state.dealer_health == 1:
        return 100

    return 0

def max_or_min(is_players_turn: bool, a, b):
    if a == None: return b
    if b == None: return a
    if is_players_turn: return max(a, b)
    return min(a, b)

def shoot_other_person_bonus(move: ValidMoves, state: BuckshotRouletteMove):
    chance_live_loaded = Fraction(state.live_shells, state.live_shells + state.blank_shells)
    
    if state.current_shell != None or chance_live_loaded < 0.5: return 0
    
    if state.is_players_turn and move == ValidMoves.SHOOT_DEALER:
        return 100 * (state.live_shells - state.blank_shells)
    elif (not state.is_players_turn) and move == ValidMoves.SHOOT_PLAYER:
        return 100 * (state.live_shells - state.blank_shells)
    
    return 0

class Move:
    def __init__(self, move_type, evaluation):
        self.move_type = move_type
        self.evaluation = evaluation
    
    def __str__(self):
        if self.move_type == None: return f"Evaluation: {float(self.evaluation)}"
        return f"Move ({self.move_type}, {float(self.evaluation)})"

class BackshotRoulette:
    def __init__(self):
        self.positions_searched = 0
        self.verbose = False
        self.transposition_table = TranspositionTable(64)
    
    def evaluate(self, move: ValidMoves, state: BuckshotRouletteMove):
        # Evaluate how good the current players position is.
        # Should utilise turn probability, health, item count, knowing shells, etc.
        
        state_eval = 0

        if state.player_health == 0: state_eval = -INF
        elif state.dealer_health == 0: state_eval = INF
        
        if state.live_shells + state.blank_shells != 0:
            state_eval += known_shell_bonus(move, state)
            state_eval += item_usage_bonus(move, state)
            state_eval += shoot_other_person_bonus(move, state)
        
        #state_eval += item_bonus(state.player_items)
        #state_eval -= item_bonus(state.dealer_items)
        
        state_eval += hand_saw_bonus(state)
        state_eval -= low_health_penalty(state)
        
        #state_eval += state.player_health * 100
        #state_eval -= state.dealer_health * 100

        health_difference = Fraction(state.player_health, state.player_health + state.dealer_health)

        state_eval += health_difference * 100

        self.transposition_table.add(state, move, state_eval)

        state_eval *= state.probabilty

        return state_eval
    
    def search(self, depth: int, state: BuckshotRouletteMove, alpha = -INF, beta = INF, parent_moves = []):
        if self.verbose: print(f"Starting search with depth {depth} on moves {', '.join(convert_move_list(parent_moves))}")
        if 0 in [depth, state.player_health, state.dealer_health, state.live_shells]:
            if len(parent_moves) >= 1:
                last_move = parent_moves[-1]
            else:
                last_move = None

            position_eval = self.evaluate(last_move, state)

            return Move(None, position_eval)
        
        all_moves = state.get_all_moves()
        all_moves = [move for move in all_moves if type(move) != int]
        
        if state.is_players_turn:
            max_eval = -INF
            for move in all_moves:
                possible_positions = state.move(move)
                
                if possible_positions == None: continue
                
                for position in possible_positions:
                    if self.transposition_table[state, move] != None:
                        eval = self.transposition_table[state, move]
                        eval *= position.probabilty
                    else:
                        eval = self.search(depth - 1, position, alpha, beta, parent_moves + [move]).evaluation
                    
                    if eval > max_eval:
                        max_eval = eval
                        best_move = move
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            
                if beta <= alpha:
                    break
            
            self.positions_searched += 1
            return Move(best_move, max_eval)

        else:
            min_eval = INF
            for move in all_moves:
                possible_positions = state.move(move)
                
                if possible_positions == None: continue
                
                for position in possible_positions:
                    if self.transposition_table[state, move] != None:
                        eval = self.transposition_table[state, move]
                        eval *= position.probabilty
                    else:
                        eval = self.search(depth - 1, position, alpha, beta, parent_moves + [move]).evaluation
                    
                    if eval < min_eval:
                        min_eval = eval
                        best_move = move
                    beta = min(beta, eval)
                    
                    if beta <= alpha:
                        break
            
                if beta <= alpha:
                    break
            
            self.positions_searched += 1
            return Move(best_move, min_eval)