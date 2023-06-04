from db import Visit
from . import main_state
from ui import menubar
from misc import vn_weekdays, check_none_to_blank
from .linedrug_state import OldLineDrugListState
from .lineprocedure_state import OldLineProcedureListState
import wx


class VisitState:
    def __get__(self, obj: "main_state.State", _) -> Visit | None:
        return obj._visit

    def __set__(self, obj: "main_state.State", value: Visit | None):
        obj._visit = value
        match value:
            case None:
                self.onUnset(obj)
            case val:
                self.onSet(obj, val)

    def onSet(self, obj: "main_state.State", v: Visit) -> None:
        mv = obj.mv
        mv.diagnosis.ChangeValue(v.diagnosis)
        mv.vnote.ChangeValue(check_none_to_blank(v.vnote))
        mv.weight.SetValue(v.weight)
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

    def onUnset(
        self,
        obj: "main_state.State",
    ) -> None:
        mv = obj.mv
        mv.diagnosis.Clear()
        mv.vnote.Clear()
        mv.weight.SetValue(0)
        mv.days.SetValue(mv.config.default_days_for_prescription)
        mv.recheck_weekday.SetLabel(
            vn_weekdays(mv.config.default_days_for_prescription)
        )
        mv.updatequantitybtn.Disable()
        mv.recheck.SetValue(mv.config.default_days_for_prescription)
        mv.follow.SetDefault()
        obj.old_linedrug_list = []
        obj.to_delete_old_linedrug_list.clear()
        obj.old_lineprocedure_list = []
        obj.to_delete_old_lineprocedure_list.clear()
        mv.price.Clear()
        mv.newvisitbtn.Disable()
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
        obj.warehouse = None
        obj.linedrug = None
