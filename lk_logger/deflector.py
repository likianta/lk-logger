import typing as t
from collections import namedtuple
from os.path import abspath
from os.path import dirname

from .printer import dbg_print  # noqa
from .printer import non_print
from .printer import std_print


class T:
    PrintFunc = t.Optional[t.Callable]
    PathToFunc = t.Dict[str, PrintFunc]
    SearchRoots = t.NamedTuple('SearchRoots', (
        ('abspath', t.Dict[str, PrintFunc]),
        ('libname', t.Dict[str, PrintFunc]),
    ))


# TODO: `libname` is not used.
SearchRoots = namedtuple('SearchRoots', 'abspath libname')


class Deflector:
    _cached_paths: T.PathToFunc
    _search_roots: T.SearchRoots
    
    def __init__(self) -> None:
        self._cached_paths = {}
        self._search_roots = SearchRoots({}, {})
        
    def add(
        self,
        source: t.Union[str, object],
        print_func: t.Optional[t.Callable] = std_print,
        scope: bool = False,
    ) -> None:
        if isinstance(source, str):
            if source.startswith('['):
                path = source
            else:
                path = _normpath(source)
        else:
            path = _normpath(source.__file__)
            if scope:
                path = dirname(path)
                
        if print_func is None:
            print_func = non_print
        
        if path.startswith('['):
            self._search_roots.libname[path] = print_func
        else:
            self._search_roots.abspath[path] = print_func
        self._cached_paths[path] = print_func
        
    def check_lib(self, libname: str) -> T.PrintFunc:
        return self._search_roots.libname.get(libname)
    
    def check_path(self, path: str) -> T.PrintFunc:
        """
        return proper print function for the given path.
        """
        # exclusive for ipython.
        if path.startswith('<ipython-input'):
            return std_print
        # the path is an absolute path.
        path = _normpath(path)
        # dbg_print(path)
        if path in self._cached_paths:
            # dbg_print('path in cache', path, self._cache[path])
            return self._cached_paths[path]
        for root, prt in self._search_roots.abspath.items():
            if path.startswith(root):
                self._cached_paths[path] = prt
                # dbg_print('use custom print', path)
                return prt
        self._cached_paths[path] = None
        return None
    
    def mute(self, source: t.Union[str, object]) -> None:
        self.add(source, print_func=non_print, scope=True)


def _normpath(path: str) -> str:
    path = abspath(path)
    return path.replace('\\', '/')


deflector = Deflector()
