from __future__ import annotations

import builtins
from typing import Any

from ._print import bprint
from ._print import debug  # noqa
from .logger import lk

STATUS = 'unloaded'  # literal['enabled', 'disabled', 'unloaded']
_HAS_WELCOME_MESSAGE_SHOWN = False


def setup(*, quiet=False, clear_preset=False, **kwargs):
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
        clear_preset:
        kwargs: see `./logger.py > LoggingConfig`.
    """
    global _HAS_WELCOME_MESSAGE_SHOWN
    
    lk.configure(clear_preset, **kwargs)
    setattr(builtins, 'print', lk.log)
    
    if not quiet and not _HAS_WELCOME_MESSAGE_SHOWN:
        _HAS_WELCOME_MESSAGE_SHOWN = True
        
        from random import randint
        color_pairs_group = (
            ('#0a87ee', '#9294f0'),  # calm blue -> light blue
            ('#2d34f1', '#9294f0'),  # ocean blue -> light blue
            ('#ed3b3b', '#d08bf3'),  # rose red -> violet
            ('#f38cfd', '#d08bf3'),  # light magenta -> violet
            ('#f47fa4', '#f49364'),  # cold sandy -> camel tan
        )
        color_pair = color_pairs_group[randint(0, len(color_pairs_group) - 1)]
        slogan = _blend_text('♥ lk-logger is ready', color_pair)
        
        # debug(slogan)
        print(slogan, ':rsp')
    
    global STATUS
    STATUS = 'enabled'


def update(clear_preset=False, **kwargs):
    lk.configure(clear_preset, **kwargs)


def unload():
    setattr(builtins, 'print', bprint)
    global STATUS
    STATUS = 'unloaded'


def enable():
    setattr(builtins, 'print', lk.log)
    global STATUS
    STATUS = 'enabled'


def disable():
    setattr(builtins, 'print', lambda *_, **__: None)
    global STATUS
    STATUS = 'disabled'


# -----------------------------------------------------------------------------
# other

def start_ipython(user_ns: dict[str, Any] = None) -> None:
    try:
        import IPython
    except (ImportError, ModuleNotFoundError) as e:
        print('ipython is not installed!', ':pv4')
        raise e
    else:
        import sys
        from IPython.core.getipython import get_ipython
        from IPython.terminal.ipapp import TerminalIPythonApp
        from rich.traceback import install
        from .console import console
        from .pipeline import pipeline
    
    pipeline.add(IPython, bprint, scope=True)
    
    backups = {
        'lklogger_config': lk.config.copy(),
        'sys.argv'       : sys.argv.copy(),
    }
    
    setup(quiet=True, clear_preset=True,
          show_source=False, show_funcname=False, show_varnames=False)
    sys.argv = ['']  # avoid ipython to parse `sys.argv`.
    
    app = TerminalIPythonApp.instance(user_ns=user_ns or {'print': lk.log})
    app.initialize()
    
    # setup except hook for ipython
    setattr(builtins, 'get_ipython', get_ipython)
    install(console=console)
    
    app.start()
    
    # afterwards
    lk.configure(**backups['lklogger_config'])
    sys.argv = backups['sys.argv']
    del backups


# -----------------------------------------------------------------------------
# neutral functions

def _blend_text(message: str, color_pair: tuple[str, str]):
    """ blend text from one color to another.
    
    source: [lib:rich_cli/__main__.py : blend_text()]
    """
    from rich.color import Color
    from rich.text import Text
    
    color1, color2 = (Color.parse(x).triplet for x in color_pair)
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    dr = r2 - r1
    dg = g2 - g1
    db = b2 - b1
    
    text = Text(message)
    size = len(text)
    
    for index in range(size):
        blend = index / size
        color = '#{}{}{}'.format(
            f'{int(r1 + dr * blend):02X}',
            f'{int(g1 + dg * blend):02X}',
            f'{int(b1 + db * blend):02X}'
        )
        text.stylize(color, index, index + 1)
    return text.markup
