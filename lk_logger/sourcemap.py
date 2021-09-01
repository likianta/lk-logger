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
    
    _frame: Optional[FrameType] = None  # frame holder
    
    def getframe(self, func):
        @wraps(func)
        def _wrap(*args, **kwargs):
            frame = currentframe()
            for _ in range(self._hierarchy[kwargs.get('h', 'self')]):
                frame = frame.f_back
            self._frame = frame  # here we hold the frame
            return func(*args, **kwargs)
        
        return _wrap
    
    @property
    def frame(self):
        assert self._frame, 'You must hold the frame (see `self.hold_frame` ' \
                            'decorator) before fetching the frame!'
        return self._frame


class SourceMap:
    
    def __init__(self):
        self._info_struct = namedtuple(
            'InfoStruct', ['filename', 'lineno', 'name', 'varnames']
        )
        self._sourcemap = {}
        #   dict[filename, dict[lineno, tuple[varname, ...]]]
        self.working_dir = os.getcwd()
        # # self.working_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    
    def get_frame_info(self, frame: FrameType, advanced=False):
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        name = frame.f_code.co_name
        
        if advanced:
            if filename not in self._sourcemap:
                self._indexing_filemap(filename)
            varnames = self._sourcemap[filename].get(lineno, ())
        else:
            varnames = ()
        
        return self._info_struct(
            os.path.relpath(filename, self.working_dir),
            lineno,
            name if name.startswith('<') else name + '()',
            varnames
        )
    
    def _indexing_filemap(self, filename: str):
        node = self._sourcemap.setdefault(filename, {})
        
        with open(filename, 'r', encoding='utf-8') as f:
            for match in get_all_blocks(
                    *(x.rstrip('\n') for x in f.readlines())
            ):
                text = match.fulltext.strip()
                if not text:
                    continue
                
                # FIXME (Warning): in lk-logger v4.0, the varname-detection
                #   feature only enables when content starts with 'lk.log'.
                if text.startswith('lkk.log'):  # TEST: lkk.log
                    varnames = []
                    for element, type_ in get_variables(text):
                        # OPTM: pos_mark turns to use OrderedDict
                        if type_ == 0:
                            varnames.append(element)
                        else:
                            varnames.append('')
                    lineno = match.cursor.lineno + 1
                    node[lineno] = tuple(varnames)


frame_finder = FrameFinder()
sourcemap = SourceMap()
