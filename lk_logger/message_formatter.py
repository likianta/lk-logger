import typing as t
from dataclasses import dataclass
from functools import partial
from io import StringIO
from math import ceil
from textwrap import indent
from time import localtime
from time import strftime as _strftime
from traceback import format_exception

import rich
# noinspection PyProtectedMember
from rich._inspect import Inspect
from rich.console import RenderableType
# from rich.padding import Padding
from rich.pretty import pretty_repr
from rich.text import Text
from rich.traceback import Traceback

from ._print import debug  # noqa
from .console import console

strftime = lambda t: (t and _strftime('%H:%M:%S', localtime(t))) or ''


@dataclass
class MarkupText:
    text: str
    mark: str = None


class T:
    Level = t.Literal['trace', 'debug', 'info', 'warning', 'error', 'fatal']
    RichText = Text


class Color:  # TODO: not used yet (and not ready).
    SEPARATOR = 'bright_black'
    
    # time
    TIME_START = 'green'
    DURATION_S = 'green'
    DURATION_M = 'green_yellow'
    DURATION_L = 'yellow'
    DURATION_XL = 'red'
    
    # verbosity
    V_DEBUG = 'grey50'
    V_INFO = 'blue'
    V_WARNING = 'yellow'
    V_ERROR = 'red'
    V_FATAL = 'bold #ffffff on red'


class MessageFormatter:
    
    @staticmethod
    def markup(*markups: t.Tuple[str, str]) -> T.RichText:
        # text = Text()
        # for t, m in markups:
        #     text.append(t, m)
        # return text
        return Text.assemble(*markups)
    
    # -------------------------------------------------------------------------
    
    def fmt_divider(
        self,
        pattern: str = '-',
        length: int = None,
        context: t.Tuple[T.RichText, ...] = None,
    ) -> T.RichText:
        if length is None:
            if context:
                con_width = console.width - 8
                length = min((con_width, 200)) - sum(map(len, context))
                # if length > 80: length = 80
                if length <= 0:
                    if len(context) > 1 and context[-1]:
                        # strip the last element and try again
                        length = con_width - sum(map(len, context[:-1]))
                        if length > 0:
                            # return self.markup((
                            #     pattern * length + '\n' + pattern * 3,
                            #     'yellow'
                            # ))
                            return self.markup(
                                (pattern * length, 'yellow'),
                                ('\n', ''),
                                (pattern * 3, 'yellow dim')
                            )
                        else:
                            length = 3
                    else:
                        # raise ValueError('invalid context', context)
                        length = 80
            else:
                length = 80
        return self.markup((pattern * length, 'yellow'))
    
    @staticmethod
    def fmt_exception(e: BaseException, show_locals=False) -> Traceback:
        trace = Traceback.from_exception(
            type(e), e, e.__traceback__,
            show_locals=show_locals
        )
        return trace
    
    def fmt_funcname(self, funcname: str, fmt_width=False) -> T.RichText:
        is_func = not funcname.startswith('<')
        if is_func:
            funcname += '()'
        else:
            funcname = funcname[1:-1]
        if fmt_width:
            funcname = self._fmt_width(
                funcname, min_width=8, step_space=4
            )
        return Text(funcname, 'green' if is_func else 'magenta')
    
    @staticmethod
    def fmt_index(idx: int) -> T.RichText:
        return Text(f'[{idx}]', 'grey50' if idx == 0 else 'red')
    
    _level_2_color = {
        'trace': '',
        'debug': 'grey50',
        'info' : 'blue',
        'warn' : 'yellow',
        'error': 'red',
        'fatal': 'bold #ffffff on red',
    }
    _level_2_label = {
        'trace': '',
        'debug': '[DEBUG]',
        'info' : '[ INFO]',
        'warn' : '[ WARN]',
        'error': '[ERROR]',
        'fatal': '[FATAL]',
    }
    
    def fmt_level(self, level: T.Level) -> t.Optional[T.RichText]:
        if level == 'trace': return None
        label = self._level_2_label[level]
        color = self._level_2_color[level]
        return Text(label, color)
    
    def fmt_message(
        self,
        arguments: t.Iterable[t.Any],
        varnames: t.Tuple[str, ...],
        rich: bool,
        expand_level: int = 0,
        separator: T.RichText = None,
        overall_style: T.Level = None,
    ) -> T.RichText:
        """
        notice the process sequence:
            1. expand
            2. varnames
            3. rich
        """
        if expand_level == 1:
            arguments = map(self._expand_object, arguments)
        elif expand_level == 2:
            arguments = map(self._inspect_object, arguments)
        if varnames:
            arguments = self._mix_arguments_with_varnames(
                tuple(arguments), varnames
            )
        else:
            arguments = map(str, arguments)
        if not rich:
            arguments = (x.replace('[', '\\[') for x in arguments)
        
        # ---------------------------------------------------------------------
        
        if overall_style:
            parse_text = partial(
                Text.from_markup,
                style=self._level_2_color[overall_style]
            )
        else:
            # parse_text = Text.from_markup
            parse_text = partial(
                Text.from_markup,
                style='default'
            )
        
        if expand_level:
            _indent = partial(indent, prefix='    ')
            text = Text.assemble(
                Text('\n'),
                Text('\n').join(
                    map(parse_text, map(_indent, arguments))
                )
            )
        else:
            # text = Text(separator, 'bright_black').join(
            #     map(Text.from_markup, arguments)
            # )
            assert separator
            text = separator.join(
                map(parse_text, arguments)
            )
        
        return text
    
    def fmt_scoped_index(
        self,
        idx: int,
        uid: str,
        color: str = ''
    ) -> T.RichText:
        return self.markup(
            (f'[{uid}]', f'{color} dim'),
            (f'[{idx}]', f'{color}'),
        )
    
    def fmt_separator(
        self,
        sep: str = ' >> ',
        color='bright_black'
    ) -> T.RichText:
        return self.markup((sep, color))
    
    def fmt_source(
        self, filepath: str, lineno: t.Union[int, str],
        is_external_lib: bool = False, fmt_width=False
    ) -> T.RichText:
        text = Text()
        
        if is_external_lib:
            assert filepath.startswith('[')
            a, b = filepath[1:].split(']', 1)
            text.append(f'[{a}]', 'bold {}'.format(
                'red' if filepath.startswith('[unknown]') else 'magenta'
            ))
            text.append(b, 'bold blue')
        else:
            text.append(filepath, 'bold blue')
        
        text.append(':', 'bright_black')
        text.append(str(lineno), 'bold blue')
        
        if fmt_width:
            text_a = f'{filepath}:{lineno}'
            text_b = self._fmt_width(text_a, min_width=12)
            additional_space = ' ' * (len(text_b) - len(text_a))
            text.append(additional_space)
        
        return text
    
    @staticmethod
    def fmt_time(start: float, end: float = None, color_s='green') -> str:
        if end is None:
            return '[{}]\\[{}][/]'.format(color_s, strftime(start))
        
        diff = end - start  # float >= 0
        
        color_s: str
        color_e: str
        color_d: str
        
        if diff < 0.500:
            color_e = 'green'
            color_d = 'green'
        elif diff < 1.000:
            color_e = 'green'
            color_d = 'green_yellow'
        elif diff < 5.000:
            color_e = 'yellow'
            color_d = 'yellow'
        else:
            color_e = 'red'
            color_d = 'red'
        if int(start) == int(end):
            color_e += ' dim'
            color_d += ' dim'
        
        # better diff
        if diff < 1.000:
            diff = '{:.0f}ms'.format(diff * 1000)
        else:
            diff = '{:.1f}s'.format(diff)
        
        return (
            '[{color_s}]\\[{start}][/]'
            '[grey50] -> [/]'
            '[{color_e}]\\[{end}][/] '
            '[{color_d}]({diff:>5})[/]'.format(
                start=strftime(start),
                end=strftime(end),
                diff=diff,
                color_s=color_s,
                color_e=color_e,
                color_d=color_d,
            )
        )
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _expand_object(obj: t.Any) -> str:
        if isinstance(obj, Exception):
            return '\n' + indent(''.join(format_exception(obj)), '│ ')
        else:
            return pretty_repr(obj)
    
    @staticmethod
    def _inspect_object(obj: t.Any) -> str:
        def to_str(rich_obj: RenderableType) -> str:
            """
            convert rich renderable type to plain (raw) string.
            """
            s = StringIO()
            rich.print(rich_obj, file=s)
            s.seek(0)
            return s.read()
    
        return to_str(Inspect(obj))
    
    @staticmethod
    def _mix_arguments_with_varnames(
        arguments: t.Sequence[str],
        varnames: t.Tuple[str, ...],
    ) -> t.Iterable[str]:
        if not arguments:
            return ()
        try:
            assert len(varnames) == len(arguments), (varnames, arguments)
        except AssertionError:
            # debug('failed extracting varnames')
            return map(str, arguments)
        else:
            return (f'{v} = {a}' if v else str(a)
                    for v, a in zip(varnames, arguments))
    
    # @staticmethod
    # def _mix_arguments_with_varnames(
    #         arguments: t.Sequence[str],
    #         varnames: t.Tuple[str, ...],
    # ) -> t.Iterator[t.Tuple[str, t.Any]]:
    #     if not arguments:
    #         return
    #     try:
    #         assert len(varnames) == len(arguments), (varnames, arguments)
    #     except AssertionError:
    #         # debug('failed extracting varnames')
    #         for arg in arguments:
    #             yield '', arg
    #     else:
    #         yield from zip(varnames, arguments)
    
    @staticmethod
    def _fmt_width(text: str, min_width: int = None, step_space=4) -> str:
        if len(text) <= min_width:
            return text.ljust(min_width)
        else:
            return text.ljust(ceil(len(text) / step_space) * step_space)


formatter = MessageFormatter()
