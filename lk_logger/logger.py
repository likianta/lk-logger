from __future__ import annotations

from inspect import currentframe

from ._internal_debug import debug  # noqa
from .console import con_print

__all__ = ['LKLogger', 'lk']


class T:  # Typehint
    from rich.console import RenderableType
    from typing import Iterable, TypedDict, Union
    from .markup import T as _TMarkup  # noqa
    
    Args = Union[list[str], tuple[str, ...]]
    MarkupPos = int
    Markup = str
    Marks = _TMarkup.Marks
    MarksMeaning = _TMarkup.MarksMeaning
    
    Info = TypedDict('Info', {
        'file_path'      : str,
        'line_number'    : str,
        'is_external_lib': bool,
        'function_name'  : str,
        'variable_names' : Iterable[str],
    })


class LKLogger:
    
    def __init__(self):
        from .cache import LoggingCache
        from .config import LoggingConfig
        from .markup import MarkupAnalyser
        from .message_builder import MessageBuilder
        
        self._analyser = MarkupAnalyser()
        self._builder = MessageBuilder()
        self._cache = LoggingCache()
        self._config = LoggingConfig()
    
    def configure(self, clear_preset=False, **kwargs) -> None:
        self._cache.clear_cache()
        if clear_preset:
            self._config.reset()
        self._config.update(**kwargs)
        self._builder.update_config(
            separator=self._config.separator,
            show_source=self._config.show_source,
            show_funcname=self._config.show_funcname,
            show_varnames=self._config.show_varnames,
        )
    
    # -------------------------------------------------------------------------
    
    def log(self, *args, **kwargs) -> None:
        msg = self._build_message(currentframe().f_back, *args)
        # debug(msg)
        con_print(msg, **kwargs)
    
    def fmt(self, *args, **_) -> str:
        return str(self._build_message(currentframe().f_back, *args))
    
    def _build_message(self, frame, *args) -> T.RenderableType:
        from .markup import MarkMeaning
        
        frame_id = f'{id(frame)}#{frame.f_lineno}'
        args, markup_pos, markup = \
            self._extract_markup_from_arguments(frame_id, args)
        marks = self._analyser.extract(markup)
        marks_meaning = self._analyser.analyse(marks)
        
        # check cache
        if self._cache.is_cached(frame_id, markup):
            cached_info = self._cache.get_cache(frame_id, markup)
            return self._builder.compose(
                args, marks_meaning, cached_info
            )
        
        # ---------------------------------------------------------------------
        
        if MarkMeaning.AGRESSIVE_PRUNE in marks_meaning:
            return self._builder.quick_compose(args)
        
        info: T.Info = {
            'file_path'      : '',
            'line_number'    : '0',
            'is_external_lib': False,
            'function_name'  : '',
            'variable_names' : (),
        }
        
        show_source = self._config.show_source
        show_funcname = self._config.show_funcname
        show_varnames = self._config.show_varnames and \
                        MarkMeaning.MODERATE_PRUNE not in marks_meaning
        
        if any((show_source, show_funcname, show_varnames)):
            from .sourcemap import sourcemap
            srcmap = sourcemap.get_sourcemap(
                frame=frame,
                traceback_level=marks['p'],
                advanced=show_varnames,
            )
            
            if show_source:
                
                def update_sourcemap():
                    """
                    this function updates follows:
                        info['is_external_lib']
                        info['file_path']
                        info['line_number']
                    """
                    from .path_helper import path_helper
                    path = srcmap.filepath
                    info['is_external_lib'] = path_helper.is_external_lib(path)
                    
                    if info['is_external_lib']:
                        if self._config.show_external_lib:
                            style = self._config.path_style_for_external_lib
                            info['file_path'] = \
                                path_helper.reformat_external_lib_path(
                                    path, style
                                )
                        else:
                            info['file_path'] = ''
                    else:
                        info['file_path'] = path_helper.relpath(path)
                    
                    info['line_number'] = str(srcmap.lineno)
                
                update_sourcemap()
            
            if show_funcname:
                info['function_name'] = srcmap.funcname
            
            if show_varnames:
                if markup_pos == 0:
                    info['variable_names'] = srcmap.varnames
                elif markup_pos == 1:
                    info['variable_names'] = srcmap.varnames[1:]
                else:
                    info['variable_names'] = srcmap.varnames[:-1]
        
        self._cache.store_info(frame_id, markup, info)
        
        return self._builder.compose(args, marks_meaning, info)
    
    def _extract_markup_from_arguments(
            self, frame_id: str, args: T.Args
    ) -> tuple[T.Args, T.MarkupPos, T.Markup]:
        if (markup_pos := self._cache.get_markup_pos(frame_id)) is None:
            is_markup = self._analyser.is_valid_markup
            if (
                    len(args) > 0 and
                    isinstance(args[0], str) and
                    args[0].startswith(':') and
                    is_markup(args[0])
            ):
                markup_pos = 1
            elif (
                    len(args) > 1 and
                    isinstance(args[-1], str) and
                    args[-1].startswith(':') and
                    is_markup(args[-1])
            ):
                markup_pos = -1
            else:
                markup_pos = 0
            self._cache.record_markup_pos(frame_id, markup_pos)
        
        # markup_pos: 0 not exists, 1 first place, -1 last place.
        args = tuple(map(str, args))
        if markup_pos == 0:
            return args, markup_pos, ''
        if markup_pos == 1:
            return args[1:], markup_pos, args[0]
        else:
            return args[:-1], markup_pos, args[-1]


lk = LKLogger()
