"""
usage:
    from ._internal_debug import debug
    
    # 1
    with debug.enable():
        debug('some message')
        
    # 2
    debug.enabled = True
    debug('some message')
    ...
    debug.enabled = False
    
    # 3
    debug('some message', condition=True)
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
    
    def __call__(self, *args, condition=None):
        if self.enabled or condition:
            std_print(*args)


debug = Debugger()
