import os
import sys
import typing as t
from functools import cached_property
from os.path import abspath
from os.path import basename

from .printer import dbg_print  # noqa


def normpath(path: str) -> str:
    return abspath(path).replace('\\', '/').rstrip('/')


class PathHelper:
    _cwd: str
    _cwdp: str
    
    @cached_property
    def _external_libs(self) -> t.Dict[str, str]:  # {libpath: libname, ...}
        """
        suggest deferring this method til the first print is called.
        """
        out = {}
        for d in set(map(normpath, sys.path)):
            if os.path.exists(d):
                out[d] = basename(d)
        return out
    
    @cached_property
    def _external_libkeys(self) -> t.Tuple[str, ...]:
        # dbg_print(sorted(self._external_libs.keys(), reverse=True))
        return tuple(
            sorted(self._external_libs.keys(), reverse=True)
        )
    
    def __init__(self) -> None:
        self._cwd = normpath(os.getcwd())
        self._cwdp = self._cwd.rsplit('/', 1)[0]
    
    def _check_path_type(self, xpath: str) -> int:
        """
        returns:
            0: path inside cwd
            1: path inside cwd parent
            2: external path
            3: unknown path
        """
        if xpath.startswith(self._cwd):
            return 0
        elif xpath.startswith(self._cwdp):
            return 1
        elif xpath.startswith('<'):
            assert xpath.endswith('>')
            return 3
        else:
            return 2
    
    def is_external_path(self, path: str) -> bool:
        return self._check_path_type(path) >= 2
    
    def get_relpath(self, path: str) -> str:
        path_type = self._check_path_type(path)
        if path_type == 0:
            return './{}'.format(path[len(self._cwd) + 1:])
        elif path_type == 1:
            return '../{}'.format(path[len(self._cwdp) + 1:])
        elif path_type == 2:
            for libpath in self._external_libkeys:
                if path.startswith(libpath):
                    relpath = path[len(libpath) + 1:]
                    # dbg_print(libpath, path, relpath)
                    if '/' in relpath:
                        return '[{}]/{}'.format(*relpath.split('/', 1))
                    else:
                        return '[{}]/{}'.format(
                            libpath.rsplit('/', 1)[-1], relpath
                        )
            a, b, c = path.rsplit('/', 2)
            return '[unknown]/{}/{}'.format(b, c)
        else:
            return '[unknown {}]'.format(path)
    
    def get_filename(self, xpath: str) -> str:
        path_type = self._check_path_type(xpath)
        if path_type == 0 or path_type == 1:
            return basename(xpath)
        elif path_type == 2:
            for libpath in self._external_libkeys:
                if xpath.startswith(libpath):
                    return '[{}]/{}'.format(
                        self._external_libs[libpath],
                        basename(xpath)
                    )
            return '[unknown]/{}'.format(basename(xpath))
        else:
            return '[unknown {}]'.format(xpath)


path_helper = PathHelper()
