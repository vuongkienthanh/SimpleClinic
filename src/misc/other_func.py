import datetime as dt
from fractions import Fraction
from functools import cache
from math import ceil

from misc.config import Config


@cache
def bd_to_vn_age(bd: dt.date) -> str:
    today = dt.date.today()
    delta = (today - bd).days
    match delta:
        case d if d <= 60:
            return f"{d} ngày tuổi"
        case d if d <= (30 * 24):
            return f"{d // 30} tháng tuổi"
        case _:
            s = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            return f"{s} tuổi"


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


def note_str_from_db(
    usage: str, times: int | str, dose: str, usage_unit: str, note: str | None
) -> str:
    match note:
        case None:
            return f"ngày {usage} {times} lần, lần {dose} {usage_unit}"
        case n:
            return n


def note_str_to_db(
    usage: str, times: int | str, dose: str, usage_unit: str, note: str
) -> str | None:
    match note.strip():
        case "":
            return None
        case n if n == f"ngày {usage} {times} lần, lần {dose} {usage_unit}":
            return None
        case n:
            return n


def sale_unit_from_db(sale_unit: str | None, usage_unit: str) -> str:
    match sale_unit:
        case None:
            return usage_unit
        case str(v):
            return v


def sale_unit_to_db(sale_unit: str, usage_unit: str) -> str | None:
    match sale_unit.strip():
        case "":
            return None
        case s if s == usage_unit.strip():
            return None
        case s:
            return s


@cache
def times_dose_quantity_note_str(
    usage: str,
    times: int | str,
    dose: str,
    quantity: int,
    usage_unit: str,
    sale_unit: str | None,
    note: str | None,
) -> tuple[str, str, str, str]:
    return (
        str(times),
        f"{dose} {usage_unit}",
        f"{quantity} {sale_unit_from_db(sale_unit, usage_unit)}",
        note_str_from_db(usage, times, dose, usage_unit, note),
    )


@cache
def calc_quantity(
    times: int, dose: str, days: int, sale_unit: str | None, config: Config
) -> int:
    def calc(times: int, dose: str, days: int) -> int:
        if "/" in dose:
            try:
                numer, denom = [int(i) for i in dose.split("/")]
                return ceil(times * Fraction(numer, denom) * days)
            except Exception:
                return 0
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


def num_to_str_price(price: int | None) -> str:
    match price:
        case None:
            return "0"
        case _:
            return f"{price:,}"


def str_to_int_price(price: str) -> int:
    return int(price.replace(",", ""))


def vn_weekdays(d: int) -> str:
    today = dt.date.today()
    target = today + dt.timedelta(days=d)
    wd = target.weekday()
    match wd:
        case 0:
            return "Thứ hai"
        case 1:
            return "Thứ ba"
        case 2:
            return "Thứ tư"
        case 3:
            return "Thứ năm"
        case 4:
            return "Thứ sáu"
        case 5:
            return "Thứ bảy"
        case 6:
            return "Chủ nhật"
        case _:
            raise IndexError("wrong date")
