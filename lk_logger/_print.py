import builtins
from inspect import currentframe
from os import name as os_name

bprint = builtins.print
std_print = builtins.print
non_print = lambda *_, **__: None


def debug(*args, condition=True) -> None:
    frame = currentframe().f_back
    filepath = _normpath(frame.f_globals["__file__"])
    lineno = frame.f_lineno
    source = '{}:{}'.format(filepath, lineno)
    if condition:
        bprint(source, '[LKDEBUG]', *args)


_is_win = os_name == 'nt'


def _normpath(path: str) -> str:
    if _is_win:
        return path.replace('\\', '/').rstrip('/')
    return path.rstrip('/')
