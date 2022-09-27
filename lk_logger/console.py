from functools import partial

from rich.console import Console as BaseConsole

__all__ = ['con_print', 'con_error', 'console']


class Console(BaseConsole):
    
    def __init__(self):
        super().__init__()
        if self._color_system is None:
            try:
                # in rich version >= 12.5, the color system is changed to be a
                # contant integer.
                from rich.console import ColorSystem
                self._color_system = ColorSystem.STANDARD
            except:
                # the older version is using a string.
                self._color_system = 'standard'
        
        # TODO (width):
        #   if width longer than default, use single line style; otherwise
        #   split sourcemap and message into different lines.
        pass


console = Console()
con_print = partial(console.print, soft_wrap=True)
con_error = partial(console.print_exception, show_locals=True)
