from roulette import *

class BackshotRoulette:
    def __init__(self):
        pass
    
    def evaluate(self, state: BuckshotRouletteMove):
        # Evaluate how good the current players position is.
        # Should utilise turn probability, health, item count, knowing shells, etc.
        pass
    
    def search(self):
        # Should return the best move for any given position. Use recursion and alpha-beta pruning and whatever.
        # Basically, create a tree of every possible move that can be done, evaluate, and select the best move.
        pass