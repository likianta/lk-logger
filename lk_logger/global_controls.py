import builtins

from pytermgui import tim

from .general import std_print
from .logger import lk


def setup(**kwargs):
    """
    args:
        kwargs: see `./logger.py > LoggingConfig > docstring`.
    """
    lk.configure(**kwargs)
    setattr(builtins, 'print', lk.log)
    tim.print('[bold !rainbow]lk-logger is ready![/]')


def uninstall():
    setattr(builtins, 'print', std_print)


def enable():
    setattr(builtins, 'print', lk.log)


def disable():
    setattr(builtins, 'print', lambda *_, **__: None)
