import lk_logger

lk_logger.update(show_source=True, path_style='relpath')
print('hello world')

lk_logger.update(show_source=True, path_style='filename')
print('hello world')

# pox tests/show_source.py
