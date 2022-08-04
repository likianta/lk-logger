from __future__ import annotations

import typing as t

from .markup import MarkMeaning
from .message_formatter import MessageFormatter


class T:
    from .markup import T as _TMarkup  # noqa
    Args = t.Iterable[str]
    Markup = _TMarkup.Markup
    MarksMeaning = _TMarkup.MarksMeaning


class MessageBuilder:
    
    def __init__(self, **kwargs):
        self._counter = 0
        self._formatter = MessageFormatter()
        self.update_config(**kwargs)
    
    # noinspection PyAttributeOutsideInit
    def update_config(self, **config):
        self._separator = config.get('separator', ';   ')
        self._show_source = config.get('show_source', False)
        self._show_funcname = config.get('show_funcname', False)
        self._show_varnames = config.get('show_varnames', False)
    
    # -------------------------------------------------------------------------
    
    def quick_compose(self, args: T.Args) -> str:
        return (
            '[bright_black]{separator}[/]'.format(
                separator=self._separator
            ).join(map(str, args))
        )
    
    def compose(self,
                args: T.Args,
                marks_meaning: T.MarksMeaning,
                info: dict) -> str:
        if MarkMeaning.AGRESSIVE_PRUNE in marks_meaning:
            return self.quick_compose(args)
        
        message_elements = []
        
        # 1. source
        if self._show_source:
            message_elements.append(
                self._formatter.fmt_source(
                    info['file_path'],
                    info['line_number'],
                    is_external_lib=info['is_external_lib'],
                    fmt_width=True,
                )
            )
            message_elements.append(
                self._formatter.fmt_separator('  >>  ')
            )
        
        # 2. funcname
        if self._show_funcname:
            message_elements.append(
                self._formatter.fmt_funcname(
                    info['function_name'],
                    fmt_width=True,
                )
            )
            message_elements.append(
                self._formatter.fmt_separator('  >>  ')
            )
        
        # 3. verbosity
        if MarkMeaning.VERBOSITY in marks_meaning:
            message_elements.append(
                self._formatter.fmt_level(
                    marks_meaning[MarkMeaning.VERBOSITY]
                )
            )
        
        # 4. index
        if MarkMeaning.RESET_INDEX in marks_meaning:
            message_elements.append(
                self._formatter.fmt_index(0)
            )
            message_elements.append(' ')
            
            assert not args
            args = ('[bright_black]reset index[/]',)
        
        elif MarkMeaning.UPDATE_INDEX in marks_meaning:
            message_elements.append(
                self._formatter.fmt_index(
                    marks_meaning[MarkMeaning.UPDATE_INDEX]
                )
            )
            message_elements.append(' ')
        
        # 5. divider
        if MarkMeaning.DIVIDER_LINE in marks_meaning:
            div = marks_meaning[MarkMeaning.DIVIDER_LINE]
            message_elements.append(
                self._formatter.fmt_divider(div)
            )
            message_elements.append(' ')
        
        # 6. arguments
        message_elements.append(
            self._formatter.fmt_message(
                arguments=args,
                varnames=info['varnames'] if self._show_varnames else (),
                rich=MarkMeaning.RICH_FORMAT in marks_meaning,
                expand=MarkMeaning.EXPAND_MULTIPLE_LINES in marks_meaning,
                separator=self._separator,
            )
        )
        
        return ''.join(message_elements)
