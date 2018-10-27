#!/usr/bin/env python
'''
Proximity Sensor Viewing Module
Braedon O'Meara, 10/24/18
'''

import functools
import math
import numpy as np
import os
import time

from ..lib.wx_loader import wx

from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import win_layout

from MAVProxy.modules.lib.mp_menu import MPMenuCheckbox
from MAVProxy.modules.lib.mp_menu import MPMenuItem
from MAVProxy.modules.lib.mp_menu import MPMenuRadio
from MAVProxy.modules.lib.mp_menu import MPMenuSeparator
from MAVProxy.modules.lib.mp_menu import MPMenuSubMenu
from MAVProxy.modules.lib.mp_menu import MPMenuTop

class MPProxViewFrame(wx.Frame):
    """ the main frame of the viewer """
    def __init__(self, state):
        wx.Frame.__init__(self, None, wx.ID_ANY, state.title)
        self.state = state
        state.frame = self
        
        state.relative = True 
        state.grid = False
        state.distance = True

        self.panel = wx.Panel(self)'''MPProxViewPanel(self, state)'''
        self.panel.SetBackgroundColour('black')
        self.last_layout_send = time.time()
        self.Bind(wx.EVT_IDLE, self.on_idle)
        self.Bind(wx.EVT_SIZE, state.panel.on_size)

        self.menu = MPMenuTop([
            MPMenuSubMenu('View', items=[
                MPMenuCheckbox('Relative Orientation\tCtrl+R',
                               'Rotate Objects Around Vehicle',
                               'toggleRelative',
                               checked=state.relative),
                MPMenuCheckbox('Grid \t Ctrl+G',
                               'Enable Grid',
                               'toggleGrid',
                               checked=state.grid),
                MPMenuCheckbox('Distance\tCtrl+D',
                               'toggleDistance',
                               checked=state.distance)])])

        self.SetMenuBar(self.menu.wx_menu())
        self.Bind(wx.EVT_MENU, self.on_menu)

    def on_menu(self, event):
        """handle menu selection"""
        state=self.state
        ret = self.menu.find_selected(event)
        if ret is None:
            return
        ret.call_handler()
        if ret.returnkey == "toggleRelative":
            state.relative = ret.IsChecked()
        elif ret.returnkey == "toggleGrid":
            state.grid = ret.IsChecked()
        elif ret.returnkey == "toggleDistance":
            state.distance = ret.IsChecked()
        state.need_redraw = True

    def on_idle(self, event):
        state = self.state
        time.sleep(0.05)
        now = time.time()
        if now - self.last_layout_send > 1:
            self.last_layout_send = now
            state.event_queue.put(win_layout.get_wx_window_layout(self))

"""
class MPProxViewPanel(wx.Panel)
    """the image panel"""
    def __init__(self, parent, state):
        from MAVProxy.modules.lib import mp_widgets

        wx.Panel.__init__(self, parent)
        self.state = state
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.Bind(wx.EVT_SET_FOCUS, self.on_focus)
        self.redraw_timer.Start(200)
        self.mouse_pos = None
        self.mouse_down = None
        self.click_pos = None
        self.last_click_pos = None

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.mainSizer)

        # display for the main image
       self.imagePanel = mp_widgets.ImagePanel(self, np.zeros((state.height, state.width, 3), dtype=np.uint8))
       self.mainSizer.Add(self.imagePanel, flag=wx.GROW, border=5)
       self.imagePanel.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
       self.imagePanel.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
       self.imagePanel.Bind(wx.EVT_MOUSEWHEEL, self.on_mouse_wheel)

       self.pixmapper = functools.patial(self.pixel_coords)

       self.last_view = None
       self.redraw_view()
       state.frame.Fit()

    def on
"""
