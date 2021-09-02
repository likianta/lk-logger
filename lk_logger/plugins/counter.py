import re
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
                        'Cannot measure an object that doesnot have __len__ '
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
        
        data = {}
        i, j = self._update_count()
        p = i / j if j else ''
        template = template if j else backup_template
        
        def _parse_template() -> set[str]:
            slot = re.compile(r'(?<={)[^}]+')
            return set(slot.findall(template))
        
        for x in _parse_template():
            if x == 'i':
                data[x] = i
            elif x == 'I':
                if j:
                    data[x] = '{{:0>{}}}'.format(len(str(j))).format(i)
                else:
                    dynamic_width = 3
                    i_width = len(str(i))
                    while dynamic_width < i_width:
                        dynamic_width += 3
                    data[x] = '0' * (dynamic_width - i_width) + ':,'.format(i)
            elif x.startswith('I'):
                data[x] = '{{:0>{}}}'.format(int(x[1:])).format(i)
            elif x == 'j' and j:
                data[x] = j
            elif x == 'p' and p:
                data[x] = '{:.2%}'.format(p)
            elif x.startswith('p.') and p:
                if x == 'p.0':
                    data[x] = '{}%'.format(round(p))
                else:
                    data[x] = '{{:.{}%}}'.format(int(x[2:])).format(p)
            elif x == 'P' and p:
                if p < 10:
                    data[x] = '0' + '{:.2%}'.format(p)
                else:
                    data[x] = '{:.2%}'.format(p)
            elif x.startswith('P.') and p:
                if p < 10:
                    data[x] = '0' + '{{:.{}%}}'.format(int(x[2:])).format(p)
                else:
                    data[x] = '{{:.{}%}}'.format(int(x[2:])).format(p)
            else:
                data[x] = ''
                # raise ValueError(x, template)
        
        return template.format(**data)
