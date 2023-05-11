from misc.paths import DEFAULT_CONFIG_PATH, CONFIG_PATH
import json
import shutil
from typing import Any
from collections import namedtuple
from dataclasses import dataclass
import dataclasses
import datetime as dt
from wx import DisplaySize, Colour


Color = namedtuple("Color", ["r", "g", "b"])


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class Config:
    clinic_name: str
    doctor_name: str
    clinic_address: str
    clinic_phone_number: str
    checkup_price: int
    default_days_for_prescription: int
    minimum_drug_quantity_alert: int
    single_sale_units: list[str]
    follow_choices: dict[str, str]
    ask_print: bool
    print_price: bool
    number_of_drugs_in_one_page: int
    display_recent_visit_count: int
    print_scale: int
    preview_scale: int
    maximize_at_start: bool
    listctrl_header_scale: int
    background_color: dict[str, Color]

    @classmethod
    def load(cls) -> "Config":
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
            doctor_name=config_json["doctor_name"],
            clinic_address=config_json["clinic_address"],
            clinic_phone_number=config_json["clinic_phone_number"],
            checkup_price=config_json["checkup_price"],
            default_days_for_prescription=config_json["default_days_for_prescription"],
            minimum_drug_quantity_alert=config_json["minimum_drug_quantity_alert"],
            single_sale_units=config_json["single_sale_units"],
            follow_choices=config_json["follow_choices"],
            ask_print=config_json["ask_print"],
            print_price=config_json["print_price"],
            number_of_drugs_in_one_page=config_json["number_of_drugs_in_one_page"],
            display_recent_visit_count=config_json["display_recent_visit_count"],
            print_scale=config_json["print_scale"],
            preview_scale=config_json["preview_scale"],
            maximize_at_start=config_json["maximize_at_start"],
            listctrl_header_scale=config_json["listctrl_header_scale"],
            background_color={
                name: Color(r, g, b)
                for (name, [r, g, b]) in config_json["background_color"].items()
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
        w: int = DisplaySize()[0]
        return round(w * p * self.listctrl_header_scale)

    def header_size(self, p: float) -> tuple[int, int]:
        return (self.header_width(p), -1)

    def get_background_color(self, name: str) -> Colour:
        try:
            return Colour(*self.background_color[name])
        except KeyError:
            return Colour(255, 255, 255)
