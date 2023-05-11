from .patient_state import PatientState
from .visit_state import VisitState
from .warehouse_state import WarehouseState
from db import *
from core import mainview
import sqlite3


class State:
    """Manage data, appearance and button state"""

    patient = PatientState()
    visit = VisitState()
    warehouse = WarehouseState()

    def __init__(self, mv: "mainview.MainView") -> None:
        self.mv = mv
        self.Init()

    def Init(self) -> None:
        self._patient: Patient | None = None
        self._visit: Visit | None = None
        self._warehouse: Warehouse | None = None
        self._visitlist: list[sqlite3.Row] = []
        self._linedruglist: list[sqlite3.Row] = []
        self._lineprocedurelist: list[sqlite3.Row] = []
        self._queue: list[sqlite3.Row] = self.fetch_queue_view()
        self._seentoday: list[sqlite3.Row] = self.fetch_seentoday_view()

        self.allwarehouselist: list[Warehouse] = self.mv.connection.selectall(Warehouse)
        self.allsampleprescriptionlist: list[
            SamplePrescription
        ] = self.mv.connection.selectall(SamplePrescription)
        self.allprocedurelist: list[Procedure] = self.mv.connection.selectall(Procedure)

    def refresh(self) -> None:
        self.patient = None
        self.visit = None
        self.warehouse = None
        self.visitlist = []
        self.linedruglist = []
        self.lineprocedurelist = []
        self.queue = self.fetch_queue_view()
        self.seentoday = self.fetch_seentoday_view()
        self.allwarehouselist = self.mv.connection.selectall(Warehouse)
        self.allsampleprescriptionlist = self.mv.connection.selectall(
            SamplePrescription
        )
        self.allprocedurelist = self.mv.connection.selectall(Procedure)
        self.mv.order_book.SetSelection(0)

    @property
    def visitlist(self) -> list[sqlite3.Row]:
        return self._visitlist

    @visitlist.setter
    def visitlist(self, lv: list[sqlite3.Row]):
        self._visitlist = lv
        self.mv.visit_list.rebuild(lv)

    @property
    def linedruglist(self) -> list[sqlite3.Row]:
        return self._linedruglist

    @linedruglist.setter
    def linedruglist(self, lld: list[sqlite3.Row]):
        self._linedruglist = lld
        self.mv.order_book.prescriptionpage.drug_list.rebuild(lld)

    @property
    def lineprocedurelist(self) -> list[sqlite3.Row]:
        return self._lineprocedurelist

    @lineprocedurelist.setter
    def lineprocedurelist(self, llp: list[sqlite3.Row]):
        self._lineprocedurelist = llp
        self.mv.order_book.procedurepage.procedure_list.rebuild(llp)

    @property
    def queue(self) -> list[sqlite3.Row]:
        return self._queue

    @queue.setter
    def queue(self, lr: list[sqlite3.Row]):
        self._queue = lr
        self.mv.patient_book.queuepatientlistctrl.rebuild(lr)

    @property
    def seentoday(self) -> list[sqlite3.Row]:
        return self._seentoday

    @seentoday.setter
    def seentoday(self, lr: list[sqlite3.Row]):
        self._seentoday = lr
        self.mv.patient_book.seentodaylistctrl.rebuild(lr)

    def get_wh_by_id(self, id: int) -> Warehouse | None:
        for wh in self.allwarehouselist:
            if id == wh.id:
                return wh

    def fetch_queue_view(self) -> list[sqlite3.Row]:
        return self.mv.connection.execute(
            f"SELECT * FROM {Queue.__tablename__}_view"
        ).fetchall()

    def fetch_seentoday_view(self) -> list[sqlite3.Row]:
        return self.mv.connection.execute(
            f"SELECT * FROM {SeenToday.__tablename__}_view"
        ).fetchall()

    def get_visits_by_patient_id(self, pid: int) -> list[sqlite3.Row]:
        query = f"""
            SELECT id AS vid, exam_datetime,diagnosis
            FROM {Visit.__tablename__}
            WHERE {Visit.__tablename__}.patient_id = {pid}
            ORDER BY exam_datetime DESC
        """
        if self.mv.config.display_recent_visit_count >= 0:
            query += f"""
                LIMIT {self.mv.config.display_recent_visit_count}
            """
        return self.mv.connection.execute(query).fetchall()

    def get_linedrugs_by_visit_id(self, vid: int) -> list[sqlite3.Row]:
        query = f"""
            SELECT 
                ld.id,
                ld.drug_id, wh.name,
                ld.times, ld.dose,
                ld.quantity, ld.note,
                wh.usage, wh.usage_unit,
                wh.sale_unit, wh.sale_price
            FROM (SELECT * FROM {LineDrug.__tablename__}
                  WHERE visit_id = {vid}
            ) AS ld
            JOIN {Warehouse.__tablename__} AS wh
            ON wh.id = ld.drug_id
        """
        return self.mv.connection.execute(query).fetchall()

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
