#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Screens.Screen import Screen
from enigma import eConsoleAppContainer


class Console2(Screen):
    # TODO move this to skin.xml
    skin = """
        <screen position="100,100" size="550,400" title="Command execution..." >
            <widget name="text" position="0,0" size="550,400" font="Console;14" />
        </screen>"""

    def __init__(self, session, title="Console", cmdlist=None, finishedCallback=None, closeOnSuccess=False):
        Screen.__init__(self, session)
        self.finishedCallback = finishedCallback
        self.closeOnSuccess = closeOnSuccess
        self.errorOcurred = False
        self["text"] = ScrollLabel("")
        self["actions"] = ActionMap(["WizardActions", "DirectionActions"],
                                    {
                                    "ok": self.cancel,
                                    "back": self.cancel,
                                    "up": self["text"].pageUp,
                                    "down": self["text"].pageDown
                                    }, -1)

        self.cmdlist = cmdlist
        self.newtitle = title
        self.onShown.append(self.updateTitle)
        self.container = eConsoleAppContainer()
        self.run = 0
        self.finished = False
        try:  # DreamOS By RAED
            self.container.appClosed.append(self.runFinished)
            self.container.dataAvail.append(self.dataAvail)
        except:
            self.container.appClosed_conn = self.container.appClosed.connect(self.runFinished)
            self.container.dataAvail_conn = self.container.dataAvail.connect(self.dataAvail)
        self.onLayoutFinish.append(self.startRun)

    def updateTitle(self):
        self.setTitle(self.newtitle)

    def startRun(self):
        self["text"].setText(_("Execution progress:") + "\n\n")
        print("Console: executing in run", self.run, " the command:", self.cmdlist[self.run])
        if self.container.execute(self.cmdlist[self.run]):  # start of container application failed...
            self.runFinished(-1)  # so we must call runFinished manual

    def runFinished(self, retval):
        if retval:
            self.errorOcurred = True
        self.run += 1
        if self.run != len(self.cmdlist):
            if self.container.execute(self.cmdlist[self.run]):  # start of container application failed...
                self.runFinished(-1)  # so we must call runFinished manual
        else:
            try:
                lastpage = self["text"].isAtLastPage()
                str = self["text"].getText()
                str += _("Execution finished!!")
                self["text"].setText(str)
                file = open("/tmp/xbmclog.txt", "w")
                file.write(str)
                file.close()
                if lastpage:
                    self["text"].lastPage()
                if self.finishedCallback is not None:
                    self.finishedCallback()
                if not self.errorOcurred and self.closeOnSuccess:
                    self.cancel()
            except:
                str = self["text"].getText()
                str += _("Execution finished!!")
                self["text"].setText(str)
                file = open("/tmp/xbmclog.txt", "w")
                file.write(str)
                file.close()

                self["text"].lastPage()
                if self.finishedCallback is not None:
                    self.finishedCallback()
                if not self.errorOcurred and self.closeOnSuccess:
                    self.cancel()

    def cancel(self):
        if self.run == len(self.cmdlist):
            self.close()
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)

    def dataAvail(self, str):
        try:
            lastpage = self["text"].isAtLastPage()
            self["text"].setText(self["text"].getText() + str)
            if lastpage:
                self["text"].lastPage()
        except:
            self["text"].setText(self["text"].getText() + str)
            self["text"].lastPage()
