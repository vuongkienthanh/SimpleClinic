from .patient_state import PatientState
from .visit_state import VisitState
from .warehouse_state import WarehouseState
from .visit_list_state import VisitListState, VisitListStateItem
from .linedrug_state import (
    LineDrugState,
    OldLineDrugListState,
    OldLineDrugListStateItem,
    NewLineDrugListState,
    NewLineDrugListStateItem,
    LineDrugListStateItem,
)
from .lineprocedure_state import (
    OldLineProcedureListState,
    OldLineProcedureListStateItem,
    NewLineProcedureListState,
    NewLineProcedureListStateItem,
    LineProcedureListStateItem,
    LineProcedureState,
)
from .queue_state import QueueState, QueueStateItem
from .seentoday_state import SeenTodayState, SeenTodayStateItem
from .appointment_state import AppointmentState, AppointmentStateItem
from db import *
from ui import mainview


class State:
    """Manage data, appearance and button state"""

    patient = PatientState()
    visit = VisitState()
    warehouse = WarehouseState()
    visit_list = VisitListState()

    linedrug = LineDrugState()
    old_linedrug_list = OldLineDrugListState()
    new_linedrug_list = NewLineDrugListState()

    lineprocedure = LineProcedureState()
    old_lineprocedure_list = OldLineProcedureListState()
    new_lineprocedure_list = NewLineProcedureListState()

    queue = QueueState()
    seentoday = SeenTodayState()
    appointment = AppointmentState()

    def __init__(self, mv: "mainview.MainView") -> None:
        self.mv = mv
        self.Init()

    def Init(self) -> None:
        self._patient: Patient | None = None
        self._visit: Visit | None = None
        self._warehouse: Warehouse | None = None
        self._visit_list: list[VisitListStateItem] = []

        self._linedrug: LineDrugListStateItem | None = None
        self._old_linedrug_list: list[OldLineDrugListStateItem] = []
        self._new_linedrug_list: list[NewLineDrugListStateItem] = []
        self.to_delete_old_linedrug_list: list[OldLineDrugListStateItem] = []

        self._lineprocedure: LineProcedureListStateItem | None = None
        self._old_lineprocedure_list: list[OldLineProcedureListStateItem] = []
        self._new_lineprocedure_list: list[NewLineProcedureListStateItem] = []
        self.to_delete_old_lineprocedure_list: list[OldLineProcedureListStateItem] = []

        self._queue: list[QueueStateItem] = []
        self._seentoday: list[SeenTodayStateItem] = []
        self._appointment: list[AppointmentStateItem] = []

        self.all_warehouse: dict[int, Warehouse] = self.mv.connection.selectall(
            Warehouse
        )
        self.all_sampleprescription: dict[
            int, SamplePrescription
        ] = self.mv.connection.selectall(SamplePrescription)
        self.all_procedure: dict[int, Procedure] = self.mv.connection.selectall(
            Procedure
        )

    def refresh(self) -> None:
        self.patient = None
        self.visit = None
        self.warehouse = None
        self.visit_list = []

        self.linedrug = None
        self.old_linedrug_list = []
        self.new_linedrug_list = []
        self.to_delete_old_linedrug_list = []

        self.lineprocedure = None
        self.old_lineprocedure_list = []
        self.new_lineprocedure_list = []
        self.to_delete_old_lineprocedure_list = []

        self.queue = QueueState.fetch(self.mv.connection)
        self.seentoday = SeenTodayState.fetch(self.mv.connection)
        self.appointment = AppointmentState.fetch(self.mv.connection)

        self.all_warehouse = self.mv.connection.selectall(Warehouse)
        self.all_sampleprescription = self.mv.connection.selectall(SamplePrescription)
        self.all_procedure = self.mv.connection.selectall(Procedure)
        self.mv.order_book.SetSelection(0)
