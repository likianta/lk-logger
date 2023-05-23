import typing as t

from rich.text import Text
from rich.traceback import Traceback

from .markup import MarkMeaning
from .markup import T as T0
from .message_formatter import formatter


class MessageStruct:
    head: t.Optional[Text]
    body: Text
    
    def __init__(self, head: t.Optional[Text], body: Text):
        self.head = head if (head and len(head)) else None
        self.body = body
    
    @property
    def text(self) -> Text:
        if self.head:
            return Text.assemble(self.head, self.body)
        else:
            return self.body


class T:
    Args = t.Tuple[t.Any, ...]
    Markup = T0.Markup
    MarksMeaning = T0.MarksMeaning
    MessageStruct = MessageStruct
    RichText = Text
    
    Info = t.TypedDict('Info', {
        'file_path'      : str,
        'function_name'  : str,
        'is_external_lib': bool,
        'line_number'    : str,
        'variable_names' : t.Tuple[str, ...],
    })


class MessageBuilder:
    _separator_a: Text
    _separator_b: Text
    
    def __init__(self, **kwargs) -> None:
        self.update_config(**kwargs)
    
    def update_config(self, **config) -> None:
        # https://fsymbols.com/signs/arrow/
        self._separator_a = Text('  ➤ ', 'bright_black')
        #   alternatives: ➤ ⪢ >> ⮕ -> ~> | │
        #   note: if we use single char, make sure there are two whitespaces
        #       before it.
        self._separator_b = Text(
            config.get('separator', ';   '), 'bright_black')
    
    # -------------------------------------------------------------------------
    
    def compose(
            self,
            args: T.Args,
            marks_meaning: T.MarksMeaning,
            info: T.Info,
            show_source: bool = True,
            show_funcname: bool = True,
            show_varnames: bool = False,
    ) -> T.MessageStruct:
        show_source = show_source and \
                      MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning
        show_funcname = show_funcname and \
                        MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning
        show_varnames = show_varnames and \
                        MarkMeaning.MODERATE_PRUNE not in marks_meaning and \
                        MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning
        
        head = Text()
        body = Text()
        # body_parts: t.List[T.RichText] = [Text(), None, Text()]
        # body = body_parts[0]
        
        # 1. source
        if show_source:
            head.append_text(
                formatter.fmt_source(
                    info['file_path'],
                    info['line_number'],
                    is_external_lib=info['is_external_lib'],
                    fmt_width=True,
                )
            )
            head.append_text(self._separator_a)
        
        # 2. funcname
        if show_funcname:
            assert info['function_name']
            head.append_text(
                formatter.fmt_funcname(
                    info['function_name'],
                    fmt_width=True,
                )
            )
            head.append_text(self._separator_a)
        
        # if not self._show_source and not self._show_funcname:
        #     head = None
        # if len(head) == 0:
        #     head = None
        
        # ---------------------------------------------------------------------
        
        # 3. verbosity
        if MarkMeaning.VERBOSITY in marks_meaning:
            if MarkMeaning.MODERATE_PRUNE not in marks_meaning:
                if x := formatter.fmt_level(
                        marks_meaning[MarkMeaning.VERBOSITY],
                ):
                    body.append_text(x)
                    body.append(' ')
        
        # 4. index
        if MarkMeaning.RESET_INDEX in marks_meaning:
            if MarkMeaning.MODERATE_PRUNE in marks_meaning:
                pass
            else:
                body.append_text(formatter.fmt_index(0))
                body.append(' ')
                if not args:
                    args = ('[grey50]reset index[/]',)
        elif MarkMeaning.SIMPLE_COUNTER in marks_meaning:
            body.append_text(
                formatter.fmt_index(
                    marks_meaning[MarkMeaning.SIMPLE_COUNTER]
                )
            )
            body.append(' ')
        elif MarkMeaning.SCOPED_COUNTER in marks_meaning:
            body.append_text(
                formatter.fmt_scoped_index(
                    *marks_meaning[MarkMeaning.SCOPED_COUNTER]
                )
            )
            body.append(' ')
        
        # 5. timestamp
        if MarkMeaning.RESET_TIMER in marks_meaning:
            if not args:
                args = ('[grey50]reset timer: [/] {}'.format(
                    formatter.fmt_time(
                        marks_meaning[MarkMeaning.RESET_TIMER],
                        color_s='green dim'
                    )
                ),)
            else:
                args = (formatter.fmt_time(
                    marks_meaning[MarkMeaning.RESET_TIMER],
                    color_s='green dim'
                ), *args)
        elif MarkMeaning.START_TIMER in marks_meaning:
            args = ('[cyan]start timer:[/] {}'.format(
                formatter.fmt_time(
                    marks_meaning[MarkMeaning.RESET_TIMER]
                )
            ), *args)
        elif MarkMeaning.STOP_TIMER in marks_meaning:
            s, e = marks_meaning[MarkMeaning.STOP_TIMER]
            args = (formatter.fmt_time(s, e), *args)
        
        # # 6. divider
        # if MarkMeaning.DIVIDER_LINE in marks_meaning:
        #     pattern = marks_meaning[MarkMeaning.DIVIDER_LINE]
        #     message_elements.append(
        #         formatter.fmt_divider(pattern)
        #     )
        #     message_elements.append(' ')
        
        # 7. arguments
        # body.append_text(
        #     formatter.fmt_message(
        #         arguments=args,
        #         varnames=info['variable_names'] if self._show_varnames else (),
        #         rich=MarkMeaning.RICH_FORMAT in marks_meaning,
        #         expand=MarkMeaning.EXPAND_MULTIPLE_LINES in marks_meaning,
        #         separator=self._separator_b,
        #         overall_style=marks_meaning.get(MarkMeaning.VERBOSITY, None),
        #     )
        # )
        temp = formatter.fmt_message(
            arguments=args,
            varnames=info['variable_names'] if show_varnames else (),
            rich=MarkMeaning.RICH_FORMAT in marks_meaning,
            expand=MarkMeaning.EXPAND_MULTIPLE_LINES in marks_meaning,
            separator=self._separator_b,
            overall_style=marks_meaning.get(MarkMeaning.VERBOSITY, None),
        )
        
        # PERF: this is compromised design.
        # 8. divider
        if MarkMeaning.DIVIDER_LINE in marks_meaning:
            pattern = marks_meaning[MarkMeaning.DIVIDER_LINE]
            divider = formatter.fmt_divider(
                pattern, context=(head, body, temp)
            )
            body.append_text(divider)
            body.append(' ')
            body.append_text(temp)
        else:
            body.append_text(temp)
        del temp
        
        return MessageStruct(head, body)
    
    @staticmethod
    def compose_exception(
            e: BaseException,
            show_locals: bool
    ) -> Traceback:
        return formatter.fmt_exception(e, show_locals)


builder = MessageBuilder()
