from db import Patient
from core import state
from core import menubar
from misc import bd_to_vn_age
import wx


class PatientState:
    def __get__(self, obj: "state.State", objtype=None) -> Patient | None:
        return obj._patient

    def __set__(self, obj: "state.State", value: Patient | None):
        obj._patient = value
        if value:
            self.onSelect(obj, value)
        else:
            self.onDeselect(obj)

    def onSelect(self, obj: "state.State", p: Patient) -> None:
        mv = obj.mv
        mv.name.ChangeValue(p.name)
        mv.gender.ChangeValue(str(p.gender))
        mv.birthdate.ChangeValue(p.birthdate.strftime("%d/%m/%Y"))
        mv.age.ChangeValue(bd_to_vn_age(p.birthdate))
        mv.address.ChangeValue(p.address or "")
        mv.phone.ChangeValue(p.phone or "")
        mv.past_history.ChangeValue(p.past_history or "")
        mv.savebtn.SetLabel("Lưu")
        mv.savebtn.Enable()
        mv.weight.Enable()
        mv.days.Enable()
        mv.recheck.Enable()
        mv.norecheck.Enable()
        mv.order_book.prescriptionpage.use_sample_prescription_btn.Enable()
        obj.visit = None
        obj.visitlist = obj.get_visits_by_patient_id(p.id)
        if len(obj.visitlist) > 0:
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

    def onDeselect(self, obj: "state.State") -> None:
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
        mv.get_weight_btn.Disable()
        mv.days.Disable()
        mv.recheck.Disable()
        mv.norecheck.Disable()
        mv.order_book.prescriptionpage.use_sample_prescription_btn.Disable()
        obj.visit = None
        obj.visitlist = []

        menubar: "menubar.MyMenuBar" = mv.MenuBar
        menubar.menuUpdatePatient.Enable(False)
        menubar.menuInsertVisit.Enable(False)
        menubar.menuPrint.Enable(False)
        menubar.menuPreview.Enable(False)
        menubar.menuDeleteQueue.Enable(False)
