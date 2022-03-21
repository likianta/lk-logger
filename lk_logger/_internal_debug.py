"""
usage:
    from ._internal_debug import debug
    with debug.enable():
        debug('some message')
"""
from contextlib import contextmanager

from .general import std_print


class Debugger:
    
    def __init__(self):
        self.enabled = False
    
    @contextmanager
    def enable(self, condition: bool = None):
        if condition is None:
            self.enabled = True
        else:
            self.enabled = condition
        yield
        self.enabled = False
    
    def __call__(self, *args):
        if self.enabled:
            std_print(*args)


debug = Debugger()
