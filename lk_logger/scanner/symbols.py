from contextlib import contextmanager

from .typehint import *


class Symbols:
    
    def __init__(self):
        self._symbols = []  # type: TSymbols
        self._matches = {}  # type: TMatches1
        self._index = -1
    
    def __str__(self):
        return str(self._symbols)
    
    def __bool__(self):
        return bool(self._symbols)
    
    def __getitem__(self, item):
        return self._symbols[item]
    
    @contextmanager
    def trace_index(self, index):
        self._index = index
        yield self
    
    def consume(self, adjust_offset=0):
        """
        Args:
            adjust_offset: if the caller is not consuming a target character,
                pass it a negative number.
                see `analyser.py > MARK@20210901190803`
        """
        pos_i, _, _ = self._symbols.pop()
        pos_o = self._index + adjust_offset
        self._matches[pos_i] = pos_o
    
    def update(self, char, token):
        index, _, _ = self._symbols[-1]
        self._symbols[-1] = (index, char, token)
    
    def append(self, char, token):
        self._symbols.append((self._index, char, token))
    
    def clear(self):
        self._symbols.clear()
        self._matches.clear()
        self._index = -1
    
    @property
    def last_symbol(self):
        return self._symbols[-1]
    
    @property
    def matches_list(self) -> TSpans:
        return [(k, v) for k, v in self._matches.items()]
    
    @property
    def matches_nest(self) -> TMatches2:
        if not self._matches:
            return {}
        
        consumed = []
        matches = self._matches
        pos_list = sorted(matches.keys())
        
        # noinspection PyUnusedLocal
        def loop(master, node, pos_s, pos_e, start, end):
            for i in range(start, end):
                if i in consumed:
                    continue
                pos_i = pos_list[i]
                pos_o = matches[pos_i]
                # lk.logt('[D1605]', pos_i, pos_o, 'field range', pos_s, pos_e)
                
                if pos_o < pos_e:
                    # lk.logt('[D1427]', 'subset of node', pos_i, pos_o, node)
                    loop(
                        master=node, node=node.setdefault((pos_i, pos_o), {}),
                        pos_s=pos_i, pos_e=pos_o,
                        start=i + 1, end=find_nearest_index(pos_o, i + 1)
                    )
                else:
                    # lk.logt('[D1453]', 'adjacent to node', pos_i, pos_o, master)
                    loop(
                        master=master, node=master.setdefault((pos_i, pos_o), {}),
                        pos_s=pos_i, pos_e=pos_o,
                        start=i + 1, end=find_nearest_index(pos_o, i + 1)
                    )
                consumed.append(i)
        
        def find_nearest_index(pos_e, start):
            for i in range(start, len(pos_list)):
                if pos_list[i] > pos_e:
                    return i
            else:
                return len(pos_list)
        
        loop(
            master=None, node=(out := {}),
            pos_s=0, pos_e=max(matches.values()) + 1,
            start=0, end=len(pos_list)
        )
        return out


symbols = Symbols()
