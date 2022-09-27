from __future__ import annotations

import posixpath
import typing as t

from ._print import bprint
from ._print import debug  # noqa


class T:
    PrintFunc = t.Optional[t.Callable]
    Pipelines = t.Dict[str, PrintFunc]


class Pipeline:
    _cache: T.Pipelines
    _lines: T.Pipelines
    
    def __init__(self):
        self._cache = {}
        self._lines = {}
    
    def add(self, x: t.Union[str, object], prt: t.Callable = bprint,
            scope=False) -> None:
        if isinstance(x, str):
            path = posixpath.abspath(x)
        else:
            # x is a package or a module
            # debug(x, x.__file__)
            path = posixpath.normpath(x.__file__)
            if scope:
                path = posixpath.dirname(path)
        # debug('add path to pipeline', path)
        self._lines[path] = prt
        self._cache[path] = prt
    
    def get(self, path: str) -> T.PrintFunc:
        # the path is an absolute path.
        path = posixpath.normpath(path)
        # debug(path)
        if path in self._cache:
            # debug('path in cache', path, self._cache[path])
            return self._cache[path]
        for root, prt in self._lines.items():
            if path.startswith(root):
                self._cache[path] = prt
                # debug('use custom print', path)
                return prt
        self._cache[path] = None
        return None


pipeline = Pipeline()
