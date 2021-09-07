from ..logger import BaseLogger
from ..sourcemap import getframe


class PycharmLogger(BaseLogger):
    
    @getframe
    def log(self, *data, h='self'):
        self.output(self.format(
            data, advanced=False
        ))
    
    @getframe
    def loga(self, *data, h='self'):
        self.output(self.format(
            data, advanced=True
        ))
    
    @getframe
    def logd(self, *data, symbol='-', length=80, h='self'):
        self.output(self.format(
            data, advanced=True, divider_line=symbol * length
        ))
    
    @getframe
    def logp(self, *data, recursive_depth=10, h='self'):
        from pprint import pformat
        from textwrap import indent
        
        temp = []
        for i, (v, d) in enumerate(zip(self._get_varnames(), data)):
            temp.append(f'[{i}] {v or "_"}:')
            temp.append(indent(pformat(d), '    '))
        
        self.output(self.format(
            temp, advanced=False, sep='\n',
            start_from_newline=True
        ))
    
    @getframe
    def logt(self, tag, *data, h='self'):
        self.output(self.format(
            data, advanced=True, tag=tag
        ))
    
    @getframe
    def logx(self, *data, h='self'):
        self.output(self.format(
            data, advanced=False, count=self._fmt_update_count()
        ))
    
    @getframe
    def logax(self, *data, h='self'):
        self.output(self.format(
            data, advanced=True, count=self._fmt_update_count()
        ))
    
    @getframe
    def logdx(self, *data, symbol='-', length=80, h='self'):
        self.output(self.format(
            data, advanced=True, divider_line=symbol * length,
            count=self._fmt_update_count()
        ))
    
    @getframe
    def logtx(self, tag, *data, h='self'):
        self.output(self.format(
            data, advanced=True, tag=tag, count=self._fmt_update_count()
        ))
    
    @getframe
    def logdtx(self, tag, *data, symbol='-', length=80, h='self'):
        self.output(self.format(
            data, advanced=True, divider_line=symbol * length, tag=tag,
            count=self._fmt_update_count()
        ))
    
    def output(self, msg: str, **kwargs):
        print(msg)


lk = PycharmLogger()
