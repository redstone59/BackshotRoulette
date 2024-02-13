class Transposition:
    def __init__(self, evaluation):
        self.evaluation = evaluation

class TranspositionTable:
    def __init__(self, max_mibibytes):
        self.transposition_dict = {}
        self.max_size = max_mibibytes * 2 ** 20
    
    def add(self, state, move, depth: int, transposition: Transposition):
        self.transposition_dict[state, move, depth] = transposition
        if self.transposition_dict.__sizeof__() >= self.max_size:
            print("culling")
            self.cull()

    def cull(self):
        while self.transposition_dict.__sizeof__() >= self.max_size:
            first_key = list(self.transposition_dict.keys())[0]
            del self.transposition_dict[first_key]

    def get(self, state, move, depth):
        if state not in self.transposition_dict: return None
        return self.transposition_dict[state, move, depth]

    def __contains__(self, key_tuple):
        if len(key_tuple) != 3: raise KeyError()
        return key_tuple in self.transposition_dict

    def __getitem__(self, key_tuple):
        if len(key_tuple) != 3: raise KeyError()
        return self.get(*key_tuple)
    
    def __setitem__(self, key_tuple, transposition: Transposition):
        if len(key_tuple) != 3: raise KeyError()
        self.add(*key_tuple, transposition)