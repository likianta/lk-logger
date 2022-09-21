"""
a general purpose, index based text scanner.

example (conceptual):
    input:
        aaa [bbb (ccc) (ddd] eee
    output:
        - text=aaa , type=plain, span=(0, 4)
        - text=[bbb (ccc) (ddd], type=pair_ab, span=(4, 20)
            - text=bbb , type=plain, span=(4, 8)
            - text=(ccc), type=pair_ab, span=(8, 13)
                - text=ccc, type=plain, span=(9, 12)
            - text= (ddd, type=plain, span=(13, 19)
        - text= eee, type=plain, span=(19, 23)

pip install (optional, for dev only):
    - argsense: a command line argument parser.
    - lk_logger: pretty print with varnames.
"""
from __future__ import annotations

import typing as t
from dataclasses import dataclass
from enum import Enum
from enum import auto as _auto

__all__ = [
    'PRESET_RULES',
    'PairRule',
    'Scanner',
]

# this is a workaround to demolish typehint warning.
auto = lambda: _auto()  # noqa


@dataclass
class Span:
    start_index: int
    start_rowx: int
    start_colx: int
    end_index: int
    end_rowx: int
    end_colx: int


@dataclass
class Segment:
    text: str
    type: str
    span: Span
    pair: tuple[str, str]
    children: list


class PairRule(Enum):
    PLAIN = auto()
    ESCAPE = auto()  # e.g. '\\'
    COMMENT = auto()  # e.g. '#'
    PAIR_AB = auto()  # e.g. '()', '[]', '{}'
    PAIR_AA = auto()  # e.g. '""', "''", '``'
    BLOCK_AA = auto()  # e.g. '```...```'
    BLOCK_AB = auto()  # e.g. '/* ... */'


class State(Enum):
    READY = auto()
    PLAIN = auto()
    PAIRING_START = auto()
    PAIR_START_DONE = auto()
    PAIRING_END = auto()


class T:
    _Start = str
    _End = str
    _Rule = PairRule
    PairRule = t.Iterable[t.Tuple[t.Tuple[_Start, _End], _Rule]]


# PERF: use namedtuple.
class PRESET_RULES:  # noqa
    BASE_RULES = {
        'block_aa.backtick'      : (('```', '```'), PairRule.BLOCK_AB),
        'block_aa.dash'          : (("---", "---"), PairRule.BLOCK_AB),
        'block_aa.double_quotes' : (('"""', '"""'), PairRule.BLOCK_AB),
        'block_aa.single_quotes' : (("'''", "'''"), PairRule.BLOCK_AB),
        'block_ab.slash'         : (('/*', '*/'), PairRule.BLOCK_AB),
        'comment.pound'          : (('#', ''), PairRule.COMMENT),
        'comment.slash'          : (('//', ''), PairRule.BLOCK_AA),
        'escape.backslash'       : (('\\', ''), PairRule.ESCAPE),
        'pair_aa.backtick'       : (('`', '`'), PairRule.PAIR_AA),
        'pair_aa.double_quotes'  : (('"', '"'), PairRule.PAIR_AA),
        'pair_aa.single_quotes'  : (("'", "'"), PairRule.PAIR_AA),
        'pair_ab.braces'         : (('{', '}'), PairRule.PAIR_AB),
        'pair_ab.brackets'       : (('[', ']'), PairRule.PAIR_AB),
        'pair_ab.parentheses'    : (('(', ')'), PairRule.PAIR_AB),
        'pair_ab.square_brackets': (('<', '>'), PairRule.PAIR_AB),
    }
    
    # -------------------------------------------------------------------------
    
    GENERAL_RULES = (
        BASE_RULES['pair_aa.double_quotes'],
        BASE_RULES['pair_aa.single_quotes'],
        BASE_RULES['pair_aa.backtick'],
        BASE_RULES['pair_ab.parentheses'],
        BASE_RULES['pair_ab.brackets'],
        BASE_RULES['pair_ab.braces'],
        BASE_RULES['pair_ab.square_brackets'],
    )
    
    PYTHON_RULES = (
        BASE_RULES['block_aa.double_quotes'],
        BASE_RULES['block_aa.single_quotes'],
        BASE_RULES['comment.pound'],
        BASE_RULES['escape.backslash'],
        BASE_RULES['pair_aa.double_quotes'],
        BASE_RULES['pair_aa.single_quotes'],
        BASE_RULES['pair_ab.parentheses'],
        BASE_RULES['pair_ab.brackets'],
        BASE_RULES['pair_ab.braces'],
    )
    
    JAVASCRIPT_RULES = (
        BASE_RULES['block_aa.backtick'],
        BASE_RULES['block_aa.double_quotes'],
        BASE_RULES['block_aa.single_quotes'],
        BASE_RULES['comment.slash'],
        BASE_RULES['escape.backslash'],
        BASE_RULES['pair_aa.double_quotes'],
        BASE_RULES['pair_aa.single_quotes'],
        BASE_RULES['pair_aa.backtick'],
        BASE_RULES['pair_ab.parentheses'],
        BASE_RULES['pair_ab.brackets'],
        BASE_RULES['pair_ab.braces'],
    )
    
    MARKDOWN_RULES = (
        BASE_RULES['block_aa.backtick'],
        # BASE_RULES['block_aa.dash'],
        BASE_RULES['escape.backslash'],
        BASE_RULES['pair_aa.double_quotes'],
        BASE_RULES['pair_aa.single_quotes'],
        BASE_RULES['pair_aa.backtick'],
        BASE_RULES['pair_ab.parentheses'],
        BASE_RULES['pair_ab.brackets'],
        BASE_RULES['pair_ab.braces'],
        BASE_RULES['pair_ab.square_brackets'],
        (('<!--', '-->'), PairRule.BLOCK_AB),
    )


class Scanner:
    
    def __init__(self, pair_rules: T.PairRule = PRESET_RULES.GENERAL_RULES):
        # print(pair_rules)
        from collections import defaultdict
        self._rules = {x[0][0]: x[1] for x in pair_rules}
        #   dict[str start, rule]
        self._pairs = dict(x[0] for x in pair_rules)
        #   dict[str start, str end]
        # self._pairs_r = {v: k for k, v in self._pairs.items()}
        # assert len(self._pairs) == len(self._pairs_r), (
        #     'text scanner does not support ambiguous pair rules, for example: '
        #     '`[` matches `]` while also `{` matches `]`!'
        # )
        self._pair_initials = defaultdict(lambda: {
            'possible_symbols': [],
            'possible_rules'  : [],
        })
        
        for (start, end), rule in pair_rules:
            self._pair_initials[start[0]]['possible_symbols'].append(start)
            self._pair_initials[start[0]]['possible_rules'].append(rule)
        ''' e.g.
            self._pair_starts = {
                '"': [PairRule.PAIR_AA, PairRule.BLOCK_AA],
                '""': [PairRule.BLOCK_AA],
                '"""': [PairRule.BLOCK_AA],
                ...
            }
        '''
        
        for v in self._pair_initials.values():
            v['possible_symbols'].sort(key=len)
    
    def scan(self, text: str) -> t.Iterator[Segment]:
        pointer = Pointer(text)
        # all indexes are zero-based.
        # last_index = 0
        # curr_index = 0
        goto_index = 0
        over_index = len(text) - 1
        
        def walk(
                start: int, end: int = over_index,
                parent_pair_ends: tuple[str, ...] = (),
                is_block: bool = False,
        ) -> t.Iterator[Segment]:
            
            state = State.READY
            last_index: int
            curr_index: int
            pair_start: str
            pair_end: str
            rule: PairRule = PairRule.PLAIN
            temp_children: list | None = None
            
            def find_line_ending(start: int, end: int = None) -> int:
                nonlocal over_index
                if end is None:
                    end = over_index
                for i in range(start, end + 1):
                    if text[i] == '\n':
                        return i
                else:
                    raise IndexError(
                        'no line ending found in range {} ~ {}:\n'
                        '    {}'.format(start, end, text[start:end])
                    )
            
            def find_new_pair_start(char: str) \
                    -> tuple[str, str, PairRule] | None:
                if x := self._pair_initials.get(char):
                    # 1/2. determine final_symbol
                    final_symbol = ''
                    for symbol in x['possible_symbols']:
                        #   note: x['possible_symbols'] is already sorted by
                        #       symbol length.
                        if match(symbol, char):
                            final_symbol = symbol
                    #   now final_symbol is determined, but it might be empty.
                    #   if empty, it means this is not a valid pair start.
                    
                    # 2/2. get rule
                    if final_symbol:
                        pair_start = final_symbol
                        try:
                            pair_end = self._pairs[pair_start]
                        except KeyError:
                            # usually this exception won't happen. but we play
                            #   a trick that somewhere else may temporarily
                            #   removed `pair_start` from `self._pairs`, thus
                            #   we are encountering an KeyError here.
                            # we can take it as a plain char insteadly.
                            # see also [code](#20220708164828).
                            return None
                        rule = self._rules[final_symbol]
                        return pair_start, pair_end, rule
                else:
                    return None
            
            def match(a: str, b: str) -> bool:
                """
                `b` is equal to `text[curr_index]`. len(b) == 1.
                `a` is a variable length string. len(a) >= 1.
                """
                nonlocal text, curr_index
                if len(a) == 1:
                    return a == b
                else:
                    return a == text[curr_index: curr_index + len(a)]
            
            def reset() -> None:
                nonlocal pair_start, pair_end, rule, state, \
                    temp_children
                state = State.READY
                pair_start = ''
                pair_end = ''
                rule = PairRule.PLAIN
                temp_children = None
            
            def submit(
                    pair: tuple[str, str],
                    rule: PairRule,
                    children: list = None,
                    submit_text: str = None,
                    _curr_index: int = None,
            ) -> Segment:
                nonlocal curr_index, last_index, pointer, text
                if submit_text is None:
                    submit_text = text[last_index: curr_index + 1]
                if _curr_index is None:
                    _curr_index = curr_index
                seg = Segment(
                    text=submit_text,
                    type=rule.name,
                    span=pointer.get_span(last_index, _curr_index),
                    pair=pair,
                    children=children or []
                )
                last_index = _curr_index + 1
                return seg
            
            def submittable(_curr_index: int = None) -> bool:
                nonlocal last_index, curr_index
                if _curr_index is None:
                    _curr_index = curr_index
                return last_index <= _curr_index
            
            # -----------------------------------------------------------------
            
            nonlocal pointer, text
            # nonlocal last_index, curr_index, goto_index, over_index
            nonlocal goto_index, over_index
            
            last_index = start
            curr_index = start
            over_index = end
            
            for curr_index in range(start, end + 1):
                if curr_index < goto_index:
                    # warning: you should make sure there is no '\n' between
                    #   `curr_index` and `goto_index`. i.e. carefully setting
                    #   `goto_index`.
                    continue
                else:
                    goto_index = curr_index
                
                char = text[curr_index]
                # print(curr_index, char, ':v')
                if char == '\n':
                    if is_block:
                        continue
                    else:
                        yield submit(('', ''), PairRule.PLAIN)
                        goto_index = curr_index + 1
                        break
                
                if state == State.READY:
                    if parent_pair_ends and \
                            any(match(x, char) for x in parent_pair_ends):
                        if submittable(curr_index - 1):
                            yield submit(
                                ('', ''), PairRule.PLAIN, [],
                                _curr_index=curr_index - 1
                            )
                        return  # go up to outer recursion.
                    if x := find_new_pair_start(char):
                        pair_start, pair_end, rule = x
                        state = State.PAIRING_START
                        goto_index = curr_index + len(pair_start)
                        continue
                    else:
                        continue
                
                if state == State.PAIRING_START:
                    # for now, we are paring start, but we don't know whether
                    #   it is a valid start. it will clear when paring end is
                    #   done.
                    assert pair_start  # noqa
                    
                    if submittable(idx := curr_index - len(pair_start) - 1):
                        yield submit(
                            ('', ''), PairRule.PLAIN, [],
                            _curr_index=idx
                        )
                    
                    if rule == PairRule.ESCAPE:
                        yield submit(('\\', ''), rule, [], '\\' + char)
                        reset()
                        continue
                    
                    if rule == PairRule.COMMENT:
                        # [#20220708164828] temporarily remove comment symbol
                        #   from self._pairs.
                        temp = self._pairs.pop(pair_start)
                        yield submit(
                            ('#', ''),
                            rule,
                            list(walk(curr_index, )),
                            '#' + text[curr_index: find_line_ending(curr_index)]
                        )
                        # then restore self._pairs.
                        self._pairs[pair_start] = temp
                        reset()
                        break
                    
                    assert pair_end  # noqa
                    if match(pair_end, char):
                        yield submit((pair_start, pair_end), rule, [])
                        reset()
                        continue
                    temp_children = list(walk(
                        curr_index,
                        parent_pair_ends=(pair_end, *parent_pair_ends),
                        is_block=bool(
                            rule in (PairRule.BLOCK_AB, PairRule.BLOCK_AA)
                        )
                    ))
                    state = State.PAIRING_END
                    continue
                
                if state == State.PAIRING_END:
                    assert pair_end and rule  # noqa
                    # rule can never be: ESCAPE, COMMENT
                    if match(pair_end, char):
                        curr_index = curr_index + len(pair_end) - 1
                        goto_index = curr_index + len(pair_end)
                        yield submit(
                            (pair_start, pair_end),
                            rule,
                            temp_children or [],
                        )
                        reset()
                        continue
                    else:
                        rule = PairRule.PLAIN
                        yield submit(
                            ('', ''), rule, [], pair_start,
                            _curr_index=last_index + len(pair_start) - 1
                        )
                        if temp_children:
                            yield from temp_children
                        last_index = curr_index + 1
                        reset()
            
            if rule == PairRule.ESCAPE:
                yield submit(('\\', ''), rule, [], '\\')
            elif rule == PairRule.COMMENT:
                yield submit(('#', ''), rule, [], '#')
            else:
                if submittable():
                    yield submit(('', ''), PairRule.PLAIN, [])
            reset()
        
        def merge_segments(segs: list[Segment]) -> t.Iterator[Segment]:
            seg_0: Segment | None = None
            plain: str = PairRule.PLAIN.name
            for seg_1 in segs:
                if seg_0:
                    if seg_0.type == plain:
                        if seg_1.type == plain:
                            seg_0 = Segment(
                                text=seg_0.text + seg_1.text,
                                type=plain,
                                span=Span(
                                    seg_0.span.start_index,
                                    seg_0.span.start_rowx,
                                    seg_0.span.start_colx,
                                    seg_1.span.end_index,
                                    seg_1.span.end_rowx,
                                    seg_1.span.end_colx
                                ),
                                pair=('', ''),
                                children=[]
                            )
                            continue
                        else:
                            yield seg_0
                    else:
                        yield seg_0
                seg_0 = seg_1
                if seg_1.children:
                    seg_1.children = list(merge_segments(seg_1.children))
            if seg_0:
                yield seg_0
        
        yield from merge_segments(
            list(walk(start=0, end=over_index, is_block=True))
        )


class Pointer:
    _map: dict[int, tuple[int, int]]
    
    #   dict[int index, tuple[int rowx, int colx]]
    
    def __init__(self, text: str):
        self._map = {}
        index = -1
        for rowx, line in enumerate(text.splitlines()):
            for colx, char in enumerate(line):
                index += 1
                self._map[index] = (rowx, colx)
            # the '\n' is counted as an additional `colx`.
            index += 1
            self._map[index] = (rowx, len(line))
    
    def get_span(self, index_0: int, index_1: int) -> Span:
        rowx_0, colx_0 = self._map[index_0]
        rowx_1, colx_1 = self._map[index_1]
        return Span(index_0, rowx_0, colx_0, index_1, rowx_1, colx_1)


if __name__ == '__main__':
    import lk_logger
    from argsense import cli
    
    lk_logger.setup(quiet=True, show_varnames=True)
    scanner = Scanner()
    
    
    def recurse_print_segment(seg: Segment, level=0):
        print('    ' * level +
              '[green]{}[/]'.format(seg.text.replace('\n', '[magenta]\\n[/]')),
              f'[magenta]{seg.pair}[/]',
              f'[red]{seg.type}[/]',
              '[grey50]{}[/]'.format((seg.span.start_index,
                                      seg.span.end_index)),
              ':rs' + ('i' if level == 0 else ''))
        if seg.children:
            print(':rs', '{spaces}[yellow i]children (#{level}):[/]'.format(
                spaces='    ' * level, level=level + 1))
            for child in seg.children:
                recurse_print_segment(child, level + 1)
    
    
    @cli.cmd()
    def test(text: str, is_file=False):
        """
        args:
            text: a string or a file path.
        kwargs:
            is_file (-f): if True, will treat param `text` as a file path.
        """
        print(':ds', text)
        if is_file:
            path = text
            text = open(path).read()
        for segment in scanner.scan(text):
            recurse_print_segment(segment)
    
    
    cli.run(test)
