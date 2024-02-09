from roulette import *

INF = mpf(inf)

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
        chance_live_loaded = state.live_shells / (state.live_shells + state.blank_shells)
        
        if state.is_players_turn and move != ValidMoves.SHOOT_DEALER: chance_live_loaded *= -1
        elif (not state.is_players_turn) and move != ValidMoves.SHOOT_PLAYER: chance_live_loaded *= -1
        
        bonus += chance_live_loaded * 100
    
    return bonus

def max_or_min(is_players_turn: bool, a, b):
    if a == None: return b
    if b == None: return a
    if is_players_turn: return max(a, b)
    return min(a, b)

class Move:
    def __init__(self, move_type, evaluation):
        self.move_type = move_type
        self.evaluation = evaluation
    
    def __str__(self):
        if self.move_type == None: return f"Evaluation: {self.evaluation}"
        return f"Move ({self.move_type}, {self.evaluation})"

class BackshotRoulette:
    def __init__(self):
        pass
    
    def evaluate(self, move: ValidMoves, state: BuckshotRouletteMove):
        # Evaluate how good the current players position is.
        # Should utilise turn probability, health, item count, knowing shells, etc.
        
        state_eval = mpf(0)

        if state.live_shells == 0: return 0 # If there are no more live shells, it is a forced reload.
        
        if state.player_health == 0: state_eval =  -INF
        if state.dealer_health == 0: state_eval = INF
        
        state_eval += known_shell_bonus(move, state)
        state_eval += hand_saw_bonus(state)
        
        state_eval += item_bonus(state.player_items)
        state_eval -= item_bonus(state.dealer_items)
        
        state_eval += state.player_health * 25
        state_eval -= state.dealer_health * 25

        state_eval *= state.probabilty

        return state_eval
    
    def search(self, depth: int, state: BuckshotRouletteMove, alpha = -INF, beta = INF, parent_moves = []):
        if 0 in [depth, state.live_shells, state.dealer_health, state.player_health]:
            if len(parent_moves) >= 1:
                last_move = parent_moves[-1]
            else:
                last_move = None
            
            return Move(None, self.evaluate(last_move, state) * 1 if state.is_players_turn else -1)

        all_moves = state.get_all_moves()
        all_moves = [move for move in all_moves if type(move) != int]
        
        best_move = Move(None, INF * -1 if state.is_players_turn else 1)

        for move in all_moves:
            next_state = state.move(move)
            
            if is_redundant_move(move, state) or next_state == None: continue

            for position in next_state:
                eval = -self.search(depth - 1, position, alpha, beta, parent_moves = parent_moves + [move]).evaluation
                
                if position.is_players_turn:
                    eval *= -1
                    alpha = max(alpha, eval)
                else:
                    beta = min(beta, eval)
                
                if beta <= alpha: break
                
                if max_or_min(position.is_players_turn, eval, best_move.evaluation):
                    best_move = Move(move, eval)
            
            if beta <= alpha: break
    
        return best_move