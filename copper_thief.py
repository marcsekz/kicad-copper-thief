#!/usr/bin/python3

import numpy as np
import math
import wx
import pcbnew
import os
import sys
import logging
from . import CopperThiefDlg
from . import copper_thief_defaults
THIEVING_ZONENAMES = ['thieving', 'theiving', 'thief', 'theif', 'dotsarray']
THIEVING_GROUPNAME = 'copper-thief-group'


def FromMM(x) -> int:
    return int(pcbnew.FromMM(float(x)))

def ToMM(x) -> float:
    return pcbnew.ToMM(float(x))

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    return math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))

def touching_npth(npth_object: list, dot_x: float, dot_y: float, clearance: float) -> bool:
    return distance(npth_object[0], npth_object[1], dot_x, dot_y) < (npth_object[2] + clearance)

class StreamToLogger(object):

    """Fake stream object that redirects writes to a logger instance."""

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self, *args, **kwargs):
        pass


# set up logger
logging.basicConfig(level=logging.DEBUG,
                    filename="thief.log",
                    filemode='w',
                    format='%(asctime)s %(name)s %(lineno)d:%(message)s',
                    datefmt='%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)
stdout_logger = logging.getLogger('STDOUT')
sl_out = StreamToLogger(stdout_logger, logging.INFO)
sys.stdout = sl_out

stderr_logger = logging.getLogger('STDERR')
sl_err = StreamToLogger(stderr_logger, logging.ERROR)
sys.stderr = sl_err


class CopperThief_Dlg(CopperThiefDlg.CopperThiefDlg):
    def SetSizeHints(self, sz1, sz2):
        if wx.__version__ < '4.0':
            self.SetSizeHintsSz(sz1, sz2)
        else:
            super(CopperThief_Dlg, self).SetSizeHints(sz1, sz2)

    def onDeleteClick(self, event):
        return self.EndModal(wx.ID_DELETE)

    def onConnectClick(self, event):
        return self.EndModal(wx.ID_REVERT)

    def __init__(self, parent):
        CopperThiefDlg.CopperThiefDlg.__init__(self, parent)
        self.SetMinSize(self.GetSize())


class Copper_Thief(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "Copper Thief"
        self.category = "Modify PCB"
        self.description = "Replace a zone with dots"
        self.icon_file_name = os.path.join(os.path.dirname(__file__), "./dots_icon.png")
        self.show_toolbar_button = True

    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(
            None, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def Run(self):

        board = pcbnew.GetBoard()
        windows = [x for x in wx.GetTopLevelWindows()]

        try:
            parent_frame = [x for x in windows if 'pcbnew' in x.GetTitle().lower()][0]
        except IndexError:
            # Kicad 6 window title is "pcb editor"
            parent_frame = [x for x in windows if 'pcb editor' in x.GetTitle().lower()][0]
                
        print(parent_frame)
        aParameters = CopperThief_Dlg(parent_frame)

        aParameters.m_spacing.SetValue(copper_thief_defaults.default_spacing)
        aParameters.m_diameter.SetValue(copper_thief_defaults.default_diameter)
        aParameters.m_clearance.SetValue(copper_thief_defaults.default_clearance)
        aParameters.m_pattern.SetSelection(copper_thief_defaults.default_pattern)
        aParameters.m_cleanup.SetValue(copper_thief_defaults.default_cleanup)
        
        modal_result = aParameters.ShowModal()
        if modal_result == wx.ID_OK:
            spacing = float(aParameters.m_spacing.GetValue())
            radius = float(aParameters.m_diameter.GetValue()) / 2
            clearance = float(aParameters.m_clearance.GetValue())
            pattern = int(aParameters.m_pattern.GetCurrentSelection())
            cleanup = bool(aParameters.m_cleanup.GetValue() == wx.CHK_CHECKED)
            
            logger.info(f"Spacing {spacing}")
            zones = []
            for z in board.Zones():
                if z.IsSelected():
                    zones.append(z)

            dotter = Dotter(pattern)
            for zone in zones:
                zonename = zone.GetZoneName()
                if zonename.lower() in THIEVING_ZONENAMES:
                    zone_backup = zone.Duplicate()
                    dotter.apply_dots(zone, spacing=spacing, radius=radius, clearance_multiplier=clearance)
                    board.Add(zone_backup)
                    if cleanup:
                        board.Remove(zone_backup)
                    board.Remove(zone)
                    filler = pcbnew.ZONE_FILLER(board)
                    filler.Fill(board.Zones())
                else:
                    wx.MessageBox("Zone name must be \"theiving\".", "Check zone name.", wx.OK)
        aParameters.Destroy()


class Dotter():

    def __init__(self, pattern: int):
        self.pcb = pcbnew.GetBoard()
        self.pattern = pattern # [ u"Squares", u"Dots in square grid", u"Dots in triangular grid"]

    def apply_dots(self, zone, spacing=2, radius=0.5, clearance_multiplier=3):
        """Iterate over the zone area and add dots if inside the zone."""
        zones = self.pcb.Zones()
        layer = zone.GetLayer()
        
        maxerror = 1
        
        self.group = None
        
        for group in self.pcb.Groups():
            if group.GetName() == THIEVING_GROUPNAME:
                self.group = group
        
        if self.group == None:
            self.group = pcbnew.PCB_GROUP(None)
            self.group.SetName(THIEVING_GROUPNAME)
            self.pcb.Add(self.group)
        
        self.clearance_factor = clearance_multiplier
        
        pads = self.pcb.GetPads()
        
        npth_pad_coords = list()
        
        for p in pads:
            t = p.GetAttribute()
            if t == pcbnew.PAD_ATTRIB_NPTH:
                npth_pad_coords.append(
                    list([
                        ToMM(p.GetX()),
                        ToMM(p.GetY()),
                        ToMM(max(p.GetDrillSizeX(),p.GetDrillSizeY()) / 2 + p.GetLocalClearance())
                    ])
                )
        
        # Get the zone outline and deflate it so we don't put dots to close to the outside
        zone_outline = zone.Outline()
        zone_outline.Deflate(FromMM(self.clearance_factor * radius), 16, maxerror)
        zone.SetOutline(zone_outline)
        
        # Increase the clearance so we move even further away from existing copper
        clearance = zone.GetLocalClearance()
        zone.SetLocalClearance(clearance + int(FromMM(self.clearance_factor * radius)))
        zone.SetNeedRefill(True)
        filler = pcbnew.ZONE_FILLER(self.pcb)
        filler.Fill(zones)
        
        bbox = zone.GetBoundingBox()
        zonepolys = zone.GetFilledPolysList(layer)

        board_edge = pcbnew.SHAPE_POLY_SET()
        self.pcb.GetBoardPolygonOutlines(board_edge)
        board_edge.Deflate(FromMM(self.clearance_factor * radius), 16, maxerror)

        # Find any keep out zones to check later when we're dotting
        keep_out_zones = []
        for koz in zones:
            if koz.GetIsRuleArea():
                keep_out_zones.append(koz)
        
        spacingX = spacing
        
        if self.pattern == 2:
            spacingY = math.cos(math.radians(30)) * spacing
            offsetX = 0.5 * spacing
        else:
            spacingY = spacing
            offsetX = 0
        
        # Iterate over the bounding box of the chosen zone
        
        for x in np.arange(ToMM(bbox.GetLeft()), ToMM(bbox.GetRight()), spacingX):
            even_row = False
            for y in np.arange(ToMM(bbox.GetTop()), ToMM(bbox.GetBottom()), spacingY):
                # If the dot centre is inside the the deflated zone poly and the deflated board outline,
                # we're ok to place a dot
                x_offs = x + offsetX if even_row else x
                even_row = not even_row 
                coords = pcbnew.VECTOR2I(FromMM(x_offs), FromMM(y))
                if zonepolys.Collide(coords) and board_edge.Collide(coords):
                    # Check that the dot wont touch any keep out zones
                    touch_keepout = False
                    for koz in keep_out_zones:
                        if koz.Outline().Collide(coords, FromMM(self.clearance_factor * radius)):
                            touch_keepout = True
                    
                    # Check for enough clearance around NPTH
                    touch_npth = False
                    for npth in npth_pad_coords:
                        if touching_npth(npth, x_offs, y, self.clearance_factor * radius):
                            touch_npth = True
                    
                    if not touch_keepout and not touch_npth:
                        dot = self.create_dot(layer, x_offs, y, radius, 0)
                        self.pcb.Add(dot)
        
        # Reset the zone clearance
        zone.SetLocalClearance(clearance)
        zone.SetNeedRefill(True)
        filler = pcbnew.ZONE_FILLER(self.pcb)
        filler.Fill(self.pcb.Zones())
        pcbnew.Refresh()
        # self.RefillBoardAreas()

    def create_dot(self, layer, x, y, r, width):
        """Create a dot."""
        print(f"Creating dot at {x}, {y} with radius {r}")

        if not self.pattern == 0:
            center = pcbnew.VECTOR2I(FromMM(x), FromMM(y))
            start = pcbnew.VECTOR2I(FromMM(x + r), FromMM(y))
            dot = pcbnew.PCB_SHAPE(self.pcb)
            dot.SetShape(pcbnew.S_CIRCLE)
            dot.SetLayer(layer)
            dot.SetStart(start)
            dot.SetEnd(start)
            dot.SetWidth(width)
            dot.SetCenter(center)
            dot.SetFilled(True)
        else:
            start = pcbnew.VECTOR2I(FromMM(x-r), FromMM(y-r))
            end = pcbnew.VECTOR2I(FromMM(x+r), FromMM(y+r))
            dot = pcbnew.PCB_SHAPE(self.pcb)
            dot.SetShape(pcbnew.S_RECT)
            dot.SetLayer(layer)
            dot.SetStart(start)
            dot.SetEnd(end)
            dot.SetWidth(width)
            dot.SetFilled(True)
        
        self.group.AddItem(dot)
        return dot

    def RefillBoardAreas(self):
        for i in range(self.pcb.GetAreaCount()):
            area = self.pcb.GetArea(i)
            area.ClearFilledPolysList()
            area.UnFill()
        filler = pcbnew.ZONE_FILLER(self.pcb)
        filler.Fill(self.pcb.Zones())
