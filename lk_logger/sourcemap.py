import os
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
        from .scanner.exceptions import UnresolvedCase
        node = self._sourcemap.setdefault(filename, {})
        
        with open(filename, 'r', encoding='utf-8') as f:
            for match in get_all_blocks(
                    *(x.rstrip('\n') for x in f.readlines())
            ):
                text = match.fulltext.strip()
                if not text:
                    continue
                
                # FIXME (Warning): in lk-logger v4.0, the varname-detection
                #   feature is only enabled when content starts with 'lk.log'.
                if not text.startswith('lk.log'):
                    continue
                    
                varnames = []
                try:
                    for element, type_ in get_variables(text):
                        # OPTM: pos_mark turns to use OrderedDict
                        if type_ == 0:
                            varnames.append(element)
                        else:
                            varnames.append('')
                except UnresolvedCase:
                    del varnames
                    continue
                else:
                    lineno = match.cursor.lineno + 1
                    node[lineno] = tuple(varnames)


frame_finder = FrameFinder()
getframe = frame_finder.getframe
sourcemap = SourceMap()

__all__ = ['frame_finder', 'getframe', 'sourcemap']
