import wx
import datetime as dt
from fractions import Fraction
from typing import Any, TypeVar
from itertools import cycle
from math import ceil


def get_background_color(s: str):
    from core.init import config

    try:
        return wx.Colour(*config["background_color"][s])
    except KeyError:
        return wx.Colour(255, 255, 255)


def bd_to_age(bd: dt.date):
    today = dt.date.today()
    delta = (today - bd).days
    if delta <= 60:
        age = f"{delta} ngày tuổi"
    elif delta <= (30 * 24):
        age = f"{int(delta / 30)} tháng tuổi"
    else:
        age = f"{today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))} tuổi"
    return age


def get_usage_note_str(usage, times, dose, usage_unit):
    return f"{usage} ngày {times} lần, lần {dose} {usage_unit}"


def check_blank(val: str):
    return None if val.strip() == "" else val.strip()


def check_none(val: Any | None):
    return str(val) if val else ""


def calc_quantity(
    times: int, dose: str, days: int, sale_unit: str | None
) -> int | None:
    def calc(times: int, dose: str, days: int) -> int:
        if "/" in dose:
            numer, denom = [int(i) for i in dose.split("/")]
            return ceil(times * Fraction(numer, denom) * days)
        else:
            return ceil(times * float(dose) * days)

    try:
        if sale_unit is not None:
            from core.init import config

            if sale_unit.casefold() in (
                item.casefold() for item in config["single_sale_units"]
            ):
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
    res = ""
    for char, cyc in zip(s[::-1], cycle(range(3))):
        res += char
        if cyc == 2:
            res += "."
    else:
        if res[-1] == ".":
            res = res[:-1]
    return res[::-1]


TC = TypeVar("TC", bound=wx.TextCtrl)
