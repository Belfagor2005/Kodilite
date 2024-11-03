#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from ..plugin import subsx
from .. import Utils

from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from Components.ServiceEventTracker import InfoBarBase, ServiceEventTracker
from Components.Sources.List import List
from Components.Task import Task, Job, job_manager as JobManager
from Components.config import config
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBarGenerics import InfoBarMenu, InfoBarSeek, InfoBarAudioSelection, \
    InfoBarSubtitleSupport, InfoBarSummarySupport, InfoBarServiceErrorPopupSupport, InfoBarNotifications
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.TaskView import JobView
from ServiceReference import ServiceReference
from enigma import eServiceReference
from enigma import eTimer
from enigma import getDesktop
from enigma import iPlayableService
from skin import parseColor
from twisted.web.client import downloadPage
import os
import re
import sys
from Plugins.Extensions.KodiLite.lib.TaskView2 import JobViewNew

global subsx


# 20221030 recoded Lululla
# 20220111 utils.py bouquet make PY3
# 20210914 utils.py showlist b removed
# 20210902 hlsclient3.py for PY3
# 20210821 Playoptions Start1 and Playvids2X2 youtube entries deleted
# 20200425 5002 option removed from two class playvid and SREF changed in Playoption & playvids2##
# 20190520 play with exteplayer option added
# 20181226 5002 option removed from two class playvid
# 20180903 new def playproxy for m3u8 to play via f4mproxy - for itv
# 20180829 changes re playhls and 5002 option for startecmob (mobdro)
# 20180618 lines 1134 and 1380
# 20180609
# #############################################################
#                                                             #
#   Mainly Coded by pcd, July 2013                            #
#                                                             #
# #############################################################

PY2 = False
PY3 = False
PY34 = False
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)
print("sys.version_info =", sys.version_info)
Credits = " Linuxsat-support Forum"
THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
SREF = " "
SERVICEAPP = 0

f1 = open("/tmp/py.txt", "a")
msg = "xUtils PY3 = " + str(PY3) + " xUtils PY2 = " + str(PY2)
f1.write(msg)
f1.close()


if PY3:
    from http.client import HTTPConnection
    from urllib.parse import quote
    from urllib.request import urlretrieve
else:
    from httplib import HTTPConnection
    from urllib import quote
    from urllib import urlretrieve


HTTPConnection.debuglevel = 1


# NOSS = 0

if subsx is True:
    try:
        from Plugins.Extensions.SubsSupport import SubsSupport, SubsSupportStatus
        subsx = True
    except ImportError:
        subsx = False

        class SubsSupport(object):
            def __init__(self, *args, **kwargs):
                pass

        class SubsSupportStatus(object):
            def __init__(self, *args, **kwargs):
                pass

else:
    subsx = False

    class SubsSupport(object):
        def __init__(self, *args, **kwargs):
            pass

    class SubsSupportStatus(object):
        def __init__(self, *args, **kwargs):
            pass


std_headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Language': 'en-us,en;q=0.5'}


class Getvid(Screen):

    def __init__(self, session, name, url, desc):
        Screen.__init__(self, session)
        self.skinName = "Showrtmp"
        title = "Play"
        self.setTitle(title)
        self.list = []
        self["list"] = List(self.list)
        self["list"] = Utils.tvList([])
        self["info"] = Label()
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button(_("Download"))
        self["key_yellow"] = Button(_("Play"))
        self["key_blue"] = Button(_("Stop Download"))
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
                                         {"red": self.close,
                                          "green": self.okClicked,
                                          "yellow": self.play,
                                          "info": self.showinfo,
                                          "blue": self.stopdl,
                                          "cancel": self.cancel,
                                          "ok": self.okClicked}, -2)
        self.icount = 0
        self.name = name
        self.url = url
        self.desc = desc
        txt = _("Must do (1) Download  (2) Play.\n\n") + self.name + "\n\n" + desc
        self["info"].setText(txt)
        self.sref = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.getrtmp)

    def showinfo(self):
        return

    def getrtmp(self):
        fold = str(config.plugins.kodiplug.cachefold.value) + "/"
        fname = "savedvid"
        svfile = fold + "/" + fname + ".mpg"
        self.svf = svfile
        if "rtmp" not in self.url:
            self.urtmp = "wget -O '" + svfile + "' -c '" + self.url + "'"
        else:
            params = self.url
            pass  # print "params A=", params
            params = params.replace(" swfVfy=", " --swfVfy ")
            params = params.replace(" playpath=", " --playpath ")
            params = params.replace(" app=", " --app ")
            params = params.replace(" pageUrl=", " --pageUrl ")
            params = params.replace(" tcUrl=", " --tcUrl ")
            params = params.replace(" swfUrl=", " --swfUrl ")
            pass  # print "params B=", params
            self.urtmp = "rtmpdump -r " + params + " -o '" + svfile + "'"

    def okClicked(self):
        self["info"].setText("Downloading ....")
        fold = str(config.plugins.kodiplug.cachefold.value) + "/xbmc/vid"
        fname = "savedvid"
        svfile = fold + "/" + fname + ".mpg"
        self.svf = svfile
        cmd = "rm " + svfile
        os.system(cmd)
        JobManager.AddJob(downloadJob(self, self.urtmp, svfile, 'Title 1'))
        self.LastJobView()

    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job
        if currentjob is not None:
            self.session.open(JobView, currentjob)

    def play(self):
        if os.path.exists(self.svf):
            # pass  # print "Showrtmp here 2"
            svfile = self.svf
            desc = self.desc
            self.session.open(Playgo, self.name, svfile, desc)
            # runKDplayer(self.session, name, svfile, desc)
        else:
            txt = _("Download Video first.")
            self["info"].setText(txt)

    def cancel(self):
        self.session.nav.playService(self.sref)
        self.close()

    def stopdl(self):
        self.session.nav.playService(self.sref)
        cmd1 = "killall -9 rtmpdump"
        cmd2 = "killall -9 wget"
        os.system(cmd1)
        os.system(cmd2)

    def keyLeft(self):
        self["list"].left()

    def keyRight(self):
        self["list"].right()

    def keyNumberGlobal(self, number):
        # pass  # print "pressed", number
        self["list"].number(number)


class Getvid2(Screen):

    def __init__(self, session, name, url, desc):
        Screen.__init__(self, session)
        self.skinName = "Showrtmp"
        self['list'] = MenuList([])
        self['info'] = Label()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Download'))
        self['key_yellow'] = Button(_('Play'))
        self['key_blue'] = Button(_('Stop Download'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'],
                                         {'red': self.close,
                                          'green': self.okClicked,
                                          'yellow': self.play,
                                          'blue': self.stopDL,
                                          'cancel': self.cancel,
                                          'ok': self.openTest}, -2)
        self.icount = 0
        self.bLast = 0
        cachefold = str(config.plugins.kodiplug.cachefold.value)
        self.svfile = cachefold + "/xbmc/vid/savedfile.mpg"
        txt = _("Play direct OR Download and Play")
        self['info'].setText(txt)
        self.updateTimer = eTimer()
        try:
            self.updateTimer_conn = self.updateTimer.timeout.connect(self.updateStatus)
        except AttributeError:
            self.updateTimer.callback.append(self.updateStatus)
        self.updateTimer.start(2000)
        self.updateStatus()
        self.name = name
        self.url = url
        self.desc = desc
        self.sref = self.session.nav.getCurrentlyPlayingServiceReference()

    def openTest(self):
        vid = self.name
        infotxt = _('Video selected :-\n\n\n') + vid
        self['info'].setText(infotxt)

    def play(self):
        desc = self.desc
        if self.icount == 0:
            url = self.url
            name = self.name
        else:
            url = self.svfile
            name = "Video"
        self.session.open(Playgo, name, url, desc)
        # runKDplayer(self.session,name,url,desc)

    def okClicked(self):
        cmd = 'rm ' + self.svfile
        os.system(cmd)
        self.icount = 1
        JobManager.AddJob(downloadJob(self, "wget -O '" + self.svfile + "' -c '" + self.url + "'", self.svfile, 'Title 1'))

    def updateStatus(self):
        if not os.path.exists(self.svfile):
            return
        if self.icount == 0:
            return
        b1 = os.path.getsize(self.svfile)
        b = b1 / 1000
        if b == self.bLast:
            infotxt = 'Download Complete....' + str(b)
            self['info'].setText(infotxt)
            return
        self.bLast = b
        infotxt = (_('Downloading....')) + str(b) + ' kb'
        self['info'].setText(infotxt)

    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job
        if currentjob is not None:
            self.session.open(JobView, currentjob)

    def cancel(self):
        self.session.nav.playService(self.sref)
        self.close()

    def stopDL(self):
        cmd = 'killall -9 wget &'
        os.system(cmd)

    def keyLeft(self):
        self['list'].left()

    def keyRight(self):
        self['list'].right()

    def keyNumberGlobal(self, number):
        self['list'].number(number)


class Playoptions(Screen):

    def __init__(self, session, name, url, desc):
        Screen.__init__(self, session)
        self.skinName = "Ploptions"
        self.hostaddr = ""
        self.list = []
        self["list"] = List(self.list)
        self["list"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Select'))
        self['key_yellow'] = Button(_('Play'))
        self['key_blue'] = Button(_('Stop Download'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.close,
                                                                                                'green': self.okClicked,
                                                                                                'yellow': self.start1,
                                                                                                'blue': self.stopDL,
                                                                                                'cancel': self.cancel,
                                                                                                'ok': self.okClicked}, -2)
        self.icount = 0
        self.bLast = 0
        self.useragent = "QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)"
        self.svfile = " "
        self.name = name.replace('-', ' ').replace('+', ' ').replace('_', ' ')
        self.url = url
        self.desc = desc
        i = 0
        while i < 11:
            self.list.append(i)
            i = i + 1
        self.list[0] = (_("Play"))
        self.list[1] = (_("Play with exteplayer (needs systemplugin serviceapp installed)"))
        self.list[2] = (_("Play with tsplayer"))
        self.list[3] = (_("Play with hlsplayer"))
        self.list[4] = (_("Play with f4mproxy"))
        self.list[5] = (_("Play with vlc (set vlc server ip in Config)"))
        self.list[6] = (_("Download"))
        self.list[7] = (_("Stop download"))
        self.list[8] = (_("Add to favorites"))
        self.list[9] = (_("Add to bouquets"))
        self.list[10] = (_("Current Downloads"))
        if "/tmp/vid.txt" in self.url:
            file1 = "/tmp/vid.txt"
            f1 = open(file1, "r + ")
            txt1 = f1.read()
            n1 = txt1.find("http", 0)
            n2 = txt1.find("\n", n1)
            txt2 = txt1[n1:n2]
            self.url = txt2
        self.urlmain = self.url
        n1 = self.url.find("|", 0)
        if n1 > -1:
            self.url = self.url[:n1]
        self.updateTimer = eTimer()
        try:
            self.updateTimer_conn = self.updateTimer.timeout.connect(self.updateStatus)
        except AttributeError:
            self.updateTimer.callback.append(self.updateStatus)
        self['info'].setText(" ")
        self.sref = self.session.nav.getCurrentlyPlayingServiceReference()
        if config.plugins.kodiplug.directpl.value is True:
            self.onShown.append(self.start1)
        elif "hds://" in url:
            self.onShown.append(self.start3)
        elif self.url.startswith("stack://"):
            self.onShown.append(self.start4)
        else:
            pass  # print "Here in no directpl"
            self.onLayoutFinish.append(self.start)

    def start1(self):
        desc = self.desc
        if "/tmp/vid.txt" in self.url:
            self.start5()
            self.cancel()
        elif "f4m" in self.url:
            from F4mProxy import f4mProxyHelper
            fplayer = f4mProxyHelper()
            url = self.url
            name = self.name
            self.url = fplayer.playF4mLink(url, name, streamtype='HDS', direct="no")
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()
        else:
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()

    def playproxy(self):
        desc = self.desc
        if "m3u8" in self.url:
            from F4mProxy import f4mProxyHelper
            fplayer = f4mProxyHelper()
            url = self.url
            name = self.name
            self.url = fplayer.playF4mLink(url, name, streamtype='HLS', direct="no")
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()

        elif "f4m" in self.url:
            from F4mProxy import f4mProxyHelper
            fplayer = f4mProxyHelper()
            url = self.url
            name = self.name
            self.url = fplayer.playF4mLink(url, name, streamtype='HDS', direct="no")
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()
        else:
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()

    def playts(self):
        desc = self.desc
        if ".ts" in self.url:
            url = self.url
            try:
                os.remove("/tmp/hls.avi")
            except:
                pass
            cmd = 'python "%s/lib/tsclient.py" "%s" "1" &' % (THISPLUG, url)
            os.system(cmd)
            os.system('sleep 3')
            self.url = '/tmp/hls.avi'
            self.session.open(Playgo, self.name, self.url, desc)
        else:
            self.session.open(Playgo, self.name, self.url, desc)

    def start3(self):
        from stream import GreekStreamTVList
        self.session.open(GreekStreamTVList, streamFile="/tmp/stream.xml")
        self.close()

    def start4(self):
        from Playlist import Playlist
        self.session.open(Playlist, self.url)
        self.close()

    def start5(self):
        desc = self.desc
        file1 = "/tmp/vid.txt"
        f1 = open(file1, "r + ")
        txt1 = f1.read()
        self.url = txt1
        self.session.open(Playgo, self.name, self.url, desc)
        self.close()

    def start(self):
        infotxt = (_("Selected video: ")) + self.name + (_("\n\nDownload as :")) + self.getlocal_filename()[0]
        self['info'].setText(infotxt)
        Utils.showlist(self.list, self['list'])

    def openTest(self):
        pass

    def playhls(self):
        print("Here in utils-py play self.icount =", self.icount)
        desc = self.desc
        if self.icount == 0:
            print("Here in utils-py play self.urlmain =", self.urlmain)
            url1 = self.urlmain
            n1 = url1.find("|", 0)
            print("Here in hlsclient-py n1, url1 =", n1, url1)
            if n1 > -1:
                url = url1[:n1]
                print("Here in hlsclient-py url =", url)
                header = url1[(n1 + 1):]
                print("Here in hlsclient-py header = ", header)
            else:
                url = url1
                header = ""
            name = self.name
            if ".ts" in url:
                url = url.replace(".ts", ".m3u8")
            else:
                print("shahid url = ", url)
                try:
                    os.remove("/tmp/hls.avi")
                except:
                    pass
                if PY3:
                    cmd = 'python "%s/lib/hlsclient3.py" "%s" "1" "%s" + &' % (THISPLUG, url, header)
                else:
                    cmd = 'python "%s/lib/hlsclient.py" "%s" "1" "%s" + &' % (THISPLUG, url, header)

                print("hls cmd = ", cmd)
                os.system(cmd)
                os.system('sleep 5')
                url = '/tmp/hls.avi'
        else:
            url = self.svfile
            name = "Video"
        # from .. import Player
        self.session.open(Playgo, name, url, desc)

    def getlocal_filename(self):
        fold = str(config.plugins.kodiplug.cachefold.value) + "/"
        name = self.name.replace("/media/hdd/xbmc/vid/", "")
        name = name.replace(" ", "-")
        pattern = r'[a-zA-Z0-9\-]'
        input = name
        output = ''.join(re.findall(pattern, input))
        self.name = output
        if self.url.endswith("mp4"):
            svfile = fold + self.name + ".mp4"
        elif self.url.endswith("flv"):
            svfile = fold + self.name + ".flv"
        elif self.url.endswith("avi"):
            svfile = fold + self.name + ".avi"
        elif self.url.endswith("ts"):
            svfile = fold + self.name + ".ts"
        else:
            svfile = fold + self.name + ".mpg"
        filetitle = os.path.split(svfile)[1]
        return svfile, filetitle

    def playexte(self):
        global SERVICEAPP
        SERVICEAPP = 1
        self.start1()

    def okClicked(self):
        idx = self["list"].getSelectionIndex()
        if idx == 0:
            self.start1()
        elif idx == 1:
            self.playexte()
        elif idx == 2:
            self.playts()
        elif idx == 3:
            self.playhls()
        elif idx == 4:
            self.playproxy()
        elif idx == 5:
            import urllib
            vlcip = config.plugins.kodiplug.vlcip.value
            self.hostaddr = "http://" + vlcip + ":8080"
            url = quote(self.url, safe='')
            cmd = self.hostaddr + "/requests/status.xml?command=in_play&input=" + url + "&option=%3Asout%3D%23transcode%7Bvcodec%3Dmp2v%2Cvb%3D2000%2Cvenc%3Dffmpeg%2Cfps%3D25%2Cvfilter%3Dcanvas%7Bwidth%3D352%2Cheight%3D288%2Caspect%3D4%3A3%7D%2Cacodec%3Dmp2a%2Cab%3D128%2Cchannels%3D2%2Csamplerate%3D0%7D%3Astd%7Baccess%3Dhttp%2Cmux%3Dts%7Bpid-video%3D68%2Cpid-audio%3D69%7D%2Cdst%3D%2Fdream.ts%7D&option=%3Asout-all&option=%3Asout-keep"
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.hostaddr, '', 'Admin')
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(handler)
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_stop")
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_empty")
            f = opener.open(cmd)
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_play")
            vurl = self.hostaddr + "/dream.ts"
            desc = self.desc
            self.session.open(Playgo, self.name, vurl, desc)

        elif idx == 6:
            if "#header#" in self.url:
                self.svfile, self.filetitle = self.getlocal_filename()
                cmd1 = "rm " + self.svfile
                os.system(cmd1)
                n1 = self.url.find("#header#", 0)
                header = self.url[(n1 + 8):]
                self.url = self.url[:n1]
                cmd = 'wget -O "' + self.svfile + '" --header="' + header + '" --user-agent="Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" "' + self.url + '" &'
                os.system(cmd)
                self.icount = 1
                return

            if "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url:
                file1 = "/tmp/vid.txt"
                f1 = open(file1, "r + ")
                txt1 = f1.read()
                self.url = txt1
                self.svfile, self.filetitle = self.getlocal_filename()
                downloadPage(self.url, self.svfile).addErrback(self.showError)
                self.updateTimer.start(2000)

            elif ".m3u8" in self.url:
                url1 = self.urlmain
                n1 = url1.find("|", 0)
                if n1 > -1:
                    self.url = url1[:n1]
                    header = url1[(n1 + 1):]
                else:
                    self.url = url1
                    header = ""
                self.svfile, self.filetitle = self.getlocal_filename()
                cmd = 'python "%s/lib/hlsdownld.py" "%s" "1" "%s" "%s" + &' % (THISPLUG, self.url, self.svfile, header)
                os.system(cmd)
                self.icount = 1

            elif self.url.startswith("https"):
                self.icount = 1
                self.svfile, self.filetitle = self.getlocal_filename()
                self.filetitle = self.filetitle.replace("-", "")
                if PY3:
                    urlretrieve(self.url, self.svfile, reporthook=self.download_progress_hook)
                    print("Done")
                else:
                    downloadPage(self.url, self.svfile).addErrback(self.showError)
                    self.updateTimer.start(2000)

            elif "rtmp" in self.url:
                params = self.url
                params = "'" + params + "'"
                params = params.replace(" swfVfy=", "' --swfVfy '")
                params = params.replace(" playpath=", "' --playpath '")
                params = params.replace(" app=", "' --app '")
                params = params.replace(" pageUrl=", "' --pageUrl '")
                params = params.replace(" tcUrl=", "' --tcUrl '")
                params = params.replace(" swfUrl=", "' --swfUrl '")
                self.svfile, self.filetitle = self.getlocal_filename()
                self.urtmp = "rtmpdump -r " + params + " -o '" + self.svfile + "'"
                self["info"].setText(_("Start downloading"))
                self.icount = 1
                cmd = "rm " + self.svfile
                os.system(cmd)
                JobManager.AddJob(downloadJob(self, self.urtmp, self.svfile, 'Title 1'))
                self.LastJobView()

            else:
                self.icount = 1
                self.svfile, self.filetitle = self.getlocal_filename()
                self.filetitle = self.filetitle.replace("-", "")
                if PY3:
                    urlretrieve(self.url, self.svfile, reporthook=self.download_progress_hook)
                    print("Done")
                else:
                    downloadPage(self.url, self.svfile).addErrback(self.showError)
                    self.updateTimer.start(2000)

        elif idx == 7:
            self.stopDL()

        elif idx == 8:
            try:
                from Plugins.Extensions.KodiLite.lib.favorites import addfavorite
            except:
                from .favorites import addfavorite
            try:
                addon_id = os.path.split(os.path.split(sys.argv[0])[0])[1]
                result = addfavorite(addon_id, self.name, self.url)
            except:
                result = False
            if result is False:
                self.session.open(MessageBox, _("Failed to add to favorites."), MessageBox.TYPE_ERROR, timeout=4)
            else:
                self.session.open(MessageBox, _("Item added successfully to favorites."), MessageBox.TYPE_INFO, timeout=4)
        elif idx == 9:
            try:
                error = stream2bouquet(self.url, self.name, 'kodilite')
            except:
                error = (_("Failed to add stream to bouquet"))
            if error == 'none':
                self.session.open(MessageBox, _((_('Stream added to ')) + 'XBMCAddons_streams ' + (_('bouquet\nrestart enigma to refresh bouquets'))), MessageBox.TYPE_INFO, timeout=10)
            else:
                self.session.open(MessageBox, _("Failed to add stream to bouquet."), MessageBox.TYPE_ERROR, timeout=4)

        elif idx == 10:
            self.ebuf = []
            Downloadpath = str(config.plugins.kodiplug.cachefold.value)
            print("Downloadpath =", Downloadpath)
            if Downloadpath.endswith('/'):
                pass
            else:
                Downloadpath = Downloadpath + '/'
            print("Downloadpath 2 =", Downloadpath)
            for root, dirs, files in os.walk(Downloadpath):
                for name in files:
                    x = name
                    if x.endswith(".mpg") or x.endswith(".ts") or x.endswith(".mp3") or x.endswith(".mp4") or x.endswith(".avi") or x.endswith(".flv") or x.endswith(".wmv"):
                        name1 = Downloadpath + name
                        self.ebuf.append((_(name1), name1))
                        print("self.ebuf =", self.ebuf)
                    else:
                        continue
            self.session.openWithCallback(self.playChoice, ChoiceBox, title="Please Select", list=self.ebuf)

    def playChoice(self, res):
        if res is None:
            self.close()
        else:
            self.ebuf2 = []
            self.ebuf2.append((_("Play"), res[1]))
            self.ebuf2.append((_("Delete"), res[1]))
            self.session.openWithCallback(self.playChoice2, ChoiceBox, title="Please Select", list=self.ebuf2)

    def playChoice2(self, res):
        if res is None:
            self.close()
        elif "play" in res[0].lower():
            print("In playChoice res =", res)
            url = res[1]
            name = url
            desc = self.desc
            self.session.open(Playgo, name, url, desc)
            self.close()
        else:
            cmd = "rm -rf " + res[1]
            os.system(cmd)
            self.close()

    def showError(self, error):
        pass

    def updateStatus(self):
        if self.pop == 1:
            try:
                ptxt = self.p.read()
                if "data B" in ptxt:
                    n1 = ptxt.find("data B", 0)
                    n2 = ptxt.find("&url", n1)
                    n3 = ptxt.find("\n", n2)
                    url = ptxt[(n2 + 5):n3]
                    url = url.replace("AxNxD", "&")
                    self.url = url.replace("ExQ", "=")
                    desc = self.desc
                    self.session.open(Playgo, self.name, self.url, desc)
                    self.close()
                    self.updateTimer.stop()
            except:
                self.openTest()
        else:
            if not os.path.exists(self.svfile):
                self.openTest()
                return

            if self.icount == 0:
                self.openTest()
                return
            b1 = os.path.getsize(self.svfile)
            b = b1 / 1000
            if b == self.bLast:
                infotxt = _('Download Complete....') + str(b)
                self['info'].setText(infotxt)
                return
            self.bLast = b
            infotxt = _('Downloading....') + str(b) + ' kb'
            self['info'].setText(infotxt)

    def download_progress_hook(self, count, blockSize, totalSize):
        b1 = count * blockSize
        if (b1 > totalSize) or (b1 == totalSize):
            infotxt = _('Download Complete....') + str(totalSize)
            self['info'].setText(infotxt)
        else:
            infotxt = _('Downloading....') + str(b1)
            self['info'].setText(infotxt)

    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job
        if currentjob is not None:
            self.session.open(JobViewNew, currentjob)

    def cancel(self):
        try:
            import urllib
            vlcip = config.plugins.kodiplug.vlcip.value
            self.hostaddr = "http://" + vlcip + ":8080"
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.hostaddr, '', 'Admin')
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(handler)
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_stop")
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_empty")
        except:
            pass
        if os.path.exists("/tmp/hls.avi"):
            os.remove("/tmp/hls.avi")
        self.close()

    def stopDL(self):
        cmd = "rm -f " + self.svfile
        os.system(cmd)
        self.session.nav.playService(self.sref)
        cmd1 = "killall -9 rtmpdump"
        cmd2 = "killall -9 wget"
        os.system(cmd1)
        os.system(cmd2)
        self['info'].setText("Current download task stopped")
        self.close()

    def keyLeft(self):
        self['list'].left()

    def keyRight(self):
        self['list'].right()

    def keyNumberGlobal(self, number):
        self['list'].number(number)


class TvInfoBarShowHide():
    """ InfoBar show/hide control,
        accepts toggleShow and hide actions,
        might start
        fancy animations.
    """
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"], {"toggleShow": self.OkPressed,
                                                                         "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(self.doTimerHide)
        except:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(5000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def OkPressed(self):
        self.toggleShow()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return
        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def serviceStarted(self):
        if self.execing:
            if config.usage.show_infobar_on_zap.value:
                self.doShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            idx = config.usage.infobar_timeout.index
            if idx:
                self.hideTimer.start(idx * 1500, True)

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def lockShow(self):
        try:
            self.__locked += 1
        except:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()

    def debug(obj, text=""):
        print(text + " %s\n" % obj)


class Playgo(InfoBarBase, TvInfoBarShowHide, InfoBarMenu, InfoBarSeek, InfoBarAudioSelection, InfoBarSubtitleSupport, InfoBarSummarySupport, InfoBarServiceErrorPopupSupport, SubsSupportStatus, InfoBarNotifications, Screen):

    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 5000

    def __init__(self, session, name, url, desc):
        global streaml
        Screen.__init__(self, session)
        global _session
        _session = session
        self.session = session
        self.skinName = 'MoviePlayer'
        streaml = False
        self.allowPiP = False
        self.service = None
        self.url = url
        self.desc = desc
        print("******** name 3 ******* %s" % name)
        self.name = Utils.decodeHtml(name)
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        InfoBarBase.__init__(self, steal_current_service=True)
        InfoBarMenu.__init__(self)
        InfoBarSeek.__init__(self, actionmap="InfobarSeekActions")
        TvInfoBarShowHide.__init__(self)
        InfoBarAudioSelection.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        InfoBarSummarySupport.__init__(self)
        InfoBarServiceErrorPopupSupport.__init__(self)
        InfoBarNotifications.__init__(self)
        if subsx is True:
            SubsSupport.__init__(self, searchSupport=True, embeddedSupport=True)
            SubsSupportStatus.__init__(self)
        try:
            self.init_aspect = int(self.getAspect())
        except:
            self.init_aspect = 0
        self.new_aspect = self.init_aspect

        self['actions'] = ActionMap(['MoviePlayerActions',
                                     'MovieSelectionActions',
                                     'MediaPlayerActions',
                                     'EPGSelectActions',
                                     'MediaPlayerSeekActions',
                                     'SetupActions',
                                     'ColorActions',
                                     'InfobarShowHideActions',
                                     'InfobarActions',
                                     'InfobarSeekActions'], {'epg': self.showIMDB,
                                                             'info': self.showIMDB,
                                                             'tv': self.cicleStreamType,
                                                             'stop': self.leavePlayer,
                                                             'cancel': self.cancel,
                                                             'back': self.cancel}, -1)
        if '8088' in str(self.url):
            self.onFirstExecBegin.append(self.slinkPlay)
        else:
            self.onFirstExecBegin.append(self.cicleStreamType)
        self.onClose.append(self.cancel)

    def getAspect(self):
        return AVSwitch().getAspectRatioSetting()

    def getAspectString(self, aspectnum):
        return {0: '4:3 Letterbox',
                1: '4:3 PanScan',
                2: '16:9',
                3: '16:9 always',
                4: '16:10 Letterbox',
                5: '16:10 PanScan',
                6: '16:9 Letterbox'}[aspectnum]

    def setAspect(self, aspect):
        map = {0: '4_3_letterbox',
               1: '4_3_panscan',
               2: '16_9',
               3: '16_9_always',
               4: '16_10_letterbox',
               5: '16_10_panscan',
               6: '16_9_letterbox'}
        config.av.aspectratio.setValue(map[aspect])
        try:
            AVSwitch().setAspectRatio(aspect)
        except:
            pass

    def av(self):
        temp = int(self.getAspect())
        temp = temp + 1
        if temp > 6:
            temp = 0
        self.new_aspect = temp
        self.setAspect(temp)

    def showIMDB(self):
        idx = self.index
        text_clear = self.names[idx]
        # if returnIMDB(text_clear):
        print('show imdb/tmdb', text_clear)

    def slinkPlay(self, url):
        name = self.name
        ref = "{0}:{1}".format(url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def openTest(self, servicetype, url):
        name = self.name
        ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
        print('reference:   ', ref)
        if streaml is True:
            url = 'http://127.0.0.1:8088/' + str(url)
            ref = "{0}:0:1:0:0:0:0:0:0:0:{1}:{2}".format(servicetype, url.replace(":", "%3a"), name.replace(":", "%3a"))
            print('streaml reference:   ', ref)

        print('final reference:   ', ref)
        sref = eServiceReference(ref)
        sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(sref)

    def cicleStreamType(self):
        global streml
        # streaml = False
        # from itertools import cycle, islice
        self.servicetype = '4097'
        print('servicetype1: ', self.servicetype)
        url = str(self.url)
        if str(os.path.splitext(self.url)[-1]) == ".m3u8":
            if self.servicetype == "1":
                self.servicetype = "4097"
        # currentindex = 0
        # streamtypelist = ["4097"]
        # # if "youtube" in str(self.url):
            # # self.mbox = self.session.open(MessageBox, _('For Stream Youtube coming soon!'), MessageBox.TYPE_INFO, timeout=5)
            # # return
        # if Utils.isStreamlinkAvailable():
            # streamtypelist.append("5002") #ref = '5002:0:1:0:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/' + url
            # streaml = True
        # if os.path.exists("/usr/bin/gstplayer"):
            # streamtypelist.append("5001")
        # if os.path.exists("/usr/bin/exteplayer3"):
            # streamtypelist.append("5002")
        # if os.path.exists("/usr/bin/apt-get"):
            # streamtypelist.append("8193")
        # for index, item in enumerate(streamtypelist, start=0):
            # if str(item) == str(self.servicetype):
                # currentindex = index
                # break
        # nextStreamType = islice(cycle(streamtypelist), currentindex + 1, None)
        # self.servicetype = str(next(nextStreamType))
        print('servicetype2: ', self.servicetype)
        self.openTest(self.servicetype, url)

    def up(self):
        pass

    def down(self):
        self.up()

    def doEofInternal(self, playing):
        self.close()

    def __evEOF(self):
        self.end = True

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if os.path.isfile('/tmp/hls.avi'):
            os.remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        if not self.new_aspect == self.init_aspect:
            try:
                self.setAspect(self.init_aspect)
            except:
                pass
        # streaml = False
        self.close()

    def leavePlayer(self):
        self.close()


class Showrtmp(Screen):

    def __init__(self, session, name, url, desc):
        Screen.__init__(self, session)
        self.skinName = "Showrtmp"
        title = "Play"
        self.setTitle(title)
        self["info"] = Label()
        self["pixmap"] = Pixmap()
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button(_("Download"))
        self["key_yellow"] = Button(_("Play"))
        self["key_blue"] = Button(_("Stop Download"))
        self.list = []
        self["list"] = List(self.list)
        self["list"] = Utils.tvList([])
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
                                         {"red": self.close,
                                          "green": self.okClicked,
                                          "yellow": self.play,
                                          "blue": self.stopdl,
                                          "cancel": self.cancel,
                                          "ok": self.okClicked}, -2)
        self.icount = 0
        self.name = name
        self.url = url
        txt = "Video stream rtmp.\n\n\nMust do (1) Download  (2) Play.\n\n"
        self["info"].setText(txt)
        self.sref = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.getrtmp)

    def getrtmp(self):
        pic = THISPLUG + "/images/default.png"
        if Utils.isFHD():
            pic = THISPLUG + "/images/defaultL.png"
        self["pixmap"].instance.setPixmapFromFile(pic)
        params = self.url
        params = params.replace("-swfVfy", " --swfVfy")
        params = params.replace("-playpath", " --playpath")
        params = params.replace("-app", " --app")
        params = params.replace("-pageUrl", " --pageUrl")
        params = params.replace("-tcUrl", " --tcUrl")
        params = params.replace("-swfUrl", " --swfUrl")
        fold = str(config.plugins.kodiplug.cachefold.value) + "/xbmc/vid"
        name = self.name.replace("/media/hdd/xbmc/vid/", "")
        name = name.replace(":", "-")
        name = name.replace("&", "-")
        name = name.replace(" ", "-")
        name = name.replace("/", "-")
        name = name.replace(".", "-")
        self.name = name
        svfile = fold + "/xbmc/vid/savedfile.mpg"
        self.svf = svfile
        self.urtmp = "rtmpdump -r " + params + " -o '" + svfile + "'"

    def okClicked(self):
        self["info"].setText("Downloading ....")
        fold = str(config.plugins.kodiplug.cachefold.value) + "/xbmc/vid"
        name = self.name.replace("/media/hdd/xbmc/vid/", "")
        name = name.replace(":", "-")
        name = name.replace("&", "-")
        name = name.replace(" ", "-")
        name = name.replace("/", "-")
        name = name.replace(".", "-")
        svfile = fold + "/xbmc/vid/savedfile.mpg"
        self.svf = svfile
        cmd = "rm " + svfile
        os.system(cmd)
        JobManager.AddJob(downloadJob(self, self.urtmp, svfile, 'Title 1'))
        self.LastJobView()

    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job
        if currentjob is not None:
            self.session.open(JobViewNew, currentjob)

    def play(self):
        if os.path.exists(self.svf):
            svfile = self.svf
            desc = self.desc
            self.session.open(Playgo, self.name, svfile, desc)
        else:
            txt = "Download Video first."
            self["info"].setText(txt)

    def cancel(self):
        self.session.nav.playService(self.sref)
        self.close()

    def stopdl(self):
        svfile = self.svf
        cmd = "rm " + svfile
        os.system(cmd)
        self.session.nav.playService(self.sref)
        cmd1 = "killall -9 rtmpdump"
        cmd2 = "killall -9 wget"
        os.system(cmd1)
        os.system(cmd2)
        self.close()

    def keyLeft(self):
        self["list"].left()

    def keyRight(self):
        self["list"].right()

    def keyNumberGlobal(self, number):
        self["list"].number(number)


class downloadJob(Job):
    def __init__(self, toolbox, cmdline, filename, filetitle):
        Job.__init__(self, _("Saving Video"))
        self.toolbox = toolbox
        self.retrycount = 0
        downloadTask(self, cmdline, filename, filetitle)

    def retry(self):
        assert self.status == self.FAILED
        self.retrycount += 1
        self.restart()


class downloadTask(Task):
    ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)

    def __init__(self, job, cmdline, filename, filetitle):
        Task.__init__(self, job, filetitle)
        self.setCmdline(cmdline)
        self.filename = filename
        self.toolbox = job.toolbox
        self.error = None
        self.lasterrormsg = None

    def processOutput(self, data):
        try:
            if data.endswith('%)'):
                startpos = data.rfind("sec (") + 5
                if startpos and startpos != -1:
                    self.progress = int(float(data[startpos:-4]))
            elif data.find('%') != -1:
                tmpvalue = data[:data.find("%")]
                tmpvalue = tmpvalue[tmpvalue.rfind(" "):].strip()
                tmpvalue = tmpvalue[tmpvalue.rfind("(") + 1:].strip()
                self.progress = int(float(tmpvalue))
            else:
                Task.processOutput(self, data)
        except Exception as e:
            print(e)
            Task.processOutput(self, data)

    def processOutputLine(self, line):
        self.error = self.ERROR_SERVER

    def afterRun(self):
        pass


def getserviceinfo(sref):  # this def returns the current playing service name and stream_url from give sref
    try:
        p = ServiceReference(sref)
        servicename = str(p.getServiceName())
        serviceurl = str(p.getPath())
        return servicename, serviceurl
    except:
        return None, None


def addstreamboq(bouquetname=None):
    boqfile = "/etc/enigma2/bouquets.tv"
    if not os.path.exists(boqfile):
        pass
    else:
        fp = open(boqfile, "r")
        lines = fp.readlines()
        fp.close()
        add = True
        for line in lines:
            if "userbouquet." + bouquetname + ".tv" in line:
                add = False
                break
        if add is True:
            fp = open(boqfile, "a")
            fp.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "userbouquet.%s.tv" ORDER BY bouquet\n' % bouquetname)
            fp.close()
            add = True


def stream2bouquet(url=None, name=None, bouquetname='kodilite'):
    error = 'none'
    fileName = "/etc/enigma2/userbouquet.%s.tv" % bouquetname
    out = '#SERVICE 4097:0:1:0:0:0:0:0:0:0:%s:%s\r\n' % (quote(url), quote(name))
    try:
        addstreamboq(bouquetname)
        if not os.path.exists(fileName):
            fp = open(fileName, 'w')
            fp.write("#NAME %s\n" % bouquetname)
            fp.close()
            fp = open(fileName, 'a')
            fp.write(out)
        else:
            fp = open(fileName, 'r')
            lines = fp.readlines()
            fp.close()
            for line in lines:
                if out in line:
                    error = (_('Stream already added to bouquet'))
                    return error
            fp = open(fileName, 'a')
            fp.write(out)
        fp.write("")
        fp.close()
    except:
        error = (_('Adding to bouquet failed'))
    return error


# added for need of aspect ratio
class StatusScreen(Screen):

    def __init__(self, session):
        desktop = getDesktop(0)
        size = desktop.size()
        self.sc_width = size.width()
        self.sc_height = size.height()
        statusPositionX = 50
        statusPositionY = 100
        self.delayTimer = eTimer()
        try:
            self.delayTimer_conn = self.delayTimer.timeout.connect(self.hideStatus)
        except AttributeError:
            self.delayTimer.callback.append(self.hideStatus)
        self.delayTimer = 1500
        self.shown = True
        self.skin = '\n            <screen name="StatusScreen" position="%s,%s" size="%s,90" zPosition="0" backgroundColor="transparent" flags="wfNoBorder">\n                    <widget name="status" position="0,0" size="%s,70" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="yellow" shadowColor="#40101010" shadowOffset="3,3" />\n            </screen>' % (str(statusPositionX),
            str(statusPositionY),  str(self.sc_width), str(self.sc_width))
        Screen.__init__(self, session)
        self.stand_alone = True

        self['status'] = Label('')
        self.onClose.append(self.__onClose)

    def setStatus(self, text, color='yellow'):
        self['status'].setText(text)
        self['status'].instance.setForegroundColor(parseColor(color))
        self.show()
        self.delayTimer.start(self.delayTimer, True)

    def hideStatus(self):
        self.hide()
        self['status'].setText('')

    def __onClose(self):
        self.delayTimer.stop()
        del self.delayTimer
