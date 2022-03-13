from .style import Style


class BaseTag(Style):
    template: str  # e.g. '[D-17:45:23]'
    
    color_mode = 'auto'  # 'auto', 'light', 'dark'
    color_range = 'full'  # 'full', 'head', 'body'
    color_sheet = {
        'auto': {
            # below colors are both suitable for light and dark mode.
            # see screenshot: '/.assets/20211217173919.png'.
            'D, DEBUG'   : '#A7A7A7',  # gray
            'I, INFO'    : '#4E55E1',  # soft blue
            'W, WARNING' : '#E3A61A',  # orange
            'E, ERROR'   : '#E31A6D',  # heavy pink
            'C, CRITICAL': '#E31A6D',  # heavy pink
        }
    }
    
    def __init__(self, template='[{level}-{hh}:{nn}:{ss}] {text}'):
        self.template = template  # e.g. '[D-17:45:23]'
        #   placeholders:
        #       level:
        #           options:
        #               D, DEBUG
        #               I, INFO
        #               W, WARNING
        #               E, ERROR
        #               C, CRITICAL
        #           DIWEC is the built-in levels. you can use any string as
        #           level. the built-in levels have predefined colors in
        #           Tag.color_sheet.
        #           you may need to extend it to support your own levels. (see
        #           also Tag.color_sheet)
        #       yyyy: full year
        #       mm: full month, 01 - 12
        #       dd: full day, 01 - 31
        #       hh: full hour, 00 - 23
        #       nn: full minute, 00 - 59
        #       ss: full second, 00 - 59
        #       no: number, starts from 1, auto increased in current session.
        #           reset when restart program.
        
    def render(self, *args, **kwargs) -> str:
        raise NotImplementedError


class TagForPycharmConsole(BaseTag):
    """
    note: currently `color_range` is not changable.
    """
    color_sheet = {
        'auto': {
            'D, DEBUG'   : 'cyan',
            'I, INFO'    : 'blue',
            'W, WARNING' : 'yellow',
            'E, ERROR'   : 'red',
            'C, CRITICAL': 'red',
        }
    }
    
    def __init__(self):
        super().__init__()
        self.color_palette = ColorPalette()
    
    def render(self, text: str, level: str) -> str:
        return self.color_palette.colorize(
            text, self.color_sheet['auto'][level]
        )


class ColorPalette:
    r""" README.zh.md
    
    ## 格式说明
    
    ```
    \033[<mode>;<fg>;<bg>m<text>\033[0m
    ```
    
    参数说明:
    
    ```
    \033        风格控制符
    <mode>      显示模式, 可选
    <fg>        前景色, 可选. pycharm 支持 8 种颜色, 分别用 30 ~ 37 表示
    <bg>        背景色, 可选. pycharm 支持 8 种颜色, 分别用 40 ~ 47 表示
    m           风格结束控制符
    <text>      要打印的文本
    \033[0m     将 \033, [, mode=0, m 连用, 可以恢复默认风格
    ```
    
    ## 说明事项
    
    - `\033` 不要使用 r-string.
    - 当前的颜色模式非常简单, 只支持用户自定义前景色. 详见本类的 format 方法.
    
    ## 参考链接
    
    - pycharm 控制台输出带颜色 https://blog.csdn.net/qq_46620129/article/details
      /112209898
    - https://stackoverflow.com/questions/287871/how-to-print-colored-text-to
      -the-terminal
    
    """
    start = '\033['
    end = 'm'
    mode = {
        'normal'   : '0',
        'bold'     : '1',
        'dim'      : '2',
        'italic'   : '3',
        'underline': '4',
        'blink'    : '5',
        'reverse'  : '7',
        'midden'   : '8',
    }
    foreground = {
        # note: in pycharm dark theme, the black and white are automatically
        #   swapped. you can consider all the following colors are in light
        #   theme, let ide to adjust them properly.
        'black' : '30',
        'red'   : '31',
        'green' : '32',
        'yellow': '33',
        'blue'  : '34',
        'purple': '35',
        'cyan'  : '36',
        'white' : '37',
    }
    background = {
        'black' : '40',
        'red'   : '41',
        'green' : '42',
        'yellow': '43',
        'blue'  : '44',
        'purple': '45',
        'cyan'  : '46',
        'white' : '47',
    }
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """
        see screenshot: /.assets/20211221173825.png
        """
        return '{start}{fg}{end}{text}{start}{normal}{end}'.format(
            start=cls.start,
            fg=cls.foreground[color],
            text=text,
            normal=cls.mode['normal'],
            end=cls.end,
        )
