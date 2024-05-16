import os as _os

from . import console
from . import printer
from .control import disable
from .control import disable as mute
from .control import enable
from .control import enable as unmute
from .control import setup
from .control import start_ipython
from .control import unload
from .control import unload as restore_builtin_print
from .control import update
from .frame_info import FrameInfo
from .logger import logger
from . import multiprocessing as _mp
from .pipeline import pipeline
from .printer import bprint
from .printer import parallel_printing

if _os.getenv('LK_LOGGER_STANDALONE', '1') == '1':
    from .multiprocessing import logger
    from .multiprocessing.delegate_control import mute
    from .multiprocessing.delegate_control import reload
    from .multiprocessing.delegate_control import setup
    from .multiprocessing.delegate_control import start_ipython
    from .multiprocessing.delegate_control import unload
    from .multiprocessing.delegate_control import unmute
    from .multiprocessing.delegate_control import update
    # from ._print import debug
    # debug(_mp.IS_MAIN_PROCESS)
    if _mp.IS_MAIN_PROCESS:
        _mp.start_mainloop()
        setup(quiet=True)
    else:
        mute()
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
    try:
        __IPYTHON__  # noqa
    except NameError:
        pass
    else:
        import IPython
        pipeline.add(IPython, bprint, scope=True)
    
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
