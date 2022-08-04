from __future__ import annotations

import os
import sys

from .general import normpath


class PathHelper:
    __project_root: str
    __external_libs: dict[str, str] | None
    
    def __init__(self):
        self.__project_root = self._find_project_root()
        self.__external_libs = None
    
    @property
    def external_libs(self) -> dict[str, str]:
        if self.__external_libs is None:
            self.__external_libs = self._indexing_external_libs()
        return self.__external_libs
    
    def is_external_lib(self, filepath: str) -> bool:
        return not filepath.startswith(self.__project_root)
    
    @staticmethod
    def _find_project_root() -> str:
        """ find personal-like project root.
    
        proposals:
            1. backtrack from current working dir to find a folder which has
               one of '.idea', '.git', etc. folders.
            2. iterate paths in sys.path, to find a folder which is parent of
               current working dir. (adopted)
               if there are more than one, choose which is shortest.
               if there is none, return current working dir.
        """
        cwd = normpath(os.getcwd())
        paths = tuple(
            x for x in map(normpath, map(os.path.abspath, sys.path))
            if cwd.startswith(x) and os.path.isdir(x)
        )
        if len(paths) == 0:
            return cwd
        elif len(paths) == 1:
            return paths[0]
        else:
            return min(paths, key=lambda x: len(x))
    
    @staticmethod
    def _indexing_external_libs() -> dict[str, str]:
        """
        return:
            dict[str path, str lib_name]
        """
        out = {}
        
        for path in reversed(sys.path):
            if not os.path.exists(path):
                continue
            for root, dirs, files in os.walk(path):
                root = normpath(root)
                out[root] = os.path.basename(root)
                
                for d in dirs:
                    if d.startswith(('.', '__')):
                        continue
                    if '-' in d or '.' in d:
                        continue
                    out[f'{root}/{d}'] = d
                
                # for f in files:
                #     name, ext = os.path.splitext(f)
                #     if ext not in ('.py', '.pyc', '.pyd', '.pyo', '.pyw'):
                #         continue
                #     if '-' in name or '.' in name:
                #         continue
                #     out[f'{root}/{f}'] = name
                break
        
        return out


path_helper = PathHelper()
