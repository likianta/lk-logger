from __future__ import annotations

import typing as t
from textwrap import indent
from time import localtime
from time import strftime as _strftime

from ._print import debug  # noqa

strftime = lambda t: _strftime('%H:%M:%S', localtime(t)) \
    if t is not None else ''


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
    def markup(*markups: tuple[str, str]) -> str:
        """
        this method produces the final strings that could be directly printed.

        args:
            markups: tuple[tuple[str text, str mark], ...]
                mark:
                    any valid patterns of pytermgui markups. for example, 'red',
                    'bold', 'dim', '#00FF00', ...
                    ps: mark allows empty.
        """
        out = []
        for text, mark in markups:
            if mark:
                out.append('[{}]{}[/]'.format(mark, text))
            else:
                out.append(text)
        return ''.join(out)
    
    # -------------------------------------------------------------------------
    
    def fmt_source(self, filepath: str, lineno: t.Union[int, str],
                   is_external_lib: bool = False, fmt_width=False) -> str:
        if fmt_width:
            text_a = f'{filepath}:{lineno}'
            text_b = self._fmt_width(text_a, min_width=12)
            additional_space = ' ' * (len(text_b) - len(text_a))
        else:
            additional_space = ''
        if is_external_lib:
            assert filepath.startswith('[')
            a, b = filepath[1:].split(']', 1)
            filepath = self.markup(
                ('\\[{}]'.format(a),
                 'bold {}'.format('red' if filepath.startswith('[unknown]')
                                  else 'magenta')),
                (f'{b}', 'bold blue'),
            )
            return self.markup(
                (filepath, ''),
                (':', 'bright_black'),
                (str(lineno), 'bold blue'),
                (additional_space, ''),
            )
        else:
            return self.markup(
                (filepath.replace('[', '\\['), 'bold blue'),
                (':', 'bright_black'),
                (str(lineno), 'bold blue'),
                (additional_space, ''),
            )
    
    def fmt_separator(self, sep: str = ' >> ', color='bright_black') -> str:
        return self.markup((sep, color))
    
    def fmt_funcname(self, funcname: str, fmt_width=False) -> str:
        is_func = not funcname.startswith('<')
        if is_func:
            funcname += '()'
        else:
            funcname = funcname[1:-1]
        if fmt_width:
            funcname = self._fmt_width(
                funcname, min_width=8, unit_spaces=4
            )
        if is_func:
            return self.markup((funcname, 'green'))
        else:
            return self.markup((funcname, 'magenta'))
    
    def fmt_index(self, idx: int) -> str:
        return self.markup(
            (f'[{idx}]', 'grey50' if idx == 0 else 'red')
        )
    
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
    
    def fmt_divider(self, div_: str = '-' * 64) -> str:
        return self.markup((div_, 'yellow'))
    
    def fmt_message(self, arguments: t.Iterable[t.Any], varnames: tuple[str],
                    rich: bool, expand=False, separator=';   ') -> str:
        """
        notice the process sequence:
            1. expand
            2. varnames
            3. rich
        """
        if expand:
            from rich.pretty import pretty_repr
            arguments = tuple(map(pretty_repr, arguments))
        if varnames:
            arguments = self._mix_arguments_with_varnames(arguments, varnames)
        else:
            arguments = map(str, arguments)
        if not rich:
            arguments = (x.replace('[', '\\[') for x in arguments)
        
        if expand:
            return '\n' + indent('\n'.join(arguments), '    ')
        else:
            return self.markup((separator, 'bright_black')).join(arguments)
    
    def fmt_level(self, level: str, text='{TAG}') -> str:
        if level == 'trace':
            return ''
        labels = {
            'trace': '',
            'debug': '[DEBUG]',
            'info' : '[ INFO]',
            'warn' : '[ WARN]',
            'error': '[ERROR]',
            'fatal': '[FATAL]',
        }
        colors = {
            'trace': '',
            'debug': 'grey50',
            'info' : 'blue',
            'warn' : 'yellow',
            'error': 'red',
            'fatal': 'bold #ffffff on red',
        }
        text = text.format(TAG=labels[level])
        return self.markup((text, colors[level]))
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _mix_arguments_with_varnames(
            arguments: t.Sequence[str], varnames: tuple[str, ...],
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
    
    @staticmethod
    def _fmt_width(text: str, min_width: int = None, unit_spaces=4) -> str:
        if len(text) <= min_width:
            return text.ljust(min_width)
        else:
            from math import ceil
            return text.ljust(ceil(len(text) / unit_spaces) * unit_spaces)
