import typing as t
from collections import defaultdict
from enum import Enum
from enum import auto
from random import choices
from re import compile as re_compile
from string import ascii_lowercase
from time import time

from .frame_info import FrameInfo


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
    PARENT_POINTER = auto()
    RESET_INDEX = auto()
    RESET_TIMER = auto()
    RICH_FORMAT = auto()
    RICH_OBJECT = auto()
    SCOPED_COUNTER = auto()
    SIMPLE_COUNTER = auto()
    START_TIMER = auto()
    STOP_TIMER = auto()
    TRACEBACK_EXCEPTION = auto()
    TRACEBACK_EXCEPTION_WITH_LOCALS = auto()
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
    
    class Counter:
        ColorHex = str
        Fid = str
        Indent = int
        Index = int
        Uid = str
        
        Fid2Uid = t.DefaultDict[Indent, t.DefaultDict[Fid, Uid]]
        ScopedCounts = t.DefaultDict[Uid, Index]
        Uid2ColorHex = t.DefaultDict[Uid, ColorHex]


class E:
    class UnsupportedMarkup(Exception):
        pass


class MarkupAnalyser:
    """
    readme: prj:/docs/markup.zh.md
    """
    _counter: '_Counter'
    _levels: t.Tuple[str, ...]
    _mark_pattern_0 = re_compile(r'^:(?:[defilprstv][0-9]?)+$')
    _mark_pattern_1 = re_compile(r'\w\d?')
    _simple_time: float
    
    def __init__(self) -> None:
        self._counter = _Counter()
        self._simple_time = time()
        # TODO or DELETE: not used. see also `def extract : local_var levels`
        self._levels = ('trace', 'debug', 'info', 'warn', 'error', 'fatal')
    
    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern_0.match(text))
    
    def extract(self, markup: T.Markup) -> T.Marks:
        """
        description: (the asterisk * means default value)
            * d0: divider line
              d1: divider block                               *(not supported)*
            * e0: exception trace back
              e1: exception trace back with showing locals
              e2: enter pdb                                   *(not supported)*
            * f0: flush
              f1: flush cutoff
              f2: flush eddy               *(not a good option, maybe removed)*
              i0: reset index
            * i1: update index
              i2: scoped counter
              i3: progress                                    *(not supported)*
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
            'f': 0,
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
    
    def analyse(self, marks: T.Marks, **kwargs) -> T.MarksMeaning:
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
                out[MarkMeaning.RESET_INDEX] = \
                    self._counter.reset_simple_count()
                out[MarkMeaning.RICH_FORMAT] = True
            elif marks['i'] == 1:
                out[MarkMeaning.SIMPLE_COUNTER] = \
                    self._counter.update_simple_count()
            elif marks['i'] == 2:
                info: FrameInfo = kwargs['frame_info']
                out[MarkMeaning.SCOPED_COUNTER] = \
                    self._counter.update_scoped_count(
                        info.id, info.indentation
                    )
            else:
                raise E.UnsupportedMarkup(f':i{marks["i"]}')
        
        if marks['l'] >= 0:
            if marks['l'] == 0:
                out[MarkMeaning.EXPAND_MULTIPLE_LINES] = True
            else:
                raise E.UnsupportedMarkup(f':l{marks["l"]}')
        
        if marks['p'] >= 0:
            out[MarkMeaning.PARENT_POINTER] = marks['p']
        else:
            out[MarkMeaning.PARENT_POINTER] = 0
        
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


class _Counter:
    _fid_2_uid: T.Counter.Fid2Uid
    _last_indent: T.Counter.Indent
    _last_uid: T.Counter.Uid
    _scoped_counts: T.Counter.ScopedCounts
    _simple_count: T.Counter.Index
    _uid_2_color: T.Counter.Uid2ColorHex
    
    def __init__(self) -> None:
        self._simple_count = 0
        self._scoped_counts = defaultdict(lambda: 0)
        self._fid_2_uid = defaultdict(lambda: defaultdict(self._generate_uid))
        self._uid_2_color = defaultdict(self._get_random_bright_color)
        self._last_indent = 0
        self._last_uid = ''
    
    @staticmethod
    def _generate_uid() -> T.Counter.Uid:
        """
        randomly generate a four-character uid.
        """
        return ''.join(choices(ascii_lowercase, k=4))
    
    @staticmethod
    def _get_random_bright_color() -> T.Counter.ColorHex:
        # https://stackoverflow.com/questions/43437309
        return '#' + ''.join(choices('89ABCDEF', k=6))
    
    def update_simple_count(self) -> T.Counter.Index:
        self._simple_count += 1
        return self._simple_count
    
    def update_scoped_count(
            self,
            fid: T.Counter.Fid,
            indent: T.Counter.Indent
    ) -> t.Tuple[T.Counter.Index, T.Counter.Uid, T.Counter.ColorHex]:
        if self._last_indent > indent:
            # reset all counts in higher indented levels
            for indent_j in sorted(self._fid_2_uid.keys(), reverse=True):
                if indent_j <= indent: break
                for uid in self._fid_2_uid[indent_j].values():
                    self._scoped_counts[uid] = 0
        self._last_indent = indent
        
        uid = self._fid_2_uid[indent][fid]
        self._scoped_counts[uid] += 1
        return self._scoped_counts[uid], uid, self._uid_2_color[uid]
    
    def reset_simple_count(self) -> T.Counter.Index:
        self._simple_count = 0
        return 0
