import wx

import state
from db import Patient
from misc import bd_to_vn_age, check_none_to_blank
from state.visit_states import VisitListState
from ui import menubar


class PatientState:
    def __get__(self, obj: "state.main_state.State", _) -> Patient | None:
        return obj._patient

    def __set__(self, obj: "state.main_state.State", value: Patient | None):
        obj._patient = value
        match value:
            case None:
                self.onUnset(obj)
            case val:
                self.onSet(obj, val)

    def onSet(self, obj: "state.main_state.State", p: Patient) -> None:
        mv = obj.mv
        mv.name.ChangeValue(p.name)
        mv.gender.ChangeValue(str(p.gender))
        mv.birthdate.ChangeValue(p.birthdate.strftime("%d/%m/%Y"))
        mv.age.ChangeValue(bd_to_vn_age(p.birthdate))
        mv.address.ChangeValue(check_none_to_blank(p.address))
        mv.phone.ChangeValue(check_none_to_blank(p.phone))
        mv.past_history.ChangeValue(check_none_to_blank(p.past_history))
        mv.savebtn.SetLabel("Lưu")
        mv.savebtn.Enable()
        mv.weight.Enable()
        mv.temperature.Enable()
        mv.height.Enable()
        mv.days.Enable()
        mv.recheck.Enable()
        mv.norecheck.Enable()
        mv.order_book.prescriptionpage.use_sample_prescription_btn.Enable()
        obj.visit = None
        obj.visit_list = VisitListState.fetch(p, mv.connection, mv.config)
        if len(obj.visit_list) > 0:
            mv.get_weight_btn.Enable()
        else:
            mv.get_weight_btn.Disable()

        idx: int = mv.patient_book.Selection
        page: wx.ListCtrl = mv.patient_book.GetPage(idx)
        page.SetFocus()

        menubar: "menubar.MyMenuBar" = mv.MenuBar
        menubar.menuUpdatePatient.Enable()
        menubar.menuInsertVisit.Enable()
        if idx == 0:
            menubar.menuDeleteQueue.Enable()
            menubar.menuPrint.Enable(False)
            menubar.menuPreview.Enable(False)

    def onUnset(self, obj: "state.main_state.State") -> None:
        mv = obj.mv
        mv.name.Clear()
        mv.gender.Clear()
        mv.birthdate.Clear()
        mv.age.Clear()
        mv.address.Clear()
        mv.phone.Clear()
        mv.past_history.Clear()
        mv.savebtn.SetLabel("Lưu")
        mv.savebtn.Disable()
        mv.weight.Disable()
        mv.temperature.Disable()
        mv.height.Disable()
        mv.get_weight_btn.Disable()
        mv.days.Disable()
        mv.recheck.Disable()
        mv.norecheck.Disable()
        mv.order_book.prescriptionpage.use_sample_prescription_btn.Disable()
        obj.visit = None
        obj.visit_list = []

        menubar: "menubar.MyMenuBar" = mv.MenuBar
        menubar.menuUpdatePatient.Enable(False)
        menubar.menuInsertVisit.Enable(False)
        menubar.menuPrint.Enable(False)
        menubar.menuPreview.Enable(False)
        menubar.menuDeleteQueue.Enable(False)
