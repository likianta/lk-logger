import os as _os

from . import console
from . import multiprocessing as _mp
from ._print import bprint
from .frame_info import FrameInfo
from .pipeline import pipeline

if _os.getenv('LK_LOGGER_MULTIPROCESSING', '1') == '1':
    from .multiprocessing import logger
    from .multiprocessing.delegate_control import mute
    from .multiprocessing.delegate_control import reload
    from .multiprocessing.delegate_control import setup
    from .multiprocessing.delegate_control import start_ipython
    from .multiprocessing.delegate_control import unload
    from .multiprocessing.delegate_control import unmute
    from .multiprocessing.delegate_control import update
    if _mp.IS_MAIN_PROCESS:
        _mp.start_mainloop()
        setup(quiet=True)
else:
    import traceback as _traceback
    from .control import mute
    from .control import reload
    from .control import setup
    from .control import start_ipython
    from .control import unload
    from .control import unmute
    from .control import update
    from .logger import logger
    pipeline.add(_traceback, bprint)
    setup(quiet=True)

__all__ = [
    'FrameInfo',
    'bprint',
    'console',
    'logger',
    'mute',
    'pipeline',
    'reload',
    'setup',
    'start_ipython',
    'unload',
    'unmute',
    'update',
]

__version__ = '6.0.0'
