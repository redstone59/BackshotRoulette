import sys

class Transposition:
    def __init__(self, evaluation, depth: int):
        self.evaluation = evaluation
        self.depth = depth

class TranspositionTable:
    def __init__(self, max_mibibytes: int | float):
        self.transposition_dict = {}
        self.max_size = max_mibibytes * 2 ** 20
    
    def add(self, state, move, transposition: Transposition):
        self.transposition_dict[state, move] = transposition
        if sys.getsizeof(self.transposition_dict) >= self.max_size:
            print("culling")
            self.cull()

    def cull(self):
        while sys.getsizeof(self.transposition_dict) >= self.max_size:
            first_key = list(self.transposition_dict.keys())[0]
            self.transposition_dict.pop(first_key)

    def get(self, state, move) -> Transposition:
        if (state, move) not in self.transposition_dict: return None
        return self.transposition_dict[state, move]

    def __contains__(self, key_tuple):
        return key_tuple in self.transposition_dict

    def __getitem__(self, key_tuple) -> Transposition:
        if len(key_tuple) != 2: raise KeyError("Transpositions take only 2 arguments: state and move")
        return self.get(*key_tuple)
    
    def __setitem__(self, key_tuple, transposition: Transposition):
        if len(key_tuple) != 2: raise KeyError("Transpositions take only 2 arguments: state and move")
        self.add(*key_tuple, transposition)