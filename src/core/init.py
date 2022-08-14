from other_func import get_config
import wx

config = get_config()

# mainview_background_color = wx.Colour(206, 219, 186)
mainview_background_color = wx.Colour(
    *config['mainview_background_color'])
patient_list_background_color = wx.Colour(
    *config['patient_list_background_color'])
visit_list_background_color = wx.Colour(
    *config['visit_list_background_color'])
diagnosis_background_color = wx.Colour(
    *config['diagnosis_background_color'])
drug_list_background_color = wx.Colour(
    *config['drug_list_background_color'])
procedure_list_background_color = wx.Colour(
    *config['procedure_list_background_color'])

# some size
w: tuple[int, int] = wx.DisplaySize()[0]


def size(p):
    return round(w*p*config['listctrl_header_scale'])


def tsize(p):
    return (size(p), -1)


# keycode
# back, del, home, end, left,right
k_special: tuple[int, ...] = (8, 314, 316, 127, 313, 312)
k_number: tuple[int, ...] = tuple(range(48, 58))
k_decimal: tuple[int] = (46,)
k_hash: tuple[int] = (35,)
k_slash: tuple[int] = (47,)
k_tab: tuple[int] = (9,)
