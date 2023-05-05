import typing as t
from collections import defaultdict
from enum import Enum
from enum import auto
from re import compile as re_compile
from time import time


# noinspection PyArgumentList
class MarkMeaning(Enum):
    AGRESSIVE_PRUNE = auto()
    BUILTIN_PRINT = auto()
    DIVIDER_LINE = auto()
    EXPAND_MULTIPLE_LINES = auto()
    FLUSH = auto()
    FLUSH_CUTOFF = auto()
    FLUSH_EDDY = auto()
    MODERATE_PRUNE = auto()
    RESET_INDEX = auto()
    RESET_TIMER = auto()
    RICH_FORMAT = auto()
    RICH_OBJECT = auto()
    START_TIMER = auto()
    STOP_TIMER = auto()
    TRACEBACK_EXCEPTION = auto()
    TRACEBACK_EXCEPTION_WITH_LOCALS = auto()
    UPDATE_INDEX = auto()
    VERBOSITY = auto()


class T:
    Markup = str
    Marks = t.TypedDict('Marks', {
        'd': int,  # divider line
        'e': int,  # exception trace back
        'i': int,  # index
        'f': int,  # flush
        'l': int,  # long / loose / expanded (multiple lines)
        'p': int,  # parent layer
        'r': int,  # rich style
        's': int,  # short / simple / single line
        't': int,  # timer / timestamp
        'v': int,  # verbosity / log level
    })
    MarksMeaning = t.Dict[MarkMeaning, t.Any]


class E:
    class UnsupportedMarkup(Exception):
        pass


class MarkupAnalyser:
    """
    readme: prj:/docs/markup.zh.md
    """
    _mark_pattern_0 = re_compile(r'^:(?:[defilprstv][0-9]?)+$')
    _mark_pattern_1 = re_compile(r'\w\d?')
    
    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern_0.match(text))
    
    def extract(self, markup: T.Markup) -> T.Marks:
        """
        description: (the asterisk * means default value)
            * d0: divider line
              d1: custom divider lines                        *(not supported)*
            * e0: exception trace back
              e1: exception trace back with showing locals
              e2: enter pdb                                   *(not supported)*
              i0: reset index
            * i1: update index
              f0: flush
            * f1: flush cutoff
              f2: flush eddy               *(not a good option, maybe removed)*
            * l0: long / loose / expanded (multiple lines)
              l1: force expand all nodes                      *(not supported)*
              p0: self layer
            * p1: parent layer
              p2: grandparent layer                    *(be careful using p2+)*
              p3: great-grandparent layer
              p4: and so on...
            * r0: rich style
              r1: rich object (rich.table.Table, rich.panel.Panel, etc.)
            * s0: short / simple / single line
              s1: builtin-like print (remains markup features)
              s2: builtin print
              t0: reset timer
              t1: start timer
            * t2: stop timer and show statistics
              v0: no obvious verbosity
            * v1: debug
              v2: info
              v3: warning
              v4: error
              v5: critical
        
        return:
            dict[literal mark, int level]
        """
        defaults = {
            'd': 0,
            'e': 0,
            'f': 1,
            'i': 1,  # `:i0` is 'reset index'
            'l': 0,
            'p': 1,  # `:p0` points to 'self' layer
            'r': 0,
            's': 0,
            't': 2,  # `:t0` is 'reset timer'; `:t1` is 'start timer'
            'v': 1,  # `:v0` is 'no obvious verbosity'
        }
        out = defaultdict(lambda: -1)
        for m in (self._mark_pattern_1.findall(markup) or ()):
            if len(m) == 1:
                out[m[0]] = defaults[m[0]]
            else:
                out[m[0]] = int(m[1:])
        return out
    
    _simple_count = 0
    _simple_time = time()
    
    def analyse(self, marks: T.Marks) -> T.MarksMeaning:
        out = {}
        
        if marks['d'] >= 0:
            if marks['d'] == 0:
                out[MarkMeaning.DIVIDER_LINE] = '-'  # pattern
                #   TODO: currently suggest using only one character.
            else:
                raise E.UnsupportedMarkup(f':d{marks["d"]}')
        
        if marks['e'] >= 0:
            if marks['e'] == 0:
                out[MarkMeaning.TRACEBACK_EXCEPTION] = True
            elif marks['e'] == 1:
                out[MarkMeaning.TRACEBACK_EXCEPTION_WITH_LOCALS] = True
            else:
                raise E.UnsupportedMarkup(f':e{marks["e"]}')
        
        if marks['f'] >= 0:
            if marks['f'] == 0:
                out[MarkMeaning.FLUSH] = True
            elif marks['f'] == 1:
                out[MarkMeaning.FLUSH_CUTOFF] = True
            elif marks['f'] == 2:
                out[MarkMeaning.FLUSH_EDDY] = True
            else:
                raise E.UnsupportedMarkup(f':f{marks["f"]}')
        
        if marks['i'] >= 0:
            if marks['i'] == 0:
                self._simple_count = 0
                out[MarkMeaning.RESET_INDEX] = 0
                out[MarkMeaning.RICH_FORMAT] = True
            elif marks['i'] == 1:
                self._simple_count += 1
                out[MarkMeaning.UPDATE_INDEX] = self._simple_count
            else:
                raise E.UnsupportedMarkup(f':i{marks["i"]}')
        
        if marks['l'] >= 0:
            if marks['l'] == 0:
                out[MarkMeaning.EXPAND_MULTIPLE_LINES] = True
            else:
                raise E.UnsupportedMarkup(f':l{marks["l"]}')
        
        if marks['r'] >= 0:
            if marks['r'] == 0:
                out[MarkMeaning.RICH_FORMAT] = True
            elif marks['r'] == 1:
                out[MarkMeaning.RICH_OBJECT] = True
            else:
                raise E.UnsupportedMarkup(f':r{marks["r"]}')
        
        if marks['s'] >= 0:
            if marks['s'] == 0:
                out[MarkMeaning.MODERATE_PRUNE] = True
            elif marks['s'] == 1:
                out[MarkMeaning.AGRESSIVE_PRUNE] = True
            elif marks['s'] == 2:
                out[MarkMeaning.BUILTIN_PRINT] = True
            else:
                raise E.UnsupportedMarkup(f':s{marks["s"]}')
        
        if marks['t'] >= 0:
            out[MarkMeaning.RICH_FORMAT] = True
            if marks['t'] == 0:
                t = self._simple_time = time()
                out[MarkMeaning.RESET_TIMER] = t
            elif marks['t'] == 1:
                t = self._simple_time = time()
                out[MarkMeaning.START_TIMER] = t
            elif marks['t'] == 2:
                start, end = self._simple_time, time()
                self._simple_time = end
                out[MarkMeaning.STOP_TIMER] = (start, end)
            else:
                raise E.UnsupportedMarkup(f':t{marks["t"]}')
        
        if marks['v'] >= 1:
            levels = ('trace', 'debug', 'info', 'warn', 'error', 'fatal')
            out[MarkMeaning.VERBOSITY] = levels[marks['v']]
        
        return out
