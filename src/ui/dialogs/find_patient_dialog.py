import datetime as dt
import sqlite3

import wx

from db import Gender, Patient, Queue, Visit
from state.patient_states import QueueState, QueueStateItem
from ui import mainview
from ui.dialogs.patient_dialog import EditPatientDialog
from ui.generics import DatePickerDialog, StatelessListCtrl


class SearchPatientList(StatelessListCtrl):
    """Listctrl with next,prev button, fetch cursor when needed"""

    def __init__(self, parent: "FindPatientDialog", num_of_lines: int):
        super().__init__(parent, mv=parent.mv, size=(-1, 26 * num_of_lines))
        self.AppendColumn("Mã BN", 0.03)
        self.AppendColumn("Họ tên", 0.1)
        self.AppendColumn("Giới", 0.03)
        self.AppendColumn("Ngày sinh", 0.06)
        self.num_of_lines = num_of_lines
        self.page_index = 0
        self.saved_pages: list[list[sqlite3.Row]] = []
        self.temp_page: list[sqlite3.Row] = []
        self.cur_page: list[sqlite3.Row] = []
        self._done = False
        self.pid: int | None = None

    def onSelect(self, e: wx.ListEvent):
        idx: int = e.Index
        self.pid = self.cur_page[idx][0]
        e.Skip()

    def onDeselect(self, e: wx.ListEvent):
        self.pid = None
        e.Skip()

    def append_ui(self, row: sqlite3.Row):
        self.Append(
            [
                row["pid"],
                row["name"],
                str(row["gender"]),
                row["birthdate"].strftime("%d/%m/%Y"),
            ]
        )

    def new_page(self):
        self.saved_pages.append(self.cur_page)
        self.cur_page = []
        self.page_index += 1
        self.DeleteAllItems()

    def append_row(self, row: sqlite3.Row):
        if len(self.cur_page) == self.num_of_lines:
            self.new_page()
        self.cur_page.append(row)
        self.append_ui(row)

    def is_first(self) -> bool:
        return self.page_index == 0

    def is_last(self) -> bool:
        return self.page_index == len(self.saved_pages)

    def is_done(self) -> bool:
        return self._done

    def done(self):
        self._done = True

    def prev(self):
        if self.is_last():
            self.temp_page = self.cur_page.copy()
        if not self.is_first():
            self.DeleteAllItems()
            self.page_index -= 1
            self.cur_page = self.saved_pages[self.page_index]
            for row in self.cur_page:
                self.append_ui(row)

    def next(self):
        if not self.is_last():
            self.DeleteAllItems()
            self.page_index += 1
            if self.is_last():
                self.cur_page = self.temp_page
            else:
                self.cur_page = self.saved_pages[self.page_index]
            for row in self.cur_page:
                self.append_ui(row)

    def Clear(self):
        self.page_index = 0
        self.saved_pages = []
        self.cur_page = []
        self._done = False
        self.pid = None
        self.DeleteAllItems()


class FindPatientDialog(wx.Dialog):
    def __init__(self, parent: "mainview.MainView"):
        super().__init__(parent, title="Tìm bệnh nhân")
        self.mv = parent
        self.cur = None
        self.num_of_lines = 15
        self.search = wx.SearchCtrl(self)
        self.search.SetHint("Tên bệnh nhân")
        self.lc = SearchPatientList(self, self.num_of_lines)

        self.prevbtn = wx.Button(self, label="<<Trước")
        self.nextbtn = wx.Button(self, label="Sau>>")
        self.prevbtn.Disable()
        self.nextbtn.Disable()

        self.allbtn = wx.Button(self, label="Danh sách toàn bộ bệnh nhân")
        self.atdatebtn = wx.Button(self, label="Danh sách bệnh nhân theo ngày")
        self.addqueuebtn = wx.Button(self, label="Thêm vào danh sách chờ")
        self.editbtn = wx.Button(self, label="Cập nhật")
        self.delbtn = wx.Button(self, label="Xóa")
        self.cancelbtn = wx.Button(self, id=wx.ID_CANCEL)
        self.addqueuebtn.Disable()
        self.editbtn.Disable()
        self.delbtn.Disable()

        def widget(w):
            return (w, 0, wx.EXPAND | wx.ALL, 5)

        navi_sizer = wx.BoxSizer(wx.HORIZONTAL)
        navi_sizer.AddMany(
            [
                (0, 0, 1),
                widget(self.prevbtn),
                widget(self.nextbtn),
                (0, 0, 1),
            ]
        )
        opt_sizer = wx.BoxSizer(wx.HORIZONTAL)
        opt_sizer.AddMany(
            [
                (0, 0, 1),
                widget(self.allbtn),
                widget(self.atdatebtn),
                (0, 0, 1),
            ]
        )
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.AddMany(
            [
                (0, 0, 1),
                widget(self.addqueuebtn),
                widget(self.editbtn),
                widget(self.delbtn),
                widget(self.cancelbtn),
            ]
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddMany(
            [
                widget(self.search),
                widget(wx.StaticText(self, label="Danh sách bệnh nhân")),
                widget(self.lc),
                widget(navi_sizer),
                widget(opt_sizer),
                widget(btn_sizer),
            ]
        )
        self.SetSizerAndFit(sizer)

        self.search.Bind(wx.EVT_SEARCH, self.onSearch)
        self.lc.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.lc.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)
        self.lc.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onEdit)
        self.allbtn.Bind(wx.EVT_BUTTON, self.onAll)
        self.atdatebtn.Bind(wx.EVT_BUTTON, self.onAtDate)
        self.nextbtn.Bind(wx.EVT_BUTTON, self.onNext)
        self.prevbtn.Bind(wx.EVT_BUTTON, self.onPrev)
        self.addqueuebtn.Bind(wx.EVT_BUTTON, self.onAddqueue)
        self.editbtn.Bind(wx.EVT_BUTTON, self.onEdit)
        self.delbtn.Bind(wx.EVT_BUTTON, self.onDelete)
        self.Bind(wx.EVT_CLOSE, self.onClose)

    def rebuild(self):
        self.lc.Clear()
        self.prevbtn.Disable()
        self.nextbtn.Disable()
        self.addqueuebtn.Disable()
        self.editbtn.Disable()
        self.delbtn.Disable()
        self.build()
        self.next_prev_status_check()

    def build(self):
        assert self.cur is not None
        for _ in range(self.num_of_lines):
            match self.cur.fetchone():
                case None:
                    self.lc.done()
                    break
                case row:
                    self.lc.append_row(row)

    def Clear(self):
        self.search.Clear()
        self.lc.Clear()
        self.prevbtn.Disable()
        self.nextbtn.Disable()
        self.addqueuebtn.Disable()
        self.editbtn.Disable()
        self.delbtn.Disable()

    def next_prev_status_check(self):
        self.prevbtn.Enable(not self.lc.is_first())
        self.nextbtn.Enable((not self.lc.is_last()) or (not self.lc.is_done()))

    def onSelect(self, e: wx.CommandEvent):
        self.addqueuebtn.Enable()
        self.editbtn.Enable()
        self.delbtn.Enable()
        e.Skip()

    def onDeselect(self, e: wx.CommandEvent):
        self.addqueuebtn.Disable()
        self.editbtn.Disable()
        self.delbtn.Disable()
        e.Skip()

    def onSearch(self, e: wx.CommandEvent):
        s: str = e.GetString()
        self.cur = self.mv.connection.execute(
            f"""
            SELECT id AS pid, name, gender, birthdate
            FROM {Patient.__tablename__}
            WHERE name LIKE ?
        """,
            ("%" + s.upper() + "%",),
        )
        self.rebuild()

    def onAll(self, _):
        self.cur = self.mv.connection.execute(
            f"""
            SELECT id AS pid, name, gender, birthdate
            FROM {Patient.__tablename__}
        """
        )
        self.rebuild()

    def onAtDate(self, _):
        dlg = DatePickerDialog(self.mv)
        if dlg.ShowModal() == wx.ID_OK:
            d = dlg.GetDate()
            self.cur = self.mv.connection.execute(
                f"""
                SELECT p.id AS pid, name, gender, birthdate
                FROM {Visit.__tablename__} as v
                JOIN {Patient.__tablename__} as p
                ON p.id = v.patient_id
                WHERE DATE(v.exam_datetime) = '{d.strftime("%Y-%m-%d")}'
            """
            )
            self.rebuild()

    def onNext(self, _):
        if (not self.lc.is_done()) and self.lc.is_last():
            self.build()
        else:
            self.lc.next()
        self.next_prev_status_check()

    def onPrev(self, _):
        self.lc.prev()
        self.next_prev_status_check()

    def onAddqueue(self, _):
        pid = self.lc.pid
        assert pid is not None
        try:
            self.mv.connection.insert(Queue, {"patient_id": pid})
            wx.MessageBox("Thêm vào danh sách chờ thành công", "OK", style=wx.ICON_NONE)
            idx: int = self.lc.GetFirstSelected()
            assert idx != -1
            item = QueueStateItem(
                pid,
                self.lc.GetItemText(idx, 1),
                Gender.from_str(self.lc.GetItemText(idx, 2)),
                dt.datetime.strptime(self.lc.GetItemText(idx, 3), "%d/%m/%Y").date(),
                dt.datetime.now(),
            )
            QueueState.append_state(self.mv, item)
        except sqlite3.IntegrityError as error:
            wx.MessageBox(f"Đã có tên trong danh sách chờ.\n{error}", "Lỗi")
        finally:
            idx: int = self.lc.GetFirstSelected()
            self.lc.Select(idx, 0)
            self.search.SetFocus()

    def onEdit(self, _):
        pid = self.lc.pid
        assert pid is not None
        EditFindPatientDialog(self).ShowModal()

    def onDelete(self, _):
        if (
            wx.MessageBox(
                "Xác nhận?",
                "Xóa bệnh nhân",
                style=wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL,
            )
            == wx.YES
        ):
            pid = self.lc.pid
            assert pid is not None
            try:
                self.mv.connection.delete(Patient, pid)
                wx.MessageBox("Xóa thành công", "OK", style=wx.ICON_NONE)
                self.mv.state.refresh()
                self.Clear()
            except sqlite3.Error as error:
                wx.MessageBox(f"Lỗi không xóa được\n{error}", "Lỗi")
            finally:
                self.search.SetFocus()

    def onClose(self, e: wx.CloseEvent):
        if self.cur is not None:
            self.cur.close()
        e.Skip()


class EditFindPatientDialog(EditPatientDialog):
    def __init__(self, parent: FindPatientDialog):
        self.parent = parent
        super().__init__(parent.mv)

    def get_patient(self) -> Patient:
        pid = self.parent.lc.pid
        assert pid is not None
        p = self.mv.connection.select(Patient, pid)
        assert p is not None
        return p
