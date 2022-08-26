# LK Print 标记方式

## 标记是什么

标记是一个轻量的打印控制方式, 它用来告诉 lk-print 如何打印目标对象.

查看下面的标记示例以获得初步的, 直观的认识:

```python
# 打印一条分割线
print(':d', 'this is a divider line')
''' 效果:
        ------------------------------------------------ this is a divider line
    备注:
        1. 宽度由 lk-print 的预设配置决定.
        2. 分割线样式, 标题位置, 颜色等也是由 lk-print 的预设配置决定.
        这些内容都是可配的.
'''

# 给内容加上序号
print(':i', 'monday')
print(':i', 'tuesday')
print(':i', 'wednesday')
''' 效果:
        [1] monday
        [2] tuesday
        [3] wednesday
    备注:
        1. 序号默认从 1 开始.
        2. 您还可以自定义序号的格式 (例如 [001], [1/7], [0x1] 等), 具体请查看后续章节.
        3. 重置序号, 反转序号等操作也有相应的标记支持. 具体请查看后续章节.
'''
```

## 为什么要有标记

我们在上个版本的 lk-print 推广过程中发现, 开发者的使用意愿普遍较低. 原因是他们已经有自己的方式来打印内容 (比如使用 python 自带的 print 或者 logging 库), **并且已经在项目中大量地应用**.

让开发者不计成本地迁移到一个新的打印库, 是一件困难的事情. 为此我们对新版本的 lk-print 做出了一些重要改变.

其中一个是, 我们在新版本中支持一行代码实现全局替换 print, 不需要对原项目进行大的改动了 (这是另一个话题, 本文不再赘述); 但它只是让核心体验得以保证, 该怎么让 lk-print 的特色功能发挥出来, 就需要给开发者们提供一种更轻松的, 可选的方式来引用.

"标记" 就是基于这样的想法被创造出来, 且它的格式是基于现实情况精心设计的结果.

标记在以下方面很有用:

1. **无需导入.** 标记使用字符串格式, 不需要引入额外的库.
2. **简洁.** 不影响观感, 且对原有的代码排版的影响很小.
3. **控制项丰富实用.** 已确认完全覆盖所有常用控制项.
4. **副作用低.** 无论是否使用标记, 都不会造成程序运行异常.
5. **可选.** 在没有标记的情况下, lk-print 按照默认的方式打印.

## 标记的使用

**标记的出现位置**

*TODO*

**单一标记和多重标记**

*TODO*

**扩展标记**

*TODO*

**标记用例演示**

*TODO*

## 索引表

### 可用的标记符

*TODO*

> 以下是备忘.

```
markup list
    :d  divider line
    :i  index
    :l  long / loose
    :p  parent layer
    :r  rich
    :s  short
    :t  timestamp / timer
    :v  verbose / log level (trace, debug, info, warning, error, fatal)
        refer to https://stackoverflow.com/a/64806781

markup options
    :d0     default divider line (default)
    :d1+    user defined (if not, fallback to :d0)

    :i0     reset index
    :i1     number width fixed to 1 (1, 2, 3, ... 9, 10, 11, ...) (default)
    :i2     number width fixed to 2 (01, 02, 03, ..., 99, 100, 101, ...)
    :i3     number width fixed to 3 (001, 002, 003, ..., 999, 1000, 1001, ...)
    :i4~8   number width fixed to 4/5/6/7/8
    :i9+    reserved, not defined yet (will be fallback to :i1)

    :l0     let lk-print decide how to format long message (default)
    :l1     force expand all nodes

    :p0     self layer
    :p1     parent layer (default)
    :p2     grand parent layer
    :p3     great grand parent layer
    :p4     great great grand parent layer
    :p5+    great ... grand parent layer
            note: be careful using :p2+, it may crash if the layer not exists

    :t0     reset timer
    :t1     start timer
    :t2     stop timer and measure duration (default)

    :v0     trace (default)
            if you don't like using number, you can use an alias :vt
    :v1     debug (alias is :vd)
    :v2     info (alias is :vi)
    :v3     warning (alias is :vw)
    :v4     error (alias is :ve)
    :v5     fatal (alias is :vf)
    :v6+    user defined (if not, fallback to :v0)
```

### 通用的配置项

*TODO*

### 每个标记的详细配置

*TODO*
