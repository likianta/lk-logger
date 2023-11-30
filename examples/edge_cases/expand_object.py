import lk_logger

lk_logger.setup()


class A:
    aaa = 123
    bbb = 'beta'
    ccc = True


print(A(), ':l0')
print(A(), ':l1')

# pox examples/edge_cases/expand_object.py
