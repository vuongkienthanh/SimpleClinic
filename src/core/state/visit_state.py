from db import Visit
from core import state
from core import menubar
from misc import vn_weekdays, check_none_to_blank
from .linedrugs_list_state import LineDrugListState


class VisitState:
    def __get__(self, obj: "state.State", objtype=None) -> Visit | None:
        return obj._visit

    def __set__(self, obj: "state.State", value: Visit | None):
        obj._visit = value
        if value:
            self.onSet(obj, value)
        else:
            self.onUnset(obj)

    def onSet(self, obj: "state.State", v: Visit) -> None:
        mv = obj.mv
        mv.diagnosis.ChangeValue(v.diagnosis)
        mv.vnote.ChangeValue(check_none_to_blank(v.vnote))
        mv.weight.SetValue(v.weight)
        mv.days.SetValue(v.days)
        mv.recheck_weekday.SetLabel(vn_weekdays(v.days))
        mv.recheck.SetValue(v.recheck)
        mv.follow.SetValue(check_none_to_blank(v.follow))
        obj.linedrug_list = LineDrugListState.fetch(v, mv.connection)
        obj.lineprocedure_list = obj.get_lineprocedures_by_visit_id(v.id)
        mv.savebtn.SetLabel("Cập nhật")
        mv.price.FetchPrice()
        if mv.patient_book.GetSelection() == 0:
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
        obj: "state.State",
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
        obj.linedrug_list = []
        obj.lineprocedure_list = []
        mv.price.Clear()
        mv.newvisitbtn.Disable()
        mv.savebtn.SetLabel("Lưu")
        mv.order_book.prescriptionpage.reuse_druglist_btn.Disable()
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
