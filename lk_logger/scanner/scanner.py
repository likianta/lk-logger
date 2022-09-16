"""
README:
    `docs/what-is-block.md`
"""
from collections import namedtuple
from re import compile
from string import whitespace

from .analyser import Analyser
from .const import *
from .exceptions import *
from .typehint import *
from .._print import debug  # noqa


def get_all_blocks(*lines: str, end_mark='\n'):
    """ Get ALL COMPLETE text blocks.
    
    Scanning lines and try to merge the adjacent incomplete lines. If the
    merged result is a complete block (type: `list[str]`), yield it to the
    caller.
    
    Args:
        lines:
        end_mark:
            warnings:
                1. whatever end_mark's value is, it is alwayse be measured as
                   one-character width.
                2. `params:lines:each` mustn't end with end_mark, i.e.
                    assert(all(not x.rstrip().endswith(end_mark)) for x in lines)
    """
    assert all(bool(not x.rstrip().endswith(end_mark)) for x in lines), (
        f'Please make sure each of lines must not end with "{end_mark}". '
        f'(You need to strip them before calling this function)'
    )
    assert len(end_mark) == 1
    
    analyser = Analyser(end=end_mark)
    #   IMPROVEMENT: if `lines:each` contains '\n', which means we can't pass
    #       '\n' to `params:end`, we can use `end=None` instead.
    #       (see reactions at MARK@20210901173115.)
    cursor = Cursor()
    fulltext = end_mark.join(lines)
    last_submit_idx = 0
    
    def _submit():
        nonlocal last_submit_idx
        yield Match(cursor.snapshot(last_submit_idx),
                    fulltext[last_submit_idx:cursor.x],
                    analyser.symbols.matches_nest)
        analyser.reset()
        last_submit_idx = cursor.x + 1
    
    for line in lines:
        cursor.update_lineno()
        
        line_ = line + end_mark
        for char in line_:  # MARK: 20210901173115
            cursor.update_charno()
            # _debug(cursor.i, line, cursor.j, char, analyser.symbols)
            
            with analyser.trace_index(cursor.x):
                ret_code = analyser.analyse(char)
            
            if ret_code == SUBMITTABLE:
                yield from _submit()
                # break
            elif ret_code == CONTINUE:
                continue
            elif ret_code == BREAK_OUT:
                # `BREAK_OUT` is recognized as continuously sending `CONTINUE`
                # command, until we meet an `end_mark` then break.
                while char != end_mark:
                    cursor.update_charno()
                    char = line_[cursor.charno]
                    # debug(cursor.charno, char)
                yield from _submit()
                break
            elif ret_code == UNREACHABLE_CASE:
                raise UnreachableCase(
                    cursor.i, line, cursor.j, char, analyser.symbols
                )
            else:
                raise UnexpectedReturnCode(ret_code)


def get_variables(line: str):
    """

    Workflow:
        1. single_line = 'A, (B, C)'
        2. split by comma: ['A', '(B', 'C)']
        3. analyse each element, try to merge every mergable parts (based on
           pairable symbols): ['A', '(B, C)']
        4. now we know there are two elements in single_line: `A` and `(B, C)`
    """
    caller_pattern = compile(r'^([.\w]+)[(\[{]')  # matching: 'requests.get('
    kwargs_pattern = compile(r'^\w+ *=')  # matching: 'a=1'
    lambda_pattern = compile(r'^lambda ')  # matching: 'lambda *_, **__: ...'
    nested_pattern = compile(r'^[(\[{]')  # matching: '(...', '[...', '{...'
    number_pattern = compile(r'^-?\d+(?:\.\d+)?$')  # matching: '123', '-123'
    quotes_pattern = compile(r'^[bfru]*[\'"]')  # matching: '"hello', 'b"hello'
    walrus_pattern = compile(r'^(\w+) *:=')  # mathcing: 'x := 12'
    
    for match0 in get_all_blocks(line):
        start, end = match0.span()  # exterior brackets span
        line = line[start + 1:end].rstrip(whitespace + ',')
        #   `~.rstrip(...)`: for example:
        #       line = 'a, b, c, \n' -> 'a, b, c'
        
        for match1 in get_all_blocks(line, end_mark=','):
            element = match1.fulltext.strip()
            # debug(f'{element = }')
            
            if not element:
                # # continue
                raise ScanningError(
                    match1.cursor.lineno, line,
                    match1.cursor.charno, (line + ',')[match1.cursor.tileno],
                    None
                )
            
            if quotes_pattern.match(element):
                yield element, QUOTED_STRING
            elif number_pattern.match(element):
                yield element, SIMPLE_NUMBER
            elif kwargs_pattern.match(element):
                continue  # continue or break out
            elif nested_pattern.match(element):
                yield element, NESTED_STRUCT
            elif lambda_pattern.match(element):
                ''' TODO (memo)
                
                How it happened?
                    For example:
                        line = 'lambda *args, **kwargs: None'
                        
                    When scanner goes here:
                        lambda *args, **kwargs: None
                                    ^
                    Because 'lambda *args' is a 'complete' part (no unresolved
                    brackets, quotes, etc. left), it treats this comma symbol
                    as an end mark, so scanner thinks it can be submitted and
                    yields 'lambda *args' as an 'element' to the caller.
                    
                    The caller (`lk_logger.sourcemap`) receives 'lambda *args'
                    and '**kwargs: None' one after another, so caller thinks
                    there're two elements found. But when logger tries to
                    demonstrate their number is equivalent (see `lk_logger
                    .logger.format > code:'assert len(info.varnames) ==
                    len(data)'`), an AssertionError is raised.
                
                How to resolve it (in the future)?
                    Before handling this example line, replace the comma with a
                    mask symbol. After handling is over, restore it.
                '''
                raise UnresolvedCase('''
                    We didn't find an ideal way to handle lambda expression
                    without breaking currently designed function.
                    The caller should catch this exception and it has to
                    abandon all its collected varnames which came from this
                    function. Say just take it as nothing received from here.
                ''')
                # see `~/lk_logger/sourcemap.py > class:SourceMap > method:
                # _indexing_filemap`
            elif m := walrus_pattern.match(element):
                yield m.group(1), VARIABLE_NAME
            elif caller_pattern.match(element):
                yield element, SUBSCRIPTABLE
            else:
                yield element, VARIABLE_NAME
        
        break


def _debug(linex, line, charx, char, symbols=None):
    # from lk_logger_3_6 import lk
    # lk.logt('[D4011]', visualize_line(
    #     linex, line, charx, char, symbols), h='parent')
    print(visualize_line(linex, line, charx, char, symbols))


class Match:
    
    def __init__(self, cursor: Union[TCursor, tuple],
                 text: str, matches: TMatches2):
        self.cursor = cursor
        self.fulltext = text
        self._matches = matches
        self.spans = list(matches)
    
    def change_depth(self, depth: int):
        def _recurse(collector, node: dict, current_depth):
            if current_depth < depth:
                for v in node.values():
                    _recurse(collector, v, current_depth + 1)
            elif current_depth == depth:
                collector.extend(node.keys())
            return collector
        
        self.spans = _recurse([], self._matches, 0)
    
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
