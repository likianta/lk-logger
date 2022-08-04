from __future__ import annotations

import typing as t


class T:  # Typehint
    from .markup import T as _TMarkup  # noqa
    
    FrameId = int
    MarkupPos = int
    Markup = str
    
    CachedInfo = t.TypedDict('CachedInfo', {
        'marks_meaning'  : _TMarkup.MarksMeaning,  # noqa
        'file_path'      : str,
        'function_name'  : str,
        'is_external_lib': bool,
        'line_number'    : int,
        'traceback_level': int,
        'varnames'       : tuple[str, ...],
    })
    
    Cache = dict[FrameId, t.TypedDict('_SubDict0', {
        'markup_pos': MarkupPos,  # noqa
        'marks_meaning': _TMarkup.MarksMeaning,  # noqa
        'info'      : dict[Markup, CachedInfo]
    })]


class LoggingCache:
    _cache: T.Cache
    
    def __init__(self):
        from collections import defaultdict
        self._cache = defaultdict(lambda: {
            'markup_pos': None,
            'marks_meaning': {},
            'info'      : {},
        })
    
    def clear_cache(self):
        self._cache.clear()
    
    # -------------------------------------------------------------------------
    
    def get_markup_pos(self, frame_id: T.FrameId) -> T.MarkupPos | None:
        return self._cache[frame_id].get('markup_pos', None)
    
    def is_cached(self, frame_id: T.FrameId, markup: T.Markup) -> bool:
        return (
                frame_id in self._cache and
                markup in self._cache[frame_id]['info']
        )
    
    def get_cache(self,
                  frame_id: T.FrameId,
                  markup: T.Markup) -> T.CachedInfo:
        # suggest checking `self.is_cached` before calling this method.
        return self._cache[frame_id]['info'][markup]
    
    # -------------------------------------------------------------------------
    
    def record_markup_pos(self, frame_id: T.FrameId, pos: T.MarkupPos) -> None:
        self._cache[frame_id]['markup_pos'] = pos
    
    def store_info(self, frame_id: T.FrameId, markup: T.Markup, info) -> None:
        self._cache[frame_id]['info'][markup] = info
