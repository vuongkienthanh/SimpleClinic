import wx
import datetime as dt
from fractions import Fraction
from typing import Any, TypeVar
from itertools import cycle
from math import ceil
from misc import Config


def bd_to_vn_age(bd: dt.date) -> str:
    today = dt.date.today()
    delta = (today - bd).days
    if delta <= 60:
        age = f"{delta} ngày tuổi"
    elif delta <= (30 * 24):
        age = f"{int(delta / 30)} tháng tuổi"
    else:
        age = f"{today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))} tuổi"
    return age


def get_usage_note_str(usage: str, times: int, dose: str, usage_unit: str) -> str:
    return f"{usage} ngày {times} lần, lần {dose} {usage_unit}"


def check_blank_to_none(val: str) -> str | None:
    val = val.strip()
    return None if val == "" else val


def check_none_to_blank(val: Any | None) -> str:
    return str(val).strip() if val else ""


def calc_quantity(
        times: int, dose: str, days: int, sale_unit: str | None, config: Config
) -> int | None:
    def calc(times: int, dose: str, days: int) -> int:
        if "/" in dose:
            numer, denom = [int(i) for i in dose.split("/")]
            return ceil(times * Fraction(numer, denom) * days)
        else:
            return ceil(times * float(dose) * days)

    try:
        if sale_unit is not None:
            if sale_unit.casefold() in (
                item.casefold() for item in config.single_sale_units
            ):
                return 1
            else:
                return calc(times, dose, days)
        else:
            return calc(times, dose, days)
    except Exception as _:
        return None


def num_to_str_price(price: int) -> str:
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


def vn_weekdays(d: int):
    """
    0 -> Thứ hai
    1 -> Thứ ba
    2 -> Thứ tư
    3 -> Thứ năm
    4 -> Thứ sáu
    5 -> Thứ bảy
    6 -> Chủ nhật
    """
    today = dt.date.today()
    target = today + dt.timedelta(days=d)
    wd = target.weekday()
    vn = {
        0: "Thứ hai",
        1: "Thứ ba",
        2: "Thứ tư",
        3: "Thứ năm",
        4: "Thứ sáu",
        5: "Thứ bảy",
        6: "Chủ nhật",
    }
    return f"=>{vn[wd]}"


TC = TypeVar("TC", bound=wx.TextCtrl)
