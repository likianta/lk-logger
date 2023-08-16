import typing as t

from rich.console import Group
from rich.padding import Padding  # DELETE
from rich.text import Text
from rich.traceback import Traceback

from ._print import debug  # noqa
from .console import console
from .markup import MarkMeaning
from .markup import T as T0
from .message_formatter import formatter


class MessageStruct:
    head: t.Optional[Text]
    body: Text
    _reverse: bool
    
    def __init__(self, head: t.Optional[Text], body: Text, reverse=False):
        self.head = head if (head and len(head)) else None
        self.body = body
        self._reverse = reverse
    
    @property
    def text(self) -> t.Union[Text, Group, Padding]:
        if self.head:
            if not self._reverse:
                return Text.assemble(self.head, self.body)
            else:
                con_width = console.width - 2
                # debug(con_width)
                if con_width <= len(self.head):  # fallback
                    if '\n' not in self.body:
                        self.body.pad_left(2)
                        return self.body
                    else:
                        lines = self.body.split()
                        for x in lines:
                            x.pad_left(2)
                        return Group(*lines)
                
                if '\n' not in self.body:  # body is single line
                    self.body.pad_left(2)
                    if (x := con_width - len(self.head) - len(self.body)) > 0:
                        self.body.append(' ' * x)
                        out = Text.assemble(self.body, self.head)
                    else:
                        part_1 = Text.assemble(
                            self.body[: con_width - len(self.head)], self.head
                        )
                        part_2 = Text.assemble(
                            '  ',
                            Text('└─', 'dim'),
                            self.body[con_width - len(self.head) :],
                        )
                        out = Group(part_1, part_2)
                else:  # body is multi-line
                    lines = self.body.split('\n')
                    for x in lines:
                        x.pad_left(2)
                    if (x := con_width - len(self.head) - len(lines[0])) > 0:
                        part_1 = Text.assemble(lines[0], ' ' * x, self.head)
                        part_2 = lines[1:]
                        out = Group(part_1, *part_2)
                    else:
                        part_1 = Text.assemble(
                            lines[0][: con_width - len(self.head)], self.head
                        )
                        part_2 = Text.assemble(
                            '  ',
                            Text('└─', 'dim'),
                            lines[0][con_width - len(self.head) :],
                        )
                        part_3 = lines[1:]
                        out = Group(part_1, part_2, *part_3)
                # return Padding(out, (0, 0, 0, 2))
                return out
        else:
            return self.body


class T:
    Args = t.Tuple[t.Any, ...]
    Markup = T0.Markup
    MarksMeaning = T0.MarksMeaning
    MessageStruct = MessageStruct
    RichText = Text
    
    Info = t.TypedDict(
        'Info',
        {
            'file_path': str,
            'function_name': str,
            'is_external_lib': bool,
            'line_number': str,
            'variable_names': t.Tuple[str, ...],
        },
    )


class MessageBuilder:
    _separator_a: Text  # l2r sep
    _separator_b: Text  # var sep
    _separator_c: Text  # r2l sep
    
    def __init__(self, **kwargs) -> None:
        self.update_config(**kwargs)
    
    def update_config(self, **config) -> None:
        # https://fsymbols.com/signs/arrow/
        self._separator_a = Text(' ⪢  ', 'bright_black')
        #   alternatives: ➤ ⪢ >> ⮕ -> ~> | │
        #   note: if we use single char, make sure there are two whitespaces
        #       before it.
        b = config.get('separator', ';   ')
        self._separator_b = Text(b, 'bright_black')
        self._separator_c = Text('  ⪡ ', 'bright_black')
    
    # -------------------------------------------------------------------------
    
    def compose(
        self,
        args: T.Args,
        marks_meaning: T.MarksMeaning,
        info: T.Info,
        show_source: bool = True,
        show_funcname: bool = True,
        show_varnames: bool = False,
        sourcemap_alignment: t.Literal['left', 'right'] = 'left',
    ) -> T.MessageStruct:
        show_source = (
            show_source  # fmt:skip
            and MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning
        )
        show_funcname = (
            show_funcname  # fmt:skip
            and MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning
        )
        show_varnames = (
            show_varnames
            and MarkMeaning.MODERATE_PRUNE not in marks_meaning
            and MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning
        )
        has_any_prune_scheme = (
            MarkMeaning.MODERATE_PRUNE in marks_meaning
            or MarkMeaning.AGRESSIVE_PRUNE in marks_meaning
        )
        
        head = Text()
        body = Text()
        
        # 1. source
        if show_source:
            head_part_1 = formatter.fmt_source(
                info['file_path'],
                info['line_number'],
                is_external_lib=info['is_external_lib'],
                fmt_width=True,
            )
            # head.append_text(
            #     formatter.fmt_source(
            #         info['file_path'],
            #         info['line_number'],
            #         is_external_lib=info['is_external_lib'],
            #         fmt_width=True,
            #     )
            # )
            # head.append_text(self._separator_a)
        else:
            head_part_1 = None
        
        # 2. funcname
        if show_funcname:
            assert info['function_name']
            head_part_2 = formatter.fmt_funcname(
                info['function_name'],
                fmt_width=True,
            )
            # head.append_text(
            #     formatter.fmt_funcname(
            #         info['function_name'],
            #         fmt_width=True,
            #     )
            # )
            # head.append_text(self._separator_a)
        else:
            head_part_2 = None
        
        if head_part_1 or head_part_2:
            if sourcemap_alignment == 'left':
                head = Text.assemble(
                    *(head_part_1 and (head_part_1, self._separator_a) or ()),
                    *(head_part_2 and (head_part_2, self._separator_a) or ()),
                )
            else:
                head = Text.assemble(
                    *(head_part_2 and (self._separator_c, head_part_2) or ()),
                    *(head_part_1 and (self._separator_c, head_part_1) or ()),
                )
        
        # if not self._show_source and not self._show_funcname:
        #     head = None
        # if len(head) == 0:
        #     head = None
        
        # ---------------------------------------------------------------------
        
        # 3. verbosity
        if MarkMeaning.VERBOSITY in marks_meaning:
            if not has_any_prune_scheme:
                if x := formatter.fmt_level(
                    marks_meaning[MarkMeaning.VERBOSITY],
                ):
                    body.append_text(x)
                    body.append(' ')
        
        # 4. index
        if MarkMeaning.RESET_INDEX in marks_meaning:
            if not has_any_prune_scheme:
                body.append_text(formatter.fmt_index(0))
                body.append(' ')
                if not args:
                    args = ('[grey50]reset index[/]',)
        elif MarkMeaning.SIMPLE_COUNTER in marks_meaning:
            body.append_text(
                formatter.fmt_index(marks_meaning[MarkMeaning.SIMPLE_COUNTER])
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
        if timestamp := MarkMeaning.RESET_TIMER in marks_meaning:
            if args:
                args = (
                    formatter.fmt_time(timestamp, color_s='green dim'),
                    *args,
                )
            else:
                args = (
                    '[grey50]reset timer: [/] {}'.format(
                        formatter.fmt_time(timestamp, color_s='green dim')
                    ),
                )
        elif MarkMeaning.STOP_TIMER in marks_meaning:
            start, end = marks_meaning[MarkMeaning.STOP_TIMER]
            args = (formatter.fmt_time(start, end), *args)
        elif MarkMeaning.TEMP_TIMER in marks_meaning:
            if not has_any_prune_scheme:
                start, end = marks_meaning[MarkMeaning.TEMP_TIMER]
                args = ('[i]{}[/]'.format(formatter.fmt_time(start, end)), *args)
        
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
            expand_level=marks_meaning.get(MarkMeaning.EXPAND_OBJECT, 0),
            separator=self._separator_b,
            overall_style=marks_meaning.get(MarkMeaning.VERBOSITY, None),
        )
        
        # PERF: this is compromised design.
        # 8. divider
        if MarkMeaning.DIVIDER_LINE in marks_meaning:
            pattern = marks_meaning[MarkMeaning.DIVIDER_LINE]
            divider = formatter.fmt_divider(pattern, context=(head, body, temp))
            body.append_text(divider)
            body.append(' ')
            body.append_text(temp)
        else:
            body.append_text(temp)
        del temp
        
        return MessageStruct(
            head, body, reverse=(sourcemap_alignment == 'right')
        )
    
    @staticmethod
    def compose_exception(e: BaseException, show_locals: bool) -> Traceback:
        return formatter.fmt_exception(e, show_locals)


builder = MessageBuilder()
