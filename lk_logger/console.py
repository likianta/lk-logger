from typing import Any

from rich.console import Console as BaseConsole


class Console(BaseConsole):
    
    def __init__(self) -> None:
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
    
    def print(
        self,
        *objects: Any,
        crop: bool = False,
        soft_wrap: bool = True,
        **kwargs
    ) -> None:
        from .message_builder import MessageStruct
        # pop incompatible arguments
        kwargs.pop('file', None)
        kwargs.pop('flush', None)
        if len(objects) == 1 and isinstance(objects[0], MessageStruct):
            super().print(
                objects[0].text, crop=crop, soft_wrap=soft_wrap, **kwargs
            )
        else:
            super().print(
                *objects, crop=crop, soft_wrap=soft_wrap, **kwargs
            )


console = Console()
