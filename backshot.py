from roulette import *

class BackshotRoulette:
    def __init__(self):
        pass
    
    def evaluate(self, state: BuckshotRouletteMove):
        # Evaluate how good the current players position is.
        # Should utilise turn probability, health, item count, knowing shells, etc.

        if state.live_shells == 0: return 0 # If there are no more live shells, it is a forced reload.
        
        state_eval = 0

        if state.current_shell != None: state_eval += 10
        
        chance_live_loaded = state.live_shells / (state.live_shells + state.blank_shells)
        state_eval += chance_live_loaded * 5
        
        state_eval += state.player_health * 25
        state_eval -= state.dealer_health * 25

        state_eval *= state.probabilty

        return state.dealer_health
    
    def search(self, depth: int, state: BuckshotRouletteMove):
        # Should return the best move for any given position. Use recursion and alpha-beta pruning and whatever.
        # Basically, create a tree of every possible move that can be done, evaluate, and select the best move.

        # TODO: alpha-beta pruning

        if depth == 0: return self.evaluate(state)
        
        all_moves = state.get_all_moves()
        all_moves = [move for move in all_moves if move != None]
        
        best_move = None
        best_eval = None

        for move in all_moves:
            next_state = state.move(move)
            
            if next_state == None: continue
            
            move = self.search(depth - 1, next_state)
            eval = self.evaluate(next_state)
            
            if best_eval == None or eval > best_eval:
                best_move = move
                best_eval = eval
        
        return best_move