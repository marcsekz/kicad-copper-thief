#!/usr/bin/python3
"""Dialog for the Copper Thief KiCad Plugin."""


from wx import ID_ANY, DefaultPosition, Size, DefaultSize, ALL, EXPAND, \
    HORIZONTAL, VERTICAL, Dialog, BoxSizer, StaticText, TextCtrl, ComboBox, CheckBox, \
    CAPTION, CLOSE_BOX, DEFAULT_DIALOG_STYLE, RESIZE_BORDER, \
    Button, ALIGN_CENTER_VERTICAL, ID_OK, \
    ID_CANCEL, ALIGN_RIGHT, BOTH, CHK_CHECKED, CHK_UNCHECKED
# import wx.xrc


class CopperThiefDlg(Dialog):

    """Gui for Copper Thief widget."""

    def __init__(self, parent):
        Dialog.__init__(self, parent, id=ID_ANY, title=u"Copper Thief Parameters", pos=DefaultPosition, size=Size(432, 532), style=CAPTION | CLOSE_BOX | DEFAULT_DIALOG_STYLE | RESIZE_BORDER)

        self.SetSizeHints(DefaultSize, DefaultSize)

        bSizer3 = BoxSizer(VERTICAL)

        self.m_comment = StaticText(self, ID_ANY, u"Select a zone to convert to dots\n", DefaultPosition, DefaultSize, 0)
        self.m_comment.Wrap(-1)

        bSizer3.Add(self.m_comment, 0, ALL | EXPAND, 5)

        bSizerSep = BoxSizer(HORIZONTAL)

        self.m_labelSep = StaticText(self, ID_ANY, u"Dot Separation  (mm)  ", DefaultPosition, DefaultSize, 0)
        self.m_labelSep.Wrap(-1)
        self.m_spacing = TextCtrl(self, ID_ANY, u"2", DefaultPosition, DefaultSize, 0)
        self.m_spacing.SetMinSize(Size(200, -1))

        bSizerSep.Add(self.m_labelSep, 1, ALL | EXPAND, 5)
        bSizerSep.Add(self.m_spacing, 1, ALL, 5)

        bSizer3.Add(bSizerSep, 1, EXPAND, 5)

        ###
        bSizerRad = BoxSizer(HORIZONTAL)

        self.m_labelRad = StaticText(self, ID_ANY, u"Dot Radius  (mm)  ", DefaultPosition, DefaultSize, 0)
        self.m_labelRad.Wrap(-1)
        self.m_radius = TextCtrl(self, ID_ANY, u"0.5", DefaultPosition, DefaultSize, 0)
        self.m_radius.SetMinSize(Size(200, -1))

        bSizerRad.Add(self.m_labelRad, 1, ALL | EXPAND, 5)
        bSizerRad.Add(self.m_radius, 1, ALL, 5)

        bSizer3.Add(bSizerRad, 1, EXPAND, 5)

        ###
        bSizerClearance = BoxSizer(HORIZONTAL)

        self.m_labelClearance = StaticText(self, ID_ANY, u"Clearance multiplier  ", DefaultPosition, DefaultSize, 0)
        self.m_labelClearance.Wrap(-1)
        self.m_clearance = TextCtrl(self, ID_ANY, u"3", DefaultPosition, DefaultSize, 0)
        self.m_clearance.SetMinSize(Size(200, -1))

        bSizerClearance.Add(self.m_labelClearance, 1, ALL | EXPAND, 5)
        bSizerClearance.Add(self.m_clearance, 1, ALL, 5)

        bSizer3.Add(bSizerClearance, 1, EXPAND, 5)
        
        ###
        bSizerPattern = BoxSizer(HORIZONTAL)

        self.m_labelPattern = StaticText(self, ID_ANY, u"Thieving pattern  ", DefaultPosition, DefaultSize, 0)
        self.m_labelPattern.Wrap(-1)

        self.m_pattern_list = [ u"Squares", u"Dots in square grid", u"Dots in triangular grid"]
        self.m_pattern = ComboBox( self, ID_ANY, u"Squares", DefaultPosition, DefaultSize, self.m_pattern_list)
        self.m_pattern.SetMinSize(Size(200, -1))

        bSizerPattern.Add(self.m_labelPattern, 1, ALL | EXPAND, 5)
        bSizerPattern.Add(self.m_pattern, 1, ALL, 5)

        bSizer3.Add(bSizerPattern, 1, EXPAND, 5)
        
        ###
        bSizerCleanup = BoxSizer(HORIZONTAL)
        self.m_labelCleanup = StaticText(self, ID_ANY, u"Clean up thieving zone  ", DefaultPosition, DefaultSize, 0)
        self.m_labelCleanup.Wrap(-1)
        
        self.m_cleanup = CheckBox(self)
        self.m_cleanup.SetMinSize(Size(200, -1))
        
        bSizerCleanup.Add(self.m_labelCleanup, 1, ALL | EXPAND, 5)
        bSizerCleanup.Add(self.m_cleanup, 1, ALL, 5)
        
        bSizer3.Add(bSizerCleanup, 1, EXPAND, 5)

        #
        bSizer1 = BoxSizer(HORIZONTAL)

        self.m_buttonGo = Button(self, ID_OK, u"Go", DefaultPosition, DefaultSize, 0)
        self.m_buttonGo.SetDefault()
        bSizer1.Add(self.m_buttonGo, 0, ALL | ALIGN_CENTER_VERTICAL, 5)

        self.m_buttonCancel = Button(self, ID_CANCEL, u"Cancel", DefaultPosition, DefaultSize, 0)
        bSizer1.Add(self.m_buttonCancel, 0, ALL | ALIGN_CENTER_VERTICAL, 5)

        bSizer3.Add(bSizer1, 0, ALIGN_RIGHT | EXPAND, 5)

        self.SetSizer(bSizer3)
        self.Layout()

        self.Centre(BOTH)

    def __del__(self):
        pass
