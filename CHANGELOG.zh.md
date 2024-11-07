# LK Logger 更新日志

### 6.0.2 (2024-11-07)

- *次要更新*
    - 修复控制流中的一些问题

### 6.0.1 (2024-11-01)

- *次要更新*
    - 修复一些问题

### 6.0.0 (2024-10-25)

- **重要更新**
    - 引入 "scope" 概念
    - 保存报错截图
    - 细分 verbosity 级别, 增加更多高亮颜色
- *次要更新*
    - 恢复多线程打印
    - 修复 `input` 在多线程打印中的表现

--------------------------------------------------------------------------------

### 5.7.7 (2024-08-03)

- *次要更新*
    - 更新 `:r2` 标记

### 5.7.6 (2024-07-18)

- *次要更新*
    - 调整 source path 风格选项

### 5.7.5 (2024-06-18)

- *次要更新*
    - 修复 ipython 环境检测
    - 修复 traceback 行裁剪问题

### 5.7.4 (2024-05-23)

- *次要更新*
    - 修复打印时的控制台换行被裁剪的问题

### 5.7.3 (2024-05-21)

- *次要更新*
    - 修复并行打印产生的递归问题

### 5.7.2 (2024-05-17)

- **重要更新**
    - 增加 `:r2` 和 `:t3` 标记, 用于识别并转换部分 python 类型为 markdown 或 table 格式

### 5.7.1 (2024-05-16)

- *次要更新*
    - 修复 ipython 中的打印现象

### 5.7.0 (2024-05-11)

- **重要更新**
    - 重新设计并行打印

### 5.6.5 (2024-05-10)

- *次要更新*
    - 更改默认的分隔符, 避免在某些终端中出现乱码

### 5.6.4 (2023-12-04)

- *次要更新*
    - 更新 `:l1` 标记效果

### 5.6.3 (2023-10-06)

- *次要更新*
    - 临时计数器 `:i2` 和 `:t2`
    - 一种可选的 sourcemap 排版风格

### 5.6.2 (2023-06-14)

- *次要更新*
    - 修复 ipython 中可能出现的报错

### 5.6.1 (2023-05-23)

- *次要更新*
    - 微调打印效果

### 5.6.0 (2023-05-22)

- **重要更新**
    - 添加分流器
    - 优化内部信息类型

### 5.5.2 (2023-05-19)

- *次要更新*
    - 修复 flush scheme 引起的断流报错

### 5.5.1 (2023-05-17)

- *次要更新*
    - 修复 windows 下的路径格式

### 5.5.0 (2023-05-10)

- **重要更新**
    - 变更部分标记功能/含义
    - 优化标记效果
    - 新增标记
- *次要更新*
    - 修复 sanic, tornado 等框架中产生的报错信息不明确的问题
    - 新增 `:e` 标记, 用于打印异常信息
    - 新增 `:i2` 嵌套打印计数器

### 5.4.9 (2023-04-28)

- *次要更新*
    - 修复 `:p` 指向错误
    - 为全局控制方法添加更易记忆的别名

### 5.4.8 (2023-02-07)

- *次要更新*
    - 使用 `:l` 标记打印异常时, 展示完整的 traceback
    - 修复部分情况下 `:p` 指向不准的问题

### 5.4.7 (2022-11-25)

- *次要更新*
    - 优化与 ipython 协同体验

### 5.4.6 (2022-10-31)

- *次要更新*
    - 增加 `:r1` 标记, 支持打印 RichRenderable 对象

### 5.4.5 (2022-10-24)

- *次要更新*
    - 优化 flush 策略

### 5.4.4 (2022-10-18)

- *次要更新*
    - 修复 `:v` 标记在部分情况下可能引起报错

### 5.4.3 (2022-10-13)

- *次要更新*
    - 修复报错时的打印流顺序异常

### 5.4.2 (2022-10-09)

- *次要更新*
    - 修复 start_ipython 在处理 sys.argv 时的错误

### 5.4.1 (2022-10-08)

- *次要更新*
    - 修复打印循环中报错导致子线程崩溃的问题

### 5.4.0 (2022-09-28)

- **重要更新**
    - 加入管线功能

### 5.3.2 (2022-09-27)

- *次要更新*
    - 优化 ipython 进入与退出
    - 增加 `:s` 对其他标记的影响力

### 5.3.1 (2022-09-23)

- *次要更新*
    - 增加 `:f` (flush and drain) 标记
    - 修复 `show_varnames` 参数

### 5.3.0 (2022-09-21)

- **重要更新**
    - 多线程加速
- *次要更新*
    - 修复部分标记的功能错误

### 5.2.4 (2022-08-30)

- *次要更新*
    - 修复 python 3.8 适配问题

### 5.2.3 (2022-08-29)

- *次要更新*
    - 添加时间戳/计时标记 (`:t`)
    - 文本颜色稍作调整, 更容易看清

### 5.2.2 (2022-08-22)

- *次要更新*
    - 优化 ipython 报错封装方式

### 5.2.1 (2022-08-22)

- *次要更新*
    - 对 ipython 报错方式封装

### 5.2.0 (2022-08-04)

- **重要更新**
    - 修复了日志配置上的一些缺陷. 现在可以正确关闭显示 source 和 funcname 信息了
    - 加入缓存机制
- *次要更新*
    - 对测试用例的文件名进行了重新规范

### 5.1.6 (2022-07-28)

- *次要更新*
    - 不在错误回溯中显示 locals 变量信息. 这有助于减少冗余的信息对排查错误造成的干扰

### 5.1.5 (2022-07-13)

- *次要更新*
    - 修复多行打印效果

### 5.1.4 (2022-07-08)

- *次要更新*
    - 调整了打印细节效果

### 5.1.3 (2022-07-06)

- *次要更新*
    - 修复了 python 3.8 运行报错

### 5.1.2 (2022-07-05)

- *次要更新*
    - 优化 logging 配置
    - 优化报错显示

### 5.1.1 (2022-07-04)

- *次要更新*
    - 避免 traceback.print_exception 的打印效果受 lk-logger 影响

### 5.1.0 (2022-07-01)

- **重要更新**
    - 将依赖库迁移到 [rich](https://github.com/Textualize/rich)

### 5.0.5 (2022-05-03)

- *次要更新*
    - 修复了 python 3.8 类型注释的语法兼容性问题

### 5.0.4 (2022-04-26)

- *次要更新*
    - 新增 `:s` (short) 标记, 用于简化排版格式

### 5.0.3 (2022-04-22)

- **重要更新**
    - 提升 markup 的稳定性
- *次要更新*
    - 修复 loose format 对部分关键词的渲染异常
    - 将 pytermgui 依赖从 4.x 升级到 5.0

### 5.0.2 (2022-03-26)

- *次要更新*
    - 微调 `lk_logger.setup` 函数传参

### 5.0.1 (2022-03-24)

- **重要更新**
    - 修复部分高亮失效的问题
- *次要更新*
    - 允许用户在 setup 时传入 quiet 参数, 以隐藏 lk-logger 初始化信息
    - 优化 log level 的间距 (padding)
    - 移除所有遗留的已弃用模块

### 5.0.0 (2022-03-22)

- **重要更新**
    - 通过黑魔法实现内置 print 的替换
    - 对 lk-logger 的用法做了大幅简化和改进
    - 引入代码高亮 (依赖 pytermgui)

--------------------------------------------------------------------------------

### 4.1.0 (2022-03-09)

- **重要更新**
    - [新增] 提供一个可选项, 可以全局替换内置的 `print` 函数

### 4.0.7 (2021-12-28)

- *次要更新*
    - [变更] 调整模式切换的函数接口

### 4.0.6 | 2021-12-17

- *次要更新*
    - [优化] 从 caller frame 查找路径的方式

### 4.0.5 (2021-12-14)

- *次要更新*
    - [优化] lk-logger 模式切换增强
    - [新增] 静默切换模式

--------------------------------------------------------------------------------

### 3.6.3 (2020-08-30)

- **重要更新**
    - [变更] lk-logger 从 lk-utils 中剥离并独立, 这是第一个从另一个主项目独立出来的版本
- *次要更新*
    - [移除] 不再引用 time_utils.simple_time() 函数
    - [更新] 默认不打印 DEBUG 级别的信息
    - [更新] 部分变量变为私有变量
    - [变更] 默认关闭 LKLogger._recorder
    - [优化] 移除实例化时的开始时间提示

### 3.5.x (2019-11-06)

- **重要更新**
    - [新增] LKLogger 新增 terminal 类变量, 用于指定输出终端
    - [优化] 重构计数器相关的方法
- *次要更新*
    - [变更] init_counter() 合并到 wrap_counter()
    - [优化] 重构计数器相关的方法
    - [优化] count(), enum() 使用更安全的类型检查
    - [优化] init_count() 调整为与 count() 行为一致
    - [修复] MsgRecorder.record() 在记录 tag 时的错误
    - [新增] 计数器增加 interval 参数
    - [变更] 计数器从 _base_print() 改为在 log*x() 方法中实现
    - [变更] _base_print() 移除 caller 参数
    - [修复] 计数器 interval 参数
    - [移除] MsgRecorder.show_important_messages() 取消对 msg_list 的排序行为
    - [优化] logp() 方法
    - [变更] init_count() 合并到 count() 方法
    - [优化] dump_log() 方法
    - [优化] 计数方法
    - [修复] log() 在打印非 str 类型的单变量时的错误

### 3.4.x (2019-10-22)

- **重要更新**
    - 取消向后兼容的方法
    - 新增 _organize_messages() 方法以减少 log*() 的结构冗余
- *次要更新*
    - 新增 logp() 方法
    - 调整 MsgRecorder.show_important_messages() 的显示效果
    - 拆除内置的 testflight() 方法
    - 优化 caller frame 的查找流程
    - _base_print() 移除 h 参数
    - 新增 _self 变量来调节内部的 direct_caller 变动
    - AstAnalyser 优化对关键字参数的裁剪处理
    - 修复外部调用者使用 h='parent' 时的指向错误
    - 调整 _organize_messages() 返回的元组中的元素类型
    - AstAnalyser.sanitize_string() 优化对 True, False, None 的处理
    - log*() 返回 _base_print() 的值
    - 优化 _extract_vars_from_srcln() 方法
    - MsgRecorder.show_important_messages() 默认不显示 DEBUG 级别的详情信息

### 3.3.x (2019-08-20)

- **重要更新**
    - 使用 AstAnalyser 取代 ParamsMatcher
- *次要更新*
    - AstAnalyser 修复关键词参数引起的报错
    - AstAnalyser 优化对字符串的识别
    - AstAnalyser 修复源码行换行引起的语法解析错误
    - AstAnalyser 修复因中文字符引起的 col_offset 偏移错误
    - logd*() 方法允许按照 loga 形式处理 var_names

### 3.2.x (2019-06-25)

- *次要更新*
    - 新增 lite_mode 简单打印方式
    - 修复 over() 在显示结束时间时的错误
    - 恢复 total_count 成员身份
    - _extract_vars_from_srcln() 修复一种新发现的折行错误
    - 优化 _base_print() 在 lite_mode 下的打印效果
    - dump_log() 缺省值改由 file_sniffer.getpath() 提供
    - print_important_msg() 若 Recorder 对象无 tag_messages 则立刻返回
    - 修复在捕获 "grand_parent" 及以上层级时由于 p3 正则表达式引起的捕获失效
    - 修复 CallerFinder 的 self.hierarchy 字典键名错误
    - MsgRecorder#print_important_msg() 在显示统计信息时附上一条快照记录
    - 允许 over() total_count 参数在未指定时使用 self.denominator
    - 优化 dump_log() 的打印显示
    - 新增 log_enable 类变量
    - 优化对 "[TEMPRINT]" 标识的判断

### 3.1.x (2019-05-14)

- **重要更新**
    - 创建 CallerFinder, 将 caller, frame 相关行为集成
    - 将 hierarchy 参数名简化为 h
- *次要更新*
    - 修复 _get_var_names() 的逻辑错误
    - 优化打印细节
    - 修复 dump_log() 对输出后的日志路径提示不当
    - 修复 _base_print() 调用 MsgRecorder.record() 时的数据类型错误
    - 补充 init_counter() 后向兼容
    - 增强向后兼容性
    - 优化对编码符的判断和处理方法
    - 修复 _extract_vars_from_srcln() 在不可用时的处理错误
    - 修复 CallerFinder.find_caller_by_hierarchy() 在 code_context 不可用时的错误
    - 优化 _base_print() 打印细节
    - MsgRecorder.show_important_messages() 跳过 '[TEMPRINT]' 的详情打印
    - over() 取消 total_count 的缺省设置
    - 修复在外部命令调用时出现的 PathManager 计算相对路径失效
    - calculate_relative_path() 简化代码
    - _base_print() 增加对 `\r` 的识别

### 3.0.x (2019-05-14)

- **重要更新**
    - 重构 lk_logger.py, 大量优化逻辑, 大幅提升速度
    - 取消 frameid, 使用 filepath + lineno 来定位
    - 增加向后兼容性
    - 增加 logdx()
- *次要更新*
    - 修复 _extract_vars_from_srcln()
    - 修复 _get_var_names() 的逻辑错误
    - 修复路径中的反斜杠引起的问题

--------------------------------------------------------------------------------

### 2.6.x

- **重要更新**
    - 将 generate_time_stamp() 独立为模块 (time_utils.py)
    - 将 smart_msg() 的主体代码独立为类 ParamsMatcher
    - 优化 smart_msg() 成对符号匹配的效率
    - 创建 hierarchy_interpreter() 以支持形象化的层次描述
- *次要更新*
    - 优化 find_caller(), 修复 pyinstaller 打包后调用出错的问题
    - 简化 init_counter() 逻辑
    - 优化 smart_msg() 判断方法
    - 根据 time_utils 的变动, 调整 generate_time_stamp() 的时间格式
    - 整理优化代码
    - smart_msg() 增加对 `(A)  # B` 格式的捕获
    - 优化 smart_msg() 的 patterns
    - 修复 smart_msg() 对 `.format()` 的错误处理
    - 修复 ParamsMatcher 匹配错误
    - 增加 test_smart_msg() 测试用例
    - 修复 smart_msg() 快速判断的失误
    - 取消 dump_log() 的 shortname 支持

### 2.5.x

- **重要更新**
    - 将 auto_create_msg() 重命名为 smart_msg()
    - 优化 smart_msg() 方案, 适配更多场景
- *次要更新*
    - 修复 smart_msg() 对 count_up 参数的识别
    - 优化 divider_line() 容错度
    - 优化 smart_msg() 输出样式的细节
    - smart_msg() 增加 len(raw_data) == 1 的快速判断
    - over() 在打印时, 增加一条分割线
    - 优化 smart_msg() 容错度
    - smart_msg() 增加对 format 的支持
    - 优化 smart_msg() 输出样式的细节 (多参数之间由 '\t' 分隔改为 ';\t' 分隔)
    - 修复 smart_msg() 对 count_up 和 hierarchy 的处理
    - smart_msg() 增加对 `(a + 'b')` 形式的捕捉
    - prt() 取消对打印重要信息时的格式美化 (空格与制表符的转换被取消了)
    - smart_msg() 修复 len(raw_data) == 1 时对字符串格式的判断
    - 将 pattern1, pattern2, smart_msg_pattern 取消类变量身份, 改为方法内变量

### 2.4.x

- **重要更新**
    - record_launch_func() 改名为 prt_fun_args(), 并简化功能
    - 取消 find_context(), 将其整合到 prt_fun_args()
    - 简化打印格式 (由 'File "main.py", line 12 ...' 变为 'main.py:12 ...')
    - prt_auto() 重命名为 smart_prt()
- *次要更新*
    - 微调 prt() 中使用 self.update_info_collector(msg) 的位置
    - 使用 sys.argv 替代 main() 方法, 省去每次初始化 logger 的操作
    - 优化 init_path_manager() 方法
    - 完善 LKLogger 的注释
    - 取消 dump_log() 的 add_funname 参数
    - 增加 prt_auto 及相关方法
    - find_caller() 增加 line 变量
    - 优化相对路径的计算方法
    - 当总耗时低于0.01s时, 切换到毫秒显示
    - 更新注释文档, 使支持最新方法格式
    - 增强 auto_create_msg() 兼容性
    - 优化 divider_line() 的样式生成方法

### 2.3.x

- **重要更新**
    - 增加 hierarchy_detain 成员, 以修复打印行号错误
    - 取消 hierarchy 和 hierarchy_detain 成员, 将 hierarchy 改为 prt() 的参数之一
- *次要更新*
    - init_counter() 逻辑调整优化
    - over() 当平均速度为 "0.0s/个" 时, 转换成毫秒显示
    - 在 main() 中打印出 start_time
    - 调整 divider_line() 的 count_up 参数位置
    - 优化 generate_time_stamp() 方法, 使更加智能
    - 调换 generate_time_stamp() 的两个参数 (ctime 和 style) 的位置
    - 将 generate_time_stamp() 的 style 的默认样式修改为 'y-m-d h:m:s'
    - counter_limit 重命名为 counter_denominator
    - 优化 update_info_collector() 的正则表达式
    - prt() 中增加多变量打印时的格式美化 (分号转制表符)
    - 创建 prt_table() 方法

### 2.2.x

- **重要更新**
    - 升级 high_level_info_collector
- *次要更新*
    - 增加一个 live template ("lke")
    - high_level_info_collector 内部根据 tag 进行排序整理
    - 将 print_important_msg() 的统计步骤放在了打印后
    - 增加一个 record_launch_func(), 用于记录当前运行程序的启动参数
    - dump_log() 增加一个格式, 可以选择打印出启动文件名 + 启动方法名
    - 将时间戳单独为一个方法 generate_time_stamp()
    - generate_time_stamp() 增加 style 参数
    - 删除 self.high_level_info_collector_activated 对象
    - 修复 prt() 中 count_up 的格式错误
    - 当 high_level_info_counter.values() 全部为0时, 则不打印
    - 将 hierarchy 改为内部对象, 不再在方法中暴露

### 2.1.x

- **重要更新**
    - 增加 log_container 列表对象和 dump_log() 方法
- *次要更新*
    - dump_log() 增加 use_shortname 参数
    - 将 dump_log() 的 use_shortname 改为 custom_filename, 并支持自定义命名前缀
    - 恢复 self.high_level_info_collector_activated 对象
    - 整合 dump_log() 的参数, 使用智能判定
    - 更新注释文档

### 2.0.x

- **重要更新**
    - 使用 inspect 模块的 stack() 方法重构 prt()
    - 大幅减少动态模板代码量
- *次要更新*
    - 精简初始化 logger 操作

--------------------------------------------------------------------------------

### 1.4.x

- **重要更新**
    - 更新了 LKLogger 的注释文档, 统一了之前的格式, 以及增加了打印重要信息时的推荐写法
- *次要更新*
    - 优化了计时器逻辑, 使用 lk.over(), 取代以前的 lk.start_timer() 和 lk.over_timer()
    - 优化了注释文档
    - 将 high_level_info_collector 中的 'enabled' 键删除
    - 扩增了 print_important_msg() 的捕获范围
    - cycle_point() 即将抛弃, 建议改用 divider_line()
    - divider_line() 增加 mirror 参数, 以及更新了进阶操作的相关说明
    - 增加一个 counter 和 counter_denominator 变量, 用来给特定打印行计数
    - 删除 lk.start_timer() 和 lk.over_timer()
    - divider_line() 增加 count_up 参数
    - divider_line() 的 "remark" 参数改为 "msg" 并调换到第一位

### 1.3.x

- *次要更新*
    - 调整了 print_important_msg() 中 output_path 参数的位置
    - 调整了 print_important_msg() 的缩进
    - print_important_msg() 的 show_details 参数默认改为 True
    - 增加了一个 total_count 内置对象
