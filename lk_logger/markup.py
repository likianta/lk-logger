import typing as t
from collections import defaultdict
from enum import Enum
from enum import auto
from random import choices
from re import compile as re_compile
from string import ascii_lowercase
from time import time

from .printer import dbg_print  # noqa

if __name__ == '__main__':
    from .frame_info import FrameInfo


# noinspection PyArgumentList
class MarkMeaning(Enum):
    AGRESSIVE_PRUNE = auto()
    BUILTIN_PRINT = auto()
    DIVIDER_LINE = auto()
    EXPAND_OBJECT = auto()
    FLUSH = auto()
    FLUSH_CUTOFF = auto()
    FLUSH_EDDY = auto()
    GLOBAL_INDEX = auto()
    LINE_INDEX = auto()
    MODERATE_PRUNE = auto()
    PARENT_POINTER = auto()
    RESET_INDEX = auto()
    RESET_TIMER = auto()
    RICH_FORMAT = auto()
    RICH_OBJECT = auto()
    RICHABLE_DATA = auto()
    STOP_TIMER = auto()
    SWIFT_INDEX = auto()
    TABULAR_DATA = auto()
    TEMP_TIMER = auto()
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
        't': int,  # timer / timestamp / tabular
        'v': int,  # verbosity / log level
    })
    MarksMeaning = t.Dict[MarkMeaning, t.Any]
    
    class Counter:
        ColorHex = str
        FrameId = str
        Indent = int
        Index = int
        UniqueId = str
        
        ScopedIndexes = t.DefaultDict[UniqueId, Index]
        Uid2ColorHex = t.DefaultDict[UniqueId, ColorHex]
        UidGenerator = t.DefaultDict[str, UniqueId]


class E:
    class UnsupportedMarkup(Exception):
        pass


class MarkupAnalyzer:
    """
    readme: prj:/docs/markup.zh.md
    """
    _counter: '_Counter'
    _levels: t.Tuple[str, ...]
    _mark_pattern_0 = re_compile(r'^:(?:[defilprstv][0-9]?)+$')
    _mark_pattern_1 = re_compile(r'\w\d?')
    _simple_time: float
    _temp_time: float
    
    def __init__(self) -> None:
        self._counter = _Counter()
        self._simple_time = time()
        self._temp_time = time()
    
    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern_0.match(text))
    
    def extract(self, markup: T.Markup) -> T.Marks:
        """
        description: (the asterisk symbol on the left means default entry)
            * d0: divider line
              d1: divider block                               *(not supported)*
            * e0: exception trace back
              e1: exception trace back with showing locals
              e2: enter pdb                                   *(not supported)*
            * f0: flush
              f1: flush cutoff
              f2: flush eddy               *(not a good option, maybe removed)*
              i0: reset index
            * i1: intelligent index
              i2: line-level index
              i3: global index
            * l0: long / loose / expanded (multiple lines)
              l1: inspect object
              p0: self layer
            * p1: parent layer
              p2: grandparent layer                    *(be careful using p2+)*
              p3: great-grandparent layer
              p4: and so on...
            * r0: rich style
              r1: rich object (rich.table.Table, rich.panel.Panel, etc.)
              r2: auto detect rich format (for a limit set of types)
            * s0: short / simple / single line
              s1: builtin-like print (remains markup features)
              s2: builtin print
              t0: reset timer
            * t1: stop timer and show statistics
              t2: temporary timer
            * v0: trace / debug / hint (gray)
              v1: negative info (magenta)
              v2: positive info (blue)
              v3: weak success (green dim)
              v4: success (green)
              v5: weak warning (yellow dim)
              v6: warning (yellow)
              v7: weak error / failure (red dim)
              v8: error / failure (red)
        
        trick to remember `v*`:
            v2, v4, v6, v8 are for primary info, success, warning, error.
            v1, v3, v5, v7 are for secondary use cases.
            see also `./message_formatter.py : MessageFormatter
            : _level_2_color`
        
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
            't': 1,  # `:t0` is 'reset timer'
            'v': 0,
        }
        out = defaultdict(lambda: -1)
        for m in (self._mark_pattern_1.findall(markup) or ()):
            if len(m) == 1:
                out[m[0]] = defaults[m[0]]
            else:
                out[m[0]] = int(m[1:])
        # if out:
        #     dbg_print(dict(out))
        return out
    
    def analyze(self, marks: T.Marks, **kwargs) -> T.MarksMeaning:
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
                self._counter.reset_all_indexes()
                out[MarkMeaning.RICH_FORMAT] = True
                out[MarkMeaning.RESET_INDEX] = 0
            elif marks['i'] == 1:
                out[MarkMeaning.SWIFT_INDEX] = \
                    self._counter.update_scoped_index(kwargs['frame_info'])
            elif marks['i'] == 2:
                out[MarkMeaning.LINE_INDEX] = \
                    self._counter.update_line_index(kwargs['frame_info'])
            elif marks['i'] == 3:
                out[MarkMeaning.GLOBAL_INDEX] = \
                    self._counter.update_global_index()
            else:
                raise E.UnsupportedMarkup(f':i{marks["i"]}')
        
        if marks['l'] >= 0:
            out[MarkMeaning.EXPAND_OBJECT] = marks['l'] + 1  # 1 or 2
        
        if marks['p'] >= 0:
            out[MarkMeaning.PARENT_POINTER] = marks['p']
        else:
            out[MarkMeaning.PARENT_POINTER] = 0
        
        if marks['r'] >= 0:
            if marks['r'] == 0:
                out[MarkMeaning.RICH_FORMAT] = True
            elif marks['r'] == 1:
                out[MarkMeaning.RICH_OBJECT] = True
            elif marks['r'] == 2:
                out[MarkMeaning.RICHABLE_DATA] = True
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
            if marks['t'] == 0:
                out[MarkMeaning.RICH_FORMAT] = True
                t = self._simple_time = time()
                out[MarkMeaning.RESET_TIMER] = t
            elif marks['t'] == 1:
                out[MarkMeaning.RICH_FORMAT] = True
                start, end = self._simple_time, time()
                out[MarkMeaning.STOP_TIMER] = (start, end)
                self._simple_time = end
            elif marks['t'] == 2:
                out[MarkMeaning.RICH_FORMAT] = True
                start, end = self._temp_time, time()
                out[MarkMeaning.TEMP_TIMER] = (start, end)
                self._temp_time = end
            elif marks['t'] == 3:
                out[MarkMeaning.TABULAR_DATA] = True
            else:
                raise E.UnsupportedMarkup(f':t{marks["t"]}')
        
        if marks['v'] >= 0:
            out[MarkMeaning.VERBOSITY] = marks['v']
        
        return out


class _Counter:
    _global_index: T.Counter.Index
    _last_indent: T.Counter.Indent
    _last_uid: T.Counter.UniqueId
    _line_indexes: T.Counter.ScopedIndexes
    _scoped_indexes: T.Counter.ScopedIndexes
    _uid_2_color: T.Counter.Uid2ColorHex
    _uid_gen: T.Counter.UidGenerator
    
    def __init__(self) -> None:
        self._global_index = 0
        self._line_indexes = defaultdict(lambda: 0)
        self._scoped_indexes = defaultdict(lambda: 0)
        self._last_indent = 0
        self._last_uid = ''
        self._uid_2_color = defaultdict(self._get_random_bright_color)
        self._uid_gen = defaultdict(self._generate_uid)
    
    @staticmethod
    def _generate_uid() -> T.Counter.UniqueId:
        """
        randomly generate a four-character uid.
        """
        return ''.join(choices(ascii_lowercase, k=4))
    
    @staticmethod
    def _get_random_bright_color() -> T.Counter.ColorHex:
        # https://stackoverflow.com/questions/43437309
        return '#' + ''.join(choices('89ABCDEF', k=6))
    
    def update_global_index(self) -> T.Counter.Index:
        self._global_index += 1
        return self._global_index
    
    def update_line_index(self, frame_info: 'FrameInfo') -> t.Tuple[
        T.Counter.Index, T.Counter.UniqueId, T.Counter.ColorHex
    ]:
        uid = self._uid_gen[frame_info.id]
        self._line_indexes[uid] += 1
        return self._line_indexes[uid], uid, self._uid_2_color[uid]
    
    def update_scoped_index(self, frame_info: 'FrameInfo') -> t.Tuple[
        T.Counter.Index, T.Counter.UniqueId, T.Counter.ColorHex
    ]:
        indent = frame_info.indentation
        if self._last_indent > indent:
            # reset all counts in higher indented levels
            prefix = '{}:{}:{}:'.format(
                frame_info.parent and frame_info.parent.id,
                frame_info.filepath,
                frame_info.funcname,
            )
            for some_uid in self._uid_gen.keys():
                if some_uid.startswith(prefix):
                    some_indent = int(some_uid.rsplit(':', 1)[1])
                    if some_indent > indent:
                        self._scoped_indexes[some_uid] = 0
        self._last_indent = indent
        
        uid = self._uid_gen['{}:{}:{}:{}'.format(
            frame_info.parent and frame_info.parent.id,
            frame_info.filepath,
            frame_info.funcname,
            frame_info.indentation,
        )]
        self._scoped_indexes[uid] += 1
        return self._scoped_indexes[uid], uid, self._uid_2_color[uid]
    
    def reset_all_indexes(self) -> None:
        self._scoped_indexes.clear()
        self._line_indexes.clear()
        self._global_index = 0


markup_analyzer = MarkupAnalyzer()
