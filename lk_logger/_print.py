import builtins
from inspect import currentframe

bprint = builtin_print = builtins.print


def debug(*args, condition=True):
    frame = currentframe().f_back
    filepath = _normpath(frame.f_globals["__file__"])
    lineno = frame.f_lineno
    source = '{}:{}'.format(filepath, lineno)
    if condition:
        builtin_print(source, '[LKDEBUG]', *args)


def _normpath(path: str) -> str:
    return path.replace('\\', '/').rstrip('/')
