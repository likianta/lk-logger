from __future__ import annotations

import typing as t

from .markup import MarkMeaning
from .message_formatter import MessageFormatter


class T:
    from .markup import T as _TMarkup  # noqa
    Args = t.Tuple[t.Any, ...]
    Markup = _TMarkup.Markup
    MarksMeaning = _TMarkup.MarksMeaning


class MessageBuilder:
    
    def __init__(self, **kwargs):
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
            assert info['function_name']
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
            if MarkMeaning.MODERATE_PRUNE not in marks_meaning:
                message_elements.append(
                    self._formatter.fmt_level(
                        marks_meaning[MarkMeaning.VERBOSITY],
                        text='{TAG} '
                    )
                )
        
        # 4. index
        if MarkMeaning.RESET_INDEX in marks_meaning:
            if MarkMeaning.MODERATE_PRUNE in marks_meaning:
                pass
            else:
                message_elements.append(self._formatter.fmt_index(0))
                message_elements.append(' ')
                if not args:
                    args = ('[grey50]reset index[/]',)
        elif MarkMeaning.UPDATE_INDEX in marks_meaning:
            message_elements.append(
                self._formatter.fmt_index(
                    marks_meaning[MarkMeaning.UPDATE_INDEX]
                )
            )
            message_elements.append(' ')
        
        # 5. timestamp
        if MarkMeaning.RESET_TIMER in marks_meaning:
            if not args:
                args = ('[grey50]reset timer: [/] {}'.format(
                    self._formatter.fmt_time(
                        marks_meaning[MarkMeaning.RESET_TIMER],
                        color_s='green dim'
                    )
                ),)
            else:
                args = (self._formatter.fmt_time(
                    marks_meaning[MarkMeaning.RESET_TIMER],
                    color_s='green dim'
                ), *args)
        elif MarkMeaning.START_TIMER in marks_meaning:
            args = ('[cyan]start timer:[/] {}'.format(
                self._formatter.fmt_time(
                    marks_meaning[MarkMeaning.RESET_TIMER]
                )
            ), *args)
        elif MarkMeaning.STOP_TIMER in marks_meaning:
            s, e = marks_meaning[MarkMeaning.STOP_TIMER]
            args = (self._formatter.fmt_time(s, e), *args)
        
        # 6. divider
        if MarkMeaning.DIVIDER_LINE in marks_meaning:
            div = marks_meaning[MarkMeaning.DIVIDER_LINE]
            message_elements.append(
                self._formatter.fmt_divider(div)
            )
            message_elements.append(' ')
        
        # 7. arguments
        message_elements.append(
            self._formatter.fmt_message(
                arguments=args,
                varnames=info['variable_names'] if self._show_varnames else (),
                rich=MarkMeaning.RICH_FORMAT in marks_meaning,
                expand=MarkMeaning.EXPAND_MULTIPLE_LINES in marks_meaning,
                separator=self._separator,
            )
        )
        if MarkMeaning.VERBOSITY in marks_meaning and \
                MarkMeaning.EXPAND_MULTIPLE_LINES not in marks_meaning:
            message_elements[-1] = self._formatter.fmt_level(
                marks_meaning[MarkMeaning.VERBOSITY],
                text=message_elements[-1]
            )
        
        return ''.join(message_elements)
