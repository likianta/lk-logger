import typing as t

from ..markup import T as T0
from ..message_builder import T as T1


class T:  # Typehint
    FrameId = str
    Info = T1.Info
    MarkupPos = int
    Markup = str
    
    # noinspection PyTypedDict
    Cache = t.Dict[FrameId, t.TypedDict('CacheValue', {
        'markup_pos'   : MarkupPos,
        'marks_meaning': T0.MarksMeaning,
        'info'         : t.Dict[Markup, T1.Info],
    })]


class LoggingCache:
    _cache: T.Cache
    
    def __init__(self) -> None:
        from collections import defaultdict
        # noinspection PyTypeChecker
        self._cache = defaultdict(lambda: {
            'markup_pos'   : None,
            'marks_meaning': {},
            'info'         : {},
        })
    
    def clear_cache(self) -> None:
        self._cache.clear()
    
    # -------------------------------------------------------------------------
    
    def get_markup_pos(self, frame_id: T.FrameId) -> t.Optional[T.MarkupPos]:
        return self._cache[frame_id].get('markup_pos', None)
    
    def is_cached(self, frame_id: T.FrameId, markup: T.Markup) -> bool:
        return (
                frame_id in self._cache and
                markup in self._cache[frame_id]['info']
        )
    
    def get_cache(self, frame_id: T.FrameId, markup: T.Markup) -> T.Info:
        # suggest checking `self.is_cached` before calling this method.
        return self._cache[frame_id]['info'][markup]
    
    # -------------------------------------------------------------------------
    
    def record_markup_pos(self, frame_id: T.FrameId, pos: T.MarkupPos) -> None:
        self._cache[frame_id]['markup_pos'] = pos
    
    def store_info(self, frame_id: T.FrameId, markup: T.Markup,
                   info: T.Info) -> None:
        self._cache[frame_id]['info'][markup] = info
