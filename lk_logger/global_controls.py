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
    print('[bold]'
          '[red]♥[/red]'
          '[!rainbow] lk-logger is ready [/!rainbow]'
          '[red]♥[/red]'
          '[/bold]', ':rp')


def unload():
    setattr(builtins, 'print', std_print)


def enable():
    setattr(builtins, 'print', lk.log)


def disable():
    setattr(builtins, 'print', lambda *_, **__: None)
