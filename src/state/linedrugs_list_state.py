from dataclasses import dataclass
import dataclasses
from . import main_state
from db import Connection, Visit, LineDrug, Warehouse
from misc import note_str


@dataclass(slots=True, match_args=False)
class LineDrugListStateItem:
    id: int
    drug_id: int
    name: str
    times: int
    dose: str
    quantity: int
    note: str | None
    usage: str
    usage_unit: str
    sale_unit: str | None
    sale_price: int

    def parse_note(self) -> str:
        match self.note:
            case None:
                return note_str(self.usage, self.times, self.dose, self.usage_unit)
            case s:
                return s.strip()

    def parse_sale_unit(self) -> str:
        match self.sale_unit:
            case None:
                return self.usage_unit
            case s:
                return s.strip()

    def parse(self) -> "ParsedLineDrugListStateItem":
        d = dataclasses.asdict(self)
        d.update({"note": self.parse_note(), "sale_unit": self.parse_sale_unit()})
        return ParsedLineDrugListStateItem(**d)


@dataclass(slots=True, match_args=False)
class ParsedLineDrugListStateItem:
    id: int
    drug_id: int
    name: str
    times: int
    dose: str
    quantity: int
    note: str
    usage: str
    usage_unit: str
    sale_unit: str
    sale_price: int

    def unparse_note(self) -> str | None:
        match self.note:
            case s if s == note_str(self.usage, self.times, self.dose, self.usage_unit):
                return None
            case s:
                return s.strip()

    def unparse_sale_unit(self) -> str | None:
        match self.sale_unit:
            case s if s == self.usage_unit:
                return None
            case s:
                return s.strip()

    def unparse(self) -> "LineDrugListStateItem":
        d = dataclasses.asdict(self)
        d.update({"note": self.unparse_note(), "sale_unit": self.unparse_sale_unit()})
        return LineDrugListStateItem(**d)


class LineDrugListState:
    def __get__(self, obj: "main_state.State", objtype=None) -> list[LineDrugListStateItem]:
        return obj._linedrug_list

    def __set__(self, obj: "main_state.State", _list: list[LineDrugListStateItem]):
        obj._linedrug_list = _list
        obj.mv.order_book.prescriptionpage.drug_list.rebuild(_list)

    @staticmethod
    def fetch(v: Visit, connection: Connection):
        query = f"""
            SELECT 
                ld.id,
                ld.drug_id, wh.name,
                ld.times, ld.dose,
                ld.quantity, ld.note,
                wh.usage, wh.usage_unit,
                wh.sale_unit, wh.sale_price
            FROM (SELECT * FROM {LineDrug.__tablename__}
                  WHERE visit_id = {v.id}
            ) AS ld
            JOIN {Warehouse.__tablename__} AS wh
            ON wh.id = ld.drug_id
        """
        rows = connection.execute(query).fetchall()
        return [LineDrugListStateItem(*row) for row in rows]
