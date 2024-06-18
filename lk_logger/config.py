import sys
import typing as t
from sys import excepthook as _default_excepthook

from rich.traceback import Traceback

from .console import console
from .printer import dprint  # noqa


class LoggingConfig:
    async_: bool
    #   run lk logger in separate thread.
    clear_unfinished_stream: bool
    console_width: t.Optional[int]
    path_style_for_external_lib: str
    #   'pretty_relpath': prettify external library path prefix.
    #       example: '[lk_logger]/sourcemap.py'
    #   'relpath': show external library path as relative path to current -
    #       working directory.
    #       example: './.venv/Lib/site-packages/lk_logger/sourcemap.py'
    #   'lib_name_only': show only the library name (surrounded by brackets).
    #       example: '[lk_logger]'
    #   (note: available only 'show_external_lib' is True.)
    rich_traceback: bool
    separator: str
    show_external_lib: bool
    #   whether to print messages from external libraries.
    show_funcname: bool
    show_source: bool
    #   attach source file path and line number info prefixed to the log -
    #   messages.
    #   True example:
    #       'main.py:10  >>  hello world'
    #   False example:
    #       'hello world'
    show_traceback_locals: bool
    show_varnames: bool
    #   show both variable names and values. (magic reflection)
    #   example:
    #       a, b = 1, 2
    #       logger.log(a, b, a + b)
    #       # enabled: 'main.py:11  >>  a = 1; b = 2; a + b = 3'
    #       # disabled: 'main.py:11  >>  1, 2, 3'
    sourcemap_alignment: t.Literal['left', 'right']
    v2_meaning: t.Literal['info', 'success']  # TODO: not used.
    
    _preset_conf = {
        'async_'                     : False,  # TODO
        'clear_unfinished_stream'    : False,
        'console_width'              : None,
        'path_style_for_external_lib': 'pretty_relpath',
        'rich_traceback'             : True,
        'separator'                  : ';   ',
        'show_external_lib'          : True,
        'show_funcname'              : False,
        'show_source'                : True,
        'show_traceback_locals'      : False,
        'show_varnames'              : False,
        'sourcemap_alignment'        : 'left',
        'v2_meaning'                 : 'info',
    }
    
    def __init__(self, **kwargs) -> None:
        for k, v in self._preset_conf.items():
            self._apply(k, kwargs.get(k, v))
    
    def to_dict(self) -> t.Dict[str, t.Any]:
        return {
            k: getattr(self, k)
            for k in self._preset_conf
        }
    
    def update(self, **kwargs) -> None:
        for k, v in kwargs.items():
            if k in self._preset_conf and v != getattr(self, k, None):
                self._apply(k, v)
    
    def reset(self) -> None:
        for k, v in self._preset_conf.items():
            if v != getattr(self, k, None):
                self._apply(k, v)
    
    def _apply(self, key: str, val: t.Union[bool, int, str]) -> None:
        setattr(self, key, val)
        if key == 'console_width':
            if val and isinstance(val, int):
                console.width = val
        elif key == 'rich_traceback':
            if val:
                sys.excepthook = self._custom_excepthook
            else:
                sys.excepthook = _default_excepthook
    
    def _custom_excepthook(self, type_, value, traceback) -> None:
        # print(':r', '[red dim]drain out message queue[/]')
        # from .logger import logger
        # if hasattr(logger, '_stop_running'):
        #     logger._stop_running()  # noqa
        if type_ is KeyboardInterrupt:
            print(':r', '[red dim]KeyboardInterrupt[/]')
            sys.exit(0)
        else:
            # https://rich.readthedocs.io/en/stable/traceback.html
            # dprint(getattr(self, 'show_traceback_locals'))
            console.print(
                Traceback.from_exception(
                    type_, value, traceback,
                    show_locals=getattr(self, 'show_traceback_locals'),
                    locals_hide_dunder=True,
                    locals_hide_sunder=True,
                    # word_wrap=True,
                ),
                soft_wrap=False,  # fixed line wrap problem.
            )
