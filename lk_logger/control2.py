import builtins
import typing as t
from contextlib import contextmanager


@contextmanager
def mute() -> t.Iterator[None]:
    _print = builtins.print
    setattr(builtins, 'print', lambda *_, **__: None)
    yield
    setattr(builtins, 'print', _print)
