import datetime as dt
import enum
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, ClassVar, Self, TypeVar


class Gender(enum.Enum):
    m = 0
    f = 1

    def __str__(self):
        match self.value:
            case 0:
                return "Nam"
            case 1:
                return "Nữ"

    @classmethod
    def from_str(cls, s: str) -> Self:
        match s:
            case "Nam":
                return Gender.m
            case "Nữ":
                return Gender.f
            case _:
                raise IndexError("Invalid gender string")


class BASE:
    """
    Base Class for derived sql table
    - `__table_name__`: name of table in sqlite database
    - `__fields__`: names of fields for sql query insert/update
    - `__extra_fields__`: names of extra fields for sql query select
    """

    __tablename__: ClassVar[str]
    __fields__: ClassVar[tuple[str, ...]]
    __extra_fields__: ClassVar[tuple[str, ...]] = ()
    id: int

    @classmethod
    def parse(cls, row: Mapping[str, Any]) -> Self:
        return cls(**row)

    @classmethod
    def fields(cls) -> tuple[str, ...]:
        return cls.__fields__

    @classmethod
    def select_fields(cls) -> tuple[str, ...]:
        return cls.__fields__ + cls.__extra_fields__

    @classmethod
    def commna_joined_fields(cls) -> str:
        return ",".join(cls.fields())

    @classmethod
    def commna_joined_select_fields(cls) -> str:
        return ",".join(cls.select_fields())

    @classmethod
    def qmark_style_placeholders(cls) -> str:
        num_of_qmark = len(cls.fields())
        return ",".join(["?"] * num_of_qmark)

    @classmethod
    def named_style_placeholders(cls) -> str:
        return ",".join([f":{f}" for f in cls.fields()])

    def qmark_style_sql_params(self) -> tuple:
        return tuple((getattr(self, field) for field in self.fields()))

    def named_style_sql_params(self) -> dict[str, Any]:
        return {field: getattr(self, field) for field in self.fields()}


@dataclass(slots=True)
class Patient(BASE):
    "Bệnh nhân"

    __tablename__ = "patients"
    __fields__ = (
        "name",
        "gender",
        "birthdate",
        "address",
        "phone",
        "past_history",
    )
    id: int
    name: str
    gender: Gender
    birthdate: dt.date
    address: str | None = None
    phone: str | None = None
    past_history: str | None = None


@dataclass(slots=True)
class Queue(BASE):
    "Lượt chờ khám"

    __tablename__ = "queue"
    __fields__ = ("patient_id",)
    __extra_fields__ = ("added_datetime",)
    id: int
    patient_id: int
    added_datetime: dt.datetime


@dataclass(slots=True)
class SeenToday(BASE):
    "Danh sách đã khám hôm nay"

    __tablename__ = "seen_today"
    __fields__ = ("patient_id", "visit_id")
    id: int
    patient_id: int
    visit_id: int


@dataclass(slots=True)
class Appointment(BASE):
    "Danh sách hẹn tái khám"

    __tablename__ = "appointment"
    __fields__ = ("patient_id", "appointed_date")
    id: int
    patient_id: int
    appointed_date: dt.date


@dataclass(slots=True)
class Visit(BASE):
    "Lượt khám"

    __tablename__ = "visits"
    __fields__ = (
        "diagnosis",
        "weight",
        "days",
        "recheck",
        "price",
        "patient_id",
        "follow",
        "vnote",
        "temperature",
        "height",
    )
    __extra_fields__ = ("exam_datetime",)
    id: int
    exam_datetime: dt.datetime
    diagnosis: str
    weight: int
    days: int
    recheck: int
    price: int
    patient_id: int
    vnote: str | None = None
    follow: str | None = None
    temperature: int | None = None
    height: int | None = None


@dataclass(slots=True)
class LineDrug(BASE):
    "Thuốc trong toa"

    __tablename__ = "linedrugs"
    __fields__ = (
        "warehouse_id",
        "times",
        "dose",
        "quantity",
        "visit_id",
        "outclinic",
        "usage_note",
    )
    id: int
    warehouse_id: int
    times: int
    dose: str
    quantity: int
    visit_id: int
    outclinic: bool
    usage_note: str | None = None


@dataclass(slots=True)
class Warehouse(BASE):
    "Thuốc trong kho"

    __tablename__ = "warehouse"
    __fields__ = (
        "name",
        "element",
        "quantity",
        "usage_unit",
        "usage",
        "purchase_price",
        "sale_price",
        "sale_unit",
        "expire_date",
        "made_by",
        "drug_note",
    )
    id: int
    name: str
    element: str
    quantity: int
    usage_unit: str
    usage: str
    purchase_price: int
    sale_price: int
    sale_unit: str | None = None
    expire_date: dt.date | None = None
    made_by: str | None = None
    drug_note: str | None = None


@dataclass(slots=True)
class SamplePrescription(BASE):
    "Toa mẫu"

    __tablename__ = "sampleprescriptions"
    __fields__ = ("name",)
    id: int
    name: str


@dataclass(slots=True)
class LineSamplePrescription(BASE):
    "Thuốc trong toa mẫu"

    __tablename__ = "linesampleprescriptions"
    __fields__ = (
        "warehouse_id",
        "sample_id",
        "times",
        "dose",
    )
    id: int
    warehouse_id: int
    sample_id: int
    times: int
    dose: str


@dataclass(slots=True)
class Procedure(BASE):
    "Danh sách thủ thuật"

    __tablename__ = "procedures"
    __fields__ = ("name", "price")
    id: int
    name: str
    price: int


@dataclass(slots=True)
class LineProcedure(BASE):
    "Thủ thuật của lượt khám"

    __tablename__ = "lineprocedures"
    __fields__ = ("procedure_id", "visit_id")
    id: int
    procedure_id: int
    visit_id: int


T = TypeVar("T", bound="BASE")
