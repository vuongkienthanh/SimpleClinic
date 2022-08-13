from paths import DEFAULT_CONFIG_PATH, CONFIG_PATH
import wx
import datetime as dt
from fractions import Fraction
from typing import Any, TypeVar
from itertools import cycle
import json
from math import ceil
import shutil


def get_config() -> dict[str, Any]:
    try:
        with (
            open(CONFIG_PATH, "r", encoding="utf-8") as f1,
            open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f2
        ):
            return json.load(f1) | json.load(f2)
    except FileNotFoundError:
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
            shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
            return json.load(f)
    except json.JSONDecodeError:
        with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)


def bd_to_age(bd: dt.date):
    today = dt.date.today()
    delta = (today - bd).days
    if delta <= 60:
        age = f'{delta} ngày tuổi'
    elif delta <= (30 * 24):
        age = f'{int(delta / 30)} tháng tuổi'
    else:
        age = f'{today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))} tuổi'
    return age


def get_usage_note_str(usage, times, dose, usage_unit):
    return f"{usage} ngày {times} lần, lần {dose} {usage_unit}"


def check_blank(val: str):
    return None if val.strip() == '' else val.strip()


def check_none(val: Any | None):
    return str(val) if val else ''


def calc_quantity(times: int, dose: str, days: int, sale_unit: str | None, list_of_unit: list[str]) -> int | None:
    def calc(times: int, dose: str, days: int) -> int:
        if '/' in dose:
            numer, denom = [int(i) for i in dose.split('/')]
            return ceil(times * Fraction(numer, denom) * days)
        else:
            return ceil(times * float(dose) * days)
    try:
        if sale_unit is not None:
            if sale_unit.casefold() in (item.casefold() for item in list_of_unit):
                return 1
            else:
                return calc(times, dose, days)
        else:
            return calc(times, dose, days)
    except Exception as e:
        return None


def num_to_str(price: int) -> str:
    """Return proper currency format str from int"""
    s = str(price)
    res = ''
    for char, cyc in zip(s[::-1], cycle(range(3))):
        res += char
        if cyc == 2:
            res += '.'
    else:
        if res[-1] == '.':
            res = res[:-1]
    return res[::-1]


TC = TypeVar('TC', bound=wx.TextCtrl)


def disable_text_ctrl(w: TC) -> TC:
    w.Disable()
    w.SetBackgroundColour(wx.Colour(168, 168, 168))
    w.SetForegroundColour(wx.Colour(0, 0, 0))
    return w
