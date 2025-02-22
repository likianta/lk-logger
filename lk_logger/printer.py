import builtins
import os
import typing as t
from inspect import currentframe
from contextlib import contextmanager
from functools import partial
from pprint import pformat

from .console import console


class BasePrinter:
    def __call__(self, *msg: t.Any) -> None:
        raise NotImplementedError


class DebugPrinter(BasePrinter):
    
    def __init__(self) -> None:
        self._root = os.path.normpath('{}/../../'.format(__file__))
        # std_print('[LKDEBUG]', self._root)
    
    def __call__(self, *msg: t.Any) -> None:
        frame = currentframe().f_back
        path = (
            os.path.relpath(frame.f_globals['__file__'], start=self._root)
            .replace('\\', '/').rstrip('/')
        )
        lineno = frame.f_lineno
        std_print(
            '[LKDEBUG] {}:{} >'.format(path, lineno),
            '\n  ' + pformat(msg, indent=2)
        )


class NothingPrinter(BasePrinter):
    def __call__(self, *msg: t.Any, **_) -> None:
        pass  # do nothing


std_print = t.cast(BasePrinter, builtins.print)
con_print = console.print
con_error = partial(console.print_exception, word_wrap=True)
dbg_print = DebugPrinter()
non_print = NothingPrinter()

# alias
bprint = std_print
dprint = dbg_print


# -----------------------------------------------------------------------------
# group control

class T:
    Printer = t.Union[BasePrinter, t.Callable[[str], None]]
    Printers = t.Tuple[Printer, ...]


class PrinterManager:
    _group: t.List[T.Printers]
    _is_under_iterating: bool
    
    def __init__(self) -> None:
        # self.is_scoping = False
        # self._group = [(std_print,)]
        self._group = [()]
        self._is_under_iterating = False
    
    @property
    def printers(self) -> t.Iterator[T.Printer]:
        # prevent recursive call
        if self._is_under_iterating:
            # dprint('under iteration')
            return
        self._is_under_iterating = True
        yield from self._group[-1]
        self._is_under_iterating = False
    
    def add_group(self, printers: T.Printers) -> None:
        self._group.append(printers)
        
    def pop_group(self) -> None:
        self._group.pop()


printer_manager = PrinterManager()


@contextmanager
def parallel_printing(*printers: T.Printer, inherit: bool = True) -> t.Iterator:
    """
    params:
        inherit: if True, will inherit the previous printers.
            for example:
                with parallel_printing(p1, p2):
                    print('aaa')  # p1, p2 called
                    with parallel_printing(p3):
                        print('bbb')  # p1, p2, p3 called
                    with parallel_printing(p4, inherit=False):
                        print('ccc')  # p4 called
                        with parallel_printing(p5):
                            print('ddd')  # p4, p5 called
    """
    if inherit:
        printers = tuple(printer_manager.printers) + printers
    printer_manager.add_group(printers)
    yield
    printer_manager.pop_group()
