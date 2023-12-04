import builtins
import typing as t

from .delegate_logger import logger
from .._print import bprint
from .._print import debug  # noqa

STATUS = 'unloaded'  # literal['enabled', 'disabled', 'unloaded']
_HAS_WELCOME_MESSAGE_SHOWN = False


def setup(
    *,
    quiet: bool = False,
    **_
) -> None:
    global _HAS_WELCOME_MESSAGE_SHOWN, STATUS
    setattr(builtins, 'print', logger.log)
    if not quiet and not _HAS_WELCOME_MESSAGE_SHOWN:
        _HAS_WELCOME_MESSAGE_SHOWN = True
        from ..control import _blend_text
        from ..markup import _Counter
        random_color = _Counter._get_random_bright_color  # noqa
        color_pair = (random_color(), random_color())
        slogan = _blend_text('lk-logger is ready', color_pair)
        print(slogan, ':rsp')
    
    STATUS = 'enabled'


def update(**_) -> None:
    pass  # do nothing


def unload() -> None:
    setattr(builtins, 'print', bprint)
    global STATUS
    STATUS = 'unloaded'


def enable() -> None:
    setattr(builtins, 'print', logger.log)
    global STATUS
    STATUS = 'enabled'


def disable() -> None:
    setattr(builtins, 'print', lambda *_, **__: None)
    global STATUS
    STATUS = 'disabled'


# aliases
mute = disable
unmute = enable
reload = enable


# -----------------------------------------------------------------------------
# other

def start_ipython(  # FIXME
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
        from ..console import console
        from ..pipeline import pipeline
    
    pipeline.add(IPython, bprint, scope=True)
    
    backups = {
        'lklogger_config': logger.config.copy(),
        'sys.argv'       : sys.argv.copy(),
    }
    
    setup(quiet=True, clear_preset=True,
          show_source=False, show_funcname=False, show_varnames=False)
    sys.argv = ['']  # avoid ipython to parse `sys.argv`.
    
    app = TerminalIPythonApp.instance(
        user_ns={'print': logger.log, **(user_ns or {})}
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
