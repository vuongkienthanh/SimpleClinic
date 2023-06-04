from ui import mainview as mv
from misc import vn_weekdays, num_to_str_price, str_to_int_price
from itertools import chain
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
        if self.mv.order_book.prescriptionpage.check_wh_do_ti_filled():
            self.mv.order_book.prescriptionpage.quantity.FetchQuantity()


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
        state = self.mv.state
        price: int = self.mv.config.checkup_price
        price += sum(
            state.all_warehouse[item.warehouse_id].sale_price * item.quantity
            for item in chain(state.old_linedrug_list, state.new_linedrug_list)
        )
        price += sum(
            state.all_procedure[item.procedure_id].price
            for item in chain(
                state.old_lineprocedure_list, state.new_lineprocedure_list
            )
        )
        self.ChangeValue(num_to_str_price(price))

    def Clear(self):
        self.ChangeValue(num_to_str_price(self.mv.config.checkup_price))

    def SetPrice(self, price: int):
        self.ChangeValue(num_to_str_price(price))

    def GetPrice(self) -> int:
        return str_to_int_price(self.Value)


class Follow(wx.ComboBox):
    """A Combobox which is able to:
    - use only the `key` in `follow_choices`
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

    def expand_when_print(self) -> str:
        "expand `key` -> `key: value` in config"
        k = self.Value.strip()
        if k in self.mv.config.follow_choices.keys():
            return f"{k}: {self.mv.config.follow_choices[k]}"
        else:
            return k

    def SetDefault(self):
        "use when visit is `None`"
        self.SetSelection(0)
