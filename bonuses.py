from roulette import *

def hand_saw_penalty(state: BuckshotRouletteMove):
    """
    Penalises the current player for having 1 or 2 health when the other player has a hand saw.
    Returns 150 if penalty conditions are met, else it returns 0.
    """
    if state.is_players_turn and Items.HAND_SAW in state.dealer_items and state.player_health <= 2:
        return 150
    
    elif (not state.is_players_turn) and Items.HAND_SAW in state.player_items and state.dealer_health <= 2:
        return 150
    
    return 0

def item_bonus(items: list):
    """
    Returns the sum of the value of every item in `items`. Analogous to material in chess.
    """
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
            if state.get_current_shell() == None and state.live_shells < state.blank_shells: return 250
            return 0
        
        case ValidMoves.USE_CIGARETTES:
            health_difference = state.max_health
            health_difference -= state.player_health if state.is_players_turn else state.dealer_health
            return 150 * health_difference
        
        case ValidMoves.USE_HAND_SAW:
            if state.get_current_shell() == "live": return 250
            if state.live_shells >= state.blank_shells: return 100
        
        case ValidMoves.USE_HANDCUFFS:
            if state.live_shells + state.blank_shells == 2: return 250
            return 100
        
        case ValidMoves.USE_MAGNIFYING_GLASS:
            return 2500
    
    return 0

def known_shell_bonus(move: ValidMoves, state: BuckshotRouletteMove):
    bonus = 0
    
    if state.get_current_shell() == "live":
        bonus += 200 * (1 if state.is_players_turn else -1)
        if state.is_players_turn and move != ValidMoves.SHOOT_DEALER: return -INF
        elif (not state.is_players_turn) and move != ValidMoves.SHOOT_PLAYER: return INF
    
    elif state.get_current_shell() == "blank":
        bonus += 100 * (1 if state.is_players_turn else -1)
        if state.is_players_turn and move != ValidMoves.SHOOT_PLAYER: return -INF
        elif (not state.is_players_turn) and move != ValidMoves.SHOOT_DEALER: return INF
    
    elif state.get_current_shell() == None:
        chance_live_loaded = Fraction(state.live_shells, state.live_shells + state.blank_shells)
        
        if state.is_players_turn and move == ValidMoves.SHOOT_DEALER: chance_live_loaded *= 100
        elif (not state.is_players_turn) and move == ValidMoves.SHOOT_PLAYER: chance_live_loaded *= 100
        
        bonus += chance_live_loaded
    
    return bonus

def low_health_penalty(state: BuckshotRouletteMove):
    """
    Penalises for having 1 health left.
    Returns 100 if the current player in the `state` has 1 health.
    Returns 0 otherwise.
    """
    if state.is_players_turn and state.player_health == 1:
        return 100
    if (not state.is_players_turn) and state.dealer_health == 1:
        return 100

    return 0

def shoot_other_person_bonus(move: ValidMoves, state: BuckshotRouletteMove):
    chance_live_loaded = Fraction(state.live_shells, state.live_shells + state.blank_shells)
    
    if state.get_current_shell() != None or chance_live_loaded < 0.5: return 0
    
    if state.is_players_turn and move == ValidMoves.SHOOT_DEALER:
        return 100 * (state.live_shells - state.blank_shells)
    elif (not state.is_players_turn) and move == ValidMoves.SHOOT_PLAYER:
        return 100 * (state.live_shells - state.blank_shells)
    
    return 0