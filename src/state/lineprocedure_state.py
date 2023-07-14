from dataclasses import dataclass

import wx

import state
from db import Connection, LineProcedure, Procedure, Visit


@dataclass(slots=True, match_args=False)
class OldLineProcedureListStateItem:
    id: int
    procedure_id: int


@dataclass(slots=True, match_args=False)
class NewLineProcedureListStateItem:
    procedure_id: int


LineProcedureListStateItem = (
    OldLineProcedureListStateItem | NewLineProcedureListStateItem
)
LineProcedureListState = (
    list[NewLineProcedureListStateItem]
    | list[OldLineProcedureListStateItem]
    | list[LineProcedureListStateItem]
)


class LineProcedureState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> LineProcedureListStateItem | None:
        return obj._lineprocedure

    def __set__(
        self, obj: "state.main_state.State", value: LineProcedureListStateItem | None
    ) -> None:
        obj._lineprocedure = value
        match value:
            case None:
                self.onUnset(obj)
            case item:
                self.onSet(obj, item)

    def onSet(self, obj: "state.main_state.State", item: LineProcedureListStateItem):
        page = obj.mv.order_book.procedurepage
        page.procedure_picker.SetDBID(item.procedure_id)
        page.SetFocus()

    def onUnset(self, obj: "state.main_state.State") -> None:
        page = obj.mv.order_book.procedurepage
        page.procedure_picker.SetSelection(wx.NOT_FOUND)
        page.SetFocus()


class NewLineProcedureListState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> list[NewLineProcedureListStateItem]:
        return obj._new_lineprocedure_list


class OldLineProcedureListState:
    def __get__(
        self, obj: "state.main_state.State", _
    ) -> list[OldLineProcedureListStateItem]:
        return obj._old_lineprocedure_list

    def __set__(
        self, obj: "state.main_state.State", _list: list[OldLineProcedureListStateItem]
    ):
        obj._old_lineprocedure_list = _list
        obj.mv.order_book.procedurepage.procedure_list.rebuild(_list)

    @staticmethod
    def fetch(v: Visit, connection: Connection) -> list[OldLineProcedureListStateItem]:
        query = f"""
            SELECT 
                lp.id, pr.id AS procedure_id
            FROM 
                (SELECT * FROM {LineProcedure.__tablename__}
                    WHERE visit_id = {v.id}
                ) AS lp
            JOIN {Procedure.__tablename__} AS pr
            ON pr.id = lp.procedure_id
        """
        rows = connection.execute(query).fetchall()
        return [OldLineProcedureListStateItem(*row) for row in rows]
