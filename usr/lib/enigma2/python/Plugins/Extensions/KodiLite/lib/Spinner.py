#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.GUIComponent import GUIComponent
from enigma import ePixmap
from enigma import eTimer


class Spinner(GUIComponent):
    def __init__(self, Bilder):
        GUIComponent.__init__(self)

    def SetBilder(self, Bilder):
        self.Bilder = Bilder

    GUI_WIDGET = ePixmap

    def start(self, Bilder):
        self.len = 0
        self.SetBilder(Bilder)
        self.timer = eTimer()
        try:
            self.timer_conn = self.timer.timeout.connect(self.Invalidate)
        except AttributeError:
            self.timer.callback.append(self.Invalidate)
        self.timer.start(100)

    def stop(self):
        try:
            self.timer.stop()
        except:
            pass

    def destroy(self):
        try:
            if self.timer:
                self.timer.callback.remove(self.Invalidate)
        except:
            pass

    def Invalidate(self):
        try:
            if self.instance:
                if self.len >= len(self.Bilder):
                    self.len = 0
                self.instance.setPixmapFromFile(self.Bilder[self.len])
                self.len += 1
        except:
            pass
