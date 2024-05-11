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


# def __init() -> None:
#     import traceback
#     pipeline.add(traceback, bprint)
#     setup(quiet=True)
#
#
# __init()
__version__ = '5.7.0'
