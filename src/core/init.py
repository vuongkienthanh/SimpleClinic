import wx
from config import Config


config = Config.load()

# some size
w: tuple[int, int] = wx.DisplaySize()[0]


def size(p):
    return round(w * p * config.listctrl_header_scale)


def tsize(p):
    return (size(p), -1)


# keycode
# back, del, home, end, left,right
k_special: tuple[int, ...] = (8, 314, 316, 127, 313, 312)
k_number: tuple[int, ...] = tuple(range(48, 58))
k_decimal: tuple[int,] = (46,)
k_hash: tuple[int,] = (35,)
k_slash: tuple[int,] = (47,)
k_tab: tuple[int,] = (9,)
