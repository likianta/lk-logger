import builtins
import typing as t

from . import control2
from .logger import logger
from .printer import bprint

status = 'unloaded'  # literal['enabled', 'disabled', 'unloaded']
_has_welcome_message_shown = False
_binput = builtins.input


def setup(
    *,
    quiet: bool = False,
    clear_preset: bool = False,
    _stdout: t.Callable = None,  # TODO: experimental
    **kwargs
) -> None:
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
    global _has_welcome_message_shown, status
    
    logger.configure(clear_preset, **kwargs)
    setattr(builtins, 'print', _stdout or logger.log)
    setattr(builtins, 'input', control2.input)
    
    if not quiet and not _has_welcome_message_shown:
        _has_welcome_message_shown = True
        print('lk-logger is ready', ':v3sp')
    
    status = 'enabled'


def update(clear_preset=False, **kwargs) -> None:
    logger.configure(clear_preset, **kwargs)


def unload() -> None:
    setattr(builtins, 'print', bprint)
    setattr(builtins, 'input', _binput)
    global status
    status = 'unloaded'


def enable() -> None:
    setattr(builtins, 'print', logger.log)
    global status
    status = 'enabled'


reload = enable


def disable() -> None:
    setattr(builtins, 'print', lambda *_, **__: None)
    global status
    status = 'disabled'


# -----------------------------------------------------------------------------
# other

def start_ipython(
        user_ns: t.Dict[str, t.Any] = None
) -> None:
    if _is_ipython_mode():
        return
    try:
        import IPython  # noqa
    except (ImportError, ModuleNotFoundError) as e:
        print('ipython is not installed!', ':pv4')
        raise e
    else:
        import sys
        from IPython.core.getipython import get_ipython  # noqa
        from IPython.terminal.ipapp import TerminalIPythonApp  # noqa
        from rich.traceback import install
        from .console import console
        from .pipeline import pipeline
    
    pipeline.add(IPython, bprint, scope=True)
    
    backups = {
        'lklogger_config': logger.config.copy(),
        'sys.argv'       : sys.argv.copy(),
    }
    
    setup(quiet=True, clear_preset=True,
          show_source=False, show_funcname=False, show_varnames=False)
    sys.argv = ['']  # avoid ipython to parse `sys.argv`.
    
    app = TerminalIPythonApp.instance(
        user_ns={'print': logger.log, '__USERNS__': user_ns, **(user_ns or {})}
    )
    app.initialize()
    
    # setup except hook for ipython
    setattr(builtins, 'get_ipython', get_ipython)
    install(console=console)
    
    app.start()
    
    # afterwards
    logger.configure(**backups['lklogger_config'])
    sys.argv = backups['sys.argv']
    del backups


def _is_ipython_mode() -> bool:
    return getattr(builtins, '__IPYTHON__', False)
