from roulette import *
from bonuses import *
from transposition_tables import *
from itertools import permutations

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
            case ValidMoves.USE_ADRENALINE:
                resultant += ["adrenaline"]
            case ValidMoves.USE_BURNER_PHONE:
                resultant += ["phone"]
            case ValidMoves.USE_EXPIRED_MEDICINE:
                resultant += ["medicine"]
            case ValidMoves.USE_INVERTER:
                resultant += ["inverter"]
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
            sawed_gun_with_dealer = not state.is_players_turn and state.gun_is_sawed
            blank_shell_with_player = state.is_players_turn and state.get_current_shell() == "blank"
            live_shell_with_dealer = not state.is_players_turn and state.get_current_shell() == "live"
            
            return sawed_gun_with_dealer or blank_shell_with_player or live_shell_with_dealer
        
        case ValidMoves.SHOOT_PLAYER:
            sawed_gun_with_player = state.is_players_turn and state.gun_is_sawed
            blank_shell_with_dealer = not state.is_players_turn and state.get_current_shell() == "blank"
            live_shell_with_player = state.is_players_turn and state.get_current_shell() == "live"
            
            return sawed_gun_with_player or blank_shell_with_dealer, live_shell_with_player

        case ValidMoves.USE_BEER:
            known_shell = state.get_current_shell() != None
            all_one_type_of_shell = 0 in [state.unknown_live_shells, state.unknown_blank_shells]
            
            return known_shell or all_one_type_of_shell
        
        case ValidMoves.USE_CIGARETTES:
            other_players_health = state.dealer_health if state.is_players_turn else state.player_health
            
            return other_players_health == state.max_health
        
        case ValidMoves.USE_HAND_SAW:
            no_live_shells = state.unknown_live_shells == 0
            other_players_health = state.dealer_health if state.is_players_turn else state.player_health
            
            return no_live_shells or other_players_health == 1
        
        case ValidMoves.USE_HANDCUFFS:
            return state.handcuffed > 0
        
        case ValidMoves.USE_MAGNIFYING_GLASS:
            known_shell = state.get_current_shell() != None
            all_one_type_of_shell = 0 in [state.unknown_live_shells, state.unknown_blank_shells]
            
            return known_shell or all_one_type_of_shell
        
        case ValidMoves.USE_ADRENALINE:
            other_players_items = state.dealer_items if state.is_players_turn else state.player_items
            if other_players_items == []: return True
        
        case ValidMoves.USE_BURNER_PHONE: # Could | with ValidMoves.USE_BEER
            known_shell = state.get_current_shell() != None
            all_one_type_of_shell = 0 in [state.unknown_live_shells, state.unknown_blank_shells]
            
            return known_shell or all_one_type_of_shell
        
        case ValidMoves.USE_EXPIRED_MEDICINE:
            current_players_health = state.player_health if state.is_players_turn else state.dealer_health
            current_players_items = state.player_items if state.is_players_turn else state.dealer_items
            
            has_cigarettes = Items.CIGARETTES in current_players_items and current_players_health == state.max_health - 1
            at_max_health = current_players_health == state.max_health
            
            return at_max_health or (has_cigarettes and current_players_health - state.max_health <= 1)
        
        case ValidMoves.USE_INVERTER:
            return state.get_current_shell() == "live"

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
    
    # Force shooting other player if the known shell is live and the other player has more than 1 health.
    other_players_health = state.dealer_health if state.is_players_turn else state.dealer_health
    is_definitely_live = state.get_current_shell() == "live" or state.unknown_blank_shells == 0
    can_use_hand_saw = not state.gun_is_sawed and Items.HAND_SAW in current_items
    
    if is_definitely_live:
        if other_players_health >= 2 and can_use_hand_saw:
            return ValidMoves.USE_HAND_SAW
        else:
            return shoot_other_player
    
    # Force shooting self if the known shell is blank.
    is_definitely_blank = state.get_current_shell() == "blank" or state.unknown_live_shells == 0
    
    if is_definitely_blank:
        return shoot_self
    
    # Force magnifying glass usage if the shell isn't known.
    has_magnifying_glass = Items.MAGNIFYING_GLASS in current_items
    unknown_shell = state.get_current_shell() == None
    one_of_each_shell = 0 not in [state.unknown_live_shells, state.unknown_blank_shells]
    
    if has_magnifying_glass and unknown_shell and one_of_each_shell:
        return ValidMoves.USE_MAGNIFYING_GLASS
    
    # Force cigarette usage if not at max health.
    if Items.CIGARETTES in current_items and current_health != state.max_health:
        return ValidMoves.USE_CIGARETTES
    
    # Force handcuff usage if there's at least one blank shell left. (Force a guaranteed shot. Or two.)
    if Items.HANDCUFFS in current_items and state.unknown_blank_shells <= 1:
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
            case Items.ADRENALINE:
                resultant += ["a"]
            case Items.EXPIRED_MEDICINE:
                resultant += ["e"]
            case Items.BURNER_PHONE:
                resultant += ["f"] # ew.
            case Items.INVERTER:
                resultant += ["i"]
    
    resultant.sort()
    return "".join(resultant)

def shots_taken(move_list: list[ValidMoves]):
    shots = move_list.count(ValidMoves.SHOOT_DEALER)
    shots += move_list.count(ValidMoves.SHOOT_PLAYER)
    return shots

class Move:
    def __init__(self, move_type: ValidMoves, evaluation: int | Fraction, path = []):
        self.move_type = move_type
        self.evaluation = evaluation
        self.path = path
    
    def gui_string(self):
        match self.move_type:
            case ValidMoves.SHOOT_DEALER:
                move = "Shoot Dealer"
            case ValidMoves.SHOOT_PLAYER:
                move = "Shoot Player"
            case ValidMoves.USE_BEER:
                move = "Drink Beer"
            case ValidMoves.USE_CIGARETTES:
                move = "Smoke Cigarettes"
            case ValidMoves.USE_HAND_SAW:
                move = "Use Hand Saw"
            case ValidMoves.USE_HANDCUFFS:
                move = "Use Handcuffs"
            case ValidMoves.USE_MAGNIFYING_GLASS:
                move = "Use Magnifying Glass"
            case ValidMoves.USE_ADRENALINE:
                move = "Use Adrenaline"
            case ValidMoves.USE_BURNER_PHONE:
                move = "Use Burner Phone"
            case ValidMoves.USE_EXPIRED_MEDICINE:
                move = "Use Expired Medicine"
            case ValidMoves.USE_INVERTER:
                move = "Use Inverter"
        
        return f"Best Move: {move}\nEvaluation: {float(self.evaluation)*100:.2f}\nPath: {', '.join(convert_move_list(self.path))}"
    
    def __str__(self):
        if self.move_type == None: return f"Evaluation: {float(self.evaluation)}"
        return f"Move ({self.move_type}, Chance dealer kills player: {float(self.evaluation)*100:.2f}%)\nPath: {', '.join(convert_move_list(self.path))}"

class BackshotRoulette:
    def __init__(self):
        self.positions_searched = 0
        self.max_depth = 0
        
        self.verbose = False
        self.transposition_table = TranspositionTable(64)
    
    def predicted_evaluation(self, move: ValidMoves, state: BuckshotRouletteMove) -> Fraction:
        """
        Estimates a position's evaluation.
        """
        
        state_eval = 0

        if state.player_health == 0: state_eval = -INF
        elif state.dealer_health == 0: state_eval = INF
        
        if state.unknown_live_shells + state.unknown_blank_shells != 0:
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
    
    def evaluate_position(self, state: BuckshotRouletteMove) -> Fraction:   
        if state.is_players_turn:
            # Since it isn't the dealer's turn, we evaluate based on the mean probability that the dealer can kill us on the next turn
            # This is done by calculating the probabilities that the dealer could kill the player after a "bullet modifying move" (shooting, beer)
            
            # Shooting the dealer can result in one less live or one less blank
            # Let L be the number of live shells and B the number of blank shells
            #   1/2(L/(L+B-1) + (L-1)/(L+B-1))
            # = 1/2((L+L-1)/(L+B-1))
            # = (2L-1)/(2*(L+B-1))
            
            denominator = state.unknown_live_shells + state.unknown_blank_shells - 1
            if denominator > 0:
                shoot_dealer_eval = Fraction(2 * state.unknown_live_shells - 1, 2 * denominator)
            else:
                shoot_dealer_eval = Fraction(1, 1)
            
            # This one is trickier to explain.
            # Just, https://cdn.discordapp.com/attachments/1214864872001634374/1216704848293134358/image.png?ex=66015bb1&is=65eee6b1&hm=a3fdd531492b59d0a5802bedaec171791997e8e04553743fb5bcf71589d44b36&
            # Same variable names as last time.
            
            shoot_self_eval = Fraction(1, 1)
            
            for n in range(1, state.unknown_blank_shells):
                denominator = state.unknown_live_shells + state.unknown_blank_shells - n
                
                if denominator > 0:
                    shoot_self_eval += Fraction(state.unknown_live_shells - 1, denominator)
                else:
                    shoot_dealer_eval += Fraction(1, 1)
            
            shoot_self_eval *= Fraction(1, state.unknown_blank_shells) if state.unknown_blank_shells > 0 else Fraction(1, 1)
            
            # Using a beer can lead to four outcomes.
            # 
            #  racking         shooting
            #
            #                     live +- (L-2)/(L+B-2)
            #    live +- (L-1)/(L+B-1) +
            #         |          blank +- (L-1)/(L+B-2)
            # L/(L+B) +
            #         |           live +- (L-1)/(L+B-2)
            #   blank +----- L/(L+B-1) +
            #                    blank +----- L/(L+B-2)
            #
            # Summing the probabilities and dividing by 4 yields the average probability of
            # (4L-3)/(4(L+B-2))
            
            if ValidMoves.USE_BEER in state.get_all_moves():
                denominator = state.unknown_live_shells + state.unknown_blank_shells - 2
                if denominator > 0:
                    use_beer_eval = Fraction(4 * state.unknown_live_shells - 3, 4 * denominator)
                else:
                    use_beer_eval = Fraction(1, 1)
            else:
                if state.unknown_blank_shells > 0:
                    use_beer_eval = Fraction(state.unknown_live_shells, state.unknown_live_shells + state.unknown_blank_shells)
                else:
                    use_beer_eval = Fraction(1, 1)
            
            return min(shoot_dealer_eval, shoot_self_eval, use_beer_eval)
        
        if state.unknown_blank_shells > 0:
            dealer_kill_probability = Fraction(state.unknown_live_shells, state.unknown_live_shells + state.unknown_blank_shells)
        else:
            dealer_kill_probability = Fraction(1, 1)
        
        return dealer_kill_probability
    
    def get_ordered_moves(self, state: BuckshotRouletteMove) -> list[ValidMoves]:
        """
        Returns a list of moves ordered by predicted evaluation or transposition.

        Args:
            state (BuckshotRouletteMove): A given state in Buckshot Roulette.

        Returns:
            list[ValidMoves]: An ordered list of moves, sorted from highest predicted evaluation to lowest.
        """
        available_moves = state.get_all_moves()
        available_moves = [move for move in available_moves if type(move) != int]
        move_eval_dict = {}
        
        for move in available_moves:
            possible_positions = state.move(move)
            
            if possible_positions == None: continue
            
            best_eval = -INF if state.is_players_turn else INF
            
            for position in possible_positions:
                if position == None: continue
                """
                transposition_key = (state, move)

                if transposition_key in self.transposition_table:
                    print("transposition accessed")
                    position_eval = self.transposition_table[transposition_key].evaluation
                else:
                """ 
                position_eval = self.predicted_evaluation(move, position)
                
                if state.is_players_turn:
                    best_eval = max(best_eval, position_eval)
                else:
                    best_eval = min(best_eval, position_eval)
            
            move_eval_dict[move] = best_eval
        
        sorted_moves = sorted(move_eval_dict, key = move_eval_dict.get)
        
        return sorted_moves
    
    def search(self, move_depth: int, state: BuckshotRouletteMove, alpha = -INF, beta = INF, parent_moves = []) -> Move:
        if self.verbose: print(f"Starting search with move_depth {move_depth} on moves {', '.join(convert_move_list(parent_moves))}")
        
        if 0 in [move_depth, state.player_health, state.dealer_health, state.unknown_live_shells]:
            chance_player_lives = 1 - self.evaluate_position(state)
            health_difference = Fraction(state.player_health, state.dealer_health + state.player_health)
            return Move(None, chance_player_lives * health_difference * state.probabilty)

        # Force play any obvious moves, otherwise search all moves ordered by predicted evaluation.
        obvious_move = obvious_move_exists(state)
        if obvious_move != None:
            all_moves = [obvious_move]
        else:
            all_moves = self.get_ordered_moves(state)
        
        best_move = ValidMoves.SHOOT_PLAYER if state.is_players_turn else ValidMoves.SHOOT_DEALER
        best_eval = -INF if state.is_players_turn else INF
        best_path = []
        
        for move in all_moves:
            if obvious_move == None and is_redundant_move(move, state): continue
            try:
                possible_positions = state.move(move)
            except InvalidMoveError:
                continue
            
            if possible_positions == None: continue
            
            for position in possible_positions:
                if position == None: continue
                """
                transposition_key = state, move
                current_turn = self.max_depth - shots_taken(parent_moves)
                
                if self.transposition_table[transposition_key] != None and self.transposition_table[transposition_key].move_depth == current_turn:
                    print("transposition accessed")
                    eval = self.transposition_table[transposition_key].evaluation
                    eval *= position.probabilty
                    path = []
                else: (next 3 lines were indented)
                """
                # Decrement depth on each shot.
                next_depth = move_depth
                if move in [ValidMoves.SHOOT_DEALER, ValidMoves.SHOOT_PLAYER]:
                    next_depth -= 1
                
                lower_search = self.search(next_depth, position, alpha, beta, parent_moves + [move])
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