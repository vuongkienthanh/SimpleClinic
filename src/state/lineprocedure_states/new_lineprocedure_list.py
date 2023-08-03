from dataclasses import dataclass

import state
from ui import mainview


@dataclass(slots=True, match_args=False)
class NewLineProcedureListStateItem:
    procedure_id: int


class NewLineProcedureListState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> list[NewLineProcedureListStateItem]:
        return obj._new_lineprocedure_list

    @staticmethod
    def append_state(mv: "mainview.MainView", item: NewLineProcedureListStateItem):
        mv.state._new_lineprocedure_list.append(item)
        mv.order_book.procedurepage.procedure_list.append_ui(item)
