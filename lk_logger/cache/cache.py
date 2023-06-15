import atexit
import os
import typing as t
from time import time

from .util import get_content_hash
from .util import pickle_dump
from .util import pickle_load
from ..frame_info import FrameInfo
from ..markup import MarkMeaning
from ..markup import MarkupAnalyser

_CACHE_DIR = os.path.abspath(f'{__file__}/../__cachemap__')
_markup_analyser = MarkupAnalyser()
_is_markup = _markup_analyser.is_valid_markup


class T:
    _Enum = t.Any
    _FilePath = str
    _LineNumber = int
    _Time = int
    
    Args = t.Tuple[t.Any, ...]
    FrameInfo = FrameInfo
    MarksMeaning = MarkMeaning
    MarkupPos = int  # -1, 0, 1
    VarNames = t.Tuple[str, ...]
    
    # TODO: `global_settings` may be removed.
    # noinspection PyTypedDict
    Cache = t.TypedDict('Cache', {
        'working_root'   : str,
        'updated_time'   : _Time,
        'global_settings': t.TypedDict('GlobalSettings', {
            'show_source'  : bool,
            'show_funcname': bool,
            'show_varnames': bool,
        }),
        'optimizations'  : t.TypedDict('Optimizations', {
            'source_width'  : t.Dict[int, int],
            'funcname_width': t.Dict[int, int],
        }),
        'file_map'       : t.Dict[_FilePath, _Time],
        'source_map'     : t.Dict[
            _FilePath, t.Dict[
                _LineNumber, t.TypedDict('MapInfo', {
                    'markup_pos'   : int,
                    'marks_meaning': t.Dict[str, _Enum],
                    'varnames'     : VarNames,
                })
            ]
        ]
    })
    # noinspection PyTypedDict
    Info = t.TypedDict('Info', {
        'markup_pos'         : int,
        'marks_meaning'      : t.Dict[str, _Enum],
        'varnames'           : VarNames,
        # 'proper_prefix_width': t.Optional[t.Tuple[int, int]],
        'proper_prefix_width': t.Tuple[t.Optional[int], t.Optional[int]],
    })


class Cache:
    _cache: T.Cache
    _path: str
    
    def __init__(self):
        root = os.path.abspath(os.getcwd()).replace('\\', '/')
        root_id = get_content_hash(root)
        self._path = f'{_CACHE_DIR}/{root_id}.pkl'
        if os.path.exists(self._path):
            self._cache = pickle_load(self._path)
            # update (reset) file_map and source_map
            for f, t in self._cache['file_map'].items():
                if not os.path.exists(f):
                    self._cache['file_map'].pop(f)
                    self._cache['source_map'].pop(f)
                    continue
                if os.path.getmtime(f) != t:
                    self._cache['file_map'][f] = os.path.getmtime(f)
                    self._cache['source_map'][f] = {}
                    # self._cache['source_map'][f].clear()
        else:
            self._cache = {
                'working_root'   : root,
                'updated_time'   : int(time()),
                'global_settings': {
                    'show_source'  : True,
                    'show_funcname': True,
                    'show_varnames': False,
                },
                'optimizations'  : {
                    'source_width'  : {},
                    'funcname_width': {},
                },
                'file_map'       : {},
                'source_map'     : {},
            }
        atexit.register(self._auto_save)
    
    @property
    def path(self) -> str:
        return self._path
    
    def get(self, frame_info: T.FrameInfo, aux: T.Args = None) -> T.Info:
        out: t.Optional[T.Info] = None
        fp = frame_info.filepath
        ln = frame_info.lineno
        d0 = self._cache['optimizations']
        if d1 := self._cache['source_map'].get(fp):
            if d2 := d1.get(ln):
                # noinspection PyTypeChecker
                out = {
                    'markup_pos'         : d2['markup_pos'],
                    'marks_meaning'      : d2['marks_meaning'],
                    'varnames'           : d2['varnames'],
                    'proper_prefix_width': (
                        (x := d0['source_width'].get(ln)),
                        (x and d0['funcname_width'].get(ln))
                    )
                }
        else:
            assert fp not in self._cache['file_map']
            self._cache['file_map'][fp] = os.path.getmtime(fp)
            self._cache['source_map'][fp] = {}
        if out is None:
            # assert aux is not None
            pos, meaning, varnames = self._analyze_arguments(frame_info, aux)
            # noinspection PyTypeChecker
            self._cache['source_map'][fp][ln] = {
                'markup_pos'   : pos,
                'marks_meaning': meaning,
                'varnames'     : varnames,
            }
            # noinspection PyTypeChecker
            out = {
                'markup_pos'         : pos,
                'marks_meaning'      : meaning,
                'varnames'           : varnames,
                'proper_prefix_width': (None, None),
            }
        return out
    
    def update_settings(self, **kwargs) -> None:
        if (x := 'show_varnames') in kwargs:
            # show_varnames has special scheme: once it *changed*, whether to
            # True or False, the cache must always be True.
            if kwargs[x] != self._cache['global_settings'][x]:
                kwargs[x] = True
        self._cache['global_settings'].update(kwargs)
    
    def _auto_save(self) -> None:
        def optimize_width_columns() -> None:
            pass  # TODO
        
        optimize_width_columns()
        pickle_dump(self._cache, self._path)
    
    @staticmethod
    def _analyze_arguments(frame_info: T.FrameInfo, args: T.Args) \
            -> t.Tuple[T.MarkupPos, T.MarksMeaning, T.VarNames]:
        """
        markup_pos: which position of `markup` in `args`.
            0 not exists, 1 first place, -1 last place.
        """
        if (
                len(args) > 0 and
                isinstance(args[0], str) and
                args[0].startswith(':') and
                _is_markup(args[0])
        ):
            markup_pos = 1
            marks = _markup_analyser.extract(args[0])
        elif (
                len(args) > 1 and
                isinstance(args[-1], str) and
                args[-1].startswith(':') and
                _is_markup(args[-1])
        ):
            markup_pos = -1
            marks = _markup_analyser.extract(args[-1])
        else:
            markup_pos = 0
            marks = {}
        
        get_varnames = frame_info.collect_varnames  # backup method pointer
        if marks['p']: frame_info = frame_info.get_parent(marks['p'])
        marks_meaning = _markup_analyser.analyze(marks, frame_info=frame_info)
        
        return markup_pos, marks_meaning, get_varnames()


cache = Cache()
