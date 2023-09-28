import dataclasses
import datetime as dt
import json
import shutil
from collections import namedtuple
from dataclasses import dataclass
from typing import Any, Self, TypedDict

import wx

from misc.paths import CONFIG_PATH, DEFAULT_CONFIG_PATH

drug_name_print_style_choices = ["Tên", "Thành phần", "Tên(thành phần)", "Thành phần(tên)"]
recheck_date_print_style_choices = ["sau x ngày", "vào ngày dd/mm/yyyy"]

Color = namedtuple("Color", ["r", "g", "b"])


class Format(TypedDict):
    bold: bool
    italic: bool


@dataclass(eq=False, repr=False, kw_only=True)
class Config:
    clinic_name: str
    clinic_address: str
    clinic_phone_number: str
    doctor_name: str
    checkup_price: int
    default_days_for_prescription: int
    minimum_drug_quantity_alert: int
    single_sale_units: list[str]
    app_font_size: int
    autochange_prescription_quantity_on_day_spin: bool
    ask_print: bool
    display_recent_visit_count: int
    maximize_at_start: bool
    outclinic_drug_checkbox: bool
    listctrl_header_scale: int
    print_scale: int
    preview_scale: int
    drug_name_print_style: int
    recheck_date_print_style: int
    background_colors: dict[str, Color]

    @classmethod
    def load(cls) -> Self:
        config_json: dict[str, Any]
        try:
            with (
                open(CONFIG_PATH, "r", encoding="utf-8") as f1,
                open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f2,
            ):
                config = json.load(f1)
                default = json.load(f2)
                config = {k: v for k, v in config.items() if k in default.keys()}
                config_json = default | config
        except FileNotFoundError:
            with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)
                config_json = json.load(f)
        except json.JSONDecodeError:
            with open(DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
                config_json = json.load(f)
        return Config(
            clinic_name=config_json["clinic_name"],
            clinic_address=config_json["clinic_address"],
            clinic_phone_number=config_json["clinic_phone_number"],
            doctor_name=config_json["doctor_name"],
            checkup_price=config_json["checkup_price"],
            default_days_for_prescription=config_json["default_days_for_prescription"],
            minimum_drug_quantity_alert=config_json["minimum_drug_quantity_alert"],
            single_sale_units=config_json["single_sale_units"],
            app_font_size=config_json["app_font_size"],
            autochange_prescription_quantity_on_day_spin=config_json[
                "autochange_prescription_quantity_on_day_spin"
            ],
            ask_print=config_json["ask_print"],
            display_recent_visit_count=config_json["display_recent_visit_count"],
            maximize_at_start=config_json["maximize_at_start"],
            outclinic_drug_checkbox=config_json["outclinic_drug_checkbox"],
            listctrl_header_scale=config_json["listctrl_header_scale"],
            print_scale=config_json["print_scale"],
            preview_scale=config_json["preview_scale"],
            drug_name_print_style=max(
                min(
                    config_json["drug_name_print_style"],
                    len(drug_name_print_style_choices),
                ),
                0,
            ),
            recheck_date_print_style=max(
                min(
                    config_json["recheck_date_print_style"],
                    len(recheck_date_print_style_choices),
                ),
                0,
            ),
            background_colors={
                name: Color(r, g, b)
                for (name, [r, g, b]) in config_json["background_colors"].items()
            },
        )

    def dump(self):
        config_json = dataclasses.asdict(self)
        with open(CONFIG_PATH, mode="w", encoding="utf-8") as f:
            json.dump(config_json, f, ensure_ascii=False, indent=4)

    @staticmethod
    def reset():
        bak = CONFIG_PATH + dt.datetime.now().strftime("%Y_%m_%d_%H_%M_%S") + ".bak"
        shutil.copyfile(CONFIG_PATH, bak)
        shutil.copyfile(DEFAULT_CONFIG_PATH, CONFIG_PATH)

    def header_width(self, p: float) -> int:
        w: int = wx.DisplaySize()[0]
        return round(w * p * self.listctrl_header_scale)

    def header_size(self, p: float) -> tuple[int, int]:
        return (self.header_width(p), -1)

    def get_background_color(self, name: str) -> wx.Colour:
        try:
            return wx.Colour(*self.background_colors[name])
        except KeyError:
            return wx.Colour(255, 255, 255)
