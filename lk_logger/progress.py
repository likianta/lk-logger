"""
a wrapper for `rich.progress`.
test case:
    test/delay_prints.py
"""
import typing as t
from contextlib import contextmanager

import rich.progress

from .control import delay

Item = t.TypeVar('Item', bound=t.Any)


def track(
    sequence: t.Union[t.Sequence[Item], t.Iterable[Item], t.Iterator[Item]],
    description: str = 'working...'
) -> t.Iterator[Item]:
    with delay():
        yield from rich.progress.track(sequence, description)


@contextmanager
def spinner(desc: str = 'working...') -> t.Iterator:
    # fix showing time elapsed for indeterminate progress
    # https://github.com/Textualize/rich/issues/1054
    cols = rich.progress.Progress.get_default_columns()
    cols[-1].elapsed_when_finished = True  # noqa
    with delay():
        with rich.progress.Progress(*cols) as prog:
            task = prog.add_task(desc, total=None)
            yield
            prog.update(task, total=1, completed=1)
