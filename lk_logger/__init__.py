"""
minimum usage: just import
    import lk_logger  # noqa
that's all.
"""
from . import console
from ._print import bprint
from .control import disable
from .control import enable
from .control import setup
from .control import start_ipython
from .control import unload
from .control import update
from .logger import lk


def __init():
    import traceback
    from .pipeline import pipeline
    pipeline.add(traceback, bprint)
    setup(quiet=True)


__init()
__version__ = '5.4.0'
