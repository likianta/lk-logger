from __future__ import annotations

import typing as t
from os import name as _os_name
from os.path import abspath
from os.path import dirname

from ._print import bprint
from ._print import debug  # noqa


class T:
    PrintFunc = t.Optional[t.Callable]
    Cache = t.Dict[str, PrintFunc]
    PipeLines = t.NamedTuple('PipeLines2', (
        ('abspath', t.Dict[str, PrintFunc]),
        ('libname', t.Dict[str, PrintFunc]),  # TODO: not used
    ))
    ''' e.g.
        ('abspath': {'/Users/.../python/3.10/lib/python3.10/traceback.py':
                     <function ...>, ...},
         'libpath': {'[tornado]': <function bprint at 0x000001D1C1D1B8B0>, ...})
    '''


class Pipeline:
    _cache: T.Cache
    _lines: T.PipeLines
    
    def __init__(self):
        self._cache = {}
        self._lines = T.PipeLines({}, {})
    
    def dump_list(self) -> t.List[str]:
        return list(self._lines.abspath.keys())
    
    def add(self,
            x: t.Union[str, object],
            prt: t.Optional[t.Callable] = bprint,
            scope=False) -> None:
        if isinstance(x, str):
            if x.startswith('['):
                path = x
            else:
                path = _normpath(x)
        else:
            # x is a package or a module
            # debug(x, x.__file__)
            path = _normpath(x.__file__)
            if scope:
                path = dirname(path)
        # debug('add path to pipeline', path)
        if prt is None:
            prt = _mute_print
        if path.startswith('['):
            self._lines.libname[path] = prt
        else:
            self._lines.abspath[path] = prt
        self._cache[path] = prt
    
    def get(self, path: str) -> T.PrintFunc:
        """
        get proper print function for the given path.
        """
        # the path is an absolute path.
        path = _normpath(path)
        # debug(path)
        if path in self._cache:
            # debug('path in cache', path, self._cache[path])
            return self._cache[path]
        for root, prt in self._lines.abspath.items():
            if path.startswith(root):
                self._cache[path] = prt
                # debug('use custom print', path)
                return prt
        self._cache[path] = None
        return None


class _MutePrint:
    def __call__(self, *_, **__):
        pass


_mute_print = _MutePrint()

_is_win = _os_name == 'nt'


def _normpath(path: str) -> str:
    path = abspath(path)
    if _is_win:
        path = path.replace('\\', '/')
    return path


pipeline = Pipeline()
