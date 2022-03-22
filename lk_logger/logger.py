import os
from inspect import currentframe

from pytermgui import parser
from pytermgui import tim
from pytermgui.prettifiers import prettify

from ._internal_debug import debug  # noqa
from .general import normpath
from .general import std_print
from .markup import MarkupAnalyser
from .message_formatter import MessageFormatter
from .path_helper import PathHelper
from .sourcemap import sourcemap

setattr(parser, 'print', std_print)
_formatter = MessageFormatter()


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
        path_format_for_external_lib: literal
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
    show_source = True
    show_varnames = False
    show_external_lib = True
    path_format_for_external_lib = 'pretty_relpath'
    
    def update(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)


class LKLogger:
    
    def __init__(self):
        # self._cache = {}  # TODO: be complete in next version
        # #   dict[tuple k, namedtuple v]
        # #       k: (filepath, lineno)
        # #       v: ...
        self._config = LoggingConfig()
        self._counter = 0
        self._cwd = normpath(os.getcwd())
        self._markup_analyser = MarkupAnalyser()
        
        # lazy loaded
        self.__external_libs = None
        self.__proj_root = None
    
    def configure(self, **kwargs):
        self._config.update(**kwargs)
    
    @property
    def _proj_root(self) -> str:
        if self.__proj_root is None:
            self.__proj_root = PathHelper.find_project_root()
        return self.__proj_root
    
    @property
    def _external_libs(self) -> dict:
        if self.__external_libs is None:
            self.__external_libs = PathHelper.indexing_external_libs()
        return self.__external_libs
    
    def log(self, *args, **_):
        msg = self._main(currentframe().f_back, *args)
        tim.print(msg)
    
    def fmt(self, *args, **_):
        return self._main(currentframe().f_back, *args)
    
    # noinspection PyUnresolvedReferences
    def _main(self, frame, *args) -> str:
        message_details = {
            'divider_line': '',
            'filepath'    : '',
            'funcname'    : '',
            'index'       : '',
            'lineno'      : '0',
            'log_level'   : '',
            'message'     : '',
        }
        
        markup_pos = 0  # 0 not exist, 1 for begining, -1 for ending.
        traceback_level = 0  # int[default 1]
        marks = {}
        
        if args:
            if (
                    isinstance(args[0], str) and args[0].startswith(':')
            ):
                markup_pos = 1
                markup, args = args[0], args[1:]
            elif len(args) > 1 and (
                    isinstance(args[-1], str) and args[-1].startswith(':')
            ):
                markup_pos = -1
                markup, args = args[-1], args[:-1]
            else:
                markup_pos = 0
                markup, args = None, args
            
            # analyse markup
            if markup:
                # analyse markup
                marks = self._markup_analyser.analyse_markup(markup)
                if marks:
                    if 'd' in marks:
                        message_details['divider_line'] = '-' * 80
                    if 'i' in marks:
                        if marks['i'] == 0:
                            self._counter = 0
                            if args:
                                self._counter += 1
                            else:
                                message_details['message'] = \
                                    '[grey](index reset)[/grey]'
                                # make sure 'r' key exists.
                                marks.setdefault('r', 0)
                        else:
                            self._counter += 1
                        message_details['index'] = str(self._counter)
                    if 'l' in marks:
                        args = tuple((
                            prettify(x, indent=4)
                            for x in args
                        ))
                    if 'p' in marks:
                        traceback_level = marks['p']
                    if 'r' in marks:
                        pass
                    if 's' in marks:
                        pass
                    if 'v' in marks:
                        message_details['log_level'] = (
                            'trace', 'debug', 'info',
                            'warn', 'error', 'fatal'
                        )[marks['v']]
        
        info = sourcemap.get_sourcemap(
            frame=frame,
            traceback_level=traceback_level,
            advanced=self._config.show_varnames,
        )
        
        if args:
            if self._config.show_varnames:
                if markup_pos == 0:
                    varnames = info.varnames
                elif markup_pos == 1:
                    varnames = info.varnames[1:]
                else:
                    varnames = info.varnames[:-1]
                try:
                    assert len(varnames) == len(args), (varnames, args)
                except AssertionError:
                    # debug('failed extracting varnames')
                    message_details['message'] = ';\t'.join(map(str, args))
                else:
                    # organize args
                    tmp_msg = []
                    for n, a in zip(varnames, args):
                        tmp_msg.append(f'{n} = {a}' if n else str(a))
                    message_details['message'] = ';\t'.join(tmp_msg)
            else:
                message_details['message'] = ';\t'.join(map(str, args))
        
        message_details['funcname'] = info.funcname
        
        # show external lib?
        if self._config.show_external_lib:
            # is external lib?
            if self._is_external_lib(info.filepath):  # yes
                # path format
                fmt = self._config.path_format_for_external_lib
                if fmt == 'relpath':
                    message_details['filepath'] = normpath(
                        os.path.relpath(info.filepath, self._cwd)
                    )
                else:
                    for lib_path in sorted(self._external_libs, reverse=True):
                        if info.filepath.startswith(lib_path):
                            lib_name = self._external_libs[lib_path].lower()
                            lib_relpath = \
                                info.filepath[len(lib_path):].lstrip('./') or \
                                os.path.basename(info.filepath)
                            break
                    else:
                        lib_name = ''
                        lib_relpath = info.filepath.lstrip('./')
                    
                    # debug(lib_name, lib_relpath)
                    
                    if fmt == 'pretty_relpath':
                        if lib_name:
                            message_details['filepath'] = \
                                '[magenta]\\[{}][/magenta]/{}'.format(
                                    lib_name, lib_relpath
                                )
                        else:
                            message_details['filepath'] = \
                                '[red]\\[{}][/red]/{}'.format(
                                    'unknown', lib_relpath
                                )
                    elif fmt == 'lib_name_only':
                        message_details['filepath'] = \
                            f'[magenta]\\[{lib_name}][/magenta]'
            else:  # no
                message_details['filepath'] = normpath(
                    os.path.relpath(info.filepath, self._cwd)
                )
        else:
            if self._is_external_lib(info.filepath):
                pass
            else:
                message_details['filepath'] = normpath(
                    os.path.relpath(info.filepath, self._cwd)
                )
        if (x := message_details['filepath']) and \
                not x.startswith(('../', '[')):
            message_details['filepath'] = './' + x
        
        message_details['lineno'] = str(info.lineno)
        
        # show message
        global _formatter
        # noinspection PyListCreation
        message_elements = []
        message_elements.append(
            _formatter.fmt_source(
                message_details['filepath'],
                message_details['lineno'],
                fmt_width=True
            )
        )
        message_elements.append(
            _formatter.fmt_separator('\t>>\t')
        )
        message_elements.append(
            _formatter.fmt_funcname(
                message_details['funcname'],
                fmt_width=True
            )
        )
        message_elements.append(
            _formatter.fmt_separator('\t>>\t')
        )
        if message_details['log_level']:
            message_elements.append(
                _formatter.fmt_level(
                    text='[bold][{}][/]'.format(
                        message_details['log_level'].upper()
                    ), level=message_details['log_level']
                )
            )
            message_elements.append(' ')
        if message_details['index']:
            message_elements.append(
                _formatter.fmt_index(
                    message_details['index']
                )
            )
            message_elements.append(' ')
        if message_details['divider_line']:
            message_elements.append(
                _formatter.fmt_divider(
                    message_details['divider_line']
                )
            )
            message_elements.append(' ')
        if 'l' in marks:
            message_details['message'] = message_details['message'].replace(
                ';\t', '\n'
            )
        message_elements.append(
            _formatter.fmt_message(
                message_details['message'],
                rich='r' in marks or 'l' in marks,
                multilines='l' in marks,
            )
        )
        if message_details['log_level'] and \
                message_details['log_level'] != 'trace':
            message_elements[-1] = _formatter.fmt_level(
                message_elements[-1],
                level=message_details['log_level']
            )
        
        return ''.join(message_elements)
    
    def _is_external_lib(self, filepath: str) -> bool:
        return not filepath.startswith(self._proj_root)


lk = LKLogger()
