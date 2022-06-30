from rich.console import Console as BaseConsole

__all__ = ['con_print', 'con_error']


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
con_print = console.print
con_error = console.print_exception
