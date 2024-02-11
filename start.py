from backshot import *
import time

bot = BackshotRoulette()

position = BuckshotRouletteMove(True,   # player's turn?
                                3, 3, 3, # health
                                4, 4,    # live / blank
                                [],
                                [Items.MAGNIFYING_GLASS, Items.MAGNIFYING_GLASS, Items.HANDCUFFS, Items.BEER, Items.MAGNIFYING_GLASS, Items.CIGARETTES])

position.current_shell = None

depth = 7

start_time = time.time()
print("Starting search with depth", depth)
print(bot.search(depth, position))
print(f"Searched {bot.positions_searched} positions in {time.time() - start_time} seconds.\a")