class MarkupAnalyser:
    """
    readme:
        ~/docs/markup.zh.md

    markup list:
        :d  divider line
        :i  index
        :l  long / loose
        :p  parent layer
        :r  rich
        :s  short
        :t  tag
        :v  verbose / log level
    """
    
    def __init__(self):
        from re import compile
        self._mark_pattern = compile(r'[a-z]\d*')
    
    def analyse(self, markup: str) -> dict:
        """
        return:
            dict[literal mark, int value]
                mark: d, i, l, p, r, s, t, v
        """
        out = {}
        defaults = {
            'd': 0,
            'i': 1,
            'l': 0,
            'p': 1,
            'r': 0,
            's': 0,
            't': 0,
            'v': 1,
        }
        marks = self._mark_pattern.findall(markup) or ()  # list[str]
        for m in marks:
            if len(m) == 1:
                out[m] = defaults[m]
            else:
                out[m[0]] = int(m[1:])
        return out
