"""
References:
    https://stackoverflow.com/questions/60745841/inheriting-from-baseexception
    -vs-exception
"""


def visualize_line(linex, line, charx, char, symbols=None):
    return '''
        ┌──────────────────────────────────────────────────────────────────────╣
        │   Tracing linex {}, charx {} (`{}`):
        │       {}
        │       {}
        │   Symbols:
        │       {}
        └──────────────────────────────────────────────────────────────────────╣
    '''.format(
        linex, charx,
        char.replace('\n', '$'),
        line.replace('\n', '$'),
        #   notice: the substitute must be one single char. otherwise the
        #   indicator will point to a wrong place.
        ' ' * charx + '^', symbols
    )


class ScanningError(Exception):
    
    def __init__(self, linex, line, charx, char, symbols):
        self.msg = visualize_line(linex, line, charx, char, symbols)
    
    def __str__(self):
        return self.msg


class UnreachableCase(ScanningError):
    pass


class UnexpectedReturnCode(Exception):
    pass


class BreakOut(Exception):
    pass


class BreakDown(Exception):
    pass
