from functools import partial
from typing import Any

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
    
    def print(self, *objects: Any, sep=" ", end="\n", style=None, justify=None,
              overflow=None, no_wrap=None, emoji=None, markup=None,
              highlight=None, width=None, height=None, crop=True,
              soft_wrap=False, new_line_start=False, **_) -> None:
        super().print(*objects, sep=sep, end=end, style=style, justify=justify,
                      overflow=overflow, no_wrap=no_wrap, emoji=emoji,
                      markup=markup, highlight=highlight, width=width,
                      height=height, crop=crop, soft_wrap=soft_wrap,
                      new_line_start=new_line_start)


console = Console()
con_print = partial(console.print, soft_wrap=True)
con_error = console.print_exception
