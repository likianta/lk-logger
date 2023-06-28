import typing as t
from atexit import register
from collections import deque
from inspect import currentframe
from threading import Thread
from time import sleep

from rich.console import RenderableType
from rich.traceback import Traceback

from ._print import bprint
from ._print import debug  # noqa
from .cache import LoggingCache
from .config import LoggingConfig
from .console import con_print
from .frame_info import FrameInfo
from .markup import MarkMeaning
from .markup import MarkupAnalyser
from .markup import T as T0
from .message_builder import MessageStruct
from .message_builder import T as T1
from .message_builder import builder as message_builder
from .path_helper import path_helper
from .pipeline import pipeline
from .shunt import Shunt
from .shunt import T as T2


class _RawArgs:  # a workaround. see its usage below.
    def __init__(self, args: t.Tuple[t.Any, ...]):
        self.args = args


class _NoMessage:
    pass


class T:  # Typehint
    Args = t.Tuple[t.Any, ...]
    ComposedMessage = t.Union[
        RenderableType, T1.MessageStruct, Traceback,
        t.Type[_NoMessage], _RawArgs
    ]
    FlushScheme = int
    #   0: no flush
    #   1: instant flush
    #   2: instant flush and drain
    #   3: wait for flush
    Info = T1.Info
    Markup = T0.Markup
    MarkupPos = int  # -1, 0, 1
    Pipe = T2.Pipe
    PipeId = T2.PipeId


class LKLogger:
    
    def __init__(self):
        self._analyser = MarkupAnalyser()
        self._cache = LoggingCache()
        self._config = LoggingConfig()
        
        self._shunt = Shunt()
        # self._shunt.add(con_print)
        self.add_pipe = self._shunt.add
        self.remove_pipe = self._shunt.remove
        
        self._running = False
        self._message_queue = deque()
        register(self._stop_running)
        self._thread = Thread(target=self._start_running)
        self._thread.daemon = True
        self._thread.start()
    
    def configure(self, clear_preset=False, **kwargs) -> None:
        self._cache.clear_cache()
        if clear_preset:
            self._config.reset()
        if 'show_varname' in kwargs:  # workaround for compatibility
            kwargs['show_varnames'] = kwargs.pop('show_varname')
        self._config.update(**kwargs)
        message_builder.update_config(
            separator=self._config.separator,
        )
    
    @property
    def config(self) -> dict:
        return self._config.to_dict()
    
    def _start_running(self) -> None:
        
        def consume() -> None:
            msg: t.Union[str, tuple]
            kwargs: dict
            custom_print: t.Optional[t.Callable]
            
            for i in range(len(self._message_queue)):
                if not self._message_queue: break
                msg, kwargs, custom_print = self._message_queue.popleft()
                if custom_print:
                    # debug(custom_print, msg, kwargs)
                    kwargs.pop('file', None)
                    custom_print(*msg, **kwargs)
                else:
                    self._cprint(msg, **kwargs)
                    self._dprint(msg)
        
        self._running = True
        while self._running:
            if self._message_queue:
                consume()
            else:
                sleep(10E-3)
        else:
            consume()
    
    def _stop_running(self) -> None:
        if self._config.clear_unfinished_stream:
            self._message_queue.clear()
        self._running = False
        self._thread.join()
    
    # -------------------------------------------------------------------------
    
    def log(
            self,
            *args: t.Any,
            _frame_info: FrameInfo = None,
            **kwargs
    ) -> None:
        if _frame_info is None:
            _frame_info = FrameInfo(currentframe().f_back)
            # debug(_frame_info.info)
        
        if (path := _frame_info.filepath) \
                and (custom_print := pipeline.get(path)):
            if self._config.async_:
                self._message_queue.append((args, kwargs, custom_print))
            else:
                custom_print(*args, **kwargs)
            return
        
        msg, flush_scheme = self._build_message(_frame_info, *args)
        if msg is _NoMessage: return
        is_raw = isinstance(msg, _RawArgs)
        # debug(msg)
        
        self._print(msg, flush_scheme, _is_raw=is_raw, **kwargs)
    
    def _print(
            self,
            msg: T.ComposedMessage,
            flush_scheme: T.FlushScheme = 0,
            _is_raw: bool = False,
            **kwargs
    ) -> None:
        if flush_scheme == 0:
            if self._config.async_:
                if _is_raw:
                    self._message_queue.append((msg.args, kwargs, bprint))
                else:
                    self._message_queue.append((msg, kwargs, None))
            else:
                if _is_raw:
                    self._bprint(msg, **kwargs)
                else:
                    self._cprint(msg, **kwargs)
                    self._dprint(msg)
        elif flush_scheme == 1:
            while self._message_queue:
                sleep(10E-3)
            if _is_raw:
                self._bprint(msg, **kwargs)
            else:
                self._cprint(msg, **kwargs)
                self._dprint(msg)
        elif flush_scheme == 2:
            if skipped_count := len(self._message_queue):
                self._message_queue.clear()
                print(':frp2', f'[red dim](... skipped '
                               f'{skipped_count} messages)[/]')
            if _is_raw:
                self._bprint(msg, **kwargs)
            else:
                self._cprint(msg, **kwargs)
                self._dprint(msg)
        elif flush_scheme == 3:
            if _is_raw:
                self._bprint(msg, **kwargs)
            else:
                self._cprint(msg, **kwargs)
                self._dprint(msg)
        else:
            raise ValueError(flush_scheme)
    
    @staticmethod
    def _bprint(msg: _RawArgs, **kwargs) -> None:
        bprint(*msg.args, **kwargs)
    
    @staticmethod
    def _cprint(msg: T.ComposedMessage, **kwargs) -> None:
        if isinstance(msg, MessageStruct):
            con_print(msg.text, **kwargs)
        else:
            con_print(msg, **kwargs)
    
    def _dprint(self, msg: T.ComposedMessage) -> None:
        if self._shunt:
            if isinstance(msg, MessageStruct):
                for caller in self._shunt:
                    caller(msg.body.plain)
    
    # FIXME
    def fmt(self, _frame_info: FrameInfo = None, *args, **_) -> str:
        return str(self._build_message(
            _frame_info or FrameInfo(currentframe().f_back), *args
        )[0])
    
    # -------------------------------------------------------------------------
    
    def _build_message(
            self, frame_info: FrameInfo, *args
    ) -> t.Tuple[T.ComposedMessage, T.FlushScheme]:
        args, markup_pos, markup = \
            self._extract_markup_from_arguments(frame_info.id, args)
        marks = self._analyser.extract(markup)
        
        get_varnames = frame_info.collect_varnames  # backup method pointer
        if marks['p']: frame_info = frame_info.get_parent(marks['p'])
        marks_meaning = self._analyser.analyze(marks, frame_info=frame_info)
        del marks
        
        flush_scheme: T.FlushScheme = 0
        if MarkMeaning.FLUSH in marks_meaning:
            flush_scheme = 1
        elif MarkMeaning.FLUSH_CUTOFF in marks_meaning:
            flush_scheme = 2
        elif MarkMeaning.FLUSH_EDDY in marks_meaning:
            flush_scheme = 3
        
        # check cache
        if self._cache.is_cached(frame_info.id, markup):
            cached_info = self._cache.get_cache(frame_info.id, markup)
            return message_builder.compose(
                args, marks_meaning, cached_info,
                self._config.show_source,
                self._config.show_funcname,
                self._config.show_varnames,
                self._config.sourcemap_alignment,
            ), flush_scheme
        
        # ---------------------------------------------------------------------
        
        if not args:
            if MarkMeaning.MODERATE_PRUNE in marks_meaning or \
                    MarkMeaning.AGRESSIVE_PRUNE in marks_meaning:
                return _NoMessage, flush_scheme
        if MarkMeaning.BUILTIN_PRINT in marks_meaning:
            return _RawArgs(args), flush_scheme
        elif MarkMeaning.RICH_OBJECT in marks_meaning:
            assert len(args) == 1 and isinstance(args[0], RenderableType)
            return args[0], flush_scheme
        elif MarkMeaning.TRACEBACK_EXCEPTION in marks_meaning:
            assert len(args) == 1 and isinstance(args[0], BaseException)
            return message_builder.compose_exception(
                args[0], show_locals=False
            ), flush_scheme
        elif MarkMeaning.TRACEBACK_EXCEPTION_WITH_LOCALS in marks_meaning:
            assert len(args) == 1 and isinstance(args[0], BaseException)
            return message_builder.compose_exception(
                args[0], show_locals=True
            ), flush_scheme
        
        info: T.Info = {
            'file_path'      : '',
            'line_number'    : '0',
            'is_external_lib': False,
            'function_name'  : '',
            'variable_names' : (),
        }
        
        show_source = (
                self._config.show_source and
                (MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning)
        )
        show_funcname = (
                self._config.show_funcname and
                (MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning)
        )
        show_varnames = (
                self._config.show_varnames and
                MarkMeaning.MODERATE_PRUNE not in marks_meaning and
                MarkMeaning.AGRESSIVE_PRUNE not in marks_meaning
        )
        
        if any((show_source, show_funcname, show_varnames)):
            if show_source:
                def update_sourcemap():
                    """
                    this function updates follows:
                        info['is_external_lib']
                        info['file_path']
                        info['line_number']
                    """
                    path = frame_info.filepath
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
                    
                    info['line_number'] = str(frame_info.lineno)
                
                update_sourcemap()
            
            if show_funcname:
                info['function_name'] = frame_info.funcname
            
            if show_varnames:
                varnames = get_varnames()
                if markup_pos == 0:
                    info['variable_names'] = varnames
                elif markup_pos == 1:
                    info['variable_names'] = varnames[1:]
                else:
                    info['variable_names'] = varnames[:-1]
        
        self._cache.store_info(frame_info.id, markup, info)
        
        return message_builder.compose(
            args, marks_meaning, info,
            show_source=show_source,
            show_funcname=show_funcname,
            show_varnames=show_varnames,
            sourcemap_alignment=self._config.sourcemap_alignment,
        ), flush_scheme
    
    def _extract_markup_from_arguments(
            self, frame_id: str, args: T.Args
    ) -> t.Tuple[T.Args, T.MarkupPos, T.Markup]:
        """
        return: (args, markup_pos, markup)
            markup_pos: which position of `markup` in `args`.
                0 not exists, 1 first place, -1 last place.
        """
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
        
        if markup_pos == 0:
            return args, markup_pos, ''
        elif markup_pos == 1:
            return args[1:], markup_pos, args[0]
        else:
            return args[:-1], markup_pos, args[-1]


lk = LKLogger()
