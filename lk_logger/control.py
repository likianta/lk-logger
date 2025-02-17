import builtins
import typing as t
from contextlib import contextmanager
from time import time

from .deflector import deflector
from .logger import logger
from .markup import markup_analyzer
from .printer import bprint

# -----------------------------------------------------------------------------
# global controls

_builtin_input = builtins.input
_has_welcome_message_shown = False


def setup(*, quiet: bool = False, clear_preset: bool = False, **kwargs) -> None:
    """
    params:
        quiet:
            - True: show a welcome message in caller side.
            - False: do not show.
            note: the welcome message is shown only once, if this function is -
            called multiple times, only the first time of which passes -
            `quiet=False` will show welcome message.
        kwargs: see `.config.LoggingConfig._preset_conf`.
    """
    global _has_welcome_message_shown
    
    logger.configure(clear_preset, **kwargs)
    setattr(builtins, 'print', logger.log)
    setattr(builtins, 'input', input)
    
    if not quiet and not _has_welcome_message_shown:
        _has_welcome_message_shown = True
        print('lk-logger is ready', ':v3sp')


def update(clear_preset: bool = False, **kwargs) -> None:
    logger.configure(clear_preset, **kwargs)


def unload() -> None:
    setattr(builtins, 'print', bprint)
    setattr(builtins, 'input', _builtin_input)


def enable() -> None:
    setattr(builtins, 'print', logger.log)
    setattr(builtins, 'input', _builtin_input)


reload = enable


def disable() -> None:
    setattr(builtins, 'print', lambda *_, **__: None)
    setattr(builtins, 'input', _builtin_input)


# -----------------------------------------------------------------------------
# local controls

# DELETE
# noinspection PyProtectedMember
@contextmanager
def counting() -> t.Iterator[None]:
    markup_analyzer._counter.reset_all_indexes()
    yield
    markup_analyzer._counter.reset_all_indexes()


# noinspection PyProtectedMember
@contextmanager
def delay() -> t.Iterator[None]:
    logger._control['stash_outputs'] = True
    yield
    logger._control['stash_outputs'] = False
    print(':fs')


# noinspection PyProtectedMember
@contextmanager
def elevate_caller_stack() -> t.Iterator[None]:
    logger._control['caller_layer_offset'] += 1
    yield
    logger._control['caller_layer_offset'] -= 1


class _Mute:
    _backup = None
    _mute_on = False
    
    def __call__(self, source: t.Union[str, object]) -> None :
        deflector.mute(source)
    
    def __enter__(self) -> None:
        if not self._mute_on:
            self._backup = builtins.print
            builtins.print = lambda *_, **__: None
            self._mute_on = True
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._mute_on:
            builtins.print = self._backup
            self._mute_on = False


mute = _Mute()


@contextmanager
def timing(sum_up: bool = False, exit_msg: str = None) -> t.Iterator[None]:
    markup_analyzer._simple_time = time()
    yield
    if exit_msg:
        print(':p2ts', exit_msg)
    elif sum_up:
        print(':p2tsv', 'over')


# -----------------------------------------------------------------------------
# other

def input(prompt: str = '', flush_scheme: int = 0) -> str:
    print(f':f{flush_scheme}s')
    return _builtin_input(prompt)


# DELETE
def start_ipython(user_ns: t.Dict[str, t.Any] = None) -> None:
    if getattr(builtins, '__IPYTHON__', False):
        # we are already in ipython environment.
        return
    try:
        import IPython  # noqa
    except (ImportError, ModuleNotFoundError) as e:
        print('ipython is not installed!', ':pv8')
        raise e
    else:
        import sys
        from IPython.core.getipython import get_ipython  # noqa
        from IPython.terminal.ipapp import TerminalIPythonApp  # noqa
        from rich.traceback import install
        from .console import console
        from .deflector import deflector
    
    deflector.add(IPython, bprint, scope=True)
    
    backup = {
        'lklogger_config': logger.config.copy(),
        'sys.argv'       : sys.argv.copy(),
    }
    
    setup(
        quiet=True,
        clear_preset=True,
        show_source=False,
        show_funcname=False,
        show_varnames=False,
    )
    sys.argv = ['']  # avoid ipython to parse `sys.argv`.
    
    app = TerminalIPythonApp.instance(
        user_ns={
            'print'     : logger.log,
            '__USERNS__': user_ns,
            **(user_ns or {})
        }
    )
    app.initialize()
    
    # setup except hook for ipython
    setattr(builtins, 'get_ipython', get_ipython)
    install(console=console)
    
    app.start()
    
    # afterwards
    logger.configure(**backup['lklogger_config'])
    sys.argv = backup['sys.argv']
    del backup
