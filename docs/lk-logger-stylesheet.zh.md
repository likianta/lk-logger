# lk-logger 样式表说明

lk-logger 以字典的形式定义样式表.

字典的键是元素名称, 值是元素的可选属性.

如下是字典的结构:

```
{
    <element>: {
        <attribute>: <value>, ...
    }, ...
}
```

## 样式如何被应用

*TODO*

## 元素列表

**filepath**

文件路径. 这是一个泛指, 包括绝对路径, 相对路径, 或者未识别的路径格式.

- 关于未识别的路径格式: 例如在解析 `exec(<string>)` 时, 我们从 `<string>:frame.co_code.co_filename`
  中获取到的是 '\<string\>' 字符串, 它也被认为是 filepath 元素.
- 关于绝对路径的分隔符: 没有明确限制, 一般使用和系统相关的分隔符, 即正斜杠反斜杠都可以有.

**filename**

文件名. 该名称包含文件格式后缀.

**file_abspath**

文件的绝对路径.

**file_relpath**

文件的相对路径.

**lineno**

行号.

**charno**

位于行中的字符位置. 一般和 `lineno` 连用, 例如 `lineno:charno` 表示第几行第几列, 能够精确定位光标的位置.

**tag**

```
class Tag(Style):
    template = str  # default '[{level}{nn}{ss}]'
    #   level
    #   yyyy: full year
    #   mm: full month 01 - 12
    #   dd: full day 00 - 31
    #   hh: full hour 00 - 23
    #   nn: full minute 00 - 59
    #   ss: full second 00 - 59
    #   no: number, auto increased in current session.
    show_thread_no: bool  # default False
    #   if True, show only when multi-threads.
    
    color_mode: str
    #   options: 'auto', 'light', 'dark'
    
    hilighted_levels: dict[str level, hex color]
    #   default: {
    #       '__mode__': 'auto',
    #       'D, DEBUG': '#00ff00',
    #   }
```

**divider_line**

```python
class DividerLine(Style):
    pattern: union[str, list[str]]  # default '-'
    #   suggest '-', '=', '*', ...
    #   and support multi-chars, like '◆◇', '◇◆◆◇', ...
    #   if pattern is a list, each str in list represents corresponding level.
    #       the final str will be used for its level and all its sub levels.
```

**divider_block**

```python
class DividerBlock(Style):
    pattern: union[str, list[str]]  # default '-'
    default_width: int  # default 80
    is_abs_width: bool  # default False
    overflow_scheme: str  # default 'ellipsis'
    #   options: 'ellipsis', 'overflow', 'wrap'
    sealed_head: bool  # default False
    sealed_tail: bool  # default False
```
