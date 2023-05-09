import datetime as dt
import enum
from dataclasses import dataclass
import dataclasses
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
    Base Abstract Class for derived sql table
    - `table_name`: name of table in sqlite database
    - `not_in_fields`: names of fields that are not returned by classmethod fields()
    """

    table_name: ClassVar[str]
    not_in_fields: ClassVar[list[str]]
    id: int

    @classmethod
    def parse(cls, row: Mapping[str, Any]):
        """
        Return the BASE object from a mapping with no conversion
        """
        return cls(**row)

    @classmethod
    def fields(cls) -> tuple[str]:
        return tuple(
            (f.name for f in dataclasses.fields(cls) if f.name not in cls.not_in_fields)
        )

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

    table_name = "patients"
    not_in_fields = ["id"]
    id: int
    name: str
    gender: Gender
    birthdate: dt.date
    address: str | None = None
    phone: str | None = None
    past_history: str | None = None


@dataclass(slots=True)
class QueueList(BASE):
    """Lượt chờ khám"""

    table_name = "queuelist"
    not_in_fields = ["id", "added_datetime"]
    id: int
    added_datetime: dt.datetime
    patient_id: int


@dataclass(slots=True)
class SeenList(BASE):
    """Danh sách đã khám hôm nay"""

    table_name = "seenlist"
    not_in_fields = ["id"]
    id: int
    patient_id: int


@dataclass(slots=True)
class AppointmentList(BASE):
    """Danh sách hẹn tái khám"""

    table_name = "appointmentlist"
    not_in_fields = ["id"]
    id: int
    appointed_date: dt.date
    patient_id: int


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

    table_name = "visits"
    not_in_fields = ["id", "exam_datetime"]
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

    table_name = "linedrugs"
    not_in_fields = ["id"]
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

    table_name = "warehouse"
    not_in_fields = ["id"]
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

    table_name = "sampleprescription"
    not_in_fields = ["id"]
    id: int
    name: str


@dataclass(slots=True)
class LineSamplePrescription(BASE):
    """Thuốc trong toa mẫu
    - `times`: Liều một cữ
    - `dose`: Số cữ
    """

    table_name = "linesampleprescription"
    not_in_fields = ["id"]
    id: int
    drug_id: int
    sample_id: int
    times: int
    dose: str


@dataclass(slots=True)
class Procedure(BASE):
    """Thủ thuật"""

    table_name = "procedures"
    not_in_fields = ["id"]
    id: int
    name: str
    price: int


@dataclass(slots=True)
class LineProcedure(BASE):
    """Thủ thuật của lượt khám"""

    table_name = "lineprocedure"
    not_in_fields = ["id"]
    id: int
    procedure_id: int
    visit_id: int


T = TypeVar("T", bound="BASE")


create_table_sql = f"""
CREATE TABLE IF NOT EXISTS {Patient.table_name} (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  gender GENDER NOT NULL,
  birthdate DATE NOT NULL,
  address TEXT,
  phone TEXT,
  past_history TEXT
);

CREATE TABLE IF NOT EXISTS last_open_date (
    last_open_date DATE
);

CREATE TABLE IF NOT EXISTS {QueueList.table_name} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    return added_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY (patient_id)
      REFERENCES {Patient.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS {SeenList.table_name} (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (patient_id)
      REFERENCES {Patient.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS {AppointmentList.table_name} (
    id INTEGER PRIMARY KEY,
    appointed_date DATE NOT NULL,
    patient_id INTEGER UNIQUE NOT NULL,
    FOREIGN KEY (patient_id)
      REFERENCES {Patient.table_name} (id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS patient_name
  ON {Patient.table_name} (name);


CREATE TABLE IF NOT EXISTS {Visit.table_name} (
  id INTEGER PRIMARY KEY,
  exam_datetime TIMESTAMP DEFAULT (datetime('now', 'localtime')),
  diagnosis TEXT NOT NULL,
  weight DECIMAL NOT NULL,
  days INTEGER NOT NULL,
  recheck INTEGER NOT NULL,
  patient_id INTEGER NOT NULL,
  vnote TEXT,
  follow TEXT,
  FOREIGN KEY (patient_id)
    REFERENCES {Patient.table_name} (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  CHECK (days >= 0 AND weight >=0 )
);

CREATE TABLE IF NOT EXISTS {Warehouse.table_name} (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  element TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  usage_unit TEXT NOT NULL,
  usage TEXT NOT NULL,
  sale_unit TEXT,
  purchase_price INTEGER NOT NULL,
  sale_price INTEGER NOT NULL,
  expire_date DATE,
  made_by TEXT,
  note TEXT,
  CONSTRAINT shortage_of_warehouse
    CHECK ( quantity >= 0 ),
  CONSTRAINT price_check 
    CHECK (( sale_price >= purchase_price) AND (purchase_price >= 0))
);

CREATE INDEX IF NOT EXISTS drug_name
  ON {Warehouse.table_name} (name);
CREATE INDEX IF NOT EXISTS drug_element 
  ON {Warehouse.table_name} (element);

CREATE TABLE IF NOT EXISTS {LineDrug.table_name} (
  id INTEGER PRIMARY KEY,
  drug_id INTEGER NOT NULL,
  times INTEGER NOT NULL,
  dose TEXT NOT NULL,
  quantity INTEGER NOT NULL,
  visit_id INTEGER NOT NULL,
  note TEXT,
  FOREIGN KEY (visit_id)
    REFERENCES {Visit.table_name} (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  FOREIGN KEY (drug_id)
    REFERENCES {Warehouse.table_name} (id)
      ON DELETE RESTRICT
      ON UPDATE NO ACTION,
  CHECK ( quantity > 0 AND times > 0 AND dose != '')
);

CREATE TABLE IF NOT EXISTS {SamplePrescription.table_name} (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS {LineSamplePrescription.table_name} (
  id INTEGER PRIMARY KEY,
  drug_id INTEGER NOT NULL,
  sample_id INTEGER NOT NULL,
  times INTEGER NOT NULL,
  dose TEXT NOT NULL,
  FOREIGN KEY (drug_id)
    REFERENCES {Warehouse.table_name} (id)
      ON DELETE RESTRICT
      ON UPDATE NO ACTION,
  FOREIGN KEY (sample_id)
    REFERENCES {SamplePrescription.table_name} (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  CHECK (times > 0 AND dose != ''),
  UNIQUE (drug_id, sample_id)
);

CREATE TABLE IF NOT EXISTS {Procedure.table_name} (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  price INTEGER NOT NULL,
  CONSTRAINT price_check 
    CHECK (price >= 0)
);

CREATE INDEX IF NOT EXISTS procedure_name
  ON {Procedure.table_name} (name);

CREATE TABLE IF NOT EXISTS {LineProcedure.table_name} (
  id INTEGER PRIMARY KEY,
  procedure_id INTEGER NOT NULL,
  visit_id INTEGER NOT NULL,
  FOREIGN KEY (visit_id)
    REFERENCES {Visit.table_name} (id)
      ON DELETE CASCADE
      ON UPDATE CASCADE,
  FOREIGN KEY (procedure_id)
    REFERENCES {Procedure.table_name} (id)
      ON DELETE RESTRICT
      ON UPDATE NO ACTION
);

CREATE TRIGGER IF NOT EXISTS linedrug_insert 
BEFORE INSERT ON {LineDrug.table_name}
BEGIN
UPDATE {Warehouse.table_name} SET quantity = quantity - NEW.quantity
WHERE id = NEW.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_delete
BEFORE DELETE ON {LineDrug.table_name}
BEGIN
UPDATE {Warehouse.table_name} SET quantity = quantity + OLD.quantity
WHERE id = OLD.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS linedrug_update
BEFORE UPDATE ON {LineDrug.table_name}
WHEN NEW.drug_id = OLD.drug_id
BEGIN
UPDATE {Warehouse.table_name} SET quantity = quantity + OLD.quantity - NEW.quantity
WHERE id = OLD.drug_id;
END;

CREATE TRIGGER IF NOT EXISTS visit_insert
BEFORE INSERT ON {Visit.table_name}
BEGIN
DELETE FROM {QueueList.table_name} WHERE patient_id = NEW.patient_id;
END;
"""
