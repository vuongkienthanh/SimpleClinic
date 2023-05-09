from paths import DEFAULT_CONFIG_PATH, CONFIG_PATH
import json
import shutil
from typing import Any
from collections import namedtuple
from dataclasses import dataclass


Color = namedtuple("Color", (r, g, b))


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
    maximize_at_start: bool
    background_color: dict[str, Color]


def get_config_json() -> dict[str, Any]:
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


def get_config():
    config_json = get_config_json()
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
        maximize_at_start=config_json["maximize_at_start"],
        background_color={
            name: Color(r, g, b)
            for (name, [r, g, b]) in config_json["background_color"]
        },
    )


config = get_config_json()
