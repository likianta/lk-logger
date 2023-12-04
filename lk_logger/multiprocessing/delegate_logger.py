import typing as t
from inspect import currentframe

from .mainloop import queue
from ..frame_info import freeze_frame_info


class DelegateLogger:
    @staticmethod
    def log(
        *args: t.Any,
        **kwargs
    ) -> None:
        queue.put((
            freeze_frame_info(frame=currentframe().f_back),
            args or None,
            kwargs or None,
        ))


logger = DelegateLogger()
