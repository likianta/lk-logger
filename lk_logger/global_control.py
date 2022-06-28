import builtins

from .general import default_print
from .logger import lk

_HAS_WELCOME_MESSAGE_SHOWN = False


def setup(*, quiet=False, clear_pre_configured=False, **kwargs):
    """
    args:
        quiet:
            True: show a welcome message in caller side.
            False: do not show.
            
            note: the welcome message is shown only once, if caller calls this
                function multi times, only the first time when passes
                `quiet=True` will show this message.
            tip: if you are developing an intermediate/supporting library, it
                is recommended to set `quiet=True`.
        clear_pre_configured:
        kwargs: see `./logger.py > LoggingConfig`.
    """
    global _HAS_WELCOME_MESSAGE_SHOWN
    
    lk.configure(clear_pre_configured, **kwargs)
    setattr(builtins, 'print', lk.log)
    
    if not quiet and not _HAS_WELCOME_MESSAGE_SHOWN:
        _HAS_WELCOME_MESSAGE_SHOWN = True
        from random import randint
        slogan = (
            '[!rainbow]lk-logger is ready[/!rainbow]',
            '[!gradient(197)]lk-logger is ready[/!gradient]',
            '[!gradient(197)]lk-logger[/!gradient] [171]is ready[/]',
        )[randint(0, 2)]
        print('[bold red]♥[/] ' + slogan + ' [bold red]♥[/]', ':rp')


def unload():
    setattr(builtins, 'print', default_print)


def enable():
    setattr(builtins, 'print', lk.log)


def disable():
    setattr(builtins, 'print', lambda *_, **__: None)
