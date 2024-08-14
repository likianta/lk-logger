import os
import sys
import typing as t
from os.path import abspath, basename
from .printer import dprint


def normpath(path: str) -> str:
    return abspath(path).replace('\\', '/').rstrip('/')


class PathHelper:
    _cwd: str
    _cwdp: str
    _external_libs: t.Dict[str, str]  # {libpath: libname, ...}
    _external_libkeys: t.Tuple[str, ...]
    
    def __init__(self) -> None:
        self._cwd = normpath(os.getcwd())
        self._cwdp = self._cwd.rsplit('/', 1)[0]
    
    def _index_external_libpaths(self) -> None:
        """
        suggest deferring this method til the first print is called.
        """
        self._external_libs = {}
        for d in set(map(normpath, sys.path)):
            self._external_libs[d] = basename(d)
        self._external_libkeys = tuple(
            sorted(self._external_libs.keys(), reverse=True)
        )
    
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
    
    def is_external_path(self, xpath: str) -> bool:
        return self._check_path_type(xpath) >= 2
    
    def get_relpath(self, xpath: str) -> str:
        path_type = self._check_path_type(xpath)
        if path_type == 0:
            return './{}'.format(xpath[len(self._cwd) + 1:])
        elif path_type == 1:
            return '../{}'.format(xpath[len(self._cwdp) + 1:])
        elif path_type == 2:
            if not hasattr(self, '_external_libs'):
                self._index_external_libpaths()
            for libpath in self._external_libkeys:
                if xpath.startswith(libpath):
                    return '[{}]/{}'.format(
                        self._external_libs[libpath],
                        xpath[len(libpath) + 1:]
                    )
            a, b, c = xpath.rsplit('/', 2)
            return '[unknown]/{}/{}'.format(b, c)
        else:
            return '[unknown {}]'.format(xpath)
    
    def get_filename(self, xpath: str) -> str:
        path_type = self._check_path_type(xpath)
        if path_type == 0 or path_type == 1:
            return basename(xpath)
        elif path_type == 2:
            if not hasattr(self, '_external_libs'):
                self._index_external_libpaths()
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
