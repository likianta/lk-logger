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


def __init() -> None:
    # import traceback
    # pipeline.add(traceback, bprint)
    # setup(quiet=True)
    
    # from .printer import dprint
    # dprint(f'{__IPYTHON__=}')
    try:
        __IPYTHON__  # noqa
    except NameError:
        pass
    else:
        import IPython
        pipeline.add(IPython, bprint, scope=True)
        # pipeline.add('[ipython]', bprint)


__init()
__version__ = '5.7.2'
