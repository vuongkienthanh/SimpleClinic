import datetime as dt
import enum
from dataclasses import dataclass
from typing import ClassVar, TypeVar
from decimal import Decimal
from typing import Any
from collections.abc import Mapping


class Gender(enum.Enum):
    m = 0
    f = 1

    def __str__(self):
        return ["Nam", "Nữ"][self.value]


@dataclass
class BASE:
    """
    Base Class for derived sql table
    - `__table_name__`: name of table in sqlite database
    - `__match_args__`: names of fields for sql query
    """

    __tablename__: ClassVar[str]
    __match_args__: ClassVar[list[str]]
    id: int

    @classmethod
    def parse(cls, row: Mapping[str, Any]):
        return cls(**row)

    @classmethod
    def fields(cls) -> list[str]:
        return cls.__match_args__

    @classmethod
    def commna_joined_field_names(cls) -> str:
        return ",".join(cls.fields())

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
    """Bệnh nhân"""

    __tablename__ = "patients"
    __match_args__ = [
        "name",
        "gender",
        "birthdate",
        "address",
        "phone",
        "past_history",
    ]
    id: int
    name: str
    gender: Gender
    birthdate: dt.date
    address: str | None = None
    phone: str | None = None
    past_history: str | None = None


@dataclass(slots=True)
class Queue(BASE):
    """Lượt chờ khám"""

    __tablename__ = "queue"
    __match_args__ = ["patient_id"]
    id: int
    patient_id: int
    added_datetime: dt.datetime


@dataclass(slots=True)
class SeenToday(BASE):
    """Danh sách đã khám hôm nay"""

    __tablename__ = "seen_today"
    __match_args__ = ["patient_id", "visit_id"]
    id: int
    patient_id: int
    visit_id: int


@dataclass(slots=True)
class Appointment(BASE):
    """Danh sách hẹn tái khám"""

    __tablename__ = "appointments"
    __match_args__ = ["patient_id", "appointed_date"]
    id: int
    patient_id: int
    appointed_date: dt.date


@dataclass(slots=True)
class Visit(BASE):
    """Lượt khám
    - `exam_datetime`: Thời điểm khám bệnh
    - `diagnoses`: Chẩn đoán
    - `weight`: Cân nặng
    - `days`: Số ngày cho thuốc
    - `recheck`: Số ngày tái khám
    - `patient_id`: Mã bệnh nhân
    - `follow`: Lời dặn dò
    - `vnote`: Bệnh sử
    """

    __tablename__ = "visits"
    __match_args__ = [
        "diagnosis",
        "weight",
        "days",
        "recheck",
        "patient_id",
        "follow",
        "vnote",
    ]
    id: int
    exam_datetime: dt.datetime
    diagnosis: str
    weight: Decimal
    days: int
    recheck: int
    patient_id: int
    follow: str | None = None
    vnote: str | None = None


@dataclass(slots=True)
class LineDrug(BASE):
    """Thuốc trong toa
    - `drug_id`: Mã thuốc
    - `dose`: Liều một cữ
    - `times`: Số cữ
    - `quantity`: Số lượng
    """

    __tablename__ = "linedrugs"
    __match_args__ = [
        "drug_id",
        "dose",
        "times",
        "quantity",
        "visit_id",
        "note",
    ]

    id: int
    drug_id: int
    dose: str
    times: int
    quantity: int
    visit_id: int
    note: str | None = None


@dataclass(slots=True)
class Warehouse(BASE):
    """Thuốc trong kho
    - `name`: Tên thuốc
    - `element`: Thành phần thuốc
    - `quantity`: Số lượng
    - `usage_unit`: Đơn vị sử dụng
    - `usage`: Cách sử dụng
    - `purchase_price`: Giá mua
    - `sale_price`: Giá bán
    - `sale_unit`: Đơn vị bán
    - `expire_date`: Ngày hết hạn
    - `made_by`: Xuất xứ
    - `note`: Ghi chú
    """

    __tablename__ = "warehouse"
    __match_args__ = [
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
        "note",
    ]
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
    note: str | None = None


@dataclass(slots=True)
class SamplePrescription(BASE):
    """Toa mẫu"""

    __tablename__ = "sampleprescription"
    __match_args__ = ["name"]
    id: int
    name: str


@dataclass(slots=True)
class LineSamplePrescription(BASE):
    """Thuốc trong toa mẫu
    - `times`: Liều một cữ
    - `dose`: Số cữ
    """

    __tablename__ = "linesampleprescription"
    __match_args__ = [
        "drug_id",
        "sample_id",
        "times",
        "dose",
    ]
    id: int
    drug_id: int
    sample_id: int
    times: int
    dose: str


@dataclass(slots=True)
class Procedure(BASE):
    """Danh sách thủ thuật"""

    __tablename__ = "procedures"
    __match_args__ = ["name", "price"]
    id: int
    name: str
    price: int


@dataclass(slots=True)
class LineProcedure(BASE):
    """Thủ thuật của lượt khám"""

    __tablename__ = "lineprocedure"
    __match_args__ = ["procedure_id", "visit_id"]
    id: int
    procedure_id: int
    visit_id: int


T = TypeVar("T", bound="BASE")
