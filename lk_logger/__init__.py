from . import console
from . import printer
from .control import disable
from .control import enable
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
from .progress import spinner
from .progress import track
from .screenshot import save_error_to_image


def _init() -> None:
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
__version__ = '6.0.0'
