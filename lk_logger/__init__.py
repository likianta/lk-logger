from . import console
from . import printer
from .control import counting
from .control import delay
from .control import disable
from .control import elevate_caller_stack
from .control import enable
from .control import input
from .control import mute
from .control import reload
from .control import setup
from .control import start_ipython
from .control import timing
from .control import unload
from .control import unload as restore_builtin_print
from .control import update
from .frame_info import FrameInfo
from .logger import logger
from .pipeline import pipeline
from .printer import bprint
from .printer import parallel_printing
from .progress import spinner
from .progress import track
from .screenshot import save_error


def _init() -> None:
    import traceback
    pipeline.add(traceback, bprint)
    
    setup(quiet=True)
    
    try:
        __IPYTHON__  # noqa
    except NameError:
        pass
    else:
        import IPython  # noqa
        pipeline.add(IPython, bprint, scope=True)
        # pipeline.add('[ipython]', bprint)


_init()
__version__ = '6.0.2'
