"""
README:
    `docs/what-is-block.md`
"""
from collections import namedtuple

from .analyser import Analyser
from .const import *
from .exceptions import *
from .typehint import *

from lk_logger import lk


def get_all_blocks(*lines: str, end_mark='\n'):
    """ Get ALL COMPLETE text blocks.
    
    Scanning lines and try to merge the adjacent incomplete lines. If the
    merged result is a complete block (type: `list[str]`), yield it to the
    caller.
    
    Args:
        lines
        end_mark:
            FIXME: whatever its value is, end_mark will alwayse be measured as
                one-character width.
    """
    analyser = Analyser(end=end_mark)
    #   IMPROVEMENT: if `lines:each` contains '\n', which means we can't pass
    #       '\n' to `params:end`, we can use `end=None` instead.
    #       (MARK@20210901173115 should also be modified to compilance with
    #        this change.)
    cursor = Cursor()
    fulltext = end_mark.join(lines)
    last_submit_no = 0
    
    def _submit():
        nonlocal last_submit_no
        yield Match(cursor.snapshot(last_submit_no),
                    fulltext[last_submit_no:cursor.x],
                    analyser.symbols.matches_nest)
        analyser.reset()
        last_submit_no = cursor.x + 1
    
    for line in lines:
        cursor.update_lineno()
        
        if end_mark is None:
            line_ = list(line) + [end_mark]
        else:
            line_ = line + end_mark
        for char in line_:  # MARK: 20210901173115
            cursor.update_charno()
            # _debug(cursor.i, line, cursor.j, char, analyser.symbols)
            
            with analyser.trace_index(cursor.x):
                ret_code = analyser.analyse(char)
            
            if ret_code == SUBMITTABLE:
                yield from _submit()
                # break
            elif ret_code == CONTINUED:
                continue
            elif ret_code == GOTO_END:
                while char != end_mark:
                    cursor.update_charno()
                    char = line_[cursor.charno]
                yield from _submit()
                break
            elif ret_code == UNREACHABLE_CASE:
                raise UnreachableCase(
                    cursor.i, line, cursor.j, char, analyser.symbols
                )
            else:
                raise UnexpectedReturnCode(ret_code)


# noinspection PyPep8Naming
def get_variables(line: str):
    """

    Workflow:
        1. single_line = 'A, (B, C)'
        2. split by comma: ['A', '(B', 'C)']
        3. analyse each element, try to merge every mergable parts (based on
           pairable symbols):
           ['A', '(B, C)']
        4. now we know there are two elements in single_line: `A` and `(B, C)`
    """
    VARIABLE_NAME = 0  # varname
    QUOTED_STRING = 1  # qstring
    
    for match in get_all_blocks(line):
        start, end = match.span()  # exterior brackets span
        line = line[start + 1:end]
        # lk.logt('[D3957]', 'strip lk.log arounded', line)
        
        for match1 in get_all_blocks(line, end_mark=','):
            element = match1.fulltext.strip()
            # lk.logt('[D5018]', element)
            if not element:
                raise ValueError(line)
            if (
                    len(element) > 1 and element[0] in ('"', "'")
            ) or (
                    len(element) > 2 and element.lstrip('bfru')[0] in ('"', "'")
            ):
                yield element, QUOTED_STRING
            else:
                yield element, VARIABLE_NAME
        
        break


def _debug(linex, line, charx, char, symbols=None):
    lk.log('''
        ┌──────────────────────────────────────────────────────────────────────╣
        │   Tracing linex {}, charx {} (`{}`):
        │       {}
        │       {}
        │   Symbols:
        │       {}
        └──────────────────────────────────────────────────────────────────────╣
        '''.format(linex, charx,
                   char.replace('\n', '\\n'),
                   line.replace('\n', '\\n'),
                   ' ' * charx + '^', symbols), h='parent')


class Match:
    
    def __init__(self, cursor: Union[TCursor, tuple],
                 text: str, matches: TMatches2):
        self.cursor = cursor
        self.fulltext = text
        self._matches = matches
        self.spans = list(matches)
    
    def change_depth(self, d: int):
        def rec(collector, node: dict, curr_d):
            if curr_d < d:
                for v in node.values():
                    rec(collector, v, curr_d + 1)
            elif curr_d == d:
                collector.extend(node.keys())
            return collector
        
        self.spans = rec([], self._matches, 0)
    
    def span(self, idx=0) -> TSpan:
        return self.spans[idx]
    
    def group(self, idx=0):
        start, end = self.span(idx)
        return self.fulltext[start:end + 1]
    
    def groups(self):
        out = []
        for i in range(len(self.spans)):
            out.append(self.group(i))
        return out


class Cursor:
    lineno = -1
    charno = -1
    tileno = -1
    
    _dict: dict  # dict[tileno, tuple[lineno, charno]]
    
    def __init__(self):
        self._dict = {}
        self._snap = namedtuple(
            'CursorShot', ['lineno', 'charno', 'tileno', 'index']
        )
        
    def indexing_fulltext(self, lines):
        for line in lines:
            self.update_lineno()
            for _ in line + '\n':
                self.update_charno()
    
    def update_lineno(self):
        self.lineno += 1
        self.charno = -1
    
    def update_charno(self):
        self.charno += 1
        self.tileno += 1
        self._dict[self.tileno] = (self.lineno, self.charno)
        self._dict[(self.lineno, self.charno)] = self.tileno
    
    @property
    def i(self):
        return self.lineno
    
    @property
    def j(self):
        return self.charno
    
    @property
    def x(self):
        return self.tileno
    
    def trans(self, no: Union[int, tuple]):
        return self._dict[no]
    
    def snapshot(self, index=None):
        if index is None:
            index = self.tileno
        (i, j), x = self.trans(index), index
        return self._snap(
            lineno=i, charno=j, tileno=x, index=index
        )
