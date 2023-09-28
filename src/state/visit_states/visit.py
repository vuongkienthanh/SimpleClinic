import wx

import state
from db import Visit
from misc import check_none_to_blank, vn_weekdays
from state.linedrug_states import OldLineDrugListState
from state.lineprocedure_states import OldLineProcedureListState
from ui import menubar


class VisitState:
    def __get__(self, obj: "state.main_state.State", _) -> Visit | None:
        return obj._visit

    def __set__(self, obj: "state.main_state.State", value: Visit | None):
        obj._visit = value
        match value:
            case None:
                self.onUnset(obj)
            case val:
                self.onSet(obj, val)

    def onSet(self, obj: "state.main_state.State", v: Visit) -> None:
        mv = obj.mv
        mv.Freeze()
        mv.diagnosis.ChangeValue(v.diagnosis)
        mv.vnote.ChangeValue(check_none_to_blank(v.vnote))
        mv.weight.SetWeight(v.weight)
        mv.temperature.SetTemperature(v.temperature)
        mv.height.SetHeight(v.height)
        mv.days.SetValue(v.days)
        mv.recheck_weekday.SetLabel(vn_weekdays(v.days))
        mv.recheck.SetValue(v.recheck)
        mv.follow.SetValue(check_none_to_blank(v.follow))
        obj.old_linedrug_list = OldLineDrugListState.fetch(v, mv.connection)
        obj.to_delete_old_linedrug_list.clear()
        obj.old_lineprocedure_list = OldLineProcedureListState.fetch(v, mv.connection)
        obj.to_delete_old_lineprocedure_list.clear()
        mv.savebtn.SetLabel("Cập nhật")
        mv.price.SetPrice(v.price)
        mv.newvisitbtn.Enable()
        mv.printbtn.Enable()
        mv.previewbtn.Enable()
        mv.order_book.prescriptionpage.reuse_druglist_btn.Enable()
        menubar: "menubar.MyMenuBar" = mv.MenuBar
        menubar.menuNewVisit.Enable()
        if obj.patient:
            mv.order_book.prescriptionpage.use_sample_prescription_btn.Disable()
            menubar.menuInsertVisit.Enable(False)
        menubar.menuUpdateVisit.Enable()
        menubar.menuDeleteVisit.Enable()
        menubar.menuPrint.Enable()
        menubar.menuPreview.Enable()
        menubar.menuCopyVisitInfo.Enable()
        mv.visit_list.SetFocus()
        mv.Thaw()

    def onUnset(
        self,
        obj: "state.main_state.State",
    ) -> None:
        mv = obj.mv
        mv.Freeze()
        mv.diagnosis.Clear()
        mv.vnote.Clear()
        mv.weight.SetWeight(0)
        mv.temperature.SetTemperature(None)
        mv.height.SetHeight(None)
        mv.days.SetValue(mv.config.default_days_for_prescription)
        mv.recheck_weekday.SetLabel(
            vn_weekdays(mv.config.default_days_for_prescription)
        )
        mv.updatequantitybtn.Disable()
        mv.recheck.SetValue(mv.config.default_days_for_prescription)
        mv.follow.Clear()

        obj.old_linedrug_list = []
        obj.new_linedrug_list.clear()
        obj.to_delete_old_linedrug_list.clear()

        obj.old_lineprocedure_list = []
        obj.new_lineprocedure_list.clear()
        obj.to_delete_old_lineprocedure_list.clear()

        obj.warehouse = None
        obj.linedrug = None

        mv.price.Clear()
        mv.newvisitbtn.Disable()
        mv.printbtn.Disable()
        mv.previewbtn.Disable()
        mv.savebtn.SetLabel("Lưu")
        mv.order_book.prescriptionpage.reuse_druglist_btn.Disable()
        mv.order_book.procedurepage.procedure_picker.Select(wx.NOT_FOUND)
        menubar: "menubar.MyMenuBar" = mv.MenuBar
        menubar.menuNewVisit.Enable(False)
        if obj.patient:
            mv.order_book.prescriptionpage.use_sample_prescription_btn.Enable()
            menubar.menuInsertVisit.Enable()
        menubar.menuUpdateVisit.Enable(False)
        menubar.menuDeleteVisit.Enable(False)
        menubar.menuPrint.Enable(False)
        menubar.menuPreview.Enable(False)
        menubar.menuCopyVisitInfo.Enable(False)
        mv.Thaw()
