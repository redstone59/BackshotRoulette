from backshot import *
import time

bot = BackshotRoulette()

position = BuckshotRouletteMove(True, 4, 4, 4, 2, 3, 
                                [Items.HANDCUFFS, Items.HANDCUFFS, Items.HANDCUFFS, Items.CIGARETTES, Items.HANDCUFFS, Items.HANDCUFFS, Items.HANDCUFFS, Items.HANDCUFFS],
                                [Items.BEER, Items.HAND_SAW, Items.HAND_SAW, Items.CIGARETTES, Items.HAND_SAW, Items.CIGARETTES])

for depth in range (10):
    start_time = time.time()
    print("Starting search with depth", depth)
    print(bot.search(depth, position))
    print(f"Found in {time.time() - start_time} seconds.")