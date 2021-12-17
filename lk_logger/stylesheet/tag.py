from .style import Style


class BaseTag(Style):
    template = '[{level}-{hh}:{nn}:{ss}]'  # e.g. '[D-17:45:23]'
    #   placeholders:
    #       level:
    #           options:
    #               D, DEBUG
    #               I, INFO
    #               W, WARNING
    #               E, ERROR
    #               C, CRITICAL
    #           DIWEC is the built-in levels. you can use any string as level.
    #           the built-in levels have predefined colors in Tag.color_sheet.
    #           you may need to extend it to support your own levels. (see also
    #           Tag.color_sheet)
    #       yyyy: full year
    #       mm: full month, 01 - 12
    #       dd: full day, 01 - 31
    #       hh: full hour, 00 - 23
    #       nn: full minute, 00 - 59
    #       ss: full second, 00 - 59
    #       no: number, starts from 1, auto increased in current session. reset
    #           when restart program.
    
    color_mode = 'auto'  # 'auto', 'light', 'dark'
    color_range = 'full'  # 'full', 'head', 'body'
    color_sheet = {
        'auto': {
            # below colors are both suitable for light and dark mode.
            # see illustration: '/.assets/20211217173919.png'.
            'D, DEBUG'   : '#A7A7A7',  # gray
            'I, INFO'    : '#4E55E1',  # soft blue
            'W, WARNING' : '#E3A61A',  # orange
            'E, ERROR'   : '#E31A6D',  # heavy pink
            'C, CRITICAL': '#E31A6D',  # heavy pink
        }
    }
    
    def __init__(self, placeholders: list):
        pass
    
    def render(self, text: str) -> str:
        raise NotImplementedError


class TagForPycharmConsole(BaseTag):
    
    def render(self, text: str) -> str:
        if self.color_range == 'full':
            pass
        
    
