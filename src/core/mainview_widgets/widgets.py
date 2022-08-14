from core import mainview as mv
import other_func as otf
from core.init import (
    config,
    recheck_background_color,
    days_background_color,
    price_background_color,
    follow_background_color
)
import wx


class DaysCtrl(wx.SpinCtrl):
    """ Changing DaysCtrl Value also changes RecheckCtrl Value """

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(
            parent,
            style=wx.SP_ARROW_KEYS,
            initial=config["so_ngay_toa_ve_mac_dinh"],
            **kwargs
        )
        self.mv = parent
        self.SetRange(0, 100)
        self.Disable()
        self.SetBackgroundColour(days_background_color)
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
                         initial=config["so_ngay_toa_ve_mac_dinh"], **kwargs)
        self.SetRange(0, 100)
        self.Disable()
        self.SetBackgroundColour(recheck_background_color)


class PriceCtrl(wx.TextCtrl):
    """A TextCtrl with proper Vietnamese currency format with default set according to config"""

    def __init__(self, parent: "mv.MainView", **kwargs):
        super().__init__(parent, **kwargs)
        self.mv = parent
        self.Clear()
        self.SetBackgroundColour(price_background_color)

    def FetchPrice(self):
        """Display new price"""
        price: int = config['cong_kham_benh']
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
        self.ChangeValue(otf.num_to_str(config['cong_kham_benh']))


class Follow(wx.ComboBox):
    """A Combobox which is able to:
    - display only the `key` in `key: value` pair in combo popup
    - display `key: value` when selected
    - return only the `key` when save
    - return `None` if text in empty
    - the displayed text is used in printing
    """

    def __init__(self, parent: 'mv.MainView', **kwargs):
        "`choice_dict`: `key: value` pair, the `key` is for popup and doing save/update, the`value` is for UI displaying and printing"
        super().__init__(
            parent,
            style=wx.CB_DROPDOWN,
            choices=list(config['loi_dan_do'].keys()),
            **kwargs
        )
        self.mv = parent
        self.SetBackgroundColour(follow_background_color)
        self.SetDefault()

    def full_value(self) -> str:
        'return `key: value` from `key`'
        k = self.GetValue().strip()
        if k in config['loi_dan_do'].keys():
            return f"{k}: {config['loi_dan_do'][k]}"
        else:
            return k

    def SetFollow(self, val: str | None):
        "use when select visit"
        if val is None:
            self.SetValue('')
        else:
            self.SetValue(val)

    def GetFollow(self) -> str | None:
        "use when save/update visit"
        val: str = self.GetValue().strip()
        if val == '':
            return None
        else:
            return val

    def SetDefault(self):
        "use when visit is `None`"
        self.SetSelection(0)
