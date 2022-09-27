import builtins
from inspect import currentframe

# DELETE: `builtin_print` is goint to be removed.
bprint = builtin_print = builtins.print
std_print = builtins.print
non_print = lambda *_, **__: None


def debug(*args, condition=True):
    frame = currentframe().f_back
    filepath = _normpath(frame.f_globals["__file__"])
    lineno = frame.f_lineno
    source = '{}:{}'.format(filepath, lineno)
    if condition:
        bprint(source, '[LKDEBUG]', *args)


def _normpath(path: str) -> str:
    return path.replace('\\', '/').rstrip('/')
