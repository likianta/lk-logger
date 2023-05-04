import typing as t
from .markup import T as T0


class T:  # Typehint
    FrameId = str
    MarkupPos = int
    Markup = str
    
    Cache = t.Dict[FrameId, t.TypedDict('_SubDict0', {
        'markup_pos'   : MarkupPos,  # noqa
        'marks_meaning': T0.MarksMeaning,  # noqa
        'info'         : t.Dict[Markup, dict]
    })]


class LoggingCache:
    _cache: T.Cache
    
    def __init__(self) -> None:
        from collections import defaultdict
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
    
    def get_cache(self, frame_id: T.FrameId, markup: T.Markup) -> dict:
        # suggest checking `self.is_cached` before calling this method.
        return self._cache[frame_id]['info'][markup]
    
    # -------------------------------------------------------------------------
    
    def record_markup_pos(self, frame_id: T.FrameId, pos: T.MarkupPos) -> None:
        self._cache[frame_id]['markup_pos'] = pos
    
    def store_info(self, frame_id: T.FrameId, markup: T.Markup, info) -> None:
        self._cache[frame_id]['info'][markup] = info
