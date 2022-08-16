from paths import DEFAULT_CONFIG_PATH, CONFIG_PATH
import json
import shutil
import wx
from typing import Any


def get_config() -> dict[str, Any]:
    try:
        with (
            open(CONFIG_PATH, "r", encoding="utf-8") as f1,
            open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f2,
        ):
            config = json.load(f1)
            default = json.load(f2)
            config = {k: v for k, v in config.items() if k in default.keys()}
            return default | config
    except FileNotFoundError:
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
            shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
            return json.load(f)
    except json.JSONDecodeError:
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)


config = get_config()

# some size
w: tuple[int, int] = wx.DisplaySize()[0]


def size(p):
    return round(w * p * config["listctrl_header_scale"])


def tsize(p):
    return (size(p), -1)


# keycode
# back, del, home, end, left,right
k_special: tuple[int, ...] = (8, 314, 316, 127, 313, 312)
k_number: tuple[int, ...] = tuple(range(48, 58))
k_decimal: tuple[int] = (46,)
k_hash: tuple[int] = (35,)
k_slash: tuple[int] = (47,)
k_tab: tuple[int] = (9,)
