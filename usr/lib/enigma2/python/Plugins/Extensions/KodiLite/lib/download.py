#!/usr/bin/python
# -*- coding: utf-8 -*-

from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.Sources.List import List
from Components.Task import Task, Job
from Components.Task import job_manager, Condition
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Downloader import downloadWithProgress
from enigma import eTimer
from os import path as os_path, system as os_system
from twisted.web.client import downloadPage
import os

total = 0
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/KodiDirect'


def stopdownload():
    cmd1 = "killall -9 rtmpdump"
    cmd2 = "killall -9 wget"
    os.system(cmd1)
    os.system(cmd2)
    return


def getdownloadrtmp(url, filename):
    try:
        parts = []
        url = url.strip()
        parts = url.split(" ")
        if len(parts) < 1:
            link = "'" + url + "'"
            commandstr = "rtmpdump -r " + link + " -o " + filename
            return commandstr
        link = "'" + parts[0] + "'"
        print(link)
        playpath = ""
        swfUrl = ""
        pageUrl = ""
        live = ""

        for item in parts:
            if 'playpath' in item:
                parts2 = item.split("=")
                playpath = " --playpath=" + "'" + parts2[1] + "'"
            if 'swfUrl' in item:
                parts2 = item.split("=")
                swfUrl = " --swfUrl=" + "'" + parts2[1] + "'"

            if 'live' in item:
                parts2 = item.split("=")
                live = " --live=" + "'" + parts2[1] + "'"

            if 'pageUrl' in item:
                parts2 = item.split("=")
                pageUrl = " --pageUrl=" + "'" + parts2[1] + "'"
        commandstr = "rtmpdump -r " + link + playpath + swfUrl + pageUrl + " -o " + filename
        return commandstr
    except:
        link = "'" + url + "'"
        commandstr = "rtmpdump -r " + link + " -o " + filename
        return commandstr


class downloadJobrtmp(Job):

    def __init__(self, cmdline, filename, filetitle):
        Job.__init__(self, "Download: %s" % filetitle)
        self.filename = filename
        self.retrycount = 0
        downloadTaskrtmp(self, cmdline, filename)

    def retry(self):
        assert self.status == self.FAILED
        self.retrycount += 1
        self.restart()

    def cancel(self):
        stopdownload()
        self.abort()


class downloadTaskrtmp(Task):
    ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)

    def __init__(self, job, cmdline, filename):
        Task.__init__(self, job, _("Downloading ..."))
        self.postconditions.append(downloadTaskPostcondition())
        self.setCmdline(cmdline)
        self.filename = filename
        # self.toolbox = job.toolbox
        self.error = None
        self.lasterrormsg = None
        self.end = 300

    def processOutput(self, data):
        if os.path.exists(self.filename):
            filesize = os.path.getsize(self.filename)
            currd = round(float((filesize) / (1024.0 * 1024.0)), 2)
            totald = 600  # round(float((totalbytes) / (1024.0 * 1024.0)),1)
            recvbytes = filesize
            totalbytes = 600 * 1024 * 1024
            self.progress = int(currd)
        try:
            if data.endswith('%)'):
                startpos = data.rfind("sec (") + 5
                if startpos and startpos != -1:
                    self.progress = int(float(data[startpos:-4]))
            elif data.find('%') != -1:
                tmpvalue = data[:data.find("%")]
                tmpvalue = tmpvalue[tmpvalue.rfind(" "):].strip()
                tmpvalue = tmpvalue[tmpvalue.rfind("(") + 1:].strip()

            else:
                Task.processOutput(self, data)
        except:
            Task.processOutput(self, data)

    def processOutputLine(self, line):
        line = line[:-1]
        self.lasterrormsg = line
        if line.startswith("ERROR:"):
            if line.find("RTMP_ReadPacket") != -1:
                self.error = self.ERROR_RTMP_ReadPacket
            elif line.find("corrupt file!") != -1:
                self.error = self.ERROR_CORRUPT_FILE
                os_system("rm -f %s" % self.filename)
            else:
                self.error = self.ERROR_UNKNOWN
        elif line.startswith("wget:"):
            if line.find("server returned error") != -1:
                self.error = self.ERROR_SERVER
        elif line.find("Segmentation fault") != -1:
            self.error = self.ERROR_SEGFAULT

    def afterRun(self):
        return
        if self.getProgress() == 0 or self.getProgress() == 100:
            Notifications.AddNotification(MessageBox, _("Video successfully transfered to your HDD!"), MessageBox.TYPE_INFO, timeout=10)


class downloadTaskPostcondition(Condition):
    RECOVERABLE = True

    def check(self, task):
        return True
        if task.returncode == 0 or task.error is None:
            return True
        else:
            return False

    def getErrorMessage(self, task):
        return {task.ERROR_CORRUPT_FILE: _("Video Download Failed!\n\nCorrupted Download File:\n%s" % task.lasterrormsg),
                task.ERROR_RTMP_ReadPacket: _("Video Download Failed!\n\nCould not read RTMP-Packet:\n%s" % task.lasterrormsg),
                task.ERROR_SEGFAULT: _("Video Download Failed!\n\nSegmentation fault:\n%s" % task.lasterrormsg),
                task.ERROR_SERVER: _("Video Download Failed!\n\nServer returned error:\n%s" % task.lasterrormsg),
                task.ERROR_UNKNOWN: _("Video Download Failed!\n\nUnknown Error:\n%s" % task.lasterrormsg)}[task.error]


class downloadJob(Job):
    def __init__(self, url, file, title):
        Job.__init__(self, title)
        downloadTask(self, url, file)


class downloadTask(Task):
    global total
    total = 0

    def __init__(self, job, url, file):
        Task.__init__(self, job, ("download task"))
        self.end = 100
        self.url = url
        self.local = file

    def prepare(self):
        self.error = None

    def run(self, callback):
        self.callback = callback
        self.download = downloadWithProgress(self.url, self.local)
        self.download.addProgress(self.http_progress)
        self.download.start().addCallback(self.http_finished).addErrback(self.http_failed)

    def http_progress(self, recvbytes, totalbytes):
        currd = round(float((recvbytes) / (1024.0 * 1024.0)), 2)
        totald = round(float((totalbytes) / (1024.0 * 1024.0)), 1)
        self.progress = int(self.end * recvbytes / float(totalbytes))

    def http_finished(self, string=""):
        Task.processFinished(self, 0)
        try:
            filetitle = os_path.basename(self.local)
        except:
            filetile = ''

    def http_failed(self, failure_instance=None, error_message=""):
        if error_message == "" and failure_instance is not None:
            error_message = failure_instance.getErrorMessage()
            Task.processFinished(self, 1)
            try:
                filetitle = os_path.basename(self.local)
            except:
                filetile = ''

    def afterRun(self):
        return


class downloadTasksScreen(Screen):

    def __init__(self, session, plugin_path, tasklist):
        Screen.__init__(self, session)
        self.skinName = 'XBMCAddonsdownloadtasks'
        self.session = session
        self.tasklist = tasklist
        self["tasklist"] = List(self.tasklist)
        self["key_red"] = Button("Exit")
        self["key_yellow"] = Button(" ")
        self["key_green"] = Button("Details")
        self["key_blue"] = Button("Downloads")
        self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions", "MediaPlayerActions", "ColorActions"],
                                      {'blue': self.showfiles,
                                       "ok": self.keyOK,
                                       "green": self.keyOK,
                                       "back": self.keyCancel,
                                       "red": self.keyCancel}, -1)

        self["title"] = Label()
        self.onLayoutFinish.append(self.layoutFinished)
        self.onShown.append(self.setWindowTitle)
        self.onClose.append(self.__onClose)
        self.Timer = eTimer()
        self.Timer.callback.append(self.TimerFire)

    def showfiles(self):
        from XBMCAddonsMediaExplorer import XBMCAddonsMediaExplorer
        self.session.open(XBMCAddonsMediaExplorer)

    def __onClose(self):
        del self.Timer

    def layoutFinished(self):
        self["title"].setText(_("XBMCAddons current downloading media "))
        self.Timer.startLongTimer(2)

    def TimerFire(self):
        self.Timer.stop()
        self.rebuildTaskList()

    def rebuildTaskList(self):
        self.tasklist = []
        for job in job_manager.getPendingJobs():
            self.tasklist.append((job, job.name, job.getStatustext(), int(100 * job.progress / float(job.end)), str(100 * job.progress / float(job.end)) + "%"))
        self['tasklist'].setList(self.tasklist)
        self['tasklist'].updateList(self.tasklist)
        self.Timer.startLongTimer(2)

    def setWindowTitle(self):
        self.setTitle(_("XBMCAddons current downloading media"))

    def keyOK(self):
        current = self["tasklist"].getCurrent()
        if current:
            job = current[0]
            from TaskView2 import JobViewNew
            self.session.openWithCallback(self.JobViewCB, JobViewNew, job)

    def JobViewCB(self, why):
        pass

    def keyCancel(self):
        self.close()

    def keySave(self):
        self.close()


def viewdownloads(session, plugin_path=None):
    tasklist = []
    for job in job_manager.getPendingJobs():
        tasklist.append((job, job.name, job.getStatustext(), int(100 * job.progress / float(job.end)), str(100 * job.progress / float(job.end)) + "%"))
    session.open(downloadTasksScreen, plugin_path, tasklist)


def startdownload(session, answer='download', myurl=None, filename=None, title=None):
    url = myurl
    if answer == "download":
        svfile = filename
    if "rtmp" not in url:
        if url.startswith("https"):
            downloadPage(url, svfile).addErrback(showError)
        else:
            # urtmp = "wget -O '" + svfile + "' -c '" + url + "'"
            job_manager.AddJob(downloadJob(url, svfile, title))
    else:
        params = url
        svfile = svfile.replace(" ", "").strip()
        params = params.replace(" swfVfy=", " --swfVfy ")
        params = params.replace(" playpath=", " --playpath ")
        params = params.replace(" app=", " --app ")
        params = params.replace(" pageUrl=", " --pageUrl ")
        params = params.replace(" tcUrl=", " --tcUrl ")
        params = params.replace(" swfUrl=", " --swfUrl ")
        cmd = "rtmpdump -r " + params + " -o '" + svfile + "'"

        job_manager.AddJob(downloadJobrtmp(cmd, svfile, title))

    currentjob = None
    from TaskView2 import JobViewNew
    for job in job_manager.getPendingJobs():
        currentjob = job
        pass  # print "currentjob =", currentjob
        if currentjob is not None:
            session.open(JobViewNew, currentjob)
        elif answer == "view":
            pass  # print "408",answer
        tasklist = []
        for job in job_manager.getPendingJobs():
                tasklist.append((job, job.name, job.getStatustext(), int(100 * job.progress / float(job.end)), str(100 * job.progress / float(job.end)) + "%"))
        session.open(downloadTasksScreen, plugin_path, tasklist)


def showError(error):
    pass  # print "ERROR :", error
