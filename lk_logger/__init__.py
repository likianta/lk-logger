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
from .pipeline import pipeline
from .printer import bprint
from .printer import parallel_printing


def _init() -> None:
    import os
    os.environ['ARGSENSE_TRACEBACK'] = '0'  # see argsense v0.5.8+
    
    import traceback
    pipeline.add(traceback, bprint)
    
    setup(quiet=True)
    
    def has_ipython() -> bool:
        try:
            __IPYTHON__  # noqa
            return True
        except NameError:
            pass
        try:
            import IPython  # noqa
            return True
        except ImportError:
            return False
    
    if has_ipython():
        import IPython
        pipeline.add(IPython, bprint, scope=True)
        # pipeline.add('[ipython]', bprint)


_init()
__version__ = '5.7.7'
