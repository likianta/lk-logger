from __future__ import annotations

import os
from inspect import currentframe

from ._internal_debug import debug  # noqa
from .console import con_print
from .general import normpath
from .markup import MarkupAnalyser
from .message_formatter import MessageFormatter
from .sourcemap import sourcemap

__all__ = ['LKLogger', 'lk']

formatter = MessageFormatter()
markup_analyser = MarkupAnalyser()


class T:  # Typehint
    from rich.console import RenderableType
    from .markup import TMarks as Marks


class LKLogger:
    
    def __init__(self):
        # self._cache = {}  # TODO: be complete in next version
        # #   dict[tuple k, namedtuple v]
        # #       k: (filepath, lineno)
        # #       v: ...
        from .config import LoggingConfig
        self._config = LoggingConfig()
        self._counter = 0
        self._cwd = normpath(os.getcwd())
        
        # lazy loaded
        self.__external_libs = None
        self.__proj_root = None
    
    def configure(self, clear_old=False, **kwargs) -> None:
        if clear_old:
            self._config.reset()
        self._config.update(**kwargs)
    
    @property
    def _proj_root(self) -> str:
        if self.__proj_root is None:
            from .path_helper import find_project_root
            self.__proj_root = find_project_root()
        return self.__proj_root
    
    @property
    def _external_libs(self) -> dict[str, str]:
        if self.__external_libs is None:
            from .path_helper import indexing_external_libs
            self.__external_libs = indexing_external_libs()
        return self.__external_libs
    
    # -------------------------------------------------------------------------
    
    def log(self, *args, **kwargs) -> None:
        msg = self._build_message(currentframe().f_back, *args)
        # debug(msg)
        con_print(msg, **kwargs)
    
    def fmt(self, *args, **_) -> str:
        return str(self._build_message(currentframe().f_back, *args))
    
    def _build_message(self, frame, *args) -> T.RenderableType:
        global formatter, markup_analyser
        
        info = {
            'arguments'        : [],
            'file_path'        : '',
            'function_name'    : '',
            'index'            : '',
            'is_external_lib'  : False,
            'is_rich_text'     : False,
            'line_number'      : '0',
            'multiple_lines'   : False,
            'log_level'        : '',
            'show_divider_line': False,
            'show_varnames'    : self._config.show_varnames,
            'traceback_level'  : 0,
        }
        
        def analyse_markup() -> tuple[int, T.Marks]:
            nonlocal args
            
            markup_pos: int
            marks: T.Marks
            
            #   0: not exist; 1: the first place; -1: the last place
            is_markup = markup_analyser.is_valid_markup
            if args \
                    and isinstance(args[0], str) \
                    and args[0].startswith(':') \
                    and is_markup(args[0]):
                markup_pos = 1
                markup, args = args[0], args[1:]
            elif len(args) > 1 \
                    and isinstance(args[-1], str) \
                    and args[-1].startswith(':') \
                    and is_markup(args[-1]):
                markup_pos = -1
                markup, args = args[-1], args[:-1]
            else:
                markup_pos = 0
                return markup_pos, {}
            
            assert markup_pos and markup
            
            # analyse markup
            marks = markup_analyser.analyse(markup)
            if not marks:
                raise Exception('Unexpected result from markup analyser',
                                markup, marks)
                # # return markup_pos, {}
            if 'd' in marks:
                info['show_divider_line'] = True
            # TODO: if 'e' in marks: ...  # not implemented yet
            if 'i' in marks:
                # TODO: add total-count feature
                if marks['i'] == 0:  # reset counter
                    self._counter = 0
                    if args:
                        self._counter += 1
                    else:
                        info['arguments'].append('(index reset)')
                else:
                    self._counter += 1
                info['index'] = str(self._counter)  # 0 based
            if 'l' in marks:
                info['multiple_lines'] = True
            if 'p' in marks:
                info['traceback_level'] = marks['p']
            if 'r' in marks and 'l' not in marks:
                info['is_rich_text'] = True
            if 's' in marks:
                # s0: disable `show_varnames`
                # s1: disable all, equivalent to `default_print`.
                # note: to make sure rick args take effect, `marks['s']` must
                #   be checked AFTER `marks['r']`.
                if marks['s'] == 0:
                    info['show_varnames'] = False
                else:  # FIXME: this is a temporary solution
                    return markup_pos, {'s': 1}
            if 'v' in marks:
                info['log_level'] = (
                    'trace', 'debug', 'info', 'warn', 'error', 'fatal'
                )[marks['v']]
            
            return markup_pos, marks
        
        markup_pos, marks = analyse_markup()
        if marks.get('s') == 1:
            return (
                '[dim]{separator}[/]'.format(
                    separator=self._config.separator
                ).join(map(str, args))
            )
        
        srcmap = sourcemap.get_sourcemap(
            frame=frame,
            traceback_level=info['traceback_level'],
            advanced=info['show_varnames'],
        )
        
        def reformat_arguments_with_varnames(markup_pos: int):
            """
            update the following info:
                info['arguments']
            """
            if args:
                if info['show_varnames']:
                    if markup_pos == 0:
                        varnames = srcmap.varnames
                    elif markup_pos == 1:
                        varnames = srcmap.varnames[1:]
                    else:
                        varnames = srcmap.varnames[:-1]
                    try:
                        assert len(varnames) == len(args), (varnames, args)
                    except AssertionError:
                        # debug('failed extracting varnames')
                        info['arguments'].extend(map(str, args))
                    else:
                        # organize args
                        for n, a in zip(varnames, args):
                            info['arguments'].append(
                                f'{n} = {a}' if n else str(a)
                            )
                else:
                    info['arguments'].extend(map(str, args))
        
        reformat_arguments_with_varnames(markup_pos)
        
        info['function_name'] = srcmap.funcname
        
        def reformat_source_for_external_lib():
            """
            update the following info:
                info['is_external_lib']
                info['file_path']
                info['line_number']
            """
            # show external lib?
            if self._config.show_external_lib:
                # is external lib?
                if self._is_external_lib(srcmap.filepath):  # yes
                    info['is_external_lib'] = True
                    # path format
                    fmt = self._config.path_style_for_external_lib
                    if fmt == 'relpath':
                        info['file_path'] = normpath(
                            os.path.relpath(srcmap.filepath, self._cwd)
                        )
                    else:
                        for lib_path in sorted(
                                self._external_libs, reverse=True
                        ):
                            if srcmap.filepath.startswith(lib_path):
                                lib_name = self._external_libs[lib_path].lower()
                                lib_relpath = (
                                        srcmap.filepath[
                                        len(lib_path):].lstrip('./') or
                                        os.path.basename(srcmap.filepath)
                                )
                                break
                        else:
                            lib_name = ''
                            lib_relpath = srcmap.filepath.lstrip('./')
                        
                        # debug(lib_name, lib_relpath)
                        
                        if fmt == 'pretty_relpath':
                            if lib_name:
                                info['file_path'] = \
                                    '[{}]/{}'.format(lib_name, lib_relpath)
                            else:
                                info['file_path'] = \
                                    '[{}]/{}'.format('unknown', lib_relpath)
                        elif fmt == 'lib_name_only':
                            info['file_path'] = f'[{lib_name}]'
                else:  # no
                    info['file_path'] = normpath(
                        os.path.relpath(srcmap.filepath, self._cwd)
                    )
            else:
                if self._is_external_lib(srcmap.filepath):
                    pass  # info['is_external_lib'] = True ?
                else:
                    info['file_path'] = normpath(
                        os.path.relpath(srcmap.filepath, self._cwd)
                    )
            if (x := info['file_path']) and \
                    not x.startswith(('../', '[')):
                info['file_path'] = './' + x
            
            info['line_number'] = str(srcmap.lineno)
        
        reformat_source_for_external_lib()
        
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
            formatter.fmt_source(
                info['file_path'],
                info['line_number'],
                is_external_lib=info['is_external_lib'],
                fmt_width=True
            )
        )
        message_elements.append(
            formatter.fmt_separator('  >>  ')
        )
        # 2. funcname
        message_elements.append(
            formatter.fmt_funcname(
                info['function_name'],
                fmt_width=True
            )
        )
        message_elements.append(
            formatter.fmt_separator('  >>  ')
        )
        # 3. log_level
        if info['log_level']:
            message_elements.append(
                formatter.fmt_level(
                    text='[{tag}]{sep}'.format(
                        tag=info['log_level'].upper(),
                        sep='\t' if info['log_level'] != 'fatal' else '     '
                        #   to be explained below...
                    ), level=info['log_level']
                )
            )
            r''' about placeholder `sep`:
            
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
                   so we have to '     ' instead.
                   the letter number of '   ' depends on the width of its
                   leading content. currently it's `4 * <integer> + 2 + <7 (the
                   length of '[FATAL]'>`. see also `./message_formatter
                   : MessageFormatter : fmt_source : (param) min_width`.
            '''
        # 4. index
        if info['index']:
            message_elements.append(
                formatter.fmt_index(
                    info['index']
                )
            )
            message_elements.append(' ')
        # 5. divider_line
        if info['show_divider_line']:
            message_elements.append(
                # PERF: use auto width?
                formatter.fmt_divider('-' * 80)
            )
            message_elements.append(' ')
        # 6. arguments
        message_elements.append(
            formatter.fmt_message(
                info['arguments'],
                rich=info['is_rich_text'],
                expand=info['multiple_lines'],
                separator=self._config.separator
            )
        )
        if info['log_level'] and \
                info['log_level'] != 'trace':
            message_elements[-1] = formatter.fmt_level(
                message_elements[-1],
                level=info['log_level']
            )
        if info['index'] == '0':
            message_elements[-1] = formatter.markup(
                (message_elements[-1], 'dim')
            )
        
        return ''.join(message_elements)
    
    def _is_external_lib(self, filepath: str) -> bool:
        return not filepath.startswith(self._proj_root)


lk = LKLogger()
