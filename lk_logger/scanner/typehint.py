from typing import *

if __name__ == '__main__':
    from lk_logger.scanner.scanner import Match as _Match
    from lk_logger.scanner.scanner import Cursor as _Cursor
else:
    _Match = None
    _Cursor = None

TLine = str
TChar = str

TCursor = _Cursor
TPos = int
TStart = TPos
TEnd = TPos

TToken = int
TSymbols = List[Tuple[TPos, TChar, TToken]]

TMatch = _Match
TSpan = Tuple[TStart, TEnd]
TSpans = List[TSpan]

TMatches1 = Dict[TStart, TEnd]
TMatches2 = Dict[Tuple[TStart, TEnd], Dict]
