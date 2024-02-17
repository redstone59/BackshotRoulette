from backshot import *
import time

bot = BackshotRoulette()

def string_to_item(item_string: str):
    item_string = item_string.lower()
    items = []
    
    for char in item_string:
        match char:
            case "h":
                items += [Items.HANDCUFFS]
            case "s":
                items += [Items.HAND_SAW]
            case "c":
                items += [Items.CIGARETTES]
            case "b":
                items += [Items.BEER]
            case "m":
                items += [Items.MAGNIFYING_GLASS]
    
    return items
        

inputter_is_idiot = True

is_players_turn = input("Is it the players turn? (Y/N) ").lower().startswith("y")

while inputter_is_idiot:
    max_health = input("Maximum health? ")
    if max_health.isdigit():
        max_health = int(max_health)
        inputter_is_idiot = False

inputter_is_idiot = True

while inputter_is_idiot:
    dealer_health = input("Dealer's health? ")
    if dealer_health.isdigit():
        dealer_health = int(dealer_health)
        inputter_is_idiot = False

inputter_is_idiot = True

while inputter_is_idiot:
    player_health = input("Player's health? ")
    if player_health.isdigit():
        player_health = int(player_health)
        inputter_is_idiot = False

inputter_is_idiot = True

while inputter_is_idiot:
    lives = input("# live shells? ")
    if lives.isdigit():
        lives = int(lives)
        inputter_is_idiot = False

inputter_is_idiot = True

while inputter_is_idiot:
    blanks = input("# blank shells? ")
    if blanks.isdigit():
        blanks = int(blanks)
        inputter_is_idiot = False

print("Item Key: [H]andcuffs, Hand [S]aw, [C]igarettes, [B]eer, [M]agnifying Glass")

inputter_is_idiot = True

while inputter_is_idiot:
    dealer_items = input("Dealer items? ")
    if len(dealer_items) <= 8:
        dealer_items = string_to_item(dealer_items)
        inputter_is_idiot = False

inputter_is_idiot = True

while inputter_is_idiot:
    player_items = input("Player items? ")
    if len(player_items) <= 8:
        player_items = string_to_item(player_items)
        inputter_is_idiot = False

inputter_is_idiot = True

while inputter_is_idiot:
    current_shell = input("Current shell? ('live', 'blank', leave empty for unknown) ").lower()
    if current_shell.startswith("l"):
        current_shell = "live"
        inputter_is_idiot = False
    elif current_shell.startswith("b"):
        current_shell = "blank"
        inputter_is_idiot = False

handcuffed = input("Is the other player handcuffed? (Y/N) ").lower().startswith("y")
sawed = input("Is the gun sawed? (Y/N) ").lower().startswith("y")

position = BuckshotRouletteMove(is_players_turn,   # player's turn?
                                max_health, dealer_health, player_health, # health
                                lives, blanks,    # live / blank
                                dealer_items,
                                player_items)

position.current_shell = current_shell
position.handcuffed = handcuffed
position.gun_is_sawed = sawed

max_depth = 18

start_time = time.time()

for depth in range (1, max_depth + 1):
    depth_start_time = time.time()
    bot.max_depth = depth
    
    print("Starting search with depth", depth)
    print(bot.search(depth, position))
    print(f"Searched {bot.positions_searched} positions in {time.time() - depth_start_time} seconds.\a")

print(f"Searched {bot.positions_searched} positions in {time.time() - start_time} seconds.\a")