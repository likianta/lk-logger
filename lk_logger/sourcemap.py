import os
import re
from collections import namedtuple
from functools import wraps
from inspect import currentframe
from types import FrameType
from typing import Optional

from .scanner import get_all_blocks
from .scanner import get_variables


class FrameFinder:
    _hierarchy = {
        'self'              : 1,
        'parent'            : 2,
        'grand_parent'      : 3,
        'great_grand_parent': 4,
    }
    
    _frame_0: Optional[FrameType] = None  # the direct caller frame
    _frame_x: Optional[FrameType] = None  # the target caller frame
    
    def getframe(self, func):
        @wraps(func)
        def _wrap(*args, **kwargs):
            frame = self._frame_0 = currentframe().f_back
            for _ in range(self._hierarchy.get(
                    (h := kwargs.get('h', 'self')), h
            ) - 1):
                frame = frame.f_back
            self._frame_x = frame
            return func(*args, **kwargs)
        
        return _wrap
    
    def getinfo(self):
        assert self._frame_0 and self._frame_x, (
            'You must hold the frame before fetching the frame! '
            '(see `FrameFinder.getframe` decorator)'
        )
        struct = namedtuple('FrameInfo', (
            'direct_filename', 'direct_lineno',
            'source_filename', 'source_lineno',
            'source_name',
        ))
        return struct(
            self._frame_0.f_code.co_filename, self._frame_0.f_lineno,
            self._frame_x.f_code.co_filename, self._frame_x.f_lineno,
            self._frame_x.f_code.co_name,
        )
    
    @property
    def frame(self):
        return self._frame_0


class SourceMap:
    
    def __init__(self):
        self._info_struct = namedtuple(
            'InfoStruct', ('filename', 'lineno', 'name', 'varnames')
        )
        self._sourcemap = {}
        #   dict[filename, dict[lineno, tuple[varname, ...]]]
        self.working_dir = os.getcwd()
        # # self.working_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    def get_frame_info(self, advanced=False):
        info = frame_finder.getinfo()
        
        filename = os.path.relpath(info.source_filename, self.working_dir)
        lineno = info.source_lineno
        name = x if (x := info.source_name).startswith('<') else x + '()'
        varnames = ()
        
        if advanced:
            if info.direct_filename not in self._sourcemap:
                self._indexing_filemap(info.direct_filename)
            varnames = self._sourcemap[info.direct_filename].get(
                info.direct_lineno, ())
        
        return self._info_struct(filename, lineno, name, varnames)
    
    def _indexing_filemap(self, filename: str):
        """
        Args:
            filename
        """
        if filename.startswith('<'):
            # e.g. filename = '<string>', that means the caller came from
            # `eval(<string>)` or `exec<string>`.
            self._sourcemap.setdefault(filename, {})
            return
        
        from .scanner.const import VARIABLE_NAME
        from .scanner.const import SUBSCRIPTABLE
        from .scanner.exceptions import ScanningError
        from .scanner.exceptions import UnresolvedCase
        
        def _get_blocks(lines):
            for match in get_all_blocks(*lines):
                text = match.fulltext.strip()
                if not text:
                    continue
                if not text.startswith('lk.log'):
                    # FIXME (Warning): in lk-logger v4.0.*, the varname-
                    #  detection feature is only enabled when content starts
                    #  with 'lk.log'.
                    continue
                elif re.match(r'^lk\.log\w*\(\)', text):
                    continue
                try:
                    nonlocal node
                    varnames = _analyse_block(text)
                    lineno = match.cursor.lineno + 1
                    node[lineno] = tuple(varnames)
                except ScanningError:
                    nonlocal filename
                    raise ScanningError(
                        match.cursor.lineno + 1, text,
                        0, '<unknown>',
                        f'<filename: {filename}>'
                    )
        
        def _analyse_block(text: str):
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
                
        def _analyse_subscriptables(
                text: str, shorten_sub_substrings=True, threshold=20
        ):
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
            
            quotes_pattern_1 = re.compile(r'\'\'\'[\w\W]*\'\'\'|"""[\w\W]*"""')
            quotes_pattern_2 = re.compile(r'\'[^\']*\'|"[^"]*"')
            
            for i in set(quotes_pattern_1.findall(text)):
                if '\n' in i or len(i) > threshold:
                    text = text.replace(i, '"""..."""')
            
            for i in set(quotes_pattern_2.findall(text)):
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

        node = self._sourcemap.setdefault(filename, {})
        
        with open(filename, 'r', encoding='utf-8') as f:
            node = self._sourcemap.setdefault(filename, {})
            _get_blocks((x.rstrip('\n') for x in f.readlines()))


frame_finder = FrameFinder()
getframe = frame_finder.getframe
sourcemap = SourceMap()

__all__ = ['frame_finder', 'getframe', 'sourcemap']
