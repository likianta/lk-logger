import argsense  # noqa
import lk_logger

# lk_logger.mute('[argsense]')
lk_logger.mute(argsense)

from argsense.renderer.rich.render2 import _roll_color_pair  # noqa
start, end = _roll_color_pair()
print(start, end)
