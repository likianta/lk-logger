from textwrap import dedent

import lk_logger
from rich.markdown import Markdown

lk_logger.setup(quiet=True, show_source=False, show_funcname=False)


print(
    Markdown(dedent('''
        # emei_r1p2
        # set IIC
        # ccc
    ''')),
    ':r1',
)
