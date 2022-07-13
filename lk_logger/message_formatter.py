from __future__ import annotations

from textwrap import indent
from typing import Union

from ._internal_debug import debug  # noqa


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
    
    def fmt_source(self, filepath: str, lineno: Union[int, str],
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
    
    def fmt_index(self, idx: Union[int, str]) -> str:
        return self.markup(
            (f'[{idx}]', 'bright_black' if idx == 0 or idx == '0' else 'red')
        )
    
    def fmt_divider(self, div_: str) -> str:
        return self.markup((div_, 'yellow'))
    
    def fmt_message(self, msg_frags: list[str], rich: bool, expand=False,
                    separator=';   ') -> str:  # FIXME
        if not rich:
            msg_frags = (x.replace('[', '\\[') for x in msg_frags)
        if expand:
            return '\n' + indent('\n'.join(msg_frags), '    ')
        else:
            return self.markup((separator, 'bright_black')).join(msg_frags)
    
    def fmt_level(self, text: str, level: str) -> str:
        colors = {
            'trace': '',
            'debug': 'bright_black',
            'info' : 'blue',
            'warn' : 'yellow',
            'error': 'red',
            'fatal': 'bold #ffffff on red',
        }
        return self.markup((text, colors[level]))
    
    # -------------------------------------------------------------------------
    
    @staticmethod
    def _fmt_width(text: str, min_width: int = None, unit_spaces=4) -> str:
        if len(text) <= min_width:
            return text.ljust(min_width)
        else:
            from math import ceil
            return text.ljust(ceil(len(text) / unit_spaces) * unit_spaces)
