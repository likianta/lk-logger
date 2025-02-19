"""
1. $env.PYTHONBREAKPOINT = 'IPython.core.debugger.set_trace'
2. run this file by `pox tests/pdb_ipython_set_trace.py`
3. try:
    print(123)
    aaa  # -> alpha
    bbb  # NameNotFoundError
    continue  # or 'c' -> exit pdb
"""
import lk_logger
lk_logger.setup()
aaa = 'alpha'
breakpoint()
print('over')
