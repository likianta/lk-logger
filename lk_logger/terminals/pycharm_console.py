from ..logger import BaseLogger
from ..sourcemap import getframe


class PycharmLogger(BaseLogger):
    
    @getframe
    def log(self, *data, h='self'):
        self._output(
            self.fmt_msg(data)
        )
    
    @getframe
    def loga(self, *data, h='self'):
        self._output(
            self.fmt_msg(data, advanced=True)
        )
    
    @getframe
    def logd(self, *data, h='self'):
        pass
    
    @getframe
    def logt(self, *data, h='self'):
        pass
    
    @getframe
    def logx(self, *data, h='self'):
        pass
    
    @getframe
    def logax(self, *data, h='self'):
        self._output(
            self.fmt_msg(
                data, advanced=True, count=self._fmt_update_count()
            )
        )
    
    @getframe
    def logdx(self, *data, h='self'):
        pass

    @getframe
    def logtx(self, *data, h='self'):
        pass

    @getframe
    def logdtx(self, *data, h='self'):
        pass
    
    def _output(self, msg: str, **kwargs):
        print(msg)


lk = PycharmLogger()
