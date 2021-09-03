from textwrap import indent

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
        
        # TODO: assign the most frequently used configs to directly acessable
        #   attributes.
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
            count
            divider_line
            indent: int[4]
            start_from_newline: bool[False]
            tag
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
            msg_body = kwargs.get('sep', ';\t').join(temp)
        else:
            msg_body = kwargs.get('sep', ';\t').join(map(str, data))
        if self._visualize_linebreaks:
            msg_body = msg_body.replace('\n', '\\n')
        if kwargs.get('start_from_newline', False):
            msg_body = indent('\n' + msg_body, ' ' * kwargs.get('indent', 4))
        
        out = self._template.format(
            filename=info.filename,
            lineno=info.lineno,
            func=info.name,
            msg=f'{msg_head} {msg_body}'.strip(' ')
        )
        return out

    # -------------------------------------------------------------------------
    # Typical implementations see: `lk_logger.terminals.pycharm_console`.
    
    @getframe
    def log(self, *data, h='self'):
        raise NotImplementedError
    
    @getframe
    def loga(self, *data, h='self'):
        raise NotImplementedError
    
    @getframe
    def logd(self, *data, symbol='-', length=80, h='self'):
        raise NotImplementedError
    
    @getframe
    def logp(self, *data, h='self'):
        raise NotImplementedError
    
    @getframe
    def logt(self, tag, *data, h='self'):
        raise NotImplementedError
    
    @getframe
    def logx(self, *data, h='self'):
        raise NotImplementedError
    
    @getframe
    def logtx(self, tag, *data, h='self'):
        raise NotImplementedError
    
    @getframe
    def logax(self, *data, h='self'):
        raise NotImplementedError
    
    @getframe
    def logdx(self, *data, symbol='-', length=80, h='self'):
        raise NotImplementedError
    
    @getframe
    def logtx(self, *data, h='self'):
        raise NotImplementedError
    
    @getframe
    def logdtx(self, tag, *data, symbol='-', length=80, h='self'):
        raise NotImplementedError
    
    def _output(self, msg: str, **kwargs):
        raise NotImplementedError

    # -------------------------------------------------------------------------
    
    @property
    @getframe
    def position(self):
        """
        
        Returns:
            (filename, lineno)
                - filename is an absolute path.
                - the lineno starts from 1.
        """
        from .sourcemap import frame_finder
        frame = frame_finder.frame
        return frame.f_code.co_filename, frame.f_lineno
