import os
from inspect import currentframe

from pytermgui import tim

from ._internal_debug import debug  # noqa
from .general import normpath
from .general import std_print
from .markup import MarkupAnalyser
from .message_formatter import MessageFormatter
from .path_helper import PathHelper
from .sourcemap import sourcemap

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
    
    def reset(self):
        self.show_source = True
        self.show_varnames = False
        self.show_external_lib = True
        self.path_format_for_external_lib = 'pretty_relpath'


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
    
    def configure(self, clear_pre_configured=False, **kwargs):
        if clear_pre_configured:
            self._config.reset()
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
        # debug(msg)
        std_print(msg)
    
    def fmt(self, *args, **_):
        return self._main(currentframe().f_back, *args)
    
    # noinspection PyUnresolvedReferences
    def _main(self, frame, *args) -> str:
        global _formatter
        
        elements = {
            'filepath'    : '',
            'lineno'      : '0',
            'funcname'    : '',
            'log_level'   : '',
            'index'       : '',
            'divider_line': '',
            'arguments'   : [],
        }
        
        is_external_lib = False
        marks = {}
        markup_pos = 0  # 0 not exist, 1 for begining, -1 for ending.
        show_varnames = self._config.show_varnames
        traceback_level = 0  # int[default 1]
        
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
                marks = self._markup_analyser.analyse(markup)  # type: dict
                if marks:
                    if 'd' in marks:
                        elements['divider_line'] = '-' * 80
                    if 'i' in marks:
                        if marks['i'] == 0:  # reset counter
                            self._counter = 0
                            if args:
                                self._counter += 1
                            else:
                                elements['arguments'].append(
                                    '(index reset)')
                        else:
                            self._counter += 1
                        elements['index'] = str(self._counter)  # 0 based
                    if 'l' in marks:
                        args = tuple(map(_formatter.expand_node, args))
                    if 'p' in marks:
                        traceback_level = marks['p']
                    if 'r' in marks and 'l' not in marks:
                        args = tuple(map(tim.parse, map(str, args)))
                    if 's' in marks:
                        # s0: disable `show_varnames`
                        # s1: disable all, equivalent to `std_print` (a slight
                        #   difference is that preserves rendered separators).
                        # note: to make sure rick args take effect, `marks['s']`
                        #   must be checked AFTER `marks['r']`.
                        if marks['s'] == 0:
                            show_varnames = False
                        elif marks['s'] == 1:
                            # # return ';\t'.join(map(str, args))
                            return _formatter.markup(
                                (';\t', 'bright-black')
                            ).join(map(str, args))
                        # TODO: else: fallback to `s0`.
                    if 'v' in marks:
                        elements['log_level'] = (
                            'trace', 'debug', 'info',
                            'warn', 'error', 'fatal'
                        )[marks['v']]
        
        info = sourcemap.get_sourcemap(
            frame=frame,
            traceback_level=traceback_level,
            advanced=show_varnames,
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
                    elements['arguments'].extend(map(str, args))
                else:
                    # organize args
                    for n, a in zip(varnames, args):
                        elements['arguments'].append(
                            f'{n} = {a}' if n else str(a)
                        )
            else:
                elements['arguments'].extend(map(str, args))
        
        elements['funcname'] = info.funcname
        
        # show external lib?
        if self._config.show_external_lib:
            # is external lib?
            if self._is_external_lib(info.filepath):  # yes
                is_external_lib = True
                # path format
                fmt = self._config.path_format_for_external_lib
                if fmt == 'relpath':
                    elements['filepath'] = normpath(
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
                            elements['filepath'] = \
                                '[{}]/{}'.format(lib_name, lib_relpath)
                        else:
                            elements['filepath'] = \
                                '[{}]/{}'.format('unknown', lib_relpath)
                    elif fmt == 'lib_name_only':
                        elements['filepath'] = f'[{lib_name}]'
            else:  # no
                elements['filepath'] = normpath(
                    os.path.relpath(info.filepath, self._cwd)
                )
        else:
            if self._is_external_lib(info.filepath):
                pass  # is_external_lib = True ?
            else:
                elements['filepath'] = normpath(
                    os.path.relpath(info.filepath, self._cwd)
                )
        if (x := elements['filepath']) and \
                not x.startswith(('../', '[')):
            elements['filepath'] = './' + x
        
        elements['lineno'] = str(info.lineno)
        
        # ---------------------------------------------------------------------
        
        # show message
        # noinspection PyListCreation
        message_elements = []
        #   element sequence:
        #       1. source (filename & lineno)
        #       2. funcname
        #       3. log_level
        #       4. index
        #       5. divider_line
        #       6. arguments
        # 1. source
        message_elements.append(
            _formatter.fmt_source(
                elements['filepath'],
                elements['lineno'],
                is_external_lib=is_external_lib,
                fmt_width=True
            )
        )
        message_elements.append(
            _formatter.fmt_separator('\t>>    ')
        )
        # 2. funcname
        message_elements.append(
            _formatter.fmt_funcname(
                elements['funcname'],
                fmt_width=True
            )
        )
        message_elements.append(
            _formatter.fmt_separator('\t>>    ')
        )
        # 3. log_level
        if elements['log_level']:
            message_elements.append(
                _formatter.fmt_level(
                    text='[{tag}]{spacing}'.format(
                        tag=elements['log_level'].upper(),
                        spacing='\t' if elements['log_level'] != 'fatal'
                        else '   '  # to be explained below
                    ), level=elements['log_level']
                )
            )
            r''' about placeholder `spacing`:
            
                q: why use '\t'?
                a: '\t' aligns its following message more tidier than spaces.
                   illustration (dot means whitespaces):
                        use ' '                 use '\t'
                        [TRACE].hello world     [TRACE]..hello world
                        [DEBUG].hello world     [DEBUG]..hello world
                        [INFO].hello world      [INFO]...hello world
                        [WARN].hello world      [WARN]...hello world
                        [FATAL].hello world     [FATAL]..hello world
                                                        (↑ looks more pretty)
            
                q: why FATAL doesn't use '\t'?
                a: FATAL's effect is white text on red background.
                   the red background effect will be invalid if we use '\t'.
                   so we have to '   ' instead.
                   the letter number of '   ' depends on the width of its
                   leading content. currently it's `4 * <integer> + 2 + <7_(the_
                   length_of_'[FATAL]'>`. see also `./message_formatter
                   : MessageFormatter : fmt_source : (param) min_width`.
            '''
        # 4. index
        if elements['index']:
            message_elements.append(
                _formatter.fmt_index(
                    elements['index']
                )
            )
            message_elements.append(' ')
        # 5. divider_line
        if elements['divider_line']:
            message_elements.append(
                _formatter.fmt_divider(
                    elements['divider_line']
                )
            )
            message_elements.append(' ')
        # 6. arguments
        message_elements.append(
            _formatter.fmt_message(
                elements['arguments'],
                rich='r' in marks or 'l' in marks,
                expand='l' in marks,
            )
        )
        if elements['log_level'] and \
                elements['log_level'] != 'trace':
            message_elements[-1] = _formatter.fmt_level(
                message_elements[-1],
                level=elements['log_level']
            )
        if elements['index'] == '0':
            message_elements[-1] = _formatter.markup(
                (message_elements[-1], 'bright-black')
            )
        
        return ''.join(message_elements)
    
    def _is_external_lib(self, filepath: str) -> bool:
        return not filepath.startswith(self._proj_root)


lk = LKLogger()
