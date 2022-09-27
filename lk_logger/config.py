from __future__ import annotations

import typing as t
from sys import excepthook as _default_excepthook


class LoggingConfig:
    """
    options:
        show_source: bool[true]
            add source info (filepath and line number) prefix to log messages.
            example:
                lk.log('hello world')
                # enabled : './main.py:10  >>  hello world'
                # disabled: 'hello world'
        show_varnames: bool[false]
            show both var names and values. (magic reflection)
            example:
                a, b = 1, 2
                lk.log(a, b, a + b)
                # enabled : 'main.py:11  >>  a = 1; b = 2; a + b = 3'
                # disabled: 'main.py:11  >>  1, 2, 3'
        show_external_lib: bool[true]
            if `param source` came from an external library, whether to print.
            for example, if a third-party library 'xxx' also used `lk.log`,
            its source path (relative to current working dir) may be very long,
            if you don't want to see any prints except your own project, you'd
            set this to False.

        # the following options are only available if `show_external_lib` is
        # true.
        path_style_for_external_lib: literal
            literal:
                'pretty_relpath': default
                    trunscate the source path of external lib to be shorter.
                    example:
                        before:
                            '../../../../site-packages/lk_logger/sourcemap.py'
                            # there may be a lot of '../'.
                        after:
                            '[lk_logger]/sourcemap.py'
                'relpath':
                    a relative path to current working dir. (<- `os.getcwd()`)
                    note there may be a lot of '../../../...' if external lib
                    is far beyond the current working dir.
                'lib_name_only':
                    show only the library name (surrounded by brackets).
                    example: '[lk_logger]'
            ps: if you don't want to show anything, you should turn to set
            `show_external_lib` to False.
    """
    async_: bool
    clear_unfinished_stream: bool
    console_width: int | None
    path_style_for_external_lib: str
    rich_traceback: bool
    separator: str
    show_external_lib: bool
    show_funcname: bool
    show_source: bool
    show_varnames: bool
    
    _preset_conf = {
        'async_'                     : True,
        'clear_unfinished_stream'    : False,
        'console_width'              : None,
        'path_style_for_external_lib': 'pretty_relpath',
        'rich_traceback'             : True,
        'separator'                  : ';   ',
        'show_external_lib'          : True,
        'show_funcname'              : True,
        'show_source'                : True,
        'show_varnames'              : False,
    }
    
    def __init__(self, **kwargs):
        for k, v in self._merge_dict(self._preset_conf, kwargs).items():
            self._apply(k, v)
    
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k in self._preset_conf and v != getattr(self, k, None):
                self._apply(k, v)
    
    def reset(self):
        for k, v in self._preset_conf.items():
            if v != getattr(self, k, None):
                self._apply(k, v)
    
    def _apply(self, key: str, val: bool | int | str):
        setattr(self, key, val)
        if key == 'console_width':
            if val and isinstance(val, int):
                from .console import console
                console.width = val
        elif key == 'rich_traceback':
            if val:
                # https://rich.readthedocs.io/en/stable/traceback.html
                from rich.traceback import install
                from .console import console
                install(console=console, show_locals=False)
            else:
                import sys
                sys.excepthook = _default_excepthook
    
    # -------------------------------------------------------------------------
    
    def to_dict(self) -> dict[str, t.Any]:
        return {
            k: getattr(self, k)
            for k in self._preset_conf
        }
    
    @staticmethod
    def _merge_dict(base: dict, update: dict) -> dict:
        return {k: update.get(k, default_v) for k, default_v in base.items()}
    
    @staticmethod
    def _diff_dict(base: dict, update: dict) -> dict:
        out = {}
        for k, v0 in base.items():
            if k in update and v0 != (v1 := update[k]):
                out[k] = v1
        return out
