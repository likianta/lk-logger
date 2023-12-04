import builtins
import os.path
from inspect import currentframe

bprint = builtins.print
std_print = builtins.print
non_print = lambda *_, **__: None


def debug(*args) -> None:
    frame = currentframe().f_back
    filepath = _normpath(frame.f_globals["__file__"])
    lineno = frame.f_lineno
    source = '{}:{}'.format(filepath, lineno)
    bprint(source, '[LKDEBUG]', *args)


def _normpath(path: str) -> str:
    return os.path.relpath(path).replace('\\', '/').rstrip('/')
