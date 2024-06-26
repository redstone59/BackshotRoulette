from enum import *
from fractions import Fraction
from copy import deepcopy
from typing import Literal

INF = 1000000

class ValidMoves(Enum):
    SHOOT_DEALER = 0
    SHOOT_PLAYER = 1
    USE_HANDCUFFS = 2
    USE_HAND_SAW = 3
    USE_CIGARETTES = 4
    USE_BEER = 5
    USE_MAGNIFYING_GLASS = 6
    USE_ADRENALINE = 7
    USE_INVERTER = 8
    USE_EXPIRED_MEDICINE = 9
    USE_BURNER_PHONE = 10

class Items(Enum):
    HANDCUFFS = 0
    HAND_SAW = 1
    CIGARETTES = 2
    BEER = 3
    MAGNIFYING_GLASS = 4
    ADRENALINE = 5
    INVERTER = 6
    EXPIRED_MEDICINE = 7
    BURNER_PHONE = 8

class LoadedShells:
    def __init__(self, *shells):
        self.shells: list[Literal["live", "blank"] | None] = list(shells)
        self.populate()
    
    def populate(self):
        """
        Ensures `len(self.shells) == 8` by filling blanks with `None`.
        """
        self.shells += [None] * (8 - len(self.shells))
    
    def get_current_shell(self):
        """
        Returns the first shell, the currently loaded shell.
        """
        return self.shells[0]
    
    def set_shell(self, index: int, shell: Literal["live", "blank"] | None = None):
        self.populate()
        if index >= 8: raise KeyError("The gun can only have 8 shells at once.")
        self.shells[index] = shell
    
    def shoot(self):
        """
        Removes and returns the currently loaded shell.
        """
        shot_shell = self.shells.pop(0)
        self.populate()
        return shot_shell

class InvalidMoveError(Exception):
    pass

class BuckshotRouletteMove:
    def __init__(self, 
                 is_players_turn: bool, 
                 max_health: int, 
                 dealer_health: int, 
                 player_health: int, 
                 unknown_live_shells: int, 
                 unknown_blank_shells: int, 
                 dealer_items: list, 
                 player_items: list
                 ):
        
        self.probabilty = Fraction(1, 1)
        
        self.unknown_live_shells = unknown_live_shells
        self.unknown_blank_shells = unknown_blank_shells
        self.loaded_shells = LoadedShells()
        
        self.is_players_turn = is_players_turn
        self.handcuffed = 0 # 0 represents no handcuffs, 1 means handcuffs are on but will go next turn, 2 means handcuffs are on and will skip next turn
        self.gun_is_sawed = False
        self.on_adrenaline = False
        self.inverter_on = False
        
        self.max_health = max_health
        self.dealer_health = dealer_health
        self.player_health = player_health
        
        self.dealer_items = dealer_items
        self.player_items = player_items
    
    def get_current_shell(self):
        return self.loaded_shells.get_current_shell()
    
    def get_all_moves(self):
        all_moves = []
        
        if not self.on_adrenaline:
            current_items = self.player_items if self.is_players_turn else self.dealer_items
        else:
            current_items = self.player_items if not self.is_players_turn else self.dealer_items
        
        if Items.ADRENALINE in current_items: all_moves += [ValidMoves.USE_ADRENALINE]
        if Items.BEER in current_items: all_moves += [ValidMoves.USE_BEER]
        if Items.BURNER_PHONE in current_items: all_moves += [ValidMoves.USE_BURNER_PHONE]
        if Items.CIGARETTES in current_items: all_moves += [ValidMoves.USE_CIGARETTES]
        if Items.EXPIRED_MEDICINE in current_items: all_moves += [ValidMoves.USE_EXPIRED_MEDICINE]
        if Items.HANDCUFFS in current_items and self.handcuffed == 0: all_moves += [ValidMoves.USE_HANDCUFFS]
        if Items.HAND_SAW in current_items and self.gun_is_sawed == False: all_moves += [ValidMoves.USE_HAND_SAW]
        if Items.INVERTER in current_items: all_moves += [ValidMoves.USE_INVERTER]
        if Items.MAGNIFYING_GLASS in current_items: all_moves += [ValidMoves.USE_MAGNIFYING_GLASS]
        
        if not self.on_adrenaline:    
            if self.is_players_turn:
                all_moves += [ValidMoves.SHOOT_DEALER, ValidMoves.SHOOT_PLAYER]
            else:
                all_moves += [ValidMoves.SHOOT_PLAYER, ValidMoves.SHOOT_DEALER]
        
        return all_moves
    
    def generate_live_and_blank_moves(self):
        next_move = deepcopy(self)
        
        if self.unknown_live_shells + self.unknown_blank_shells == 0:
            live_probability = Fraction(0, 1)
        elif self.get_current_shell() == "live":
            live_probability = Fraction(1, 1)
        else:
            live_probability = Fraction(self.unknown_live_shells, self.unknown_live_shells + self.unknown_blank_shells)
            
        blank_probability = 1 - live_probability # Since live_probability + blank_probability must equal 1
        
        live_move = deepcopy(self)
        live_move.probabilty *= live_probability
        live_move.unknown_live_shells = max(0, live_move.unknown_live_shells - 1)
        
        blank_move = deepcopy(self)
        blank_move.probabilty *= blank_probability
        blank_move.unknown_blank_shells = max(0, blank_move.unknown_blank_shells - 1)
        
        return next_move, live_move, blank_move
    
    def move(self, move: ValidMoves):
        if move not in self.get_all_moves(): 
            error_message = f"Move {move} not possible in position\n---\n{self}\n---"
            raise InvalidMoveError(error_message)
        
        next_move, live_move, blank_move = self.generate_live_and_blank_moves()
        
        match move:
            case ValidMoves.SHOOT_DEALER:
                live_move.dealer_health -= 1 if not self.gun_is_sawed else 2
                live_move.dealer_health = max(0, live_move.dealer_health)
                live_move.loaded_shells.shoot()
                live_move.gun_is_sawed = False
                
                if self.handcuffed > 0: # Decrement turns left until next handcuff
                    live_move.handcuffed -= 1
                    blank_move.handcuffed -= 1
                else:
                    live_move.is_players_turn = False if self.is_players_turn else True # If the player shoots dealer with a live, it is not the players turn. If the dealer shoots themself with a live, it is the players turn.
                
                blank_move.loaded_shells.shoot()
                blank_move.is_players_turn = False # If the player shoots the dealer with a blank, it is not the players turn. If the dealer shoots themself with a blank, it is not the players turn.
                blank_move.gun_is_sawed = False
                
                return live_move, blank_move
            
            case ValidMoves.SHOOT_PLAYER:
                live_move.player_health -= 1 if not self.gun_is_sawed else 2
                live_move.player_health = max(0, live_move.player_health)
                live_move.loaded_shells.shoot()
                live_move.gun_is_sawed = False
                
                if self.handcuffed > 0: # Decrement turns left until next handcuff
                    live_move.handcuffed -= 1
                    blank_move.handcuffed -= 1
                else:
                    live_move.is_players_turn = False if self.is_players_turn else True # If the player shoots themself with a live, it is not the players turn. If the dealer shoots the player with a live, it is the players turn.
                
                blank_move.loaded_shells.shoot()
                blank_move.is_players_turn = True # If the player shoots themself with a blank, it is the players turn. If the dealer shoots the player with a blank, it is the players turn.
                blank_move.gun_is_sawed = False

                return live_move, blank_move
                
            case ValidMoves.USE_BEER:
                # LoadedShells.shoot() just removes the first bullet. I should probably rename that.
                live_move.loaded_shells.shoot()
                blank_move.loaded_shells.shoot()
                
                self.remove_item(live_move, Items.MAGNIFYING_GLASS)
                self.remove_item(blank_move, Items.MAGNIFYING_GLASS)
                
                return live_move, blank_move
            
            case ValidMoves.USE_MAGNIFYING_GLASS:
                live_move.loaded_shells.set_shell(0, "live")
                blank_move.loaded_shells.set_shell(0, "blank")
                
                self.remove_item(live_move, Items.MAGNIFYING_GLASS)
                self.remove_item(blank_move, Items.MAGNIFYING_GLASS)
                
                return live_move, blank_move
            
            case ValidMoves.USE_CIGARETTES:
                if self.is_players_turn:
                    next_move.player_health += 1
                    next_move.player_health = max(self.max_health, next_move.player_health)
                else:
                    next_move.dealer_health += 1
                    next_move.dealer_health = max(self.max_health, next_move.dealer_health)
                
                self.remove_item(next_move, Items.CIGARETTES)
                
                return next_move,
            
            case ValidMoves.USE_HANDCUFFS:
                if self.handcuffed: return None
                
                self.remove_item(next_move, Items.HANDCUFFS)
                
                next_move.handcuffed = 2
                
                return next_move,
                
            case ValidMoves.USE_HAND_SAW:
                if self.gun_is_sawed: return None
                
                self.remove_item(next_move, Items.HAND_SAW)
                
                next_move.gun_is_sawed = True
                
                return next_move,

            case ValidMoves.USE_ADRENALINE:
                if self.on_adrenaline: return None
                
                self.remove_item(next_move, Items.ADRENALINE)
                
                next_move.on_adrenaline = True
                
                return next_move,
            
            case ValidMoves.USE_BURNER_PHONE:
                total_shells = self.unknown_live_shells + self.unknown_blank_shells
                possible_outcomes = []
                
                for i in range(0, total_shells):
                    possible_live_move = deepcopy(self)
                    possible_blank_move = deepcopy(self)
                    
                    shell_probability = Fraction(1, total_shells)
                    
                    possible_live_move.loaded_shells.set_shell(i, "live")
                    possible_live_move.probabilty *= shell_probability
                    possible_blank_move.loaded_shells.set_shell(i, "blank")
                    possible_blank_move.probabilty *= shell_probability
                    
                    self.remove_item(possible_live_move, Items.BURNER_PHONE)
                    self.remove_item(possible_blank_move, Items.BURNER_PHONE)
                    
                    possible_outcomes += [possible_live_move, possible_blank_move]
                
                return tuple(possible_outcomes)
            
            case ValidMoves.USE_EXPIRED_MEDICINE:
                heal_move = live_move
                heal_move.probabilty = self.probabilty * Fraction(2, 5) # 40% change for 2 charges
                if self.is_players_turn:
                    heal_move.player_health += 2
                    heal_move.player_health = max(self.max_health, heal_move.player_health)
                else:
                    heal_move.dealer_health += 2
                    heal_move.dealer_health = max(self.max_health, heal_move.dealer_health)
                
                bad_move = blank_move
                bad_move.probabilty = self.probabilty * Fraction(3, 5)
                if self.is_players_turn:
                    heal_move.player_health -= 1
                    bad_move.player_health = min(0, bad_move.player_health)
                else:
                    heal_move.dealer_health -= 1
                    bad_move.dealer_health = min(0, bad_move.dealer_health)
                
                self.remove_item(heal_move, Items.EXPIRED_MEDICINE)
                self.remove_item(bad_move, Items.EXPIRED_MEDICINE)
                
                return heal_move, bad_move
            
            case ValidMoves.USE_INVERTER:
                if self.inverter_on: return None

                next_move.inverter_on = True
                
                self.remove_item(next_move, Items.INVERTER)
                
                return next_move,
    
    def remove_item(self, next_move, item: Items): # Hate how I can't type hint BuckshotRouletteMove for next_move here.
        # The below truth table shows why the conditional is why it is.
        # 
        #  is_players_turn | on_adrenaline | items getting removed |
        # -----------------+---------------+-----------------------+
        #            false |         false | dealer                |
        #            false |          true | player                |
        #             true |         false | player                |
        #             true |          true | dealer                |
        # -----------------+---------------+-----------------------+
        
        if self.is_players_turn != self.on_adrenaline:
            next_move.player_items.remove(item)
        else:
            next_move.dealer_items.remove(item)
        
        next_move.on_adrenaline = False
    
    def __str__(self):
        return f"""Buckshot Roulette Move

Turn: {"Player" if self.is_players_turn else "Dealer"}
Turn probability: {self.probabilty}

Number of live shells: {self.unknown_live_shells}
Number of blank shells: {self.unknown_blank_shells}

Handcuffed? {"Yes" if self.handcuffed else "No"}
Sawed gun? {"Yes" if self.gun_is_sawed else "No"}
Current shell? {"Unknown" if self.get_current_shell == None else self.get_current_shell}

Player's Health: {self.player_health} / {self.max_health}
Player's Items: {self.player_items}

Dealer's Health: {self.dealer_health} / {self.max_health}
Dealer's Items: {self.dealer_items}
"""