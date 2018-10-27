#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Plan Position Indicator like viewer
Braedon O'Meara
October 2018
'''

import math
import numpy as np
import os
import sys
import time

from MAVProxy.modules.lib import mp_util
from MAVProxy.modules.lib import win_layout
from MAVProxy.modules.lib import multiproc


class MPPpi():
    '''
    a Ppi like viewer widget for displaying obstacle ranges
    '''
    def __init__(self,
                 title='Ppi',
                 width=800,
                 height=600,
                 view_range=10,
                 zoom_increment=1,
                 debug=False):

        self.width = width
        self.height = height
        self.view_range = 10
        self.zoom_increment = 1

        self.title = title
        self.event_queue = multiproc.Queue()
        self.object_queue = multiproc.Queue()
        self.close_window = multiproc.Semaphore()
        self.close_window.acquire()
        self.child = multiproc.Process(target=self.child_task)
        self.child.start()
        self._callbacks = set()

    def child_task(self):
        '''child process - holds all of the GUI elements'''
        mp_util.child_close_fds()

        from MAVProxy.modules.lib import wx_processguard
        from MAVProxy.modules.lib.wx_loader import wx
        from MAVProxy.modules.mavproxy_proxview.mp_ppi_ui import MPPpiFrame

        state = self

        state.layers = {}
        state.info = {}
        state.need_redraw = True

        self.app = wx.App(False)
        self.app.SetExitOnFrameDelete(True)
        self.app.frame = MPPpiFrame(state=self)
        self.app.frame.Show()
        self.app.MainLoop()

    def close(self):
        '''close the window'''
        self.close_window.release()
        count = 0
        while self.child.is_alive() and count < 30:  # 3 seconds to die
            time.sleep(0.1)
            count += 1

        if self.child.is_alive():
            self.child.terminate()

        self.child.join()

    def is_alive(self):
        return self.child.is_alive()

    def add_object(self, obj):
        '''add or update an object in the view'''
        self.object_queue.put(obj)

    def remove_object(self, key):
        '''remove an object in the view by key'''
        self.object_queue.put(PpiRemoveObject(key))

    def hide_object(self, key, hide=True):
        '''hide an object in the view by key'''
        self.object_queue.put(SlipHideObject(key, hide))

    def set_position(self, key_layer='', rotation=0, label=none, colour=None):
        '''move an object in the view'''
        self.object_queue.put(PpiPosition(key, layer, rotation, label, colour))

    def event_count(self):
        '''return number of events waiting to be processed'''
        return self.event_queue.qsize()

    def set_layout(self, layout):
        '''set window layout'''
        self.object_queue.put(layout)

    def get_event(self):
        '''return next event or None'''
        if self.event_queue.qsize() == 0:
            return None
        evt = self.event_queue.get()
        while isinstance(evt, win_layout.WinLayout):
            win_layout.set_layout(evt, self.set_layout)
            if self.event_queue.qsize() == 0:
                return None
            evt = self.event_queue.get()
        return evt

    def add_callback(self, callback):
        '''add a callback for events from the view'''
        self._callbacks.add(callback)

    def check_events(self):
        while self.event_count() > 0:
            event = self.get_event()
            for callback in self._callbacks:
                callback(event)

    def icon(self, filename):
        '''load an icon from the data directory'''
        return PpiIcon.mp_icon(filename)

if __name__ == "__main__":
    multiproc.freeze_support()
    import time

    from optparse import OptionParser
    parser = OptionParser("mp_ppi.py [options]")
    parser.add_option("--debug", action='store_true', default=False, help="Show debug info")
    parser.add_option("--grid", default=True, action='store_false', help="Add Polar Grid")
    parser.add_option("--icon", default=None, help="Show icon")
    parser.add_option("--range", type='float', default=10, help="The radius of the view")
    parser.add_option("--verbose", action="store_true", default=False, help="Show mouse events")
    parser.add_option("--zoom-increment", type='float', default=1, help="Adjust the zoom in/out step size")
    (opts, args) = parser.parse_args()

    ppi = MPPpi( view_range=opts.range,
                 zoom_increment=opts.zoom-increment,
                 debug=opts.debug)

    if opts.grid:
        ppi.add_object(PpiPolar())
    
    if opts.icon:
        icon = cv2.imread(opts.icon)
        ppi.add_object(PpiIcon())

    while ppi.is_alive():
        while ppi.event_count() > 0:
            obj = ppi.get_event()
            if not opts.verbose:
                continue
            if isinstance(obj, PpiMouseEvent):
                print("Mouse event at (X/Y=%u/%u) for %u objects" % (obj.event.X, obj.event.Y, len(obj.selected)))

            if isinstance(obj, PpiKeyEvent):
                print("Key event at %s for %u objects" % (obj.latlon, len(obj.selected)))
        time.sleep(0.1)
