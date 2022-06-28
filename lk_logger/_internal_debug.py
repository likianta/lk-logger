from inspect import currentframe

from .general import normpath
from .general import default_print


def debug(*args, condition=True):
    frame = currentframe().f_back
    filepath = normpath(frame.f_globals["__file__"])
    lineno = frame.f_lineno
    source = '{}:{}'.format(filepath, lineno)
    if condition:
        default_print(source, '[LKDEBUG]', *args)
