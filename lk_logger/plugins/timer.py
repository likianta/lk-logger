from time import time


class Timer:
    
    def __init__(self):
        self._start_time = time()
        self._end_time = None
    
    def start_timer(self):
        self._start_time = time()
    
    def end_timer(self):
        self._end_time = time()
    
    @property
    def _elapsed_time(self):
        return self._end_time and self._end_time - self._start_time
