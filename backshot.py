from roulette import *

class BackshotRoulette:
    def __init__(self):
        pass
    
    def evaluate(self, state: BuckshotRouletteMove):
        # Evaluate how good the current players position is.
        # Should utilise turn probability, health, item count, knowing shells, etc.

        state_eval = 0

        if state.current_shell != None: state_eval += 1
        

        state_eval *= state.probabilty

        return state.dealer_health
    
    def search(self, depth: int, state: BuckshotRouletteMove):
        # Should return the best move for any given position. Use recursion and alpha-beta pruning and whatever.
        # Basically, create a tree of every possible move that can be done, evaluate, and select the best move.

        # TODO: alpha-beta pruning

        if depth == 0: return self.evaluate(state)
        
        all_moves = state.get_all_moves()
        best_move = None
        best_eval = None

        for move in all_moves:
            move = self.search(depth - 1, move)
            eval = self.evaluate(move)
            
            if eval > best_eval:
                best_move = move
                best_eval = eval
        
        return best_move