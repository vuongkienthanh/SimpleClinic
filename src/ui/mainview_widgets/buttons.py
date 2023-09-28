import dataclasses
from itertools import chain

import wx

from db import LineDrug, LineProcedure, Patient, Visit
from misc import (
    calc_quantity,
    check_blank_to_none,
    sale_unit_from_db,
    update_druglist_bm,
    weight_bm,
)
from misc.printer import PrintOut, printdata
from ui import mainview as mv


class GetWeightBtn(wx.BitmapButton):
    "Get latest weight"

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
    "Set RecheckCtrl Value to 0"

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(parent, label="Không tái khám", **kwargs)
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        self.mv.recheck.SetValue(0)


class UpdateQuantityBtn(wx.Button):
    "Update quantity in druglist based on days"

    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent)
        self.mv = parent
        self.SetLabelText("Cập nhật số lượng thuốc")
        self.SetBitmap(wx.Bitmap(update_druglist_bm))
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        self.update_quantity()
        self.Disable()

    def update_quantity(self):
        """Update quantity in DrugList, also update price"""
        state = self.mv.state
        drug_list = self.mv.order_book.prescriptionpage.drug_list
        for idx, item in enumerate(
            chain(state.old_linedrug_list, state.new_linedrug_list)
        ):
            wh = state.all_warehouse[item.warehouse_id]
            item.quantity = calc_quantity(
                times=item.times,
                dose=item.dose,
                days=self.mv.days.Value,
                sale_unit=wh.sale_unit,
                config=self.mv.config,
            )
            drug_list.SetItem(
                idx,
                5,
                f"{item.quantity} {sale_unit_from_db(wh.sale_unit , wh.usage_unit)}",
            )
        self.mv.price.FetchPrice()


class NewVisitBtn(wx.Button):
    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, label="Lượt khám mới")
        self.mv = parent
        self.Bind(wx.EVT_BUTTON, self.onClick)
        self.Disable()

    def onClick(self, _):
        if self.mv.patient_book.Selection == 1:
            self.mv.state.visit = None
        else:
            idx: int = self.mv.visit_list.GetFirstSelected()
            self.mv.visit_list.Select(idx, 0)


class SaveBtn(wx.Button):
    "Insert/update visit"

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
        if self.mv.check_diag_wt_filled():
            mv = self.mv
            state = mv.state
            p = state.patient
            assert p is not None
            assert state.old_linedrug_list == []
            assert state.old_lineprocedure_list == []
            past_history = check_blank_to_none(mv.past_history.Value)
            try:
                with mv.connection as con:
                    con.execute(
                        f"UPDATE {Patient.__tablename__} SET past_history = ? WHERE id = {p.id}",
                        (past_history,),
                    )
                    vid = con.execute(
                        f"""
                        INSERT INTO {Visit.__tablename__} ({Visit.commna_joined_fields()})
                        VALUES ({Visit.named_style_placeholders()})
                    """,
                        {
                            "diagnosis": mv.diagnosis.Value.strip(),
                            "weight": mv.weight.GetWeight(),
                            "days": mv.days.Value,
                            "recheck": mv.recheck.Value,
                            "price": mv.price.GetPrice(),
                            "patient_id": p.id,
                            "vnote": check_blank_to_none(mv.vnote.Value),
                            "follow": check_blank_to_none(mv.follow.Value),
                            "temperature": mv.temperature.GetTemperature(),
                            "height": mv.height.GetHeight(),
                        },
                    ).lastrowid
                    assert vid is not None
                    con.executemany(
                        f"""
                        INSERT INTO {LineDrug.__tablename__}
                        ({LineDrug.commna_joined_fields()})
                        VALUES ({LineDrug.named_style_placeholders()})
                    """,
                        (
                            dataclasses.asdict(item) | {"visit_id": vid}
                            for item in state.new_linedrug_list
                        ),
                    )
                    con.executemany(
                        f"""
                        INSERT INTO {LineProcedure.__tablename__}
                        ({LineProcedure.commna_joined_fields()})
                        VALUES ({LineProcedure.named_style_placeholders()})
                    """,
                        (
                            dataclasses.asdict(item) | {"visit_id": vid}
                            for item in state.new_lineprocedure_list
                        ),
                    )
                    wx.MessageBox(
                        "Lưu lượt khám mới thành công",
                        "Lưu lượt khám mới",
                        style=wx.OK_DEFAULT | wx.ICON_NONE,
                    )
                    if self.mv.config.ask_print:
                        if (
                            wx.MessageBox("In toa về?", "In toa", style=wx.YES | wx.NO)
                            == wx.YES
                        ):
                            printout = PrintOut(self.mv)
                            wx.Printer(wx.PrintDialogData(printdata)).Print(
                                self.mv, printout, False
                            )
                    self.mv.state.refresh()
            except Exception as error:
                wx.MessageBox(f"Lỗi không lưu lượt khám được\n{error}", "Lỗi")

    def update_visit(self):
        mv = self.mv
        state = mv.state
        if self.mv.check_diag_wt_filled():
            p = state.patient
            assert p is not None
            past_history = check_blank_to_none(mv.past_history.Value)
            v = state.visit
            assert v is not None
            v.diagnosis = mv.diagnosis.Value.strip()
            v.weight = mv.weight.GetWeight()
            v.days = mv.days.Value
            v.recheck = mv.recheck.Value
            v.price = mv.price.GetPrice()
            v.vnote = check_blank_to_none(mv.vnote.Value)
            v.follow = check_blank_to_none(mv.follow.Value)
            v.temperature = mv.temperature.GetTemperature()
            v.height = mv.height.GetHeight()

            try:
                with mv.connection as con:
                    con.execute(
                        f"UPDATE {Patient.__tablename__} SET past_history = ? WHERE id = ?",
                        (past_history, p.id),
                    )
                    con.execute(
                        f"""
                        UPDATE {Visit.__tablename__} SET ({Visit.commna_joined_fields()})
                        = ({Visit.qmark_style_placeholders()})
                        WHERE id = ?
                    """,
                        (*v.qmark_style_sql_params(), v.id),
                    )
                    con.executemany(
                        f"""
                        UPDATE {LineDrug.__tablename__}
                        SET (dose, times, quantity, usage_note, outclinic) = (?,?,?,?,?)
                        WHERE id=?
                    """,
                        (
                            (
                                item.dose,
                                item.times,
                                item.quantity,
                                item.usage_note,
                                item.outclinic,
                                item.id,
                            )
                            for item in state.old_linedrug_list
                        ),
                    )
                    con.executemany(
                        f"DELETE FROM {LineDrug.__tablename__} WHERE id = ?",
                        ((item.id,) for item in state.to_delete_old_linedrug_list),
                    )
                    con.executemany(
                        f"""
                        INSERT INTO {LineDrug.__tablename__}
                        ({LineDrug.commna_joined_fields()})
                        VALUES ({LineDrug.named_style_placeholders()})
                    """,
                        (
                            dataclasses.asdict(item) | {"visit_id": v.id}
                            for item in state.new_linedrug_list
                        ),
                    )
                    con.executemany(
                        f"DELETE FROM {LineProcedure.__tablename__} where id = ?",
                        ((item.id,) for item in state.to_delete_old_lineprocedure_list),
                    )
                    con.executemany(
                        f"""
                        INSERT INTO {LineProcedure.__tablename__} ({LineProcedure.commna_joined_fields()})
                        VALUES ({LineProcedure.qmark_style_placeholders()})
                    """,
                        (
                            (item.procedure_id, v.id)
                            for item in state.new_lineprocedure_list
                        ),
                    )
                wx.MessageBox(
                    "Cập nhật lượt khám thành công",
                    "Cập nhật lượt khám",
                    style=wx.OK_DEFAULT | wx.ICON_NONE,
                )
                if mv.config.ask_print:
                    if (
                        wx.MessageBox("In toa về?", "In toa", style=wx.YES | wx.NO)
                        == wx.YES
                    ):
                        printout = PrintOut(mv)
                        wx.Printer(wx.PrintDialogData(printdata)).Print(
                            self, printout, False
                        )
                mv.state.refresh()
            except Exception as error:
                wx.MessageBox(f"Lỗi không Cập nhật lượt khám được\n{error}", "Lỗi")


class PrintBtn(wx.Button):
    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, label="In")
        self.mv = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        from misc.printer import PrintOut, printdata

        printout = PrintOut(self.mv)
        printdialog = wx.PrintDialog(self.mv)
        if printdialog.ShowModal() == wx.ID_OK:
            printdialog.PrintDialogData.SetPrintData(printdata)
            wx.Printer(printdialog.PrintDialogData).Print(mv, printout, False)


class PreviewBtn(wx.Button):
    def __init__(self, parent: "mv.MainView"):
        super().__init__(parent, label="Xem trước")
        self.mv = parent
        self.Disable()
        self.Bind(wx.EVT_BUTTON, self.onClick)

    def onClick(self, _):
        from misc.printer import PrintOut, printdata

        printout = PrintOut(self.mv, preview=True)
        printdialogdata = wx.PrintDialogData(printdata)
        printpreview = wx.PrintPreview(printout, data=printdialogdata)
        printpreview.SetZoom(100)
        frame = wx.PreviewFrame(printpreview, self.mv)
        frame.Maximize()
        frame.Initialize()
        frame.Show()
