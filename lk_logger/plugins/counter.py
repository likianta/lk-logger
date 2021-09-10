from collections import defaultdict
from contextlib import contextmanager


class Counter:
    
    def __init__(self, auto_reset_count=False):
        self._auto_reset_count = auto_reset_count
        self._count_id = 0
        self._count_mgr = defaultdict(int)
        self._total_count_mgr = defaultdict(int)
    
    def init_count(self):
        self._count_mgr[self._count_id] = 0
        self._total_count_mgr[self._count_id] = 0
    
    reset_count = init_count
    
    @property
    def count(self):  # current count
        return self._count_mgr[self._count_id]
    
    @property
    def total_count(self):  # current total count
        return self._total_count_mgr[self._count_id]
    
    @staticmethod
    def _measure_obj_length(obj):
        if obj:
            if isinstance(obj, int):
                return obj
            else:
                try:
                    return len(obj)
                except AttributeError:
                    raise AttributeError(
                        'Cannot measure an object that doesnot have `__len__` '
                        'attribute', obj
                    )
        else:
            return 0
    
    @contextmanager
    def counting(self, x=None):
        try:
            self._count_id += 1
            self._total_count_mgr[self._count_id] = self._measure_obj_length(x)
            yield self
        finally:
            self.reset_count()
            self._count_id -= 1
    
    @property
    def status(self):
        if self.total_count == 0:
            return 'stable'
        elif self.total_count > self.count:
            return 'stable'
        elif self.total_count == self.count:
            return 'finished'
        else:
            return 'overwhelm'
    
    def _update_count(self):
        if self._auto_reset_count \
                and self.total_count \
                and self.count >= self.total_count:
            # note: donot use `self.reset_count()` or `self.init_count()`, they
            # will reset total count manager, too. here we just reset only
            # current count, not total count.
            self._count_mgr[self._count_id] = 0
        self._count_mgr[self._count_id] += 1
        return self.count, self.total_count
    
    def _fmt_update_count(self, template='[{i}/{j}]', backup_template='[{i}]'):
        """
        Args:
            template:
                optional keys:
                    key     example     note
                    i       12
                    I       012      <- j=100
                            001,112  <- j=0
                    I1, I2, I3, ...
                            0012     <- I4
                    j       100
                    p       1.00%    <- i=1, j=100
                    p.0, p.1, p.2, ...
                            1.0000%  <- p.4
                    P       01.00%   <- i=1, j=100
                    P.0, P.1, P.2, ...
                            01.000%  <- P.3
            backup_template:
                if total count is zero, will use this.
        
        References:
            https://www.runoob.com/python/att-string-format.html
        """
        from .formatter import fmt_count
        return fmt_count(*self._update_count(),
                         template=template, backup_template=backup_template)
