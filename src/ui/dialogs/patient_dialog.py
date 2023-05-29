from state.seentoday_state import SeenTodayState
from db import Patient, Patient, Queue
from state.queue_state import QueueState, QueueStateItem
from ui.generic_widgets import (
    DateTextCtrl,
    CalendarDatePicker,
    ReadonlyVNAgeCtrl,
    PhoneTextCtrl,
    GenderChoice,
)
from misc import check_blank_to_none, check_none_to_blank
from ui import mainview
import datetime as dt
import sqlite3
import wx
import wx.adv as adv


class BasePatientDialog(wx.Dialog):
    def __init__(self, parent: "mainview.MainView", title):
        super().__init__(
            parent, title=title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        self.mv = parent

        self.name = wx.TextCtrl(self, size=(300, -1), name="Họ tên")
        self.gender = GenderChoice(self, name="Giới tính")
        self.birthdate_text = DateTextCtrl(self, name="Ngày sinh")
        self.birthdate = CalendarDatePicker(self, name="")
        self.birthdate.SetDateRange(
            wx.DateTime.Today() - wx.DateSpan(years=100), wx.DateTime.Today()
        )
        self.age = ReadonlyVNAgeCtrl(self, name="Tuổi")
        self.address = wx.TextCtrl(self, style=wx.TE_MULTILINE, name="Địa chỉ")
        self.phone = PhoneTextCtrl(self, name="Điện thoại")
        self.past_history = wx.TextCtrl(
            self, style=wx.TE_MULTILINE, name="Bệnh nền, dị ứng"
        )

        self.mandatory: tuple = (
            self.name,
            self.gender,
            self.birthdate_text,
        )

        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.okbtn = wx.Button(self, id=wx.ID_OK)
        self._setSizer()

        self.birthdate_text.Bind(wx.EVT_TEXT, self.onBirthdateText)
        self.birthdate.Bind(adv.EVT_CALENDAR_SEL_CHANGED, self.onBirthdate)
        self.okbtn.Bind(wx.EVT_BUTTON, self.onOkBtn)

    def _setSizer(self):
        def widget(w: wx.Window):
            name: str = w.GetName()
            if w in self.mandatory:
                name += "*"
            return (
                wx.StaticText(self, label=name),
                0,
                wx.ALIGN_CENTER_VERTICAL | wx.ALL,
                3,
            ), (w, 1, wx.EXPAND | wx.ALL, 3)

        entry = wx.FlexGridSizer(rows=8, cols=2, vgap=5, hgap=2)
        entry.AddGrowableCol(1, 1)
        entry.AddGrowableRow(5, 1)
        entry.AddGrowableRow(7, 1)
        entry.AddMany(
            [
                *widget(self.name),
                *widget(self.gender),
                *widget(self.birthdate_text),
                *widget(self.age),
                *widget(self.birthdate),
                *widget(self.address),
                *widget(self.phone),
                *widget(self.past_history),
            ]
        )
        btn = wx.BoxSizer(wx.HORIZONTAL)
        btn.AddMany(
            [
                (0, 0, 1),
                (self.cancelbtn, 0, wx.ALL ^ wx.RIGHT, 10),
                (self.okbtn, 0, wx.ALL, 10),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                (entry, 6, wx.ALL | wx.EXPAND, 10),
                (wx.StaticText(self, label="* là bắt buộc"), 0, wx.ALL, 5),
                (btn, 0, wx.EXPAND),
            ]
        )
        self.SetSizerAndFit(sizer)

    def is_valid(self) -> bool:
        name: str = self.name.Value
        if name.strip() == "":
            wx.MessageBox("Chưa nhập tên bệnh nhân", "Lỗi")
            return False
        elif not self.birthdate_text.is_valid():
            wx.MessageBox("Chưa nhập ngày sinh", "Lỗi")
            return False
        else:
            return True

    def onOkBtn(self, _) -> None:
        ...

    def onBirthdateText(self, e: wx.CommandEvent):
        s = e.GetString()
        if len(s) == 10 and self.birthdate_text.is_valid():
            date = self.birthdate_text.GetDate()
            self.birthdate.SetDate(date)
            self.age.SetBirthdate(date)
            e.Skip()
        else:
            self.birthdate_text.SetToolTip("Sai ngày sinh")

    def onBirthdate(self, e: adv.CalendarEvent):
        date = self.birthdate.GetDate()
        self.age.SetBirthdate(date)
        self.birthdate_text.SetDate(date)
        e.Skip()


class NewPatientDialog(BasePatientDialog):
    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent, title="Bệnh nhân mới")

    def onOkBtn(self, e):
        if self.is_valid():
            name: str = self.name.Value.strip().upper()
            gender = self.gender.GetGender()
            birthdate = self.birthdate.GetDate()
            address = check_blank_to_none(self.address.Value)
            phone = check_blank_to_none(self.phone.Value)
            past_history = check_blank_to_none(self.past_history.Value)
            try:
                new_patient_id = self.mv.connection.insert(
                    Patient,
                    {
                        "name": name,
                        "gender": gender,
                        "birthdate": birthdate,
                        "address": address,
                        "phone": phone,
                        "past_history": past_history,
                    },
                )
                assert new_patient_id is not None
                if (
                    wx.MessageDialog(
                        self,
                        message="Thêm bệnh nhân mới vào danh sách chờ khám?",
                        caption="Danh sách chờ khám",
                        style=wx.OK_DEFAULT | wx.CANCEL,
                    ).ShowModal()
                    == wx.ID_OK
                ):
                    try:
                        self.mv.connection.insert(Queue, {"patient_id": new_patient_id})
                        item = QueueStateItem(
                            new_patient_id, name, gender, birthdate, dt.datetime.now()
                        )
                        self.mv.state.queue.append(item)
                        self.mv.patient_book.queuelistctrl.append_ui(item)
                    except Exception as error:
                        wx.MessageBox(
                            f"Lỗi không thêm vào danh sách chờ được.\n{error}", "Lỗi"
                        )
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Lỗi không thêm bệnh nhân mới được\n{error}", "Lỗi")


class EditPatientDialog(BasePatientDialog):
    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent, title="Cập nhật thông tin bệnh nhân")
        self.mv = parent
        self.patient = self.get_patient()
        self.name.ChangeValue(self.patient.name)
        self.gender.SetGender(self.patient.gender)
        self.birthdate.SetDate(self.patient.birthdate)
        self.age.SetBirthdate(self.patient.birthdate)
        self.birthdate_text.SetDate(self.patient.birthdate)
        self.address.ChangeValue(check_none_to_blank(self.patient.address))
        self.phone.ChangeValue(check_none_to_blank(self.patient.phone))
        self.past_history.ChangeValue(check_none_to_blank(self.patient.past_history))

    def get_patient(self) -> Patient:
        p = self.mv.state.patient
        assert p is not None
        return p

    def onOkBtn(self, e):
        if self.is_valid():
            updated_patient = Patient(
                id=self.patient.id,
                name=self.name.Value.strip().upper(),
                gender=self.gender.GetGender(),
                birthdate=self.birthdate.GetDate(),
                address=check_blank_to_none(self.address.Value),
                phone=check_blank_to_none(self.phone.Value),
                past_history=check_blank_to_none(self.past_history.Value),
            )
            try:
                self.mv.connection.update(updated_patient)
                page: wx.ListCtrl = self.mv.patient_book.GetCurrentPage()
                idx: int = page.GetFirstSelected()
                self.mv.state.queue = QueueState.fetch(self.mv.connection)
                self.mv.state.seentoday = SeenTodayState.fetch(self.mv.connection)
                page.EnsureVisible(idx)
                page.Select(idx)
                e.Skip()
            except Exception as error:
                wx.MessageBox(f"Lỗi không cập nhật được\n{error}", "Lỗi")
