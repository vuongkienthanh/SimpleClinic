from .linedrug_state import LineDrugState
from .patient_state import PatientState
from .visit_state import VisitState
from .warehouse_state import WarehouseState
from .visit_list_state import VisitListState, VisitListStateItem
from .linedrugs_list_state import LineDrugListState, LineDrugListStateItem
from .queue_state import QueueState, QueueStateItem
from .seentoday_state import SeenTodayState, SeenTodayStateItem
from db import *
from core import mainview
import sqlite3


class State:
    """Manage data, appearance and button state"""

    patient = PatientState()
    visit = VisitState()
    warehouse = WarehouseState()
    linedrug = LineDrugState()
    visit_list = VisitListState()
    linedrug_list = LineDrugListState()
    queue = QueueState()

    def __init__(self, mv: "mainview.MainView") -> None:
        self.mv = mv
        self.Init()
        self.refresh()

    def Init(self) -> None:
        self._patient: Patient | None = None
        self._visit: Visit | None = None
        self._warehouse: Warehouse | None = None
        self._visit_list: list[VisitListStateItem] = []
        self._linedrug: LineDrugListStateItem | None = None
        self._linedrug_list: list[LineDrugListStateItem] = []
        self._lineprocedure_list: list[sqlite3.Row] = []
        self._queue: list[QueueStateItem] = []
        self._seentoday: list[SeenTodayStateItem] = []
        self.allwarehouselist: list[Warehouse] = []
        self.allsampleprescriptionlist: list[SamplePrescription] = []
        self.allprocedurelist: list[Procedure] = []

    def refresh(self) -> None:
        self.patient = None
        self.visit = None
        self.warehouse = None
        self.visit_list = []
        self.linedrug_list = []
        self.lineprocedure_list = []
        self.queue = QueueState.fetch(self.mv.connection)
        self.seentoday = SeenTodayState.fetch(self.mv.connection)
        self.allwarehouselist = self.mv.connection.selectall(Warehouse)
        self.allsampleprescriptionlist = self.mv.connection.selectall(
            SamplePrescription
        )
        self.allprocedurelist = self.mv.connection.selectall(Procedure)
        self.mv.order_book.SetSelection(0)

    @property
    def lineprocedure_list(self) -> list[sqlite3.Row]:
        return self._lineprocedure_list

    @lineprocedure_list.setter
    def lineprocedure_list(self, llp: list[sqlite3.Row]):
        self._lineprocedure_list = llp
        self.mv.order_book.procedurepage.procedure_list.rebuild(llp)


    def get_lineprocedures_by_visit_id(self, vid: int) -> list[sqlite3.Row]:
        query = f"""
            SELECT 
                lp.id, pr.id AS pr_id, pr.name, pr.price
            FROM (SELECT * FROM {LineProcedure.__tablename__}
                  WHERE visit_id = {vid}
            ) AS lp
            JOIN {Procedure.__tablename__} AS pr
            ON pr.id = lp.procedure_id
        """
        return self.mv.connection.execute(query).fetchall()
