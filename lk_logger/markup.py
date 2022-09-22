from __future__ import annotations

import typing as t
from enum import Enum
from enum import auto
from time import time


# noinspection PyArgumentList
class MarkMeaning(Enum):
    AGRESSIVE_PRUNE = auto()
    DIVIDER_LINE = auto()
    EXPAND_MULTIPLE_LINES = auto()
    FLUSH = auto()
    FLUSH_AND_DRAIN = auto()
    MODERATE_PRUNE = auto()
    RESET_INDEX = auto()
    RESET_TIMER = auto()
    RICH_FORMAT = auto()
    START_TIMER = auto()
    STOP_TIMER = auto()
    UPDATE_INDEX = auto()
    VERBOSITY = auto()


class T:
    Markup = str
    Marks = t.TypedDict('Marks', {
        'd': int,  # divider line
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


class MarkupAnalyser:
    """
    readme: prj:/docs/markup.zh.md
    """
    from re import compile
    _mark_pattern_0 = compile(r'^:(?:[dfilprstv][0-9]?)+$')
    _mark_pattern_1 = compile(r'\w\d?')
    
    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern_0.match(text))
    
    def extract(self, markup: T.Markup) -> T.Marks:
        """
        return:
            dict[literal mark, int value]
        """
        defaults = {
            'd': -1,
            'f': -1,
            'i': -1,
            'l': -1,
            'p': 0,
            'r': -1,
            's': -1,
            't': -1,
            'v': 0,
        }
        shortcuts = {
            'd': 0,
            'f': 0,
            'i': 1,
            'l': 0,
            'p': 1,
            'r': 0,
            's': 0,
            't': 2,
            'v': 1,
        }
        
        out = defaults.copy()
        for m in (self._mark_pattern_1.findall(markup) or ()):
            if len(m) == 1:
                out[m[0]] = shortcuts[m[0]]
            else:
                out[m[0]] = int(m[1:])
        return out
    
    _simple_count = 0
    _simple_time = time()
    
    def analyse(self, marks: T.Marks) -> T.MarksMeaning:
        out = {}
        
        if marks['d'] >= 0:
            out[MarkMeaning.DIVIDER_LINE] = '-' * 64
        
        if marks['f'] >= 0:
            if marks['f'] == 0:
                out[MarkMeaning.FLUSH] = True
            else:
                out[MarkMeaning.FLUSH_AND_DRAIN] = True
        
        if marks['i'] == 0:
            self._simple_count = 0
            out[MarkMeaning.RESET_INDEX] = 0
            out[MarkMeaning.RICH_FORMAT] = True
        elif marks['i'] >= 1:
            self._simple_count += 1
            out[MarkMeaning.UPDATE_INDEX] = self._simple_count
        
        if marks['l'] >= 0:
            out[MarkMeaning.EXPAND_MULTIPLE_LINES] = True
        
        if marks['r'] >= 0:
            out[MarkMeaning.RICH_FORMAT] = True
        
        if marks['s'] == 0:
            out[MarkMeaning.MODERATE_PRUNE] = True
        elif marks['s'] >= 1:
            out[MarkMeaning.AGRESSIVE_PRUNE] = True
        
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
        
        if marks['v'] >= 1:
            levels = ('trace', 'debug', 'info', 'warn', 'error', 'fatal')
            out[MarkMeaning.VERBOSITY] = levels[marks['v']]
        
        # postfix
        # if any((
        #     MarkMeaning.RESET_INDEX in out,
        #     MarkMeaning.EXPAND_MULTIPLE_LINES in out,
        # )):
        #     out[MarkMeaning.RICH_FORMAT] = True
        
        return out
