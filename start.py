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

def idiot_input(prompt: object = "", condition = lambda x: 1):
    inputter_is_idiot = True
    
    while inputter_is_idiot:
        var = input(prompt)
        if condition(var): return var

IS_DIGIT_STRING = lambda x: x.isdigit() if type(x) == str else False

is_players_turn = input("Is it the players turn? (Y/N) ").lower().startswith("y")

max_health = int(idiot_input("Maximum health? ", IS_DIGIT_STRING))
dealer_health = int(idiot_input("Dealer's health? ", IS_DIGIT_STRING))
player_health = int(idiot_input("Player's health? ", IS_DIGIT_STRING))

lives = int(idiot_input("# live shells? ", IS_DIGIT_STRING))
blanks = int(idiot_input("# blank shells? ", IS_DIGIT_STRING))

print("Item Key: [H]andcuffs, Hand [S]aw, [C]igarettes, [B]eer, [M]agnifying Glass")

dealer_items = string_to_item(idiot_input("Dealer's items? ", lambda x: len(x) <= 8))
player_items = string_to_item(idiot_input("Player's items? ", lambda x: len(x) <= 8))

current_shell = input("Current shell? ('live', 'blank', leave empty for unknown) ").lower()

if current_shell.startswith("l"):
    current_shell = "live"
elif current_shell.startswith("b"):
    current_shell = "blank"
else:
    current_shell = None

handcuffed = int(idiot_input("Is the other player handcuffed? (0 - No, 1 - Has already skipped turn, 2 - Has not skipped turn) ", lambda x: IS_DIGIT_STRING(x) and x in ["0", "1", "2"]))
sawed = input("Is the gun sawed? (Y/N) ").lower().startswith("y")

position = BuckshotRouletteMove(is_players_turn,
                                max_health, dealer_health, player_health,
                                lives, blanks,
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