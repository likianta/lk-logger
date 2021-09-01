"""
References:
    https://stackoverflow.com/questions/60745841/inheriting-from-baseexception
    -vs-exception
"""


class UnreachableCase(Exception):
    
    def __init__(self, linex, line, charx, char, symbols):
        # noinspection PyProtectedMember
        self.msg = '''\
            Error happened at line {} char {} (`{}`):
                {}
                {}
            Symbols:
                {}
        '''.format(
            linex, charx, char,
            line,
            ' ' * charx + '^',
            symbols
        )
    
    def __str__(self):
        return self.msg


class UnexpectedReturnCode(Exception):
    pass


class BreakOut(Exception):
    pass


class BreakDown(Exception):
    pass
