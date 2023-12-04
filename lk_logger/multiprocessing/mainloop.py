import multiprocessing as mp

from .._print import debug
from ..logger import Logger
from ..logger import logger

IS_MAIN_PROCESS = (mp.current_process().name == 'MainProcess')
queue = mp.Queue()


def start() -> mp.Process:
    """
    this function should only be called in main process and only be once.
    """
    assert IS_MAIN_PROCESS
    debug('starting mainloop')
    proc = mp.Process(target=_mainloop, args=(logger, queue), daemon=True)
    proc.start()
    return proc


def _mainloop(main_logger: Logger, queue: mp.Queue) -> None:
    while True:
        frame_info, args, kwargs = queue.get()
        main_logger.log(
            *(args or ()),
            _frame_info=frame_info,
            **(kwargs or {})
        )
