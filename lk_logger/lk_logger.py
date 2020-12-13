"""
@Author  : Likianta <likianta@foxmail.com>
@Module  : lk_logger.py
@Created : 2018-00-00
@Updated : 2020-12-13
@Version : 3.6.3
@Desc    :

Abbreviations:
    curr: current
    ele: element
    fmt: format
    h: hierarchy. it shows which hierarchy that caller located
    lineno: line number
    loga: log with advanced format
    logd: log with divider line
    logp: log with pretty format
    logt: log with tag
    logx: log with index
    msg: message
    pos: position
    prt: print
    relpath: relative path
    srcln: source code line
    val: value
    var: variant

Features:
    1. 打印时会将源码所在的文件名, 所在行号, 所属函数名 (无所属函数则显示
       '<module>') 打印出来
        code: lk.log('hello world')
        print: app.py:1  >>  <module>  >>  'hello world'
    2. 源码行存在变量, 打印时会将变量名也打印出来 (注: 需要使用 loga 函数)
        code: lk.loga(A, B, C)
        print: app.py:3  >>  <module>  >>  A = 'aa'; B = 'bb'; C = 'cc'
    3. 源码行的参数是字符串, 则不显示变量名 (因为字符串没有变量名)
        code: lk.loga(A, B, 'hello')
        print: app.py:7  >>  <module>  >>  A = 'aa'; B = 'bb'; 'hello'
    4. 源码行的参数复杂的情况, 也能正确显示
        code: lk.loga(A, B[C:D], E if F else G, "hello-{}".format('ni\'hao'))
        print: app.py:12  >>  <module>  >>  A = 'aa'; B[C:D] = 'bb'; E if F else
            G = 'ee'; "hello-ni'hao"
    5. 此外, 利用 lk.log 的 h 关键字可以打印调用者的调用者所在位置
        code: lk.loga('hello', h='parent')
        print: app.py: 23  >>  parent()  >>  'hello'
    6. 使用 logt 可以打印 tag (该 tag 可在 lk.over() 中被自动统计)
        code: lk.logt('[WARNING]', A)
        print: app.py: 24  >>  main()  >>  [WARNING] A = 'aa'
    7. 更多功能: logd (打印分割线), logx (带序号打印), dump_log (保存日志), ...
"""
import re
import sys
import time
from ast import iter_child_nodes, parse as ast_parse
from inspect import stack
from os.path import abspath, split as ossplit
from typing import *

"""
待更新:
    增加打印风格配置, 例如不打印所属的函数等
    将 base_print() 的 prefix 设置为定宽
    支持 tag 打印时的高亮显示, 并设定高亮颜色
    增加动态抹除的进度条显示方法
"""


class CallerFinder:
    """
    层级的传递必须坚持三个必须:
        1. 层级信息必须由 direct_caller 产生
        2. 层级最终能且只能被 find_caller_* 处理
        3. 层级必须经历以下层次的传递
            ... > great_grand_caller > grand_caller > parent_caller >
            direct_caller > lk.log* > _organize_msg > _get_var_names >
            find_caller_* (see self.find_caller_by_hierarchy())
    """
    hierarchy = {
        'self'              : 4,
        'parent'            : 5,
        'grand_parent'      : 6,
        'great_grand_parent': 7,
        #   注意: 1. 数字不可小于 4
        #         2. 更高级别的调用者, 请手动传入数字: 8, 9, 10, ...
        #         3. 当传入数字超过最大层级时, 会报 IndexError
    }
    
    SELF_HIERARCHY = hierarchy['self']
    
    def interpret_hierarchy(self, h) -> int:
        return h if isinstance(h, int) \
            else self.hierarchy.get(h, self.SELF_HIERARCHY)
    
    # noinspection PyProtectedMember
    def find_caller_frame(self, hierarchy):
        """ NOTE: No usage. """
        hierarchy = self.interpret_hierarchy(hierarchy)
        # noinspection PyUnresolvedReferences,PyUnresolvedReferences
        return sys._getframe(hierarchy)
    
    @staticmethod
    def find_caller_by_frame(frame):
        """
        NOTE: No usage.
        ARGS:
            frame: e.g.
                last_frame = <frame at 0x0000021C15C8E9F8, file
                'D:/.../test.py', line 9, code <module>>
                    last_frame.f_code.co_filename -> 'D:/.../test.py'
                    last_frame.f_lineno -> 9
                    last_frame.f_code.co_name -> <module>
                        (you can see that in the source of last_frame.f_code)
        REF:
            https://stackoverflow.com/questions/2203424/python-how-to-retrieve
             -class-information-from-a-frame-object
        """
        filepath = frame.f_code.co_filename.replace('\\', '/')
        lineno = frame.f_lineno
        function = frame.f_code.co_name
        return filepath, lineno, function
    
    def find_caller_by_hierarchy(self, hierarchy):
        """ Find the source caller related to the target hierarchy.

        caller frame hierarchy:
            | caller                     | hierarchy |
            | -------------------------- | --------- |
            | find_caller_by_hierarchy() |  0        |
            | lk._get_var_names()        |  1        |
            | lk._organize_msg()         |  2        |
            | lk.log*()                  |  3        |
            | direct_caller              |  4        |
            | parent_caller              |  5        |
            | grand_parent_caller        |  6        |
            | great_grand_parent_caller  |  7        |
            | ...                        | ...       |

        IN: hierarchy
        OT: (filepath, lineno, function, source_code_line)

        NOTE: 目前该函数只在 LKLogger._get_var_names() 使用.

        REF:
            https://blog.csdn.net/qiqiyingse/article/details/70766993
            http://www.cnblogs.com/qq78292959/p/3289658.html
            https://www.cnblogs.com/yyds/p/6901864.html
        """
        hierarchy = self.interpret_hierarchy(hierarchy)
        
        context = stack()[hierarchy]
        
        filepath = context.filename.replace('\\', '/')
        lineno = context.lineno
        function = context.function
        if x := context.code_context:
            srcln = x[0].strip()
        else:
            srcln = ''
        
        return filepath, lineno, function, srcln


# ------------------------------------------------------------------------------

class PathManager:
    
    def __init__(self):
        # init path manager
        self.launch_path = abspath(sys.argv[0]).replace('\\', '/')
        self.path_manager = {self.launch_path: ossplit(self.launch_path)[1]}
        # fmt: {filepath: filename}. e.g. {'d:/myprj/app/run.py': 'run.py'}
    
    def get_relpath(self, path):
        """
        IN: path (str): an absolute path.
        OT: (str) a relative path.
        """
        if not self.path_manager.get(path, ''):
            self.update_path_manager(path)
        return self.path_manager.get(path)
    
    def update_path_manager(self, new_abspath):
        """ 该函数用于将导入的模块所在的绝对路径加入到路径管理器中. """
        new_relpath = self._calculate_relative_path(
            self.launch_path, new_abspath
        )
        # relpath -> relative path
        self.path_manager[new_abspath] = new_relpath
    
    @staticmethod
    def _calculate_relative_path(a, b):
        """ 已知两个绝对路径 a 和 b, 求 b 相对于 a 的相对路径. """
        a, b = a.split('/'), b.split('/')
        
        intersection = -1
        
        for m, n in zip(a, b):
            intersection += 1
            if m != n:
                break
        
        def backward():
            return (len(a) - intersection - 1) * '../'
        
        def forward():
            return '/'.join(b[intersection:])
        
        return backward() + forward()


class MsgRecorder:
    
    def __init__(self, tag_record_level='I'):
        builtin_tags = ('D', 'I', 'W', 'E', 'C')
        
        try:
            pos = builtin_tags.index(tag_record_level)
            self._tag_ignores = builtin_tags[:pos]
        except IndexError:
            self._tag_ignores = ()
        
        self._log_messages = []
        self._tag_messages = {t: {} for t in builtin_tags}
        #   e.g. {'D': {'D2324': [<str msg>, ...], 'D5332': [...], ...}, ...}
    
    def record(self, msg, tag=''):
        self._log_messages.append(msg)
        if tag:
            tag_initial = tag.rsplit('[', 1)[1][0]
            """ e.g.
                tag = '[E2345]' -> ['', 'E2345]'] -> 'E2345]' -> 'E'
                tag = '[Writer][D5211]' -> ['[Writer]', 'D5211]'] -> 'D'
            """
            if tag_initial not in self._tag_ignores:
                node = self._tag_messages.setdefault(tag_initial, {})
                node = node.setdefault(tag, [])
                node.append(msg)
    
    def show_important_messages(self, show_details=True, output='console'):
        """
        NOTE: 在输出时排下序, 让相同标签的出现在一起.
        """
        msg_container = []
        
        """
        NOTE: 注意前后顺序. msg_container 需要先装载 details info, 后装载
        summary info. 这样有利于阅读.
        """
        # details info
        if show_details:
            for msg_chunk in self._tag_messages.values():  # type: dict
                """ {tag: [<str msg>]}
                    -> tag: e.g. 'D2324'
                       msg: e.g. 'app.py:28  >>  main()  >>  [D2324] hello'
                """
                for tag, msg_list in msg_chunk.items():
                    msg_container.extend(msg_list)
        
        # summary info
        for msg_chunk in self._tag_messages.values():  # type: dict
            for tag, msg_list in msg_chunk.items():
                one_msg = msg_list[0]
                if (token := '\t>>\t') in one_msg:
                    path_prefix = one_msg.split(token, 1)[0]
                else:
                    path_prefix = 'PATH'
                msg_container.append(
                    f'{path_prefix}{token}'
                    f'◆◆◆◆ {tag} count = {len(msg_list)} ◆◆◆◆'
                )
                # -> e.g. 'app.py:28  >>  ◆◆◆◆ [D2342] count = 234 ◆◆◆◆'
        
        # print the msg or save it into file.
        if output == 'console':
            for i in msg_container:
                print(i)
        else:
            with open(output, 'w', encoding='utf-8') as file:
                file.write('\n'.join(msg_container))
        
        # also take record to log_messages. (for the future to do dump_log())
        self._log_messages += msg_container
    
    def dump_log(self, log_path, launch_path):
        with open(log_path, encoding='utf-8', mode='w') as f:
            prefix = f"""
script launched at {launch_path}.
script filename is {ossplit(launch_path)[1]}.

----------------------------------------------------------------

            """.strip(' ')
            f.write(prefix)
            f.write('\n'.join(self._log_messages))


# ------------------------------------------------------------------------------

class AstAnalyser:
    
    def __init__(self):
        # see self.fake_text()
        self.char = re.compile(r'\w')
        # `f'{A}'` -> ``
        self.string_fmt = re.compile(r'^[frb]*["\']')
        # `True` -> ``
        self.builtin_ele = re.compile(r'True|False|None')
        # `A(` -> `A`
        self.strip_start = re.compile(r'\(.*$')
        # `A)  # B` -> `A`
        self.strip_end = re.compile(
            r', ?h=["\'\w]+\).*$'
            r'|\) *#.*$'
            r'|\) *$')
    
    def mask_text(self, text: str):
        """ 对文本中出现的汉字等双字节字符进行 "掩码" 处理.
        一个有意思的现象, 当 text 中含有汉字等非西文字符时, 会导致 ast 在解析时
        的 col_offset 计算错误. 该问题在 https://bugs.python.org/issue21295 中
        有所体现, 并得到了一些解释:
            "...col_offset 是生成节点的第一个 token 的 utf-8 字节偏移."
        由于一个汉字占用两个字节, 就产生了 col_offset 偏移的问题.
        为了解决它, 我们需要将汉字转换成一个伪造的字母表示. 例如:
            `lk.loga('你好', '不客气')` -> `lk.loga('xx', 'xxx')`
        """
        return re.sub(self.char, 'x', text)
    
    def main(self, text: str) -> Union[List, None]:
        """
        IN: text: make sure it had been stripped.
        OT: list|None.
        """
        fake_text = self.mask_text(text)
        last_index = 0
        out = []
        
        try:
            root = ast_parse(fake_text)
        except SyntaxError:
            """ 这种情况发生的原因是, text 是不符合语法的代码.
            例如:
                lk.logt(A, B
            B 的右侧没有括号封尾, 因此不符合语法规范. 将导致此项报错.
            遇到这种错误, 会返回 None. 请调用方继续处理 (认定为不可解析).
            """
            return None
        
        # 利用 ast 对源码行 (fake_text) 中的各元素 "断句", ast 返回断句处的下标,
        # 我们根据这些下标来分割 fake_text, 从而获取到各个独立的 "元素".
        # 根据测试, 第三层的遍历才是我们想要的正文.
        for a in iter_child_nodes(root):  # 1st layer: _ast.Expr (pass break)
            for b in iter_child_nodes(a):  # 2nd layer: _ast.Call (pass break)
                for c in iter_child_nodes(b):  # 3rd layer: _ast.Attribute, ...
                    if getattr(c, 'col_offset', 0) == 0:
                        continue
                    else:
                        curr_index = c.col_offset
                    r = text[last_index:curr_index]
                    out.append(self.sanitize_string(r))
                    last_index = curr_index
                break  # pass break
            break  # pass break
        # 注意把最后一个断句后的元素补上
        out.append(text[last_index:])
        
        out[0] = self.sanitize_string(out[0], pos='start')
        out[-1] = self.sanitize_string(out[-1], pos='end')
        # print('[LKTEST]', 'lk_logger.py:380', out)
        # text = `lk.loga("ABC", a)` -> out = ['lk.loga', '', 'a']
        
        return out[1:]  # -> ['', 'a']
    
    def sanitize_string(self, s: str, pos=None):
        """
        ARGS:
            s: string to be handled
            pos (None, 'start', 'end'): position. 元素在列表中的位置
        """
        if pos == 'start':
            if s.endswith('('):
                s = s[:-1]
                # 'lk.loga(' -> 'lk.loga'
            else:
                s = re.sub(self.strip_start, '', s)
                # 'lk.loga( ' -> 'lk.loga'
        elif pos == 'end':
            s = re.sub(self.strip_end, '', s)
            # 1) 'a)  # this is a comment' -> 'a'
            # 2) 'a, h="parent")' -> 'a'
        
        # common strip
        s = s.strip(', ')
        
        if self.string_fmt.findall(s) or self.builtin_ele.findall(s):
            return ''
        else:
            return s


# ------------------------------------------------------------------------------

class LKLogger:
    """
    注: 本类中的所有 h = 'self' 均指向 log 函数的直接调用者 (direct caller).
        'parent' 均指向直接调用者的调用者, 'grand_parent' 是直接调用者的调用者的
        调用者, 以此类推.
        例如, 外部函数 fx() 调用了 LKLogger.log(), 则 fx() 是直接调用者.
        例如, 外部函数 fx() 调用了 LKLogger.over(), 而 over() 调用了
        LKLogger.log(), 则 over() 是直接调用者, fx() 是间接调用者. (因此你可以
        看到, 为了让指向到达外部函数 fx(), over() 函数中特意将层级参数上调为
        'parent' 了)
    """
    _code_tracker: dict
    _direct_caller = None
    _self = 'self'  # direct caller hierarchy. 绝大多数情况下, 此值是固定不变的
    #   (始终为 'self'); 少数情况下, 例如开发者想要特意将 direct caller 指向其他
    #   调用者, 则可以操作此变量. 目前操作此变量的函数只有 LKLogger 内部的方法:
    #       self.over(), self.dump_log() and self.print_important_msg().
    
    log_enable = True  # total logger switcher.
    lite_mode = False  # TODO: more works need to be done.
    terminal = None  # None means terminal to console.
    _log_style: dict
    
    __start_time = 0
    __end_time = 0
    
    _finder: CallerFinder
    _tag_recorder: MsgRecorder
    
    _ast_analyser: AstAnalyser
    _path_mgr: PathManager
    
    def __init__(self, tag_record_level='I', enable_recorder=False):
        self._finder = CallerFinder()
        self._ast_analyser = AstAnalyser()
        self._path_mgr = PathManager()
        
        if enable_recorder:
            self._recorder = MsgRecorder(tag_record_level)
        else:
            self._recorder = None
        
        # fmt: {source_filepath: {source_lineno: [direct_var_name]}}
        self._code_tracker = {}
        
        self._log_style = {  # related to self.set_log_style
            'show_func'          : True,
            'graphic_progressbar': False,
            'align_counter'      : True,
        }
        
        # start timing
        self.__start_time = time.time()
    
    def set_log_style(self, style: dict):
        """ TODO: Overwrite self.log_style configurations.

        support properties:
            `show_func`: bool. default True.
                True: e.g. printing 'myapp.py:12 >> main() >> hello'
                False: e.g. printing 'myapp.py:12 >> hello'
            `graphic_progressbar`: bool. default False.
                True: e.g. '■■■■-------------------------- 13%' (writing and
                swiping msg in one line.)
                False: e.g.
                    [01/30] loop index count 1
                    [02/30] loop index count 2
                    [03/30] loop index count 3
                    ...
            `align_counter`: bool. default True.
                True: e.g. '[01/30] loop index count 1'
                False: e.g. '[1/30] loop index count 1'

        e.g. style = {'shor_func': False, 'align_counter': False}
        """
        self._log_style.update(style)
    
    # --------------------------------------------------------------------------
    
    def _base_print(self, *msg, **kwargs):
        """
        kwargs.keys: cnt, tag
        """
        if self.log_enable is False:
            return
        
        msg = ';\t'.join(map(str, msg))
        
        if self.terminal is not None:
            return self.terminal(msg)
        
        # personal settings (aka log style)
        cnt = kwargs.get('cnt', '')
        tag = kwargs.get('tag', '')
        divide_line = kwargs.get('divide_line', '')
        prtend = ' ' if (cnt or tag or divide_line) else ''
        
        if self.lite_mode:
            # prefix
            prefix = '{}{}{}{}'.format(
                cnt, divide_line, tag, prtend
            )
        else:
            filepath, lineno, function, _ = self._direct_caller
            filepath = self._path_mgr.get_relpath(filepath)
            if function != '<module>':
                function += '()'
            
            # prefix
            prefix = '{}:{}\t>>\t{}\t>>\t{}{}{}{}'.format(
                filepath, lineno, function, cnt, divide_line, tag, prtend
            )
        
        print(prefix, end='')
        """ 注意这里我们把 print 的 end 参数设为空字符串, 而由 prtend 控制是否在
            末尾加空格. 这样做的目的是, 在 MsgRecorder 记录的时候, 也能记录到这
            个 rtend; 否则就会在 dump 的时候发现对齐不是很美观 (特别是涉及到
            log*x, logd, logt, logdt 的对齐的时候).
        """
        
        # strip r-char
        # msg = (i.replace('\r', '') for i in msg)  # 去除 \\r 的影响
        # 注: 去除 \\r 的方法暂时不用. 因为它会引起 self.recorder.record() 记录
        #   失败的问题. 原因尚在调查中.
        
        # print it
        print(msg)
        if self._recorder:
            self._recorder.record(prefix + msg, tag=tag)
        return msg
    
    # --------------------------------------------------------------------------
    
    def log(self, *data, h='self'):
        """ log (normal style). """
        self._organize_messages(data, 'log', h)
        return self._base_print(*data)
    
    def loga(self, *data, h='self'):
        """ log in advanced mode.

        NOTICE: 目前 (2019年7月7日) 无法解决以下问题:
            def foo(*x):
                lk.loga(*x)
            foo(1, 2, 3)
        在这种情况下, 只能打印出第一个参数的值: *x = 1
        """
        # print('[LKTEST]', 'lk_logger.py:520', id(data), data)
        msg = self._organize_messages(data, 'loga', h)
        return self._base_print(*msg)
    
    def logd(self, *data, style='-', length=64, h='self'):
        """ log with divide line. """
        msg = self._organize_messages(data, 'logd', h)
        return self._base_print(*msg, divide_line=style * length)
    
    def logt(self, tag, *data, h='self'):
        """ log with tag.

        ARGS:
            tag: support list:
                D, I, W, E, C
                DEBUG, INFO, WARNING, ERROR, CRITICAL
                D0323, I3234, W3145, E2345, C3634, ... (use live templates to
                    generate a timestamp (like `MMSS`) as a uniq code stamp.)
            data
            h
        """
        msg = self._organize_messages(data, 'logt', h)
        return self._base_print(*msg, tag=tag)
    
    def logp(self, *data, h='self'):
        """ log with pretty format.
        IN: [A, B, C]
        OT: [
                A,
                B,
                C
            ]
        """
        from collections import Iterable
        
        msg = self._organize_messages(data, 'logp', h)
        msg_list = []
        for m, d in zip(msg, data):
            if '=' in m and not isinstance(d, str) and isinstance(d, Iterable):
                if isinstance(d, dict):
                    d = (f'{k}: {v}' for k, v in d.items())
                msg_list.append('UNZIP {} (type of {}): \n\t\t{}'.format(
                    m.split('=', 1)[0], type(d), '\n\t\t'.join(map(str, d))
                ))
            else:
                msg_list.append(m)
        
        self._base_print('')
        for msg in msg_list:
            print(f'\t{msg}')
        return msg_list
    
    # --------------------------------------------------------------------------
    
    def logx(self, *data, interval=1, h='self'):
        """ log with index counter. """
        if cnt := self._count_up(interval):
            self._organize_messages(data, 'logx', h)
            return self._base_print(*data, cnt=cnt)
    
    def logax(self, *data, interval=1, h='self'):
        """ log in advanced with index counter. """
        if cnt := self._count_up(interval):
            msg = self._organize_messages(data, 'logax', h)
            return self._base_print(*msg, cnt=cnt)
    
    def logdx(self, *data, style='-', length=64, interval=1, h='self'):
        """ log with divide line and index counter. """
        if cnt := self._count_up(interval):
            msg = self._organize_messages(data, 'logdx', h)
            return self._base_print(*msg, divide_line=style * length, cnt=cnt)
    
    def logtx(self, tag, *data, interval=1, h='self'):
        """ log with tag and index counter. """
        if cnt := self._count_up(interval):
            msg = self._organize_messages(data, 'logtx', h)
            return self._base_print(*msg, tag=tag, cnt=cnt)
    
    # --------------------------------------------------------------------------
    
    def logdt(self, tag, *data, style='-', length=64, h='self'):
        """ log with divide line and index counter. """
        msg = self._organize_messages(data, 'logdt', h)
        return self._base_print(*msg, tag=tag, divide_line=style * length)
    
    def logdtx(self, tag, *data, style='-', length=64, interval=1, h='self'):
        if cnt := self._count_up(interval):
            msg = self._organize_messages(data, 'logdtx', h)
            return self._base_print(*msg, tag=tag, divide_line=style * length,
                                    cnt=cnt)
    
    # --------------------------------------------------------------------------
    # Counter
    
    counter = _denominator = 0
    
    def count(self, x):
        self.counter = 0
        self._denominator = self._measure_obj_length(x)
        return x
    
    def init_count(self, x=0):
        return self.count(x)
    
    reset_count = init_count
    
    def enum(self, x, offset=0):
        self.counter = 0
        self._denominator = self._measure_obj_length(x)
        return enumerate(x, offset)
    
    @staticmethod
    def _measure_obj_length(x):
        if x:
            if isinstance(x, (int, float)):
                return int(x)
            elif hasattr(x, '__len__'):
                return len(x)
        return 0
    
    def _count_up(self, interval=1):
        self.counter += 1
        
        # 当分子超过分母时, 自动释放分母
        if self.counter > self._denominator > 0:
            self._denominator = 0
        
        if interval == 1 or self.counter % interval == 0:
            if self._denominator:
                return '[{}/{}]'.format(
                    str(self.counter).zfill(len(str(self._denominator))),
                    self._denominator
                )
            else:
                return f'[{self.counter}]'
        else:
            return ''
    
    def over(self, total_count=0):
        total_count = max((total_count, self._denominator, self.counter))
        
        self._self = 'parent'  # prompt
        h = 'parent'
        
        self.logd('计时结束', h=h)
        self.__end_time = time.time()
        
        self.log('开始运行: {}'.format(
            _simple_timestamp('y-m-d h:n:s', self.__start_time)
        ), h=h)
        self.log('结束运行: {}'.format(
            _simple_timestamp('y-m-d h:n:s', self.__end_time)
        ), h=h)
        
        # calculate duration
        total_elapsed_time_sec = self.__end_time - self.__start_time
        if total_elapsed_time_sec < 0.01:
            duration = '{}ms'.format(round(total_elapsed_time_sec * 1000, 2))
        elif total_elapsed_time_sec < 60:
            duration = '{}s'.format(round(total_elapsed_time_sec, 2))
        else:
            duration = '{}min'.format(round(total_elapsed_time_sec / 60, 2))
        self.log('总耗时 {}'.format(duration), h=h)
        
        # calculate speed
        if total_count > 0:
            speed = total_elapsed_time_sec / total_count
            if speed < 0.01:
                speed *= 1000
                unit = 'ms'
            else:
                unit = 's'
            self.log(
                '共处理 {} 个. 平均速度 {}{}/个'.format(
                    total_count, round(speed, 2), unit
                ), h=h)
        
        self._self = 'self'  # reset
    
    # --------------------------------------------------------------------------
    # After things
    
    def print_important_msg(self, show_details=True, output='console'):
        if self._recorder:
            self._self = 'parent'  # prompt
            self.logd('here collected important messages', h='parent')
            self._recorder.show_important_messages(show_details, output)
            self._self = 'self'  # reset
    
    def dump_log(self, output, timestamp=True):
        """
        ARGS:
            output: str. 可以传入一个 log 目录, 或者指定一个具体的 log 文件作为
                输出目标.
            timestamp: Add a time stamp.
        """
        if not self._recorder:
            return
        
        if timestamp:
            from os.path import splitext
            a, b = splitext(output)
            output = f'{a}_{_simple_timestamp("ymd_hns")}.{b}'
        
        self._recorder.dump_log(output, self._path_mgr.launch_path)
        self._self = 'parent'  # prompt
        self.log(f'log dumped at "{output}"', h='parent')
        self._self = 'self'  # reset
    
    # --------------------------------------------------------------------------
    # Source Map
    
    def _organize_messages(self, data: Tuple, caller: str,
                           h: Union[str, int]) -> tuple:
        """ Analyse source code line, extract and orgnize params' names and
        values.

        E.g.
            source code line: `lk.loga(name, gender, height, 'Engineer')`
            param data: ('Mike', 'Male', 180, 'Engineer')
            -> return: ('name = Mike', 'gender = Male', 'height = 180',
             'Engineer')
        """
        var_names = self._get_var_names(caller, h)
        if var_names is None:
            msg = tuple(map(str, data))
            # | msg = data
        else:
            msg = tuple(  # var: variant; val: value
                f'{var} = {val}' if var else str(val)
                for var, val in zip(var_names, data)
            )
        return msg
    
    def _get_var_names(self, caller, h):
        """ Extract variants' names from source code line.
        E.g.
            `lk.loga(A, B, C[D], '123')`
            -> ['A', 'B', 'C[D]', '123']
        NOTE: source_caller 关联 filepath, lineno 和 function; direct_caller 关
            联 srcln. 有一个特殊情况, 如果 direct_caller 是 self.over(), 则需要
            将 direct_caller 向上提升一级.
        """
        self._direct_caller = self._finder.find_caller_by_hierarchy(self._self)
        srcln = self._direct_caller[-1]
        
        # source caller
        if self._self == h:
            filepath, lineno, _, _ = self._direct_caller
        else:
            filepath, lineno, _, _ = self._direct_caller = \
                self._finder.find_caller_by_hierarchy(h)
        
        try:
            return self._code_tracker[filepath][lineno]
        except KeyError:
            var_names = self._extract_vars_from_srcln(srcln)
            # print('[LKTEST]', 'lk_logger.py:810', srcln, var_names)
            
            if var_names is not None:
                if caller in ('logt', 'logtx', 'logdt', 'logdtx'):
                    # 这些 caller 的原型都是 logt.
                    # logt 有个特殊的地方在于, 它的第一个参数是 tag. 我们必须把
                    #   它剔除.
                    var_names.pop(0)
            
            node = self._code_tracker.setdefault(filepath, {})
            node[lineno] = var_names
            
            return var_names
    
    def _extract_vars_from_srcln(self, raw_line):
        """ Extract variants' names from source code line.

        IN: source_code_line (str): e.g. 'lk.loga(a, b, c, "hello")  # comment'
        OT: list or None. e.g. ['a', 'b', 'c', '']
            1. in this example, the 4th parameter has no variant name, so we
               would pass it as an empty string instead (both f-string is
               treated as this)
            2. _get_var_names() can auto strip interferences like comments,
               external logger wrapper (`lk.log*()`), etc.
            3. if the source code line contains break lines,
               _get_var_names() **cannot handle it**. we have to return a bad
               result (-> None)

        NOTE: This method will slow down the process, please use it as less as
            possible.
        """
        if not raw_line.startswith('lk.log'):
            if x := re.compile(r'lk\.log.+').findall(raw_line):
                raw_line = x[0]
            else:
                return None
        return self._ast_analyser.main(raw_line)


def _simple_timestamp(style='y-m-d h:n:s', ctime=0.0) -> str:
    """ 生成时间戳.

    转换关系:
        year  : %Y
        month : %m
        day   : %d
        hour  : %H
        minute: %M
        second: %S

    E.g. 'y-m-d h:n:s' -> '2018-12-27 15:13:45'
    """
    style = style \
        .replace('y', '%Y').replace('m', '%m').replace('d', '%d') \
        .replace('h', '%H').replace('n', '%M').replace('s', '%S')
    if ctime:
        return time.strftime(style, time.localtime(ctime))
    else:
        return time.strftime(style)


lk = LKLogger()
