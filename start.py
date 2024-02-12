from backshot import *
import time

bot = BackshotRoulette()

position = BuckshotRouletteMove(True,   # player's turn?
                                3, 3, 3, # health
                                4, 4,    # live / blank
                                [Items.CIGARETTES, Items.HAND_SAW],
                                [Items.MAGNIFYING_GLASS, Items.BEER, Items.HANDCUFFS, Items.MAGNIFYING_GLASS, Items.CIGARETTES])

position.current_shell = None

max_depth = 15
start_time = time.time()
for depth in range(1, max_depth):
    print("Starting search with depth", depth)
    print(bot.search(depth, position))
print(f"Searched {bot.positions_searched} positions in {time.time() - start_time} seconds.\a")