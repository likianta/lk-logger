from inspect import currentframe

from .general import builtin_print
from .general import normpath


def debug(*args, condition=True):
    frame = currentframe().f_back
    filepath = normpath(frame.f_globals["__file__"])
    lineno = frame.f_lineno
    source = '{}:{}'.format(filepath, lineno)
    if condition:
        builtin_print(source, '[LKDEBUG]', *args)
