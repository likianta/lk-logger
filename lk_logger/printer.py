import builtins
import typing as t
from inspect import currentframe
from contextlib import contextmanager
from os import name as os_name


class BasePrinter:
    def __call__(self, msg: str, *_, **__) -> None:
        raise NotImplementedError


class DebugPrinter(BasePrinter):
    def __call__(self, msg: str, *_, **__) -> None:
        frame = currentframe().f_back
        filepath = _normpath(frame.f_globals["__file__"])
        lineno = frame.f_lineno
        source = '{}:{}'.format(filepath, lineno)
        std_print(source, '[LKDEBUG]', msg)


class NothingPrinter(BasePrinter):
    def __call__(self, msg: str, *_, **__) -> None:
        pass  # do nothing


std_print = t.cast(BasePrinter, builtins.print)
dbg_print = DebugPrinter()
non_print = NothingPrinter()

# alias
bprint = std_print
dprint = dbg_print


# -----------------------------------------------------------------------------
# group control

class T:
    Printers = t.Tuple[BasePrinter, ...]


class PrinterManager:
    _group: t.List[T.Printers]
    
    def __init__(self) -> None:
        self._group = [(std_print,)]
    
    @property
    def printers(self) -> T.Printers:
        return self._group[-1]
    
    def add_group(self, printers: T.Printers) -> None:
        self._group.append(printers)
        
    def pop_group(self) -> None:
        self._group.pop()


printer_manager = PrinterManager()


@contextmanager
def parallel_printing(
    *printers: BasePrinter, inherit: bool = True
) -> t.Iterator:
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
        printers = printer_manager.printers + printers
    printer_manager.add_group(printers)
    yield
    printer_manager.pop_group()


# -----------------------------------------------------------------------------
# general

_IS_WIN = os_name == 'nt'


def _normpath(path: str) -> str:
    if _IS_WIN:
        return path.replace('\\', '/').rstrip('/')
    return path.rstrip('/')
