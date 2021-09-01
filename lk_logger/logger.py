from .sourcemap import frame_finder, sourcemap


class Logger:
    
    def __init__(self, **kwargs):
        self.var_seg = kwargs.get('var_seg', ';\t')
    
    @staticmethod
    def fmt_msg(data):
        frame = frame_finder.frame
        info = sourcemap.get_frame_info(frame)
        
        if info.varnames:
            assert len(info.varnames) == len(data)
            new_data = []
            for k, v in zip(info.varnames, data):
                new_data.append(f'{k} = {v}' if k else v)
            data = ';\t'.join(new_data)
        else:
            data = str(data)[1:-1]
        
        out = '{}:{}\t>>\t{}\t>>\t{}'.format(
            info.filename, info.lineno, info.name, data
        )
        return out
    
    # noinspection PyUnusedLocal
    @frame_finder.getframe
    def loga(self, *data, h='self'):
        msg = self.fmt_msg(data)
        print(msg)


# TEST
lkk = Logger()


class BaseLogger:
    
    def __init__(self, **kwargs):
        from json import load
        config = load(open(f'{__file__}/../config/base.json'))  # type: dict
        config.update(kwargs)
        
        self._var_seg = config.get('var_seg', ';\t')
        self._template = '{filename}:{lineno}\t>>\t{func}\t>>\t{msg}'

    def fmt_msg(self, data, **kwargs):
        frame = frame_finder.frame
        info = sourcemap.get_frame_info(
            frame, advanced=kwargs.get('advanced', False)
        )
        
        if info.varnames:
            assert len(info.varnames) == len(data)
            msg = []
            for k, v in zip(info.varnames, data):
                msg.append(f'{k} = {v}' if k else v)
            msg = ';\t'.join(msg)
        else:
            msg = str(data)[1:-1]

        out = self._template.format(
            filename=info.filename,
            lineno=info.lineno,
            func=info.name,
            msg=msg
        )
        return out
    
    @frame_finder.getframe
    def log(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError

    @frame_finder.getframe
    def loga(self, *data, h='self'):
        # msg = self.fmt_msg(data, advanced=True)
        # ...
        raise NotImplementedError
