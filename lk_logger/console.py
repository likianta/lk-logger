import traceback
from functools import partial
from functools import wraps

from rich.console import Console as BaseConsole

__all__ = ['con_print', 'con_error', 'console']


class Console(BaseConsole):
    
    def __init__(self):
        super().__init__()
        if self._color_system is None:
            self._color_system = 'standard'
        # TODO (width):
        #   if width longer than default, use single line style; otherwise
        #   split sourcemap and message into different lines.
        pass


console = Console()
con_print = partial(console.print, soft_wrap=True)
con_error = partial(console.print_exception, show_locals=True)


def temporarily_reset_lk_logger(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        import lk_logger
        
        if lk_logger.global_control.STATUS == 'enabled':
            before = lk_logger.unload
            after = lk_logger.enable
        elif lk_logger.global_control.STATUS == 'disabled':
            before = lk_logger.unload
            after = lk_logger.disable
        else:
            before = lambda: None
            after = lambda: None
        
        before()
        out = func(*args, **kwargs)
        after()
        
        return out
    
    return wrapper


setattr(traceback, 'print_exception',
        temporarily_reset_lk_logger(traceback.print_exception))

setattr(traceback, 'print_exc',
        temporarily_reset_lk_logger(traceback.print_exc))
