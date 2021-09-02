from .plugins import Counter
from .sourcemap import getframe
from .sourcemap import sourcemap


class BaseLogger(Counter):
    
    def __init__(self, **kwargs):
        super().__init__(auto_reset_count=kwargs.get('auto_reset_count', True))
        
        # TODO
        # from json import load
        # config = load(open(f'{__file__}/../config/base.json'))  # type: dict
        # config.update(kwargs)
        self.config = kwargs
        
        # uplevel most frequent used configurations
        self._template = self.config.get(
            'template', '{filename}:{lineno}\t>>\t{func}\t>>\t{msg}')
        self._var_seg = self.config.get('var_seg', ';\t')
        self._visualize_linebreaks = self.config.get(  # DEL
            'visualize_linebreaks', False)
        
        self.__fmt_msg = None
    
    def enable_lite_mode(self):
        self.__fmt_msg = self.fmt_msg
        # tip: here we use `setattr(...)` not `self.fmt_msg = ...` to avoid
        # PEP-8 (weak) warnings and fix code navigation problem (and some
        # intelli-sense problems) when developing in pycharm.
        setattr(self, 'fmt_msg', lambda data, **_: ';\t'.join(map(str, data)))
        # # self.fmt_msg = lambda data, **_: ';\t'.join(map(str, data))
    
    def disable_lite_mode(self):
        setattr(self, 'fmt_msg', self.__fmt_msg)
        # # self.fmt_msg = self.__fmt_msg
        self.__fmt_msg = None
    
    def fmt_msg(self, data, **kwargs):
        """
        
        Args:
            data:
            **kwargs:
        
        Keyword Args:
            advanced
            tag
            count
            divider_line
        """
        info = sourcemap.get_frame_info(
            advanced=kwargs.get('advanced', False)
        )
        
        # message head
        msg_head = ' '.join(filter(None, (
            kwargs.get('tag'),
            kwargs.get('count'),
            kwargs.get('divider_line'),
        ))).strip()
        
        # message body
        if info.varnames:
            assert len(info.varnames) == len(data), (info, data)
            temp = []
            for k, v in zip(info.varnames, data):
                temp.append(f'{k} = {v}' if k else str(v))
            msg_body = ';\t'.join(temp)
        else:
            msg_body = ';\t'.join(map(str, data))
        if self._visualize_linebreaks:
            msg_body = msg_body.replace('\n', '\\n')
        
        out = self._template.format(
            filename=info.filename,
            lineno=info.lineno,
            func=info.name,
            msg=f'{msg_head} {msg_body}'.strip()
        )
        return out

    # -------------------------------------------------------------------------
    
    @getframe
    def log(self, *data, h='self'):
        # msg = self.fmt_msg(data)
        # ...
        raise NotImplementedError
    
    @getframe
    def loga(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
    
    @getframe
    def logd(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
    
    @getframe
    def logt(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
    
    @getframe
    def logx(self, *data, h='self'):
        # msg = self.fmt_msg(data)
        # ...
        raise NotImplementedError
    
    @getframe
    def logtx(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
    
    @getframe
    def logax(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
    
    @getframe
    def logdx(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
    
    @getframe
    def logtx(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
    
    @getframe
    def logdtx(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
    
    def _output(self, msg: str, **kwargs):
        raise NotImplementedError
