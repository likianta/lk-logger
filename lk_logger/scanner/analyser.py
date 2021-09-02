from contextlib import contextmanager

from .const import *
from .symbols import Symbols


class Analyser:
    
    def __init__(self, end='\n'):
        self.end = end
        self.last_char = None
        self.last_last_char = None
        self.safe_period = 0
        self.symbols = Symbols()
    
    def reset(self):
        self.symbols.clear()
    
    @contextmanager
    def trace_index(self, index):
        """
        This is an optional feature. When we use:
            with my_analyser.trace_index(index):
                my_analyser.analyse(some_char)
        The `self.symbols.nested_struct` property will be available to use.
        """
        with self.symbols.trace_index(index):
            yield self
    
    def analyse(self, char):
        last_last_char, last_char = self.last_last_char, self.last_char
        symbols = self.symbols
        ret_code = INIT
        
        if symbols:
            _, target_char, token = symbols.last_symbol
            
            if token == TOKEN_A00:
                if char == target_char:
                    symbols.consume()
                elif char in PAIRED_SYMBOLS:
                    symbols.append(*PAIRED_SYMBOLS[char])
                else:
                    pass
            elif token == TOKEN_B00:
                if char == '\\':
                    symbols.append(*PAIRED_SYMBOLS[char])
                elif last_last_char is not None:
                    if last_char is not None:
                        # cases:
                        #   xxx'
                        #   xxx''
                        #   xxx'xxx
                        if char == target_char:
                            if last_last_char == last_char == char:
                                # case: xxx'' + ' = xxx'''
                                symbols.update(target_char, TOKEN_B21)
                            elif last_char == char:
                                # case: xxx' + ' = xxx''
                                pass
                            else:
                                # case: xxx'xxx + ' = xxx'xxx'
                                symbols.update(target_char, TOKEN_B10)
                                symbols.consume()
                        else:
                            if last_last_char == last_char == target_char:
                                # case: xxx'' + x = xxx''x
                                symbols.update(target_char, TOKEN_B10)
                                symbols.consume(-1)  # MARK: 20210901190803
                                #   notice: here we are consuming LAST_CHAR's
                                #   case, not current char's case. this is the
                                #   ONLY position that current char doesn't get
                                #   consumed, we need to recall `main_analyse`
                                #   to consume it forcely.
                                return self.analyse(char)
                    else:
                        ret_code = UNREACHABLE_CASE
                else:
                    if last_char is not None:
                        # case: '
                        assert last_char == target_char
                        if char == target_char:
                            # case: ' + ' = ''
                            pass
                        else:
                            # case: ' + x = 'x
                            symbols.update(target_char, TOKEN_B10)
                    else:
                        ret_code = UNREACHABLE_CASE
            elif token == TOKEN_B10:
                if char == target_char:
                    symbols.consume()
                elif char == '\\':
                    symbols.append(*PAIRED_SYMBOLS[char])
                else:
                    pass
            elif token == TOKEN_B20:
                # the TOKEN_B2 is a virtual node and has no instances in
                # this method. we could only see its sub node instances
                # (TOKEN_B21, TOKEN_B22).
                ret_code = UNREACHABLE_CASE
            elif token == TOKEN_B21:
                self.safe_period += 1
                if self.safe_period == 1:
                    if char == '\\':
                        self.safe_period = 0
                        symbols.update(target_char, TOKEN_B22)
                        symbols.append(*PAIRED_SYMBOLS[char])
                    else:
                        pass
                elif self.safe_period == 2:
                    self.safe_period = 0
                    symbols.update(target_char, TOKEN_B22)
                    if char == '\\':
                        symbols.append(*PAIRED_SYMBOLS[char])
                    else:
                        pass
                else:
                    ret_code = UNREACHABLE_CASE
            elif token == TOKEN_B22:
                # cases:
                #   xxx'''x'
                #   xxx'''xx
                #   xxx''''x
                #   xxx'''''
                # assert last_last_char is not None
                # assert last_char is not None
                if last_last_char == last_char == char == target_char:
                    # case: xxx''''' + ' = xxx''''''
                    symbols.consume()
                elif char == '\\':
                    symbols.append(*PAIRED_SYMBOLS[char])
                else:
                    pass
            elif token == TOKEN_C00:
                symbols.consume()
            elif token == TOKEN_D00:
                symbols.consume()
                ret_code = BREAK_OUT
            else:
                ret_code = UNREACHABLE_CASE
        else:
            if char in PAIRED_SYMBOLS:
                if char == '#':
                    ret_code = BREAK_OUT
                else:
                    symbols.append(*PAIRED_SYMBOLS[char])
            elif char == self.end:
                ret_code = SUBMITTABLE
        
        self.last_last_char, self.last_char = self.last_char, char
        
        if ret_code == INIT:
            if self.symbols:
                ret_code = CONTINUE
            elif char == self.end:
                ret_code = SUBMITTABLE
            else:
                ret_code = CONTINUE
        return ret_code
