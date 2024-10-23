import builtins
import typing as t
from contextlib import contextmanager
from time import time

from .logger import logger


# noinspection PyProtectedMember
@contextmanager
def counting() -> t.ContextManager:
    logger._markup_analyzer._counter.reset_simple_count()
    yield
    logger._markup_analyzer._counter.reset_simple_count()


# noinspection PyProtectedMember
@contextmanager
def delay() -> t.ContextManager:
    logger._control['stash_outputs'] = True
    yield
    if logger._message_queue:
        for (msg, is_raw, kwargs) in logger._message_queue:
            logger._print(msg, is_raw, **kwargs)
    logger._message_queue.clear()
    logger._control['stash_outputs'] = False


# noinspection PyProtectedMember
@contextmanager
def elevate_caller_stack() -> t.ContextManager:
    logger._control['caller_layer_offset'] += 1
    yield
    logger._control['caller_layer_offset'] -= 1


_builtin_input = builtins.input


def input(prompt: str = '', flush_scheme: int = 0) -> str:
    print(f':f{flush_scheme}s')
    return _builtin_input(prompt)


@contextmanager
def mute() -> t.ContextManager:
    _backup = builtins.print
    builtins.print = lambda *_, **__: None
    yield
    builtins.print = _backup


# noinspection PyProtectedMember
@contextmanager
def timing(sum_up: bool = False, exit_msg: str = None) -> t.ContextManager:
    logger._markup_analyzer._simple_time = time()
    yield
    if exit_msg:
        print(':p2ts', exit_msg)
    elif sum_up:
        print(':p2tsv', 'over')
