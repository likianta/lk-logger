from . import console
from ._print import bprint
from .control import disable
from .control import disable as mute
from .control import enable
from .control import enable as unmute
from .control import setup
from .control import start_ipython
from .control import unload
from .control import unload as restore_builtin_print
from .control import update
from .logger import lk
from .pipeline import pipeline


def __init():
    import traceback
    pipeline.add(traceback, bprint)
    setup(quiet=True)


__init()
__version__ = '5.4.9'
