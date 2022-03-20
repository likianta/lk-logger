import os
import sys
from inspect import currentframe

from pytermgui import parser
from pytermgui import tim

from .general import normpath
from .general import std_print
from .message_formatter import MessageFormatter
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


class PathHelper:
    @staticmethod
    def find_project_root() -> str:
        """ find personal-like project root.
        
        proposals:
            1. backtrack from current working dir to find a folder which has
               one of '.idea', '.git', etc. folders.
            2. iterate paths in sys.path, to find a folder which is parent of
               current working dir. (adopted)
               if there are more than one, choose which is shortest.
               if there is none, return current working dir.
        """
        cwd = normpath(os.getcwd())
        paths = tuple(
            x for x in map(normpath, map(os.path.abspath, sys.path))
            if cwd.startswith(x) and os.path.isdir(x)
        )
        if len(paths) == 0:
            return cwd
        elif len(paths) == 1:
            return paths[0]
        else:
            return min(paths, key=lambda x: len(x))
    
    @staticmethod
    def indexing_external_libs() -> dict:
        """
        return:
            dict[str path, str lib_name]
        """
        out = {}
        
        for path in reversed(sys.path):
            if not os.path.exists(path):
                continue
            for root, dirs, files in os.walk(path):
                root = normpath(root)
                out[root] = os.path.basename(root)
                
                for d in dirs:
                    if d.startswith(('.', '__')):
                        continue
                    if '-' in d or '.' in d:
                        continue
                    out[f'{root}/{d}'] = d
                
                # for f in files:
                #     name, ext = os.path.splitext(f)
                #     if ext not in ('.py', '.pyc', '.pyd', '.pyo', '.pyw'):
                #         continue
                #     if '-' in name or '.' in name:
                #         continue
                #     out[f'{root}/{f}'] = name
                break
        
        return out


class MarkupAnalyser:
    """
    readme:
        ~/docs/markup.zh.md
    
    markup list:
        :d  divider line
        :i  index
        :l  long / loose
        :p  parent layer
        :r  rich
        :s  short
        :t  tag
        :v  verbose / log level
    """
    
    def __init__(self):
        from re import compile
        self._mark_pattern = compile(r'[a-z]\d*')
    
    def analyse_markup(self, markup: str) -> list:
        """
        return:
            iterable[tuple[literal mark, int number]]
                mark:
                    a ':'-prefixed character.
                    literal: ':d', ':i', ':l', ':p', ':r', ':s', ':t', ':v'.
                number: 0, 1, 2, ...
        """
        marks = self._mark_pattern.findall(markup)  # list[str]
        out = []
        defaults = {
            'd': 0,
            'i': 1,
            'l': 0,
            'p': 1,
            'r': 0,
            's': 0,
            't': 0,
            'v': 0,
        }
        for m in marks:
            if len(m) == 1:
                # out.append((m, None))
                out.append((m, defaults[m]))
            else:
                out.append((m[0], int(m[1:])))
        return out


class LKLogger:
    
    def __init__(self):
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
    
    # noinspection PyUnresolvedReferences
    def log(self, *args, **_):
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
        has_rich_mark = False
        
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
                    for m, i in marks:
                        if m == 'd':
                            message_details['divider_line'] = '-' * 80
                        elif m == 'i':
                            if i == 0:
                                self._counter = 0
                            self._counter += 1
                            message_details['index'] = str(self._counter)
                        elif m == 'l':
                            pass
                        elif m == 'p':
                            traceback_level = i
                        elif m == 'r':
                            has_rich_mark = True
                        elif m == 's':
                            pass
                        elif m == 'v':
                            message_details['log_level'] = (
                                'trace', 'debug', 'info',
                                'warn', 'error', 'fatal'
                            )[i]
        
        info = sourcemap.get_sourcemap(
            frame=currentframe().f_back,
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
                assert len(varnames) == len(args), (varnames, args)
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
                    for lib_path in reversed(self._external_libs):
                        if info.filepath.startswith(lib_path):
                            lib_name = self._external_libs[lib_path]
                            lib_relpath = info.filepath[len(lib_path):] or \
                                          os.path.basename(info.filepath)
                            break
                    else:
                        lib_name = ''
                        lib_relpath = info.filepath.lstrip('./')
                    
                    if fmt == 'pretty_relpath':
                        if lib_name:
                            message_details['filepath'] = '[{}]/{}'.format(
                                lib_name, lib_relpath)
                        else:
                            message_details['filepath'] = '[{}]/{}'.format(
                                'unknown', lib_relpath)
                    elif fmt == 'lib_name_only':
                        message_details['filepath'] = f'[{lib_name}]'
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
        if (x := message_details['filepath']) and not x.startswith('../'):
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
            _formatter.fmt_separator(' : ')
        )
        message_elements.append(
            _formatter.fmt_funcname(
                message_details['funcname'],
                fmt_width=True
            )
        )
        message_elements.append(
            _formatter.fmt_separator(' : ')
        )
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
        message_elements.append(
            _formatter.fmt_message(
                message_details['message'],
                has_rich_mark
            )
        )
        
        tim.print(''.join(message_elements))
    
    def _is_external_lib(self, filepath: str) -> bool:
        return not filepath.startswith(self._proj_root)


lk = LKLogger()
