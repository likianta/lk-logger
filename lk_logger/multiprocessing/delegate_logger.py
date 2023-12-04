import typing as t
from inspect import currentframe

from .mainloop import queue
from .._print import debug  # noqa
from ..frame_info import freeze_frame_info, FrameInfo


class DelegateLogger:
    @staticmethod
    def log(
        *args: t.Any,
        **kwargs
    ) -> None:
        # debug(args, kwargs)
        queue.put((
            freeze_frame_info(frame=currentframe().f_back),
            # FrameInfo(frame=currentframe().f_back),
            args or None,
            kwargs or None,
        ))


logger = DelegateLogger()
