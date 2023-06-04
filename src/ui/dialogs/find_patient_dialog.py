from db.classes import Gender
import datetime as dt
from ui import mainview
from ui.dialogs.patient_dialog import EditPatientDialog
from db import Patient, Queue, Visit
from ui.dialogs.picker_dialog import DatePickerDialog
from state.queue_state import QueueStateItem
import wx
import sqlite3


class SearchPatientList(wx.ListCtrl):
    """Listctrl with next,prev button, fetch cursor when needed"""

    def __init__(self, parent: "FindPatientDialog", num_of_lines: int):
        super().__init__(
            parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL, size=(-1, 26 * num_of_lines)
        )
        self.mv = parent.mv
        self.AppendColumn("Mã BN", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Họ tên", width=self.mv.config.header_width(0.1))
        self.AppendColumn("Giới", width=self.mv.config.header_width(0.03))
        self.AppendColumn("Ngày sinh", width=self.mv.config.header_width(0.06))
        self.num_of_lines = num_of_lines
        self.page_index: int = 0
        self.saved_pages: list[list] = []
        self.temp_page: list = []
        self.cur_page: list = []
        self._done: bool = False
        self.pid: int | None = None

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onDeselect)

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

    def append(self, row: sqlite3.Row):
        if len(self.cur_page) == self.num_of_lines:
            self.new_page()
        self.cur_page.append(row)
        self.append_ui(row)

    def is_first(self) -> bool:
        return self.page_index == 0

    def is_last(self) -> bool:
        return self.page_index == len(self.saved_pages)

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

    def is_done(self) -> bool:
        return self._done

    def done(self):
        self._done = True

    def clear(self):
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

    def onSearch(self, e: wx.CommandEvent):
        "Enter (EVT_SEARCH) to activate"
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

    def rebuild(self):
        self.lc.clear()
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
            row = self.cur.fetchone()
            if row is not None:
                self.lc.append(row)
            else:
                self.lc.done()
                break

    def clear(self):
        self.search.Clear()
        self.lc.clear()
        self.prevbtn.Disable()
        self.nextbtn.Disable()
        self.addqueuebtn.Disable()
        self.editbtn.Disable()
        self.delbtn.Disable()

    def next_prev_status_check(self):
        if self.lc.is_first():
            self.prevbtn.Disable()
        else:
            self.prevbtn.Enable()

        if self.lc.is_last():
            if self.lc.is_done():
                self.nextbtn.Disable()
            else:
                self.nextbtn.Enable()
        else:
            self.nextbtn.Enable()

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
            qid = self.mv.connection.insert(Queue, {"patient_id": pid})
            assert qid is not None
            wx.MessageBox("Thêm vào danh sách chờ thành công", "OK", style=wx.ICON_NONE)
            idx: int = self.lc.GetFirstSelected()
            assert idx != -1
            self.lc.GetItemText(idx, 2)
            item = QueueStateItem(
                pid,
                self.lc.GetItemText(idx, 1),
                Gender.from_s(self.lc.GetItemText(idx, 2)),
                dt.datetime.strptime(self.lc.GetItemText(idx, 3), "%d/%m/%Y").date(),
                dt.datetime.now(),
            )
            self.mv.state.queue.append(item)
            self.mv.patient_book.queuelistctrl.append_ui(item)
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
                style=wx.YES_NO | wx.NO_DEFAULT | wx.CENTRE,
            )
            == wx.YES
        ):
            pid = self.lc.pid
            assert pid is not None
            try:
                self.mv.connection.delete(Patient, pid)
                wx.MessageBox("Xóa thành công", "OK", style=wx.ICON_NONE)
                self.mv.state.refresh()
                self.clear()
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