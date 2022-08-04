from core import mainview as mv
import wx
import other_func as otf


class DaysCtrl(wx.SpinCtrl):
    """ Changing DaysCtrl Value also changes RecheckCtrl Value """

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(
            parent,
            style=wx.SP_ARROW_KEYS,
            initial=parent.config["so_ngay_toa_ve_mac_dinh"],
            **kwargs
        )
        self.mv = parent
        self.SetRange(0, 100)
        self.Disable()
        self.Bind(wx.EVT_SPINCTRL, self.onSpin)

    def onSpin(self, e: wx.SpinEvent):
        self.mv.recheck.SetValue(e.GetPosition())
        self.mv.updatequantitybtn.Enable()
        if self.mv.order_book.page0.check_wh_do_ti_filled():
            self.mv.order_book.page0.quantity.FetchQuantity()


class RecheckCtrl(wx.SpinCtrl):
    """Independant of DaysCtrl"""

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(parent, style=wx.SP_ARROW_KEYS,
                         initial=parent.config["so_ngay_toa_ve_mac_dinh"], **kwargs)
        self.SetRange(0, 100)
        self.Disable()


class PriceCtrl(wx.TextCtrl):
    """A TextCtrl with proper Vietnamese currency format with default set according to config"""

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(parent, **kwargs)
        self.mv = parent
        self.Clear()

    def FetchPrice(self):
        """Display new price"""
        price: int = self.mv.config['cong_kham_benh']
        price += sum(
            item.sale_price * item.quantity
            for item in self.mv.order_book.page0.drug_list.d_list
        )
        price += sum(
            pr.price
            for pr in self.mv.order_book.page1.procedurelistctrl.pr_list
        )
        self.ChangeValue(otf.num_to_str(price))

    def Clear(self):
        self.ChangeValue(otf.num_to_str(self.mv.config['cong_kham_benh']))


class Follow(wx.ComboBox):
    """A Combobox which is able to:
    - display only the `key` in `key: value` pair in combo popup
    - display `key: value` when selected
    - return only the `key` when save
    - return `None` if text in empty
    - the displayed text is used in printing
    """

    def __init__(self, parent: wx.Window, choice_dict: dict[str, str], **kwargs):
        "`choice_dict`: `key: value` pair, the `key` is for popup and doing save/update, the`value` is for UI displaying and printing"
        super().__init__(
            parent,
            style=wx.CB_DROPDOWN,
            choices=list(choice_dict.keys()),
            **kwargs
        )
        self.choice_dict = choice_dict
        self.Bind(wx.EVT_COMBOBOX, self.onChoose)
        k = list(self.choice_dict.keys())[0]
        self.ChangeValue(self.format(k))

    def format(self, key: str) -> str:
        'return `key: value` from `key`'
        return f"{key}: {self.choice_dict[key]}"

    def onChoose(self, e: wx.CommandEvent):
        "return `key: value` instead of only the `key`"
        k: str = e.GetString()
        self.SetValue(self.format(k))

    def SetFollow(self, key: str | None):
        "use when select visit"
        if key is None:
            self.SetValue('')
        elif key in self.choice_dict.keys():
            self.SetValue(self.format(key))
        else:
            self.SetValue(key)

    def GetFollow(self) -> str | None:
        "use when save/update visit"
        val: str = self.GetValue().strip()
        if val == '':
            return None
        else:
            try:
                k, v = tuple(val.split(": ", 1))
                if (k, v) in self.choice_dict.items():
                    return k
                else:
                    return val
            except ValueError:
                return val

    def SetDefault(self):
        "use when visit is `None`"
        k = list(self.choice_dict.keys())[0]
        self.ChangeValue(self.format(k))
