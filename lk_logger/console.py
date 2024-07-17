import os
from typing import Any

from rich.console import Console as BaseConsole


class Console(BaseConsole):
    
    def __init__(self) -> None:
        # https://github.com/Textualize/rich/issues/2622
        super().__init__(
            color_system='standard' if os.name == 'nt' else 'auto',
            # force_terminal=True,
            legacy_windows=False if os.name == 'nt' else None,
        )
        
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
