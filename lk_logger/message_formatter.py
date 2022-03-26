"""
note:
    pytermgui color names for basic colors:
        there are some name changes between 4.1.0 and 4.2.0, for example the
        color number 8 before is 'grey', after is 'bright-black', number 9
        before is 'brightred', after is 'bright-red'.
        i'd like to keep pace with the latest version of ptg. so i'll use
        'bright-black', not 8 although it's not quite compatible insurance.
        *this decision remains to be changeable in the future.*
        ref: `pytermgui/colors.py > (var) XTERM_NAMED_COLORS`
    there are some markup issues should be known. see `gitbook > ptg-markup.md`.
"""
import re
from textwrap import indent
from typing import Union

from ._internal_debug import debug  # noqa


class MessageFormatter:
    # see `self.fmt_message`.
    _braket_pattern = re.compile(r'\[[-/@_a-z! ():]+]')
    
    def fmt_source(self, filepath: str, lineno: Union[int, str],
                   is_external_lib: bool = False, fmt_width=False) -> str:
        if fmt_width:
            text_a = f'{filepath}:{lineno}'
            text_b = self._fmt_width(text_a, min_width=16)
            additional_space = ' ' * (len(text_b) - len(text_a))
        else:
            additional_space = ''
        if is_external_lib:
            assert filepath.startswith('[')
            a, b = filepath[1:].split(']', 1)
            filepath = (
                '[bold {color}]\\[{a}]'
                '[bold blue]{b}[/]'.format(
                    a=a, b=b, color='red' if filepath.startswith('[unknown]')
                    else 'magenta'
                )
            )
            # FIXME: `tim.print('[blue][magenta]aaa[blue]bbb')`
            #   'bbb' color is invalid!
            #   below is a workaround.
            return (
                '{0}'
                '[bright-black]:[/]'
                '[bold blue]{1}{2}[/]'.format(
                    filepath, lineno, additional_space
                )
            )
        return (
            '[bold blue]{0}[/]'
            '[bright-black]:[/]'
            '[bold blue]{1}{2}[/]'.format(
                filepath, lineno, additional_space
            )
        )
    
    @staticmethod
    def fmt_separator(sep: str = ' >> ') -> str:
        return '[bright-black]{}[/]'.format(sep)
    
    def fmt_funcname(self, funcname: str, fmt_width=False) -> str:
        is_func = not funcname.startswith('<')
        if is_func:
            funcname += '()'
        else:
            funcname = funcname[1:-1]
        if fmt_width:
            funcname = self._fmt_width(
                funcname, min_width=8, incremental_unit=2
            )
        if is_func:
            return '[green]{}[/]'.format(funcname)
        else:
            return '[magenta]{}[/]'.format(funcname)
    
    @staticmethod
    def fmt_index(idx: Union[int, str]) -> str:
        return '[red]\\[{}][/]'.format(idx)
    
    @staticmethod
    def fmt_divider(div_: str) -> str:
        return '[yellow]{}[/]'.format(div_)
    
    def fmt_message(self, msg: str, rich: bool, multilines=False) -> str:
        if rich:
            if multilines:
                x = []
                for line in msg.splitlines():
                    if line.startswith('    '):
                        how_many = len(line) - len(line.lstrip())
                        spaces = line[:how_many]
                        rich_indent = spaces.replace(
                            '    ', '[bright-black]│[/]   '
                        )
                        x.append(rich_indent + line[how_many:])
                    else:
                        x.append(line)
                out = '\n' + indent('\n'.join(x), '    ')
                return out
            else:
                return msg.replace(';\t', '[bright-black];\t[/]')
        else:
            # FIXME: this is a workaround for pytermgui's parser.
            #   1. ptg cannot parse backslash, so we convert it to slash.
            #   2. ptg tries to parse any valid patterns, but ignore the
            #      invalid ones. we should add a backslash to the former, but
            #      do nothing to the latter.
            msg = msg.replace('\\', '■')
            # # msg = msg.replace('[', '\\[')
            msg = self._braket_pattern.sub(lambda x: '\\' + x.group(), msg)
            if '■' in msg:
                # # msg = msg.replace('■', '[magenta]/[/]')
                msg = re.sub('■+', lambda x: r'[magenta]{}[/]'.format(
                    '/' * len(x.group())), msg)
            # debug(f'{msg = }')
            if multilines:
                out = '\n' + indent(msg, '    ')
                return out
            else:
                return msg.replace(';\t', '[bright-black];\t[/]')
    
    @staticmethod
    def fmt_level(text: str, level: str) -> str:
        colors = {
            'trace': '',
            'debug': 'bright-black',
            'info' : 'bright-blue',
            'warn' : 'yellow',
            'error': 'bright-red',
            'fatal': 'bold bright-cyan @bright-red',
        }
        if c := colors.get(level):
            # debug('[{}]{}[/]'.format(c, text))
            return '[{}]{}[/fg]'.format(c, text)
        else:
            return text
    
    _width_cache = {}  # dict[int raw_width_of_text, int suggested_width]
    
    def _fmt_width(self, text: str,
                   min_width: int = None,
                   incremental_unit=4) -> str:
        
        def _fmt(text, suggested_width) -> str:
            return '{{:<{}}}'.format(suggested_width).format(text)
        
        if len(text) in self._width_cache:
            return _fmt(text, self._width_cache[len(text)])
        
        if min_width is None:
            min_width = incremental_unit
        if len(text) <= min_width:
            suggested_width = min_width
        else:
            increasing_part = len(text) - min_width
            if increasing_part % incremental_unit == 0:
                suggested_width = min_width + increasing_part
            else:
                suggested_width = min_width + (
                        increasing_part // incremental_unit + 1
                ) * incremental_unit
        self._width_cache[len(text)] = suggested_width
        return _fmt(text, suggested_width)
