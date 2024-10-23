from . import console
from . import printer
from .control import disable
from .control import enable
from .control import setup
from .control import start_ipython
from .control import unload
from .control import unload as restore_builtin_print
from .control import update
from .control2 import counting
from .control2 import delay
from .control2 import elevate_caller_stack
from .control2 import input
from .control2 import mute
from .control2 import timing
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
__version__ = '6.0.0'
