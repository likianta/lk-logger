# import multiprocessing as mp
# import sys
# from queue import Empty

import multiprocess as mp

from .._print import debug  # noqa
from ..logger import Logger
from ..logger import logger

# noinspection PyUnresolvedReferences
IS_MAIN_PROCESS = (mp.current_process().name == 'MainProcess')
# noinspection PyUnresolvedReferences
queue = mp.Queue()


# noinspection PyUnresolvedReferences
def start() -> mp.Process:
    """
    this function should only be called in main process and only be once.
    """
    assert IS_MAIN_PROCESS
    # old, new = sys.argv.copy(), [sys.executable, '-m', 'lk_logger']
    # sys.argv = new
    proc = mp.Process(target=_mainloop, args=(logger, queue), daemon=True)
    proc.start()
    # sys.argv = old
    return proc


# noinspection PyUnresolvedReferences
def _mainloop(main_logger: Logger, queue: mp.Queue) -> None:
    debug('starting main loop')
    while True:
        frame_info, args, kwargs = queue.get()
        # debug(frame_info, args, kwargs)
        main_logger.log(
            *(args or ()),
            _frame_info=frame_info,
            **(kwargs or {})
        )
        # try:
        #     data = queue.get(timeout=100e-3)
        # except Empty:
        #     continue
        # else:
        #     frame_info, args, kwargs = data
        #     # debug(frame_info, args, kwargs)
        #     main_logger.log(
        #         *(args or ()),
        #         _frame_info=frame_info,
        #         **(kwargs or {})
        #     )
