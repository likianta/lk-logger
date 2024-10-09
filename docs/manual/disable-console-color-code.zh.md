# 禁用颜色代码输出

## 需求

因为某些原因, 我不得不在传统的 windows 控制台查看打印内容. 但是 windows 控制台无法正常显示颜色代码 (会变成类似于 "\[0m" 这种文字). 我该如何禁止 lk-logger 输出颜色代码?

## 回答

设置环境变量:

```sh
import os
os.environ['LK_LOGGER_MODERN_WINDOW'] = '0'
```

它不但能够避免主进程的颜色代码输出, 还能避免子进程的颜色代码输出.

特别地, 当使用 `lk_utils : run_cmd_args : force_term_color=True` 时, 以上环境变量也能抑制 `lk_utils` 的参数生效.

## 关联

- `lk_logger.console.Console.__init__`
- `[prj] lk-utils : /lk_utils/subproc/subprocess.py : run_command_args : [param] force_term_color`
