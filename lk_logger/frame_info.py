import inspect
import typing as t
from dataclasses import dataclass
from textwrap import dedent
from types import FrameType

from .markup import MarkMeaning
from .markup import T as T0
from .markup import markup_analyzer
from .path_helper import normpath
from .sourcemap import T as T1
from .sourcemap import sourcemap


class T:
    EvaluatedMarks = T0.MarksMeaning
    Markup = T0.Markup
    StaticMarks = T0.Marks
    VarNames = T1.VarNames
    
    MarkupPos = int  # -1, 0, 1
    RawArgs = t.Tuple[t.Any, ...]


class FrameInfo:
    
    def __init__(self, frame: FrameType) -> None:
        self._frame = frame
    
    def __str__(self) -> str:
        return self.info
    
    @property
    def info(self) -> str:
        return dedent(f'''
            <FrameInfo object>
                filepath: {self.filepath}
                lineno: {self.lineno}
                funcname: {self.funcname}
        ''').rstrip()
    
    @property
    def id(self) -> str:
        return f'{self.filepath}:{self.lineno}'
    
    @property
    def filepath(self) -> str:
        """
        notice:
            - the returned value may be '<string>', '<unknown>' etc.
            - (2023-05-22):
                we do not use `__file__` anymore, because it may cause markup
                analyser broken when the `__file__` is not real (for example
                when caller passes `globals()` to `exec` function).
                see also `examples/start_ipython.py : line 11`.
            - in python 3.8, `co_filename` may be a relative path, so we need
                to convert it to absolute.
            - (2023-06-30):
                the path may be unexisted, for example a kernel file using
                `background_zmq_ipython` library.
        """
        # from ._print import debug
        # debug(self._frame.f_code.co_filename,
        #       self._frame.f_globals.get('__file__'))
        x = self._frame.f_code.co_filename
        if x.startswith('<') and x.endswith('>'):
            return '<{}@{}>'.format(x[1:-1], id(self._frame))
        else:
            return normpath(x)
    
    @property
    def lineno(self) -> int:
        return self._frame.f_lineno
    
    @property
    def indentation(self) -> int:
        # https://stackoverflow.com/a/39172552
        if x := inspect.getframeinfo(self._frame).code_context:
            ctx = x[0]
            return len(ctx) - len(ctx.lstrip())
        return 0
    
    @property
    def funcname(self) -> str:
        return self._frame.f_code.co_name
    
    def collect_varnames(self) -> T.VarNames:
        return sourcemap.get_varnames(self.filepath, self.lineno)
    
    def get_parent(self, traceback_level: int = 1) -> 'FrameInfo':
        return FrameInfo(_get_parent_frame(self._frame, traceback_level))


# -----------------------------------------------------------------------------
# DELETE?

@dataclass
class FrozenFrameInfo:
    """
    this is picklable. used for multiprocessing queue.
    """
    filepath: str
    lineno: int
    indentation: int
    funcname: str
    _parent: 'FrozenFrameInfo' = None
    
    @property
    def id(self) -> str:
        return f'{self.filepath}:{self.lineno}'
    
    def collect_varnames(self) -> T.VarNames:
        return sourcemap.get_varnames(self.filepath, self.lineno)
    
    def get_parent(self, _) -> 'FrozenFrameInfo':
        assert self._parent
        return self._parent


def freeze_frame_info(
    frame: FrameType,
    _traceback_level: int = 0,
) -> FrozenFrameInfo:
    info = FrameInfo(frame)
    return FrozenFrameInfo(
        info.filepath,
        info.lineno,
        info.indentation,
        info.funcname,
        (
            _traceback_level > 0 and
            freeze_frame_info(_get_parent_frame(frame, _traceback_level)) or
            None
        )
    )


def _get_parent_frame(frame: FrameType, level: int = 1) -> FrameType:
    for _ in range(level):
        frame = frame.f_back
    return frame


# -----------------------------------------------------------------------------
# TODO: work in progress

class ArgSpec:
    def __init__(self, frame_info: FrameInfo, raw_args: T.RawArgs) -> None:
        args, markup_pos, markup = (
            self._separate_markup_from_arguments(raw_args)
        )
        self.args = args
        self.markspec = MarkSpec(markup)
        varnames = frame_info.collect_varnames()
        if markup_pos == 1:
            varnames = varnames[1:]
        elif markup_pos == -1:
            varnames = varnames[:-1]
        self.varnames = varnames
    
    @staticmethod
    def _separate_markup_from_arguments(
        args: T.RawArgs
    ) -> t.Tuple[T.RawArgs, T.MarkupPos, T.Markup]:
        """
        return: (args, markup_pos, markup)
            markup_pos: which position of `markup` in `args`.
                0 not exists, 1 first place, -1 last place.
        """
        is_markup = markup_analyzer.is_valid_markup
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
        
        if markup_pos == 0:
            return args, markup_pos, ''
        elif markup_pos == 1:
            return args[1:], markup_pos, args[0]
        else:  # -1
            return args[:-1], markup_pos, args[-1]


class MarkSpec:
    _evaluated_marks: T.EvaluatedMarks
    _static_marks: T.StaticMarks
    
    def __init__(self, markup: str) -> None:
        self._static_marks = markup_analyzer.extract(markup)
        self.execute()
    
    def __contains__(self, item: MarkMeaning) -> bool:
        return item in self._evaluated_marks
    
    def execute(self) -> None:
        # refresh evaluated marks
        self._evaluated_marks = markup_analyzer.analyze(self._static_marks)
