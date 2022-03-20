from textwrap import indent
from typing import Union


class MessageFormatter:
    
    def fmt_source(self, filepath: str, lineno: Union[int, str],
                   fmt_width=False) -> str:
        if fmt_width:
            text_a = f'{filepath}:{lineno}'
            text_b = self._fmt_width(text_a, min_width=20)
            additional_space = ' ' * (len(text_b) - len(text_a))
        else:
            additional_space = ''
        return '[bold cyan]{}[/][dim]:[/][cyan]{}{}[/]'.format(
            filepath, lineno, additional_space
        )
    
    @staticmethod
    def fmt_separator(sep: str = ' >> ') -> str:
        return '[grey]{}[/]'.format(sep)
    
    def fmt_funcname(self, funcname: str, fmt_width=False) -> str:
        is_func = not funcname.startswith('<')
        if is_func:
            funcname += '()'
        else:
            funcname = funcname[1:-1]
        if fmt_width:
            funcname = self._fmt_width(
                funcname, min_width=10, incremental_unit=2
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
    
    @staticmethod
    def fmt_message(msg: str, rich: bool, multilines=False) -> str:
        if rich:
            if multilines:
                x = []
                for line in msg.splitlines():
                    if line.startswith('    '):
                        how_many = len(line) - len(line.lstrip())
                        spaces = line[:how_many]
                        rich_indent = spaces.replace('    ', '[236]│[/]   ')
                        x.append(rich_indent + line[how_many:])
                    else:
                        x.append(line)
                out = '\n' + indent('\n'.join(x), '    ')
                return out
            else:
                return msg.replace(';\t', '[grey];\t[/]')
        else:
            if multilines:
                out = msg.replace('[', '\\[')
                out = '\n' + indent(out, '    ')
                return out
            else:
                return msg.replace('[', '\\[').replace(';\t', '[grey];\t[/]')
    
    @staticmethod
    def fmt_level(text: str, level: str) -> str:
        colors = {
            'trace': '',
            'debug': 'dim',
            'info' : 'brightblue',
            'warn' : 'yellow',
            'error': 'brightred',
            'fatal': 'red',
        }
        if c := colors.get(level):
            return '[{}]{}[/]'.format(c, text)
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
