import builtins

from .general import std_print
from .logger import lk


def setup(**kwargs):
    """
    args:
        kwargs: see `./logger.py > LoggingConfig`.
    """
    quiet = kwargs.pop('quiet', False)
    
    lk.configure(**kwargs)
    setattr(builtins, 'print', lk.log)
    
    if not quiet:
        from random import randint
        slogan = (
            '[!rainbow]lk-logger is ready[/!rainbow]',
            '[!gradient(197)]lk-logger is ready[/!gradient]',
            '[!gradient(197)]lk-logger[/!gradient] [171]is ready[/]',
        )[randint(0, 2)]
        print('[bold red]♥[/] ' + slogan + ' [bold red]♥[/]', ':rp')


def unload():
    setattr(builtins, 'print', std_print)


def enable():
    setattr(builtins, 'print', lk.log)


def disable():
    setattr(builtins, 'print', lambda *_, **__: None)
