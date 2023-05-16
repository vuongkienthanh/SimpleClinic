import datetime as dt
from fractions import Fraction
from itertools import cycle
from math import ceil
from misc import Config


def bd_to_vn_age(bd: dt.date) -> str:
    today = dt.date.today()
    delta = (today - bd).days
    match delta:
        case d if d <= 60:
            return f"{d} ngày tuổi"
        case d if d <= (30 * 24):
            return f"{d // 30} tháng tuổi"
        case _:
            return f"{today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))} tuổi"


def check_blank_to_none(val: str) -> str | None:
    match val.strip():
        case "":
            return None
        case v:
            return v


def check_none_to_blank(val: str | None) -> str:
    match val:
        case None:
            return ""
        case v:
            return v.strip()


def note_str(usage: str, times: int | str, dose: str, usage_unit: str,note:str | None) -> str:
    match note:
        case None: return f"{usage} ngày {times} lần, lần {dose} {usage_unit}"
        case n: return n


def sale_unit_str(sale_unit: str | None, usage_unit: str) -> str:
    match sale_unit:
        case None:
            return usage_unit
        case str(v):
            return v


def times_dose_quantity_note_str(
    usage: str,
    times: int | str,
    dose: str,
    quantity: int,
    usage_unit: str,
    sale_unit: str | None,
    note:str | None
) -> tuple[str, str, str, str]:
    return (
        str(times),
        f"{dose} {usage_unit}",
        f"{quantity} {sale_unit_str(sale_unit, usage_unit)}",
        note_str(usage, times, dose, usage_unit,note),
    )


def calc_quantity(
    times: int, dose: str, days: int, sale_unit: str | None, config: Config
) -> int:
    def calc(times: int, dose: str, days: int) -> int:
        if "/" in dose:
            numer, denom = [int(i) for i in dose.split("/")]
            return ceil(times * Fraction(numer, denom) * days)
        else:
            return ceil(times * float(dose) * days)

    if sale_unit is not None:
        if sale_unit.casefold() in (
            item.casefold() for item in config.single_sale_units
        ):
            return 1
        else:
            return calc(times, dose, days)
    else:
        return calc(times, dose, days)


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
