import re
from collections import namedtuple
from types import FrameType

from ._print import debug  # noqa
from .scanner import get_all_blocks
from .scanner import get_variables


class SourceMap:
    
    def __init__(self):
        self._sourcemap = {}
        #   dict[str filepath, dict[int lineno, tuple[str varname, ...]]]
    
    @staticmethod
    def get_frame_info(frame: FrameType, traceback_level: int):
        from .path_helper import normpath
        
        frame_0 = frame
        frame_x: FrameType
        for _ in range(traceback_level):
            frame = frame.f_back
        frame_x = frame
        
        struct = namedtuple('FrameInfo', (
            'direct_filepath', 'direct_lineno',
            'target_filepath', 'target_lineno',
            'target_funcname',
        ))
        
        return struct(
            normpath(frame_0.f_globals.get('__file__', '<unknown>')),
            frame_0.f_lineno,
            normpath(frame_x.f_globals.get('__file__', '<unknown>')),
            frame_x.f_lineno,
            frame_x.f_code.co_name,
        )
    
    def get_sourcemap(self, frame: FrameType, traceback_level: int = 0,
                      advanced=False):
        info = self.get_frame_info(frame, traceback_level)
        
        struct = namedtuple('InfoStruct', (
            'filepath', 'lineno', 'funcname', 'varnames'
        ))
        
        if advanced:
            if info.direct_filepath not in self._sourcemap:
                self._indexing_filemap(info.direct_filepath)
            varnames = self._sourcemap[info.direct_filepath].get(
                info.direct_lineno, ())
        else:
            varnames = ()
        
        return struct(
            info.target_filepath,
            info.target_lineno,
            info.target_funcname,
            varnames,
        )
    
    def _indexing_filemap(self, filepath: str):
        """
        Args:
            filepath
        """
        if filepath.startswith('<'):
            # see `FrameFinder.getinfo._fix_filepath_location`
            self._sourcemap.setdefault(filepath, {})
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
                if not text.startswith('print'):  # FIXME: this is not stable
                    continue
                try:
                    nonlocal node
                    varnames = _analyse_block(text)
                    lineno = match.cursor.lineno + 1
                    node[lineno] = tuple(varnames)
                except ScanningError:
                    nonlocal filepath
                    raise ScanningError(
                        match.cursor.lineno + 1, text,
                        0, '<unknown>',
                        f'<filepath: {filepath}>'
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
        
        node = self._sourcemap.setdefault(filepath, {})
        
        with open(filepath, 'r', encoding='utf-8') as f:
            node = self._sourcemap.setdefault(filepath, {})
            _get_blocks((x.rstrip('\n') for x in f.readlines()))


sourcemap = SourceMap()

__all__ = ['sourcemap']
