from __future__ import annotations

from textwrap import indent
from typing import Union

from pytermgui import tim

from ._internal_debug import debug  # noqa

_SEPARATOR = (' ', '')  # see also `MessageFormatter._safe_markup`.


# noinspection PyUnusedLocal
def new_preffity(
        target,
        indent: int = 2,
        force_markup: bool = False,
        expand_all: bool = False,
        parse: bool = True,
) -> str:
    """
    this function was copied from `pytermgui.prettifiers.prettify`, but removed
    checking whether `target` in builtin module.
    """
    from pytermgui.prettifiers import (
        CONTAINER_TYPES, AnsiSyntaxError, MarkupSyntaxError,  # noqa
        _prettify_container, _prettify_str,  # noqa
    )
    
    buff = ""
    
    if isinstance(target, CONTAINER_TYPES):
        buff = _prettify_container(
            target, indent=indent, expand_all=expand_all,
            force_markup=force_markup
        )
    
    elif isinstance(target, str):
        buff = _prettify_str(target, force_markup=force_markup)
    
    elif isinstance(target, int):
        buff = f"[pprint-int]{target}[/]"
    
    elif isinstance(target, type):
        buff = f"[pprint-type]{target.__name__}[/]"
    
    elif target is None:
        buff = f"[pprint-none]{target}[/]"
    
    else:
        try:
            iterator = iter(target)
        except TypeError:
            return str(target)
        
        for inner in iterator:
            buff += new_preffity(inner, parse=False)
    
    if parse:
        try:
            return tim.parse(buff)
        except (AnsiSyntaxError, MarkupSyntaxError):
            pass
    
    return str(buff) or str(target)


from pytermgui import prettifiers
setattr(prettifiers, 'prettify', new_preffity)


# -----------------------------------------------------------------------------

class MessageFormatter:
    
    @staticmethod
    def markup(*markups: tuple[str, str]) -> str:
        """
        thid method produces the final strings that could be directly printed.

        args:
            markups: tuple[tuple[str text, str mark], ...]
                mark:
                    any valid patterns of pytermgui markups. for example, 'red',
                    'bold', 'bright-black', '#00FF00', ...
                    ps: mark allows empty.

        tip:
            if you want add a separator, use `global _SEPARATOR`.

        warning:
            - if two adjacent marks are same, merge them into one. otherwise
              the latter one's effect will be lost. (this is a bug)
            - `tim.parse` will ignore invalid bracket patterns, in case it
              breaks the origin content of `text`, we take some escape method.
              (see code for details)
        """
        out = []
        last_mark = None
        for text, mark in markups:
            if mark == last_mark:
                out[-1] += text
            if mark and text.strip():
                if '[' in text:
                    out.append(tim.parse('[{}]{{}}[/]'.format(mark)).format(text))
                else:
                    out.append(tim.parse('[{}]{}[/]'.format(mark, text)))
            else:
                out.append(text)
            last_mark = mark
        return ''.join(out)
    
    @staticmethod
    def expand_node(target) -> str:
        return prettifiers.prettify(target, indent=4)
    
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
                (f'[{a}]', 'bold {}'.format(
                    'red' if filepath.startswith('[unknown]') else 'magenta'
                )),
                (f'{b}', 'bold blue'),
            )
            return self.markup(
                (filepath, ''),
                (':', 'bright-black'),
                (str(lineno), 'bold blue'),
                (additional_space, ''),
            )
        return self.markup(
            (filepath, 'bold blue'),
            (':', 'bright-black'),
            (str(lineno), 'bold blue'),
            (additional_space, ''),
        )
    
    def fmt_separator(self, sep: str = ' >> ', color='bright-black') -> str:
        return self.markup((sep, color))
    
    def fmt_funcname(self, funcname: str, fmt_width=False) -> str:
        is_func = not funcname.startswith('<')
        if is_func:
            funcname += '()'
        else:
            funcname = funcname[1:-1]
        if fmt_width:
            funcname = self._fmt_width(
                funcname, min_width=6, incremental_unit=2
            )
        if is_func:
            return self.markup((funcname, 'green'))
        else:
            return self.markup((funcname, 'magenta'))
    
    def fmt_index(self, idx: Union[int, str]) -> str:
        return self.markup(
            (f'[{idx}]', 'bright-black' if idx == 0 or idx == '0' else 'red')
        )
    
    def fmt_divider(self, div_: str) -> str:
        return self.markup((div_, 'yellow'))
    
    def fmt_message(self, msg_frags: list[str], rich: bool, expand=False) -> str:  # FIXME
        if rich:
            if expand:
                lines = []
                for frag in msg_frags:
                    for line in frag.splitlines():
                        if line.startswith('    '):
                            how_many = len(line) - len(line.lstrip())
                            spaces = line[:how_many]
                            rich_indent = spaces.replace(
                                '    ', self.markup(
                                    ('|', 'bright-black'),
                                    ('   ', ''),
                                )
                            )
                            lines.append(rich_indent + line[how_many:])
                        else:
                            lines.append(line)
                return '\n' + indent('\n'.join(lines), '    ')
            else:
                return self.markup((';\t', 'bright-black')).join(msg_frags)
        else:
            if expand:
                return '\n' + indent('\n'.join(msg_frags), '    ')
            else:
                return self.markup((';\t', 'bright-black')).join(msg_frags)
    
    def fmt_level(self, text: str, level: str) -> str:
        colors = {
            'trace': '',
            'debug': 'bright-black',
            'info' : 'bright-blue',
            'warn' : 'yellow',
            'error': 'bright-red',
            'fatal': 'bold bright-cyan @bright-red',
        }
        return self.markup((text, colors[level]))
    
    # -------------------------------------------------------------------------
    
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
