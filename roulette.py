from enum import *
from mpmath import *

class ValidMoves(Enum):
    SHOOT_DEALER = 0
    SHOOT_PLAYER = 1
    USE_HANDCUFFS = 2
    USE_HAND_SAW = 3
    USE_CIGARETTES = 4
    USE_BEER = 5
    USE_MAGNIFYING_GLASS = 6

class Items(Enum):
    HANDCUFFS = 0
    HAND_SAW = 1
    CIGARETTES = 2
    BEER = 3
    MAGNIFYING_GLASS = 4

class InvalidMoveError(Exception):
    pass

class BuckshotRouletteMove:
    def __init__(self, 
                 is_players_turn: bool, 
                 max_health: int, 
                 dealer_health: int, 
                 player_health: int, 
                 live_shells: int, 
                 blank_shells: int, 
                 dealer_items = [], 
                 player_items = []
                 ):
        
        self.probabilty = mpf(1.00)
        
        self.live_shells = live_shells
        self.blank_shells = blank_shells
        
        self.is_players_turn = is_players_turn
        self.handcuffed = False
        self.gun_is_sawed = False
        self.current_shell = None
        
        self.max_health = max_health
        self.dealer_health = dealer_health
        self.player_health = player_health
        
        self.dealer_items = dealer_items
        self.player_items = player_items
    
    def deep_copy(self):
        return BuckshotRouletteMove(self.is_players_turn,
                                    self.max_health,
                                    self.dealer_health,
                                    self.player_health,
                                    self.live_shells,
                                    self.blank_shells,
                                    self.dealer_items,
                                    self.player_items)
    
    def get_all_moves(self):
        all_moves = [ValidMoves.SHOOT_DEALER, ValidMoves.SHOOT_PLAYER]
        current_items = self.player_items if self.is_players_turn else self.dealer_items
        
        for item in current_items:
            match item:
                case Items.HANDCUFFS:
                    all_moves += [ValidMoves.USE_HANDCUFFS]
                
                case Items.HAND_SAW:
                    all_moves += [ValidMoves.USE_HAND_SAW]
                
                case Items.CIGARETTES:
                    all_moves += [ValidMoves.USE_CIGARETTES]
                
                case Items.BEER:
                    all_moves += [ValidMoves.USE_BEER]
                
                case Items.MAGNIFYING_GLASS:
                    all_moves += [ValidMoves.USE_MAGNIFYING_GLASS]
        
        return all_moves
    
    def move(self, move: ValidMoves):
        if move not in self.get_all_moves(): 
            error_message = f"Move {move} not possible in position\n{self}"
            raise InvalidMoveError(error_message)
        
        next_move = self.deep_copy()
        
        if self.live_shells + self.blank_shells == 0:
            live_probability = 0
        else:
            live_probability = self.live_shells / (self.live_shells + self.blank_shells)
            
        blank_probability = 1 - live_probability # Since live_probability + blank_probability must equal 1
        
        live_move = self.deep_copy()
        live_move.probabilty *= live_probability
        live_move.live_shells = max(0, live_move.live_shells - 1)
        
        blank_move = self.deep_copy()
        blank_move.probabilty *= blank_probability
        blank_move.blank_shells = max(0, blank_move.blank_shells - 1)
        
        match move:
            case ValidMoves.SHOOT_DEALER:
                live_move.dealer_health -= 1
                live_move.current_shell = None
                live_move.is_players_turn = False if self.is_players_turn else True # If the player shoots dealer with a live, it is not the players turn. If the dealer shoots themself with a live, it is the players turn.

                blank_move.current_shell = None
                blank_move.is_players_turn = False # If the player shoots the dealer with a blank, it is not the players turn. If the dealer shoots themself with a blank, it is not the players turn.
                
                return live_move, blank_move
            
            case ValidMoves.SHOOT_PLAYER:
                live_move.player_health -= 1
                live_move.current_shell = None
                live_move.is_players_turn = False if self.is_players_turn else True # If the player shoots themself with a live, it is not the players turn. If the dealer shoots the player with a live, it is the players turn.
                
                blank_move.current_shell = None
                blank_move.is_players_turn = True # If the player shoots themself with a blank, it is the players turn. If the dealer shoots the player with a blank, it is the players turn.

                return live_move, blank_move
                
            case ValidMoves.USE_BEER:
                live_move.current_shell = None
                blank_move.current_shell = None
                
                return live_move, blank_move
            
            case ValidMoves.USE_MAGNIFYING_GLASS:
                live_move.current_shell = "live"
                blank_move.current_shell = "blank"
                
                return live_move, blank_move
            
            case ValidMoves.USE_CIGARETTES:
                if self.is_players_turn:
                    next_move.player_health += 1 if next_move.player_health != next_move.max_health else 0
                    next_move.player_items.remove(Items.CIGARETTES)
                else:
                    next_move.dealer_health += 1 if next_move.player_health != next_move.max_health else 0
                    next_move.dealer_items.remove(Items.CIGARETTES)
                
                return next_move,
            
            case ValidMoves.USE_HANDCUFFS:
                if self.handcuffed: return None
                
                if self.is_players_turn:
                    next_move.player_items.remove(Items.HANDCUFFS)
                else:
                    next_move.dealer_items.remove(Items.HANDCUFFS)
                
                next_move.handcuffed = True
                
                return next_move,
                
            case ValidMoves.USE_HAND_SAW:
                if self.gun_is_sawed: return None
                
                if self.is_players_turn:
                    next_move.player_items.remove(Items.HAND_SAW)
                else:
                    next_move.dealer_items.remove(Items.HAND_SAW)
                
                next_move.gun_is_sawed = True
                
                return next_move,
    
    def __str__(self):
        return f"""Buckshot Roulette Move

Turn: {"Player" if self.is_players_turn else "Dealer"}
Turn probability: {self.probabilty}

Number of live shells: {self.live_shells}
Number of blank shells: {self.blank_shells}

Handcuffed? {"Yes" if self.handcuffed else "No"}
Sawed gun? {"Yes" if self.gun_is_sawed else "No"}
Current shell? {"Unknown" if self.current_shell == None else self.current_shell}

Player's Health: {self.player_health} / {self.max_health}
Player's Items: {self.player_items}

Dealer's Health: {self.dealer_health} / {self.max_health}
Dealer's Items: {self.dealer_items}
"""