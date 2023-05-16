from misc import weight_bm, update_druglist_bm
from db import LineProcedure, Visit, Patient, LineDrug, SeenToday
from misc import calc_quantity, check_blank_to_none, sale_unit_str
from ui import mainview as mv
from misc.printer import PrintOut, printdata

import sqlite3
import wx


class GetWeightBtn(wx.BitmapButton):
    """Used in conjuction with WeightCtrl"""

    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, bitmap=wx.Bitmap(weight_bm))
        self.mv = parent
        self.SetToolTip("Lấy cân nặng mới nhất")
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        visit_count = self.mv.visit_list.GetItemCount()
        if self.mv.state.patient and (visit_count > 0):
            self.mv.weight.SetWeight(
                self.mv.connection.execute(
                    f"""
                SELECT weight
                FROM {Visit.__tablename__}
                WHERE (patient_id) = {self.mv.state.patient.id}
                ORDER BY exam_datetime DESC
                LIMIT 1
            """
                ).fetchone()["weight"]
            )


class NoRecheckBtn(wx.Button):
    """Set RecheckCtrl Value to 0"""

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(parent, label="Không tái khám", **kwargs)
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        self.mv.recheck.SetValue(0)


class UpdateQuantityBtn(wx.BitmapButton):
    """Provide `update_quantity` method for DrugList, also update price"""

    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, bitmap=wx.Bitmap(update_druglist_bm))
        self.mv = parent
        self.SetToolTip("Cập nhật lại số lượng thuốc trong toa theo ngày")
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        self.update_quantity()

    def update_quantity(self):
        """Update quantity in DrugList, also update price"""
        state = self.mv.state
        drug_list = self.mv.order_book.prescriptionpage.drug_list
        for idx, item in enumerate(state.old_linedrug_list + state.new_linedrug_list):
            wh = state.all_warehouse[item.warehouse_id]
            item.quantity = calc_quantity(
                times=item.times,
                dose=item.dose,
                days=self.mv.days.GetValue(),
                sale_unit=wh.sale_unit,
                config=self.mv.config,
            )
            drug_list.SetItem(
                idx,
                4,
                f"{item.quantity} {sale_unit_str(wh.sale_unit , wh.usage_unit)}",
            )
        self.mv.price.FetchPrice()
        self.Disable()


class NewVisitBtn(wx.Button):
    """Deselect a visit from visitlist to simulate new visit"""

    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, label="Lượt khám mới")
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        idx: int = self.mv.visit_list.GetFirstSelected()
        self.mv.visit_list.Select(idx, 0)


class SaveBtn(wx.Button):
    """Change between insert/update base on visit selecting"""

    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, id=wx.ID_SAVE, label="Lưu")
        self.mv = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        if self.mv.state.visit:
            self.update_visit()
        else:
            self.insert_visit()

    def insert_visit(self):
        if self.mv.check_filled():
            p = self.mv.state.patient
            assert p is not None
            past_history = check_blank_to_none(self.mv.past_history.GetValue())
            v = {
                "diagnosis": self.mv.diagnosis.GetValue().strip(),
                "weight": self.mv.weight.GetWeight(),
                "days": self.mv.days.GetValue(),
                "recheck": self.mv.recheck.GetValue(),
                "patient_id": p.id,
                "vnote": check_blank_to_none(self.mv.vnote.GetValue()),
                "follow": check_blank_to_none(self.mv.follow.GetValue()),
            }
            try:
                with self.mv.connection as con:
                    con.execute(
                        f"""
                        UPDATE {Patient.__tablename__} SET past_history = ?
                        WHERE id = {p.id}
                    """,
                        (past_history,),
                    )
                    vid = con.execute(
                        f"""
                        INSERT INTO {Visit.__tablename__} ({Visit.commna_joined_field_names()})
                        VALUES ({Visit.named_style_placeholders()})
                    """,
                        v,
                    ).lastrowid
                    assert vid is not None
                    insert_ld = []
                    for item in self.mv.order_book.prescriptionpage.drug_list.d_list:
                        insert_ld.append(
                            {
                                "drug_id": item.drug_id,
                                "dose": item.dose,
                                "times": item.times,
                                "quantity": item.quantity,
                                "visit_id": vid,
                                "note": item.note,
                            }
                        )
                    con.executemany(
                        f"""
                        INSERT INTO {LineDrug.__tablename__} ({LineDrug.commna_joined_field_names()})
                        VALUES ({LineDrug.named_style_placeholders()})
                    """,
                        insert_ld,
                    )
                    insert_lp = []
                    for item in self.mv.order_book.procedurepage.procedure_list.pr_list:
                        insert_lp.append(
                            {
                                "procedure_id": item.pr_id,
                                "visit_id": vid,
                            }
                        )
                    con.executemany(
                        f"""
                        INSERT INTO {LineProcedure.__tablename__} ({LineProcedure.commna_joined_field_names()})
                        VALUES ({LineProcedure.named_style_placeholders()})
                    """,
                        insert_lp,
                    )
                    con.execute(
                        f"""
                        INSERT INTO {SeenToday.__tablename__} ({SeenToday.commna_joined_field_names()})
                        VALUES ({SeenToday.qmark_style_placeholders()})
                    """,
                        (p.id,),
                    )
                    wx.MessageBox("Lưu lượt khám mới thành công", "Lưu lượt khám mới")
                    if self.mv.config.ask_print:
                        if (
                            wx.MessageBox("In toa về?", "In toa", style=wx.YES | wx.NO)
                            == wx.YES
                        ):
                            printout = PrintOut(self.mv)
                            wx.Printer(wx.PrintDialogData(printdata)).Print(
                                self, printout, False
                            )
                    self.mv.state.refresh()
            except sqlite3.IntegrityError as error:
                for a in error.args:
                    if a == "CHECK constraint failed: shortage":
                        wx.MessageBox("Lỗi hết thuốc trong kho", "Lỗi")
                    else:
                        wx.MessageBox(f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")
            except Exception as error:
                wx.MessageBox(f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")

    def update_visit(self):
        diagnosis: str = self.mv.diagnosis.GetValue()
        if self.mv.check_filled():
            p = self.mv.state.patient
            assert p is not None
            past_history = check_blank_to_none(self.mv.past_history.GetValue())
            v = self.mv.state.visit
            assert v is not None
            v.diagnosis = diagnosis.strip()
            v.weight = self.mv.weight.GetWeight()
            v.days = self.mv.days.GetValue()
            v.recheck = self.mv.recheck.GetValue()
            v.vnote = check_blank_to_none(self.mv.vnote.GetValue())
            v.follow = check_blank_to_none(self.mv.follow.GetValue())
            update_ld = []
            update_ld_id = []
            update_drug_id = []
            insert_ld = []
            delete_ld = []
            drug_list = self.mv.order_book.prescriptionpage.drug_list.d_list
            lld = self.mv.state.old_linedrug_list
            # update same drug_id
            for drug in drug_list:
                for origin in lld:
                    if drug.drug_id == origin.warehouse_id:
                        update_ld.append(
                            (
                                drug.dose,
                                drug.times,
                                drug.quantity,
                                drug.note,
                                origin.id,
                            )
                        )
                        update_ld_id.append(origin.id)
                        update_drug_id.append(origin.warehouse_id)
            # delete those in lld but not in update
            for origin in lld:
                if origin.id not in update_ld_id:
                    delete_ld.append((origin.id,))
            # insert those in drug_list but not in update
            for drug in drug_list:
                if drug.drug_id not in update_drug_id:
                    insert_ld.append(
                        {
                            "drug_id": drug.drug_id,
                            "dose": drug.dose,
                            "times": drug.times,
                            "quantity": drug.quantity,
                            "visit_id": v.id,
                            "note": drug.note,
                        }
                    )

            insert_lp = [
                {"procedure_id": pr.pr_id, "visit_id": v.id}
                for pr in self.mv.order_book.procedurepage.procedure_list.pr_list
            ]

            try:
                with self.mv.connection as con:
                    con.execute(
                        f"""
                        UPDATE {Patient.__tablename__} SET past_history = ?
                        WHERE id = {p.id}
                    """,
                        (past_history,),
                    )
                    con.execute(
                        f"""
                        UPDATE {Visit.__tablename__} SET ({Visit.commna_joined_field_names()})
                        = ({Visit.qmark_style_placeholders()})
                        WHERE id = {v.id}
                    """,
                        v.qmark_style_sql_params(),
                    )
                    con.executemany(
                        f"""
                        UPDATE {LineDrug.__tablename__}
                        SET (dose, times, quantity, note) = (?,?,?,?)
                        WHERE id=?
                    """,
                        update_ld,
                    )
                    con.executemany(
                        f"DELETE FROM {LineDrug.__tablename__} WHERE id = ?", delete_ld
                    )
                    con.executemany(
                        f"""
                        INSERT INTO {LineDrug.__tablename__} ({LineDrug.commna_joined_field_names()})
                        VALUES ({LineDrug.named_style_placeholders()})
                    """,
                        insert_ld,
                    )
                    con.execute(
                        f"DELETE FROM {LineProcedure.__tablename__} WHERE visit_id = ?",
                        (v.id,),
                    )
                    con.executemany(
                        f"""
                        INSERT INTO {LineProcedure.__tablename__} ({LineProcedure.commna_joined_field_names()})
                        VALUES ({LineProcedure.named_style_placeholders()})
                    """,
                        insert_lp,
                    )
                wx.MessageBox("Cập nhật lượt khám thành công", "Cập nhật lượt khám")
                if self.mv.config.ask_print:
                    if (
                        wx.MessageBox("In toa về?", "In toa", style=wx.YES | wx.NO)
                        == wx.YES
                    ):
                        printout = PrintOut(self.mv)
                        wx.Printer(wx.PrintDialogData(printdata)).Print(
                            self, printout, False
                        )
                self.mv.state.refresh()
            except sqlite3.IntegrityError as error:
                for a in error.args:
                    if a == "CHECK constraint failed: shortage":
                        wx.MessageBox("Lỗi hết thuốc trong kho", "Lỗi")
                    else:
                        wx.MessageBox(f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")
            except Exception as error:
                wx.MessageBox(f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")
