from ..logger import BaseLogger
from ..sourcemap import getframe


class PycharmLogger(BaseLogger):
    
    @getframe
    def log(self, *data, h='self'):
        self._output(self.fmt_msg(
            data, advanced=False
        ))
    
    @getframe
    def loga(self, *data, h='self'):
        self._output(self.fmt_msg(
            data, advanced=True
        ))
    
    @getframe
    def logd(self, *data, symbol='-', length=80, h='self'):
        self._output(self.fmt_msg(
            data, advanced=True, divider_line=symbol * length
        ))
    
    @getframe
    def logp(self, *data, recursive_depth=10, indent=2, h='self'):
        
        def rec(node, depth):
            if depth > recursive_depth:
                yield f'- {node}', depth
                return
            
            if isinstance(node, dict):
                for k, v in node.items():
                    if isinstance(v, (dict, list, set, tuple)):
                        yield f'- {k}:', depth
                        yield from rec(v, depth + 1)
                    else:
                        yield f'- {k}: {v}', depth
            elif isinstance(node, (list, set, tuple)):
                for i in node:
                    yield from rec(i, depth + 1)
            else:
                yield f'- {node}', depth
        
        new_data = ['Expand data']
        for i, depth in rec(data, 0):
            new_data.append(' ' * depth * indent + str(i))
        
        self._output(self.fmt_msg(
            new_data, advanced=False, sep='\n'
        ))
    
    @getframe
    def logt(self, tag, *data, h='self'):
        self._output(self.fmt_msg(
            data, advanced=True, tag=tag
        ))
    
    @getframe
    def logx(self, *data, h='self'):
        self._output(self.fmt_msg(
            data, advanced=False, count=self._fmt_update_count()
        ))
    
    @getframe
    def logax(self, *data, h='self'):
        self._output(self.fmt_msg(
            data, advanced=True, count=self._fmt_update_count()
        ))
    
    @getframe
    def logdx(self, *data, symbol='-', length=80, h='self'):
        self._output(self.fmt_msg(
            data, advanced=True, divider_line=symbol * length,
            count=self._fmt_update_count()
        ))
    
    @getframe
    def logtx(self, tag, *data, h='self'):
        self._output(self.fmt_msg(
            data, advanced=True, tag=tag, count=self._fmt_update_count()
        ))
    
    @getframe
    def logdtx(self, tag, *data, symbol='-', length=80, h='self'):
        self._output(self.fmt_msg(
            data, advanced=True, divider_line=symbol * length, tag=tag,
            count=self._fmt_update_count()
        ))
    
    def _output(self, msg: str, **kwargs):
        print(msg)


lk = PycharmLogger()
