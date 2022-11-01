#!/usr/bin/python
# -*- coding: utf-8 -*-

from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
import os

THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"


class XBMChelpinfo(Screen):

    def __init__(self, session, plugin_id=None, sender=None, data=None):
        Screen.__init__(self, session)
        self.skinName = 'XBMCAddonsinfoScreen'
        self.color = "#00060606"
        title = "Help"
        self.sender = sender
        self.data = data
        self.finishedCallback = None
        self.closeOnSuccess = False
        cmdlist = None
        self.plugin_id = plugin_id
        self["title"] = Button(title)
        self["text"] = ScrollLabel("")
        self["actions"] = ActionMap(["WizardActions",
                                     "DirectionActions",
                                     "ColorActions"], {
                                                       "ok": self.cancel,
                                                       "back": self.cancel,
                                                       "up": self["text"].pageUp,
                                                       "down": self["text"].pageDown
                                                       }, -1)
        self.cmdlist = cmdlist
        self.newtitle = title
        self.onShown.append(self.updateTitle)
        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        data = ''
        fpath = THISPLUG + "/Tips.txt"
        if os.path.exists(fpath):
            f = open(fpath, 'r')
            lines = f.readlines()
            for line in lines:
                data = data+line
        else:
            data = "No info available"
            self["text"].setText(data)

    def cancel(self):
        self.close()
