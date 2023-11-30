import inspect
import re
import typing as t
from os.path import abspath
from os.path import exists
from textwrap import dedent
from types import FrameType

from .scanner import get_all_blocks
from .scanner import get_variables
from .scanner.const import SUBSCRIPTABLE
from .scanner.const import VARIABLE_NAME
from .scanner.exceptions import ScanningError
from .scanner.exceptions import UnresolvedCase


class T:
    VarNames = t.Tuple[str, ...]
    SourceMap = t.Dict[str, t.Dict[int, VarNames]]


class SourceMap:
    _sourcemap: T.SourceMap
    
    def __init__(self):
        self._sourcemap = {}
    
    def get_varnames(self, filepath: str, lineno: int) -> T.VarNames:
        if filepath not in self._sourcemap:
            self._indexing_filemap(filepath)
        return self._sourcemap[filepath].get(lineno, ())
    
    def _indexing_filemap(self, filepath: str) -> None:
        if filepath.startswith('<') or filepath.endswith('>') \
                or not exists(filepath):
            # see `FrameInfo > property filepath > docstring notice`
            self._sourcemap.setdefault(filepath, {})
            return
        
        def get_blocks(lines: t.Iterator[str]) -> t.Dict[int, T.VarNames]:
            out = {}
            for match in get_all_blocks(*lines):
                text = match.fulltext.strip()
                if not text:
                    continue
                if not text.startswith('print'):  # FIXME: this is not stable
                    continue
                try:
                    varnames = _analyse_block(text)
                    lineno = match.cursor.lineno + 1
                    out[lineno] = tuple(varnames)
                except ScanningError:
                    raise ScanningError(
                        match.cursor.lineno + 1, text,
                        0, '<unknown>',
                        f'<filepath: {filepath}>'
                    )
            return out
        
        def _analyse_block(text: str) -> t.List[str]:
            varnames = []
            try:
                for element, type_ in get_variables(text):
                    if type_ == VARIABLE_NAME:
                        varnames.append(element)
                    elif type_ == SUBSCRIPTABLE:
                        varnames.append(_analyse_subscriptables(
                            element, shorten_sub_substrings=True
                        ))
                    else:
                        varnames.append('')
            except UnresolvedCase:
                varnames.clear()
            finally:
                return varnames
        
        _quotes_pattern_1 = re.compile(r'\'\'\'[\w\W]*\'\'\'|"""[\w\W]*"""')
        _quotes_pattern_2 = re.compile(r'\'[^\']*\'|"[^"]*"')
        
        def _analyse_subscriptables(
                text: str,
                shorten_sub_substrings: bool = True,
                threshold: int = 20
        ) -> str:
            """
            shorten_sub_strings:
                example:
                    case 1: when captured a "varname" like "xxx('hello world')":
                        if shorten_sub_strings is True:
                            varname updated: "xxx('...')"
                        if shorten_sub_strings is False:
                            varname updated: "xxx('hello world')"
                    case 2: when captured a "varname" like "xxx('''hello world\n
                            hello world\nhello world\nhello world\nhello...''')"
                            (which is a very long sentense):
                        if shorten_sub_strings is True:
                            varname updated: "xxx('...')"
                        if shorten_sub_strings is False:
                            varname updated: "xxx('''hello world\nhello world\n
                                hello world\nhello world\nhello world\n...)"
                note: the character threshold length to trigger shortening a
                    string is adjustable, the default threshold is 10 chars and
                    must with no line break in it.
            """
            if not shorten_sub_substrings:
                return text
            
            backslash_mask = []
            for i in re.findall(r'\\.', text):
                backslash_mask.append(i)
            if backslash_mask:
                text = re.sub(r'\\.', '__BACKSLASK_MASK__', text)
            
            for i in set(_quotes_pattern_1.findall(text)):
                if '\n' in i or len(i) > threshold:
                    text = text.replace(i, '"""..."""')
            
            for i in set(_quotes_pattern_2.findall(text)):
                if '\n' in i or len(i) > threshold:
                    text = text.replace(i, '"..."')
            
            # restore backslashes
            if backslash_mask:
                for i in backslash_mask:
                    text = text.replace('__BACKSLASK_MASK__', i, 1)
                del backslash_mask
            
            text = re.sub(r'\s+', ' ', text)
            #   note: this ^measure takes a side effect that it may replace
            #   sequential whitespaces to one whitespace inside quote strings.
            
            return text
        
        with open(filepath, 'r', encoding='utf-8') as f:
            self._sourcemap.setdefault(
                filepath, get_blocks((x.rstrip('\n') for x in f.readlines()))
            )


sourcemap = SourceMap()


class FrameInfo:
    
    def __init__(self, frame: FrameType):
        self._frame = frame
    
    def __str__(self) -> str:
        return self.info
    
    @property
    def info(self) -> str:
        return dedent(f'''
            <FrameInfo object>
                filepath: {self.filepath}
                lineno: {self.lineno}
                funcname: {self.funcname}
        ''').rstrip()
    
    @property
    def id(self) -> str:
        return f'{self.filepath}:{self.lineno}'
    
    @property
    def filepath(self) -> str:
        """
        notice:
            - the returned value may be '<string>', '<unknown>' etc.
            - (2023-05-22):
                we do not use `__file__` anymore, because it may cause markup
                analyser broken when the `__file__` is not real (for example
                when caller passes `globals()` to `exec` function).
                see also `examples/start_ipython.py : line 11`.
            - in python 3.8, `co_filename` may be a relative path, so we need
                to convert it to absolute.
            - (2023-06-30):
                the path may be unexisted, for example a kernel file using
                `background_zmq_ipython` library.
        """
        # from ._print import debug
        # debug(self._frame.f_code.co_filename,
        #       self._frame.f_globals.get('__file__'))
        return abspath(self._frame.f_code.co_filename).replace('\\', '/')
    
    @property
    def lineno(self) -> int:
        return self._frame.f_lineno
    
    @property
    def indentation(self) -> int:
        # https://stackoverflow.com/a/39172552
        if x := inspect.getframeinfo(self._frame).code_context:
            ctx = x[0]
            return len(ctx) - len(ctx.lstrip())
        return 0
    
    @property
    def funcname(self) -> str:
        return self._frame.f_code.co_name
    
    def collect_varnames(self) -> T.VarNames:
        return sourcemap.get_varnames(self.filepath, self.lineno)
    
    def get_parent(self, traceback_level: int = 1) -> 'FrameInfo':
        frame = self._frame
        for _ in range(traceback_level):
            frame = frame.f_back
        return FrameInfo(frame)
