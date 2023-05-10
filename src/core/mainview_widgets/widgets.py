from core import mainview as mv
from misc import vn_weekdays, num_to_str_price
import wx


class DaysCtrl(wx.SpinCtrl):
    """Changing DaysCtrl Value also changes RecheckCtrl Value"""

    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(
            mv,
            style=wx.SP_ARROW_KEYS,
            initial=mv.config.default_days_for_prescription,
            **kwargs,
        )
        self.mv = mv
        self.SetRange(0, 100)
        self.Disable()
        self.Bind(wx.EVT_SPINCTRL, self.onSpin)

    def onSpin(self, e: wx.SpinEvent):
        self.mv.recheck.SetValue(e.GetPosition())
        self.mv.recheck_weekday.SetLabel(vn_weekdays(e.GetPosition()))
        self.mv.updatequantitybtn.Enable()
        if self.mv.order_book.page0.check_wh_do_ti_filled():
            self.mv.order_book.page0.quantity.FetchQuantity()


class RecheckCtrl(wx.SpinCtrl):
    """Independant of DaysCtrl"""

    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(
            mv,
            style=wx.SP_ARROW_KEYS,
            initial=mv.config.default_days_for_prescription,
            **kwargs,
        )
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
        price: int = self.mv.config.checkup_price
        price += sum(
            item.sale_price * item.quantity
            for item in self.mv.order_book.page0.drug_list.d_list
        )
        price += sum(pr.price for pr in self.mv.order_book.page1.procedure_list.pr_list)
        self.ChangeValue(num_to_str_price(price))

    def Clear(self):
        self.ChangeValue(num_to_str_price(self.mv.config.checkup_price))


class Follow(wx.ComboBox):
    """A Combobox which is able to:
    - use only the `key` in `follow_choices`
    - return `None` if text in empty
    - when print use full_value
    """

    def __init__(self, mv: "mv.MainView", **kwargs):
        super().__init__(
            mv,
            style=wx.CB_DROPDOWN,
            choices=list(mv.config.follow_choices.keys()),
            **kwargs,
        )
        self.mv = mv
        self.SetDefault()

    def full_value(self) -> str:
        "return `key: value` from `key`"
        k = self.GetValue().strip()
        if k in self.mv.config.follow_choices.keys():
            return f"{k}: {self.mv.config.follow_choices[k]}"
        else:
            return k

    def SetFollow(self, val: str | None):
        "use when select visit"
        if val is None:
            self.SetValue("")
        else:
            self.SetValue(val)

    def GetFollow(self) -> str | None:
        "use when save/update visit"
        val: str = self.GetValue().strip()
        if val == "":
            return None
        else:
            return val

    def SetDefault(self):
        "use when visit is `None`"
        self.SetSelection(0)
