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

def obvious_move_exists(state: BuckshotRouletteMove):
    if state.is_players_turn:
        current_items = state.player_items
        current_health = state.player_health
        shoot_other_player = ValidMoves.SHOOT_DEALER
        shoot_self = ValidMoves.SHOOT_PLAYER
    else:
        current_items = state.dealer_items
        current_health = state.dealer_health
        shoot_other_player = ValidMoves.SHOOT_PLAYER
        shoot_self = ValidMoves.SHOOT_DEALER
    
    # Force shooting other player if the known shell is live.
    if state.current_shell == "live":
        if Items.HAND_SAW in current_items:
            return ValidMoves.USE_HAND_SAW
        else:
            return shoot_other_player
    
    # Force shooting self if the known shell is blank.
    if state.current_shell == "blank":
        return shoot_self
    
    # Force magnifying glass usage if the shell isn't known.
    unknown_shell = state.current_shell == None
    one_of_each_shell = 0 not in [state.live_shells, state.blank_shells]
    
    if Items.MAGNIFYING_GLASS in current_items and unknown_shell and one_of_each_shell:
        return ValidMoves.USE_MAGNIFYING_GLASS
    
    # Force cigarette usage if not at max health.
    if Items.CIGARETTES in current_items and current_health != state.max_health:
        return ValidMoves.USE_CIGARETTES
    
    # Force handcuff usage if there's only one blank shell left. (Force a guaranteed shot.)
    if Items.HANDCUFFS in current_items and state.blank_shells == 1:
        return ValidMoves.USE_HANDCUFFS
    
    return None

def items_to_string(item_list: list[Items]):
    resultant = []

    for item in item_list:
        match item:
            case Items.HANDCUFFS:
                resultant += ["h"]
            case Items.HAND_SAW:
                resultant += ["s"]
            case Items.CIGARETTES:
                resultant += ["c"]
            case Items.BEER:
                resultant += ["b"]
            case Items.MAGNIFYING_GLASS:
                resultant += ["m"]
    
    resultant.sort()
    return "".join(resultant)

def state_to_key(state: BuckshotRouletteMove):
    """
    Turns a given `BuckshotRouletteMove` into a key for the transposition table.

    Args:
        state (BuckshotRouletteMove): The position to convert.

    Returns:
        tuple: Transposition table key.
    """

    #
    # position key (should be) a 17 bit number
    # lllbbbPhsccdddppp
    #
    # l, b -> live and blank shells
    # P, h, s, c -> is_players_turn, handcuffed?, sawed gun?, current shell 
    # d, p -> dealer, player health
    #

    key = state.live_shells
    key <<= 3
    key += state.blank_shells
    key <<= 3
    key += state.is_players_turn
    key <<= 1
    key += state.handcuffed
    key <<= 1
    key += state.gun_is_sawed
    key <<= 1
    match state.current_shell:
        case None:
            key += 0b00
        case "live":
            key += 0b01
        case "blank":
            key += 0b10
    key <<= 2
    key += state.dealer_health
    key <<= 3
    key += state.player_health

    return key, items_to_string(state.dealer_items), items_to_string(state.player_items)

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
    
    def evaluate_position(self, move: ValidMoves, state: BuckshotRouletteMove) -> Fraction:
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
    
    def get_ordered_moves(self, state: BuckshotRouletteMove) -> list[ValidMoves]:
        available_moves = state.get_all_moves()
        available_moves = [move for move in available_moves if type(move) != int]
        move_eval_dict = {}
        
        for move in available_moves:
            possible_positions = state.move(move)
            
            if possible_positions == None: continue
            
            best_eval = -INF if state.is_players_turn else INF
            
            for position in possible_positions:
                if position == None: continue
                
                transposition_key = (state, move)

                if transposition_key in self.transposition_table:
                    print("transposition accessed")
                    position_eval = self.transposition_table[transposition_key].evaluation
                else:
                    position_eval = position.probabilty * 10
                
                if state.is_players_turn:
                    best_eval = max(best_eval, position_eval)
                else:
                    best_eval = min(best_eval, position_eval)
            
            move_eval_dict[move] = best_eval
        
        sorted_moves = sorted(move_eval_dict, key = move_eval_dict.get)
        
        return sorted_moves
    
    def search(self, depth: int, state: BuckshotRouletteMove, alpha = -INF, beta = INF, parent_moves = []) -> Move:
        if self.verbose: print(f"Starting search with depth {depth} on moves {', '.join(convert_move_list(parent_moves))}")
        
        if 0 in [depth, state.player_health, state.dealer_health, state.live_shells]:
            if len(parent_moves) >= 1:
                last_move = parent_moves[-1]
            else:
                last_move = None

            position_eval = self.evaluate_position(last_move, state)
            
            transposition = Transposition(position_eval, self.max_depth - shots_taken(parent_moves))
            self.transposition_table.add(state, last_move, transposition)

            return Move(None, position_eval * state.probabilty, [last_move])

        #all_moves = self.get_ordered_moves(state)
        all_moves = state.get_all_moves()
        
        # Force play any obvious moves. Explained in the comments of the function.
        obvious_move = obvious_move_exists(state)
        if obvious_move != None:
            all_moves = [obvious_move]
        
        best_move = ValidMoves.SHOOT_PLAYER if state.is_players_turn else ValidMoves.SHOOT_DEALER
        best_eval = -INF if state.is_players_turn else INF
        best_path = []
        
        for move in all_moves:
            if is_redundant_move(move, state): continue
            
            possible_positions = state.move(move)
            
            if possible_positions == None: continue
            
            for position in possible_positions:
                if position == None: continue
                
                transposition_key = state, move
                current_turn = self.max_depth - shots_taken(parent_moves)
                
                if self.transposition_table[transposition_key] != None and self.transposition_table[transposition_key].depth == current_turn:
                    print("transposition accessed")
                    eval = self.transposition_table[transposition_key].evaluation
                    eval *= position.probabilty
                    path = []
                else:
                    lower_search = self.search(depth - 1, position, alpha, beta, parent_moves + [move])
                    eval = lower_search.evaluation
                    path = lower_search.path
                
                if state.is_players_turn:
                    if eval > best_eval:
                        best_eval = eval
                        best_move = move
                        best_path = path
                    
                    alpha = max(alpha, eval)
                else:
                    if eval < best_eval:
                        best_eval = eval
                        best_move = move
                        best_path = path
                    
                    beta = min(beta, eval)
                
                if beta <= alpha:
                    break
        
            if beta <= alpha:
                break
        
        self.positions_searched += 1
        
        return Move(best_move, best_eval, [best_move] + best_path)