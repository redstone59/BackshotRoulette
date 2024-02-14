from roulette import *
from bonuses import *
from transposition_tables import *

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
            if (not state.is_players_turn) and (state.gun_is_sawed or state.live_shells >= state.blank_shells): return True
            if state.is_players_turn and state.current_shell == "blank": return True
            if (not state.is_players_turn) and state.current_shell == "live": return True
        
        case ValidMoves.SHOOT_PLAYER:
            if state.is_players_turn and (state.gun_is_sawed or state.live_shells >= state.blank_shells): return True
            if (not state.is_players_turn) and state.current_shell == "blank": return True
            if state.is_players_turn and state.current_shell == "live": return True

        case ValidMoves.USE_BEER:
            if state.current_shell != None: return True
            if 0 in [state.live_shells, state.blank_shells]: return True
        
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

def state_to_key(state: BuckshotRouletteMove):
    """
    Turns a given `BuckshotRouletteMove` into a key for the transposition table.

    Args:
        state (BuckshotRouletteMove): The position to convert.

    Returns:
        tuple: Transposition table key.
    """
    return (state.live_shells, state.blank_shells,
            state.is_players_turn,
            state.handcuffed, state.gun_is_sawed, state.current_shell,
            state.dealer_health, state.player_health,
            state.dealer_items, state.player_items)

def shots_taken(move_list: list[ValidMoves]):
    shots = move_list.count(ValidMoves.SHOOT_DEALER)
    shots += move_list.count(ValidMoves.SHOOT_PLAYER)
    return shots

class Move:
    def __init__(self, move_type: ValidMoves, evaluation: int | Fraction, path = []):
        self.move_type = move_type
        self.evaluation = evaluation
        self.path = path
    
    def __str__(self):
        if self.move_type == None: return f"Evaluation: {float(self.evaluation)}"
        return f"Move ({self.move_type}, {float(self.evaluation)})\nPath: {', '.join(convert_move_list(self.path))}"

class BackshotRoulette:
    def __init__(self):
        self.positions_searched = 0
        self.max_depth = 0
        
        self.verbose = False
        self.transposition_table = TranspositionTable(64)
    
    def evaluate_position(self, move: ValidMoves, state: BuckshotRouletteMove):
        # Evaluate how good the current players position is.
        # Should utilise turn probability, health, item count, knowing shells, etc.
        
        state_eval = 0

        if state.player_health == 0: state_eval = -INF
        elif state.dealer_health == 0: state_eval = INF
        
        if state.live_shells + state.blank_shells != 0:
            state_eval += known_shell_bonus(move, state)
            state_eval += shoot_other_person_bonus(move, state)
        
        #state_eval += item_bonus(state.player_items)
        #state_eval -= item_bonus(state.dealer_items)
        state_eval += item_usage_bonus(move, state)
        
        state_eval -= hand_saw_penalty(state)
        state_eval -= low_health_penalty(state)

        health_difference = Fraction(state.player_health, state.player_health + state.dealer_health)
        state_eval += health_difference * 100

        return state_eval
    
    def search(self, depth: int, state: BuckshotRouletteMove, alpha = -INF, beta = INF, parent_moves = []):
        if self.verbose: print(f"Starting search with depth {depth} on moves {', '.join(convert_move_list(parent_moves))}")
        
        if 0 in [depth, state.player_health, state.dealer_health, state.live_shells]:
            if len(parent_moves) >= 1:
                last_move = parent_moves[-1]
            else:
                last_move = None

            position_eval = self.evaluate_position(last_move, state)
            
            transposition = Transposition(position_eval)
            self.transposition_table.add(state, last_move, self.max_depth - shots_taken(parent_moves), transposition)

            return Move(None, position_eval * state.probabilty, [last_move])

        all_moves = state.get_all_moves()
        all_moves = [move for move in all_moves if type(move) != int]
        
        # This looks really gross. Maybe compact into a single function? Or multiple functions? I don't know.
        if (Items.MAGNIFYING_GLASS in (state.player_items if state.is_players_turn else state.dealer_items)) \
           and (state.current_shell == None) \
           and (0 not in [state.live_shells, state.blank_shells]):
            all_moves = [ValidMoves.USE_MAGNIFYING_GLASS]
        
        best_move = ValidMoves.SHOOT_PLAYER if state.is_players_turn else ValidMoves.SHOOT_DEALER
        best_eval = -INF if state.is_players_turn else INF
        
        for move in all_moves:
            if is_redundant_move(move, state): continue
            
            possible_positions = state.move(move)
            
            if possible_positions == None: continue
            
            for position in possible_positions:
                if position == None: continue
                
                transposition_key = state, move, self.max_depth - shots_taken(parent_moves)
                if self.transposition_table[transposition_key] != None:
                    print("transposition accessed")
                    eval = self.transposition_table[transposition_key].evaluation
                    eval *= position.probabilty
                else:
                    lower_search = self.search(depth - 1, position, alpha, beta, parent_moves + [move])
                    eval = lower_search.evaluation
                    path = lower_search.path
                
                if state.is_players_turn:
                    if eval > best_eval:
                        best_eval = eval
                        best_move = move
                    
                    alpha = max(alpha, eval)
                else:
                    if eval < best_eval:
                        best_eval = eval
                        best_move = move
                    
                    beta = min(beta, eval)
                
                if beta <= alpha:
                    break
        
            if beta <= alpha:
                break
        
        self.positions_searched += 1
        
        return Move(best_move, best_eval, [best_move] + path)