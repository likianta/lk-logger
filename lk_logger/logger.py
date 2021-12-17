from inspect import currentframe
from os import getcwd
from textwrap import indent

from .plugins import Counter
from .sourcemap import getframe
from .sourcemap import sourcemap


class BaseLogger(Counter):
    
    def __init__(self, **kwargs):
        super().__init__(auto_reset_count=kwargs.get('auto_reset_count', True))
        
        self.config = kwargs
        self._working_dir = getcwd()
        
        # TODO: assign the most frequently used configs to directly acessable
        #   attributes.
        self._template = self.config.get(
            'template', '{filename}:{lineno}\t>>\t{func}\t>>\t{msg}')
        self._var_seg = self.config.get('var_seg', ';\t')
        self._visualize_linebreaks = self.config.get(  # DEL
            'visualize_linebreaks', False)
        
        self.mode = 'full_mode'
        self.__mode = {
            'disabled' : (
                lambda *_, **__: None,
                lambda *_, **__: None,
            ),
            'lite_mode': (
                lambda data, **__: ';\t'.join(map(str, data)),
                lambda data, **__: print(data)
            ),
            'full_mode': (
                self.format,
                self.output,
            ),
        }
        
        # PERF: more controls
        self._print_scope = 0
        #   0: print all
        #   1: full print in self._working_dir, simple print in external modules.
        #   2: print only in self._working_dir, no print in external modules.
    
    # -------------------------------------------------------------------------
    # master control
    
    def switch_mode(self, mode: str, quiet=False, _h=1):
        # mode: str['lite_mode', 'full_mode', 'disabled']
        if self.mode == mode:
            return
        else:
            self.mode = mode
            
            if not quiet:
                # reference: `.sourcemap.FrameFinder.getframe._wrap` and
                # `self.position`.
                frame = currentframe()
                for _ in range(_h): frame = frame.f_back
                filename, lineno = frame.f_code.co_filename, frame.f_lineno
                print(f'{filename}:{lineno}\t>>\t'
                      f'[lk_logger] mode switched: {mode}')
        
        a, b = self.__mode[self.mode]
        # tip: here we use `setattr(...)` not `self.format = ...` to avoid
        # PEP-8 (weak) warnings and fix code navigation problem (and some
        # intelli-sense problems) when developing in pycharm.
        setattr(self, 'format', a)
        setattr(self, 'output', b)
    
    def disable(self):
        if self.mode == 'disabled':
            return
        else:
            self.mode = 'disabled'
        a, b = self.__mode[self.mode]
        setattr(self, 'format', a)
        setattr(self, 'output', b)
    
    def enable_lite_mode(self, quiet=False):
        self.switch_mode('lite_mode', quiet=quiet, _h=2)
    
    def disable_lite_mode(self, quiet=False):
        if self.mode == 'disabled':
            raise Exception(
                '[lk_logger.logger.BaseLogger]',
                'lk logger is disabled, you should call `lk.enable()` first to '
                'reactivate master control.'
            )
        self.switch_mode('full_mode', quiet=quiet, _h=2)
    
    def change_print_scope(self, scope: int):
        assert scope in (0, 1, 2)
        self._print_scope = scope
    
    # -------------------------------------------------------------------------
    
    def format(self, data, **kwargs):
        """
        
        Args:
            data:
            **kwargs:
        
        Keyword Args:
            advanced
            count
            divider_line
            indent: int[4]
            start_from_newline: bool[False].
            tag:
            title: effect when `start_from_newline` is True.
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
            if kwargs.get('tag'):
                varnames = info.varnames[1:]
            else:
                varnames = info.varnames
            assert len(varnames) == len(data), (info, data)
            temp = []
            for k, v in zip(varnames, data):
                temp.append(f'{k} = {v}' if k else str(v))
            msg_body = kwargs.get('sep', ';\t').join(temp)
        else:
            msg_body = kwargs.get('sep', ';\t').join(map(str, data))
        if self._visualize_linebreaks:
            msg_body = msg_body.replace('\n', '\\n')
        if kwargs.get('start_from_newline', False):
            title = kwargs.get('title', '')
            msg_body = title + indent(
                '\n' + msg_body, ' ' * kwargs.get('indent', 4)
            )
        
        out = self._template.format(
            # source=f'{info.filename}:{info.lineno}',  # TODO: fixed width
            filename=info.filename,
            lineno=info.lineno,
            func=info.name,
            msg=f'{msg_head} {msg_body}'.strip(' ')
        )
        return out
    
    @staticmethod
    def _get_varnames():
        info = sourcemap.get_frame_info(advanced=True)
        return info.varnames
    
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
    
    def output(self, msg: str, **kwargs):
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
    
    @property
    def version(self):
        from . import __version__
        return __version__
