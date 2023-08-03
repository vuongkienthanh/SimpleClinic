from dataclasses import dataclass

import state
from ui import mainview


@dataclass(slots=True, match_args=False)
class NewLineDrugListStateItem:
    warehouse_id: int
    times: int
    dose: str
    quantity: int
    usage_note: str | None
    outclinic: bool | None


class NewLineDrugListState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> list[NewLineDrugListStateItem]:
        return obj._new_linedrug_list

    @staticmethod
    def append_state(mv: "mainview.MainView", item: NewLineDrugListStateItem):
        mv.state._new_linedrug_list.append(item)
        mv.order_book.prescriptionpage.drug_list.append_ui(item)
