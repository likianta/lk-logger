import typing as t


class T:
    Pipe = t.Callable[..., t.Any]
    PipeId = str
    Pipes = t.Dict[PipeId, Pipe]


class Shunt:
    _pipes: T.Pipes
    
    def __init__(self):
        self._pipes = {}
        self._id_gen = 0
        
    def __call__(self, msg: t.Union[str, t.Any], **kwargs) -> None:
        for p in self._pipes.values():
            p(msg, **kwargs)
    
    def add(self, pipe: T.Pipe, name: str = '') -> T.PipeId:
        self._pipes[id := name or self._random_id()] = pipe
        return id
    
    def remove(self, id: T.PipeId) -> None:
        self._pipes.pop(id)
    
    def _random_id(self) -> T.PipeId:
        self._id_gen += 1
        return f'pipe_{self._id_gen}'
