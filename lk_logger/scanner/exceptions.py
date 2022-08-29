"""
References:
    https://stackoverflow.com/questions/60745841/inheriting-from-baseexception
    -vs-exception
"""


def visualize_line(linex, line, charx, char, symbols=None):
    block = '''
        ┌──────────────────────────────────────────────────────────────────────┐
        │   Tracing linex {}, charx {} (`{}`):
        │       {}
        │       {}
        │   Symbols:
        │       {}
        └──────────────────────────────────────────────────────────────────────┘
    '''.format(
        linex, charx,
        char.replace('\n', '■'),
        line.replace('\n', '■'),
        #   notice: the substitute character width must be ONE. otherwise the
        #   indicator will point to a wrong place.
        ' ' * charx + '^', symbols
    )
    
    temp = []
    for i, line in enumerate(block.splitlines()):
        if i == 0 or i == 7 or i == 8:
            temp.append(line)
        else:
            if len(line) < 80:
                line += ' ' * (80 - len(line) - 1) + '│'
            temp.append(line)
    block = temp
    
    return '\n'.join(block)


class ScanningError(Exception):
    
    def __init__(self, linex, line, charx, char, symbols):
        self.msg = visualize_line(linex, line, charx, char, symbols)
    
    def __str__(self):
        return self.msg


class UnreachableCase(ScanningError):
    pass


class UnresolvedCase(Exception):
    pass


class UnexpectedReturnCode(Exception):
    pass


class BreakOut(Exception):
    pass
