# py examples/other/colorful_slogan.py
import lk_logger

for _ in range(10):
    lk_logger.setup()
    lk_logger.control._HAS_WELCOME_MESSAGE_SHOWN = False
