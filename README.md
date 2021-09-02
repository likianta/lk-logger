
📝 English document is not complete. See Chinese version (lk-logger v3.6.3) at
<https://blog.csdn.net/Likianta/article/details/109883527>.

# Install

```
pip install lk-logger
```

# Quick Start

```python
from lk_logger import lk
a = 1
b = 2
print(a + b)
lk.log(a + b)
lk.loga(a + b)
```

Screenshot:

![](.assets/20201121014611469.png)

# Performance

Timeit:

```shell
cd <lk_logger_project>/unittest
python -m timeit -n <test_round> -s "import sys" "sys.path.insert(0, <lk_logger_project>)" "import basic_tests" "basic_tests.main()"
```

| test round | v3.6.3 | v4.0.0-alpha | v4.0.0-alpha with lite mode |
| ---------- | ------ | ------------ | --------------------------- |
| 5   | 62.7ms/loop | 8.22ms/loop | 1.27ms/loop |
| 500 | 64.7ms/loop | 8.14ms/loop | 2.41ms/loop |
