class TranspositionTable:
    def __init__(self, max_megabytes):
        self.transposition_dict = {}
        self.max_size = max_megabytes * 2 ** 20
    
    def add(self, state, move, eval):
        self.transposition_dict[state, move] = eval
        if self.transposition_dict.__sizeof__() >= self.max_size:
            print("culling")
            self.cull()

    def cull(self):
        while self.transposition_dict.__sizeof__() >= self.max_size:
            first_key = self.transposition_dict.keys()[0]
            del self.transposition_dict[first_key]

    def get(self, state, move):
        if state not in self.transposition_dict: return None
        return self.transposition_dict[state, move]

    def __getitem__(self, key_tuple):
        if len(key_tuple) != 2: raise KeyError()
        return self.get(*key_tuple)
    
    def __setitem__(self, key_tuple, eval):
        if len(key_tuple) != 2: raise KeyError()
        self.add(*key_tuple, eval)