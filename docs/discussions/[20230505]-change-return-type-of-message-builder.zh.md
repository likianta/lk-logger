# 关于变更 `LKLogger._build_message` 的返回类型的决定

## 概述

- `_build_message` 的返回类型将从 `str` 变更为 `rich.console.RenderableType`.
- 该变更将在 5.5.0 版本中生效.

## 为什么

### 尺寸推断

原先的分割线由固定长度的 '-' 组成 (形如 '--------------------'), 但是在终端宽度不足时, 会显示为 "多行" (开启 line wrap 的情况下), 影响美观.

为了解决这个问题, 我们想要根据终端宽度动态调整. 这就需要 `lk_logger/console.py > console > width` 和 `lk_logger/message_builder.py > MessageBuilder > compose > var message_elements` 的配合. 

但后者的元素可能包含了 rich markup, 导致不能简单地使用 `len()` 去计算, ...
