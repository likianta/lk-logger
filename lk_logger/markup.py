from typing import TypedDict


class TMarks(TypedDict, total=False):
    d: int
    e: int
    i: int
    l: int
    p: int
    r: int
    s: int
    v: int


class MarkupAnalyser:
    """
    readme:
        ~/docs/markup.zh.md

    markup list:
        :d  divider line
        :e  error
        :i  index
        :l  long / loose format (multiple lines)
        :p  parent layer
        :r  rich
        :s  short / simple / single line
        :t  tag
        :v  verbose / log level
    """
    
    def __init__(self):
        from re import compile
        self._mark_pattern = compile(r'^:([deilprsv][0-9]?)+$')
    
    def is_valid_markup(self, text: str) -> bool:
        return bool(self._mark_pattern.match(text))
    
    @staticmethod
    def analyse(markup: str) -> TMarks:
        """
        return:
            dict[literal mark, int value]
                mark: d, e, i, l, p, r, s, t, v
        """
        out = {}
        defaults = {
            'd': 0,
            'e': 0,
            'i': 1,
            'l': 0,
            'p': 1,
            'r': 0,
            's': 0,
            't': 0,
            'v': 1,
        }
        
        from re import compile
        pattern = compile(r'\w\d?')
        for m in (pattern.findall(markup) or ()):
            if len(m) == 1:
                out[m] = defaults[m]
            else:
                out[m[0]] = int(m[1:])
        return out
