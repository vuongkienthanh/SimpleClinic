from db import *
from ui import mainview

from .all_dict_states import (
    AllProcedureState,
    AllSamplePrescriptionState,
    AllWarehouseState,
)
from .linedrug_states import (
    LineDrugListStateItem,
    LineDrugState,
    NewLineDrugListState,
    NewLineDrugListStateItem,
    OldLineDrugListState,
    OldLineDrugListStateItem,
)
from .lineprocedure_states import (
    LineProcedureListStateItem,
    LineProcedureState,
    NewLineProcedureListState,
    NewLineProcedureListStateItem,
    OldLineProcedureListState,
    OldLineProcedureListStateItem,
)
from .patient_states import (
    AppointmentState,
    AppointmentStateItem,
    PatientState,
    QueueState,
    QueueStateItem,
    SeenTodayState,
    SeenTodayStateItem,
)
from .visit_states import VisitListState, VisitListStateItem, VisitState
from .warehouse_state import WarehouseState


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

    all_procedure = AllProcedureState()
    all_sampleprescription = AllSamplePrescriptionState()
    all_warehouse = AllWarehouseState()

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

        self._all_warehouse: dict[int, Warehouse] = {}
        self._all_sampleprescription: dict[int, SamplePrescription] = {}
        self._all_procedure: dict[int, Procedure] = {}

    def refresh_all(self) -> None:
        self.refresh()
        self.refresh_rest()

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

        self._all_warehouse = AllWarehouseState.fetch(self.mv.connection)

        self.mv.order_book.SetSelection(0)
        VisitListState.clear_cache()
        OldLineDrugListState.clear_cache()
        OldLineProcedureListState.clear_cache()

    def refresh_rest(self) -> None:
        self._all_sampleprescription = AllSamplePrescriptionState.fetch(
            self.mv.connection
        )
        self.all_procedure = AllProcedureState.fetch(self.mv.connection)
