#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
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
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
# this import no utilised
# from Components.ConfigList import ConfigList, ConfigListScreen
# from Components.FileList import FileList
# from Components.Input import Input
# from Screens.InfoBarGenerics import *    
# from enigma import eServiceCenter
# #
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
from Components.ServiceEventTracker import InfoBarBase
from Components.Sources.List import List
from Components.Task import Task, Job, job_manager as JobManager
from Components.config import config, ConfigSubsection, ConfigDirectory, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBar import InfoBar
from Screens.InfoBar import MoviePlayer
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarAudioSelection, InfoBarNotifications
from Screens.InfoBarGenerics import InfoBarSubtitleSupport, InfoBarMenu, InfoBarShowHide
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.TaskView import JobView
from ServiceReference import ServiceReference
from Tools.Directories import fileExists
from enigma import eListboxPythonMultiContent
from enigma import gFont, getDesktop
from enigma import eServiceReference, iServiceInformation
from enigma import eTimer
from enigma import RT_HALIGN_LEFT
from twisted.web.client import downloadPage
from skin import parseColor
import os
import re
import sys
from Plugins.Extensions.KodiLite.lib.TaskView2 import JobViewNew
from Plugins.Extensions.KodiLite.lib import xpath
from Plugins.Extensions.KodiLite.lib.download import startdownload  # mfaraj2608 to for new download management
from Plugins.Extensions.KodiLite.adnutils import *
from .. import Player  
# import HTTPConnection
# HTTPConnection.debuglevel = 1

# from ..plugin import cfg  # cfg.cachefold, cfg.directpl
config.plugins.kodiplug = ConfigSubsection()
cfg = config.plugins.kodiplug
# cfg.cachefold = ConfigText("/media/hdd", False)
cfg.cachefold = ConfigDirectory("/tmp")
cfg.directpl = ConfigYesNo(False)


PY3 = sys.version_info[0] == 3
if PY3:
    from urllib.request import urlopen, Request
    from http.client import HTTPConnection
    from urllib.error import URLError, HTTPError
    from urllib.parse import urlparse
    from urllib.parse import urlencode, quote, unquote_plus, unquote
    from urllib.request import urlretrieve
else:
    from urllib2 import urlopen, Request
    from httplib import HTTPConnection
    from urllib2 import URLError, HTTPError
    from urlparse import urlparse
    from urllib import urlencode, quote, unquote_plus, unquote
    from urllib import urlretrieve


HTTPConnection.debuglevel = 1


THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
SREF = " "
SERVICEAPP = 0
NOSS = 0
try:
    from Plugins.Extensions.SubsSupport import SubsSupport, SubsSupportStatus, initSubsSettings
except ImportError:
    class SubsSupport(object):
        def __init__(self, *args, **kwargs):
            pass

    class SubsSupportStatus(object):
        def __init__(self, *args, **kwargs):
            pass
    NOSS = 1 

# if os.path.exists("/usr/bin/exteplayer3"):
#      SERVICEAPP = 1


def getDesktopSize():
    from enigma import getDesktop
    s = getDesktop(0).size()
    return (s.width(), s.height())


def isFHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] == 1920


std_headers = {
                'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
                'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
              }



class tvList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 22))
        self.l.setFont(2, gFont('Regular', 24))
        self.l.setFont(3, gFont('Regular', 26))
        self.l.setFont(4, gFont('Regular', 28))
        self.l.setFont(5, gFont('Regular', 30))
        self.l.setFont(6, gFont('Regular', 32))
        self.l.setFont(7, gFont('Regular', 34))
        self.l.setFont(8, gFont('Regular', 36))
        self.l.setFont(9, gFont('Regular', 40))
        if isFHD():
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(50)


class Getvid(Screen):

    def __init__(self, session, name, url, desc):
        Screen.__init__(self, session)
        self.skinName = "Showrtmp"
        # title = PlugDescription
        # self["title"] = Button(title + Version)
        title = "Play"
        self.setTitle(title)
        self.list = []
        self["list"] = List(self.list)
        self["list"] = RSList([])
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
        txt = _("Must do (1) Download  (2) Play.\n\n") + self.name + "\n\n" + desc
        self["info"].setText(txt)
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.getrtmp)

    def showinfo(self):
        return

    def getrtmp(self):
        fold = cfg.cachefold.value + "/"
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
        fold = cfg.cachefold.value + "/xbmc/vid"
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
            desc = " "
            self.session.open(Playvid2, self.name, svfile, desc)
            # runKDplayer(self.session,name,svfile,desc)
        else:
            txt = _("Download Video first.")
            self["info"].setText(txt)

    def cancel(self):
        self.session.nav.playService(self.srefOld)
        self.close()

    def stopdl(self):
        # svfile = self.svf
        # cmd = "rm " + svfile
        # os.system(cmd)
        self.session.nav.playService(self.srefOld)
        cmd1 = "killall -9 rtmpdump"
        cmd2 = "killall -9 wget"
        os.system(cmd1)
        os.system(cmd2)
        # self.close()

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
        # title = PlugDescription
        # self["title"] = Button(title + Version)
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
        cachefold = cfg.cachefold.value
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
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()

    def openTest(self):
        vid = self.name
        infotxt = _('Video selected :-\n\n\n') + vid
        self['info'].setText(infotxt)

    def play(self):
        desc = " "
        if self.icount == 0:
            url = self.url
            name = self.name
        else:
            url = self.svfile
            name = "Video"
        self.session.open(Playvid2, name, url, desc)
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
        self.session.nav.playService(self.srefOld)
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
        global SREF
        Screen.__init__(self, session)
        self.name = name.replace('-', ' ').replace('+', ' ').replace('_', ' ')
        self.url = url
        self.skinName = "Ploptions"
        # title = PlugDescription
        # self["title"] = Button(title + Version)
        self.hostaddr = ""
        self.list = []
        self["list"] = List(self.list)
        self["list"] = tvList([])
        self['infoc'] = Label(_('Info'))
        Credits = " Linuxsat-support Forum"
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
        cachefold = cfg.cachefold.value
        self.svfile = " "
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
        #############################
        if "/tmp/vid.txt" in self.url:
            file1 = "/tmp/vid.txt"
            f1 = open(file1, "r + ")
            txt1 = f1.read()
            pass  # print "In Playvid txt1 =", txt1
            n1 = txt1.find("http", 0)
            n2 = txt1.find("\n", n1)
            txt2 = txt1[n1:n2]
            self.url = txt2
        # ############################
        # self.url = self.url.replace("|", "\|")
        self.urlmain = self.url
        n1 = self.url.find("|", 0)
        if n1 > -1:
            self.url = self.url[:n1]
        pass  # print "Here in Playvid self.url B=", self.url
        self.updateTimer = eTimer()
        try:
            self.updateTimer_conn = self.updateTimer.timeout.connect(self.updateStatus)
        except AttributeError:
            self.updateTimer.callback.append(self.updateStatus)
        self['info'].setText(" ")
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        pass  # print "Here in Playoptions SREF =", SREF
        if cfg.directpl.value is True:
            pass  # print "Here in directpl"
            self.onShown.append(self.start1)
        elif "hds://" in url:
            self.onShown.append(self.start3)
        elif self.url.startswith("stack://"):
            self.onShown.append(self.start4)
        # elif "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :
        # self.onShown.append(self.start5)
        else:
            pass  # print "Here in no directpl"
            self.onLayoutFinish.append(self.start)
            # self.onShown.append(self.start1)

    def start1(self):
        desc = " "
        if "/tmp/vid.txt" in self.url:
            self.start5()
            self.cancel()
        elif "f4m" in self.url:
            pass  # print "In playVideo f4m url A=", self.url
            from F4mProxy import f4mProxyHelper
            player = f4mProxyHelper()
            url = self.url
            name = self.name
            self.url = player.playF4mLink(url, name, streamtype='HDS', direct="no")
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()
        else:
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()

    def playproxy(self):
        desc = " "
        if "m3u8" in self.url:
            pass  # print "In playVideo proxy m3u8 url A=", self.url
            from F4mProxy import f4mProxyHelper
            player = f4mProxyHelper()
            url = self.url
            name = self.name
            self.url = player.playF4mLink(url, name, streamtype='HLS', direct="no")
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()

        elif "f4m" in self.url:
            pass  # print "In playVideo proxy f4m url A=", self.url
            from F4mProxy import f4mProxyHelper
            player = f4mProxyHelper()
            url = self.url
            name = self.name
            self.url = player.playF4mLink(url, name, streamtype='HDS', direct="no")
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()
        else:
            self.session.open(Playgo, self.name, self.url, desc)
            self.cancel()

    def playts(self):
        desc = " "
        if ".ts" in self.url:
            url = self.url
            pass  # print "shahid url A= ", url
            try:
                os.remove("/tmp/hls.avi")
            except:
                pass
            # url=url.split("?hls")[0]
            cmd = 'python "%s/lib/tsclient.py" "%s" "1" &' % (THISPLUG, url)
            # ok cmd = 'python "/usr/lib/enigma2/python/hlsclient.py" "' + url + '" "1" > /tmp/hls.txt 2>&1 &'
            # cmd = 'python "/usr/lib/enigma2/python/hlsclient.py" "' + url + '" "1" &'
            pass  # print "hls cmd = ", cmd
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

    # def start5X(self):
        # self.pop = 1
        # n1 = self.url.find("video_id", 0)
        # n2 = self.url.find("=", n1)
        # vid = self.url[(n2+1):]
        # cmd = "python '%s/%s/plugin.video.youtube/default.py' '6' '?plugin://plugin.video.youtube/play/?video_id=%s' &" % (THISPLUG, ADDONCAT, vid)
        # self.p = os.popen(cmd)

    def start5(self):
        file1 = "/tmp/vid.txt"
        f1 = open(file1, "r + ")
        txt1 = f1.read()
        pass  # print "In Playvid txt1 =", txt1
        self.url = txt1
        self.session.open(Playgo, self.name, self.url, desc=" ")
        self.close()

    def start(self):
        # infotxt=(_("Selected: ")) + self.name
        infotxt = (_("Selected video: ")) + self.name + (_("\n\nDownload as :"))+self.getlocal_filename()[0]
        self['info'].setText(infotxt)
        pass  # print "Going in showlist, self.list =", self.list
        showlist(self.list, self['list'])

    def openTest(self):
        pass

    # def playsl(self):
        # pass  # print "Here in utils-py play with streamlink self.url =", self.url
        # url = str(self.url)
        # if ".ts" in url:
            # pass  # print "playsl url A= ", url
            # url = url.replace(".ts", ".m3u8")
        # url = url.replace(":", "%3a")
        # url = url.replace("\\", "/")
        # pass  # print "url final= ", url
        # ref = "5002:0:1:1:0:0:0:0:0:0:http%3a//127.0.0.1%3a8088/" + url
        # pass  # print "ref= ", ref
        # self.session.open(Playgo, self.name, ref, desc=" ")
        # self.close()

    # def play2(self):
        # pass  # print "We are in play2"
        # url = "http://192.168.1.65:8080/dream.ts"
        # url = url.replace(":", "%3a")
        # ref = "4097:0:1:0:0:0:0:0:0:0:" + url
        # sref = eServiceReference(ref)
        # self.name = "Test"
        # sref.setName(self.name)
        # self.session.nav.stopService()
        # self.session.nav.playService(sref)
        # self.close()

    def playhls(self):
        print("Here in utils-py play self.icount =", self.icount)
        desc = " "
        if self.icount == 0:
            print("Here in utils-py play self.urlmain =", self.urlmain)
            url1 = self.urlmain
            n1 = url1.find("|", 0)
            print("Here in hlsclient-py n1, url1 =", n1, url1)
            if n1 > -1:
                url = url1[:n1]
                print("Here in hlsclient-py url =", url)
                header = url1[(n1+1):]
                print("Here in hlsclient-py header = ", header)
            else:
                url = url1
                header = ""
            # url = self.url
            name = self.name
            if ".ts" in url:
                pass  # print "shahid url A= ", url
                url = url.replace(".ts", ".m3u8")
            else:
                # if "shahid.net" in url:
                print("shahid url = ", url)
                try:
                    os.remove("/tmp/hls.avi")
                except:
                    pass
                # url=url.split("?hls")[0]
                if PY3:
                    cmd = 'python "%s/lib/hlsclient3.py" "%s" "1" "%s" + &' % (THISPLUG, url, header)
                else:
                    cmd = 'python "%s/lib/hlsclient.py" "%s" "1" "%s" + &' % (THISPLUG, url, header)
                    
                # ok cmd = 'python "/usr/lib/enigma2/python/hlsclient.py" "' + url + '" "1" > /tmp/hls.txt 2>&1 &'
                # cmd = 'python "/usr/lib/enigma2/python/hlsclient.py" "' + url + '" "1" &'
                print("hls cmd = ", cmd)
                os.system(cmd)
                os.system('sleep 5')
                url = '/tmp/hls.avi'
        else:
            url = self.svfile
            name = "Video"
        self.session.open(Playgo, name, url, desc)

    def getlocal_filename(self):
        fold = cfg.cachefold.value + "/"
        name = self.name.replace("/media/hdd/xbmc/vid/", "")
        name = name.replace(" ", "-")
        pattern = '[a-zA-Z0-9\-]'
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
        pass  # print "idx",idx
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
            import urllib  # try with py3  - py2
            # transcode based on vlcplayerIHAD and vlc 2.0.5
            vlcip = cfg.vlcip.value
            self.hostaddr = "http://" + vlcip + ":8080"
            url = quote(self.url, safe='')
            pass  # print "In Playvid going in vlc url =", url
            cmd = self.hostaddr + "/requests/status.xml?command=in_play&input=" + url + "&option=%3Asout%3D%23transcode%7Bvcodec%3Dmp2v%2Cvb%3D2000%2Cvenc%3Dffmpeg%2Cfps%3D25%2Cvfilter%3Dcanvas%7Bwidth%3D352%2Cheight%3D288%2Caspect%3D4%3A3%7D%2Cacodec%3Dmp2a%2Cab%3D128%2Cchannels%3D2%2Csamplerate%3D0%7D%3Astd%7Baccess%3Dhttp%2Cmux%3Dts%7Bpid-video%3D68%2Cpid-audio%3D69%7D%2Cdst%3D%2Fdream.ts%7D&option=%3Asout-all&option=%3Asout-keep"
            # cmd = self.hostaddr + "/requests/status.xml?command=in_play&input=" + url + "&option=%3Asout%3D%23transcode%7Bvcodec%3Dmp2v%2Cvb%3D2000%2Cvenc%3Dffmpeg%2Cfps%3D25%2Cvfilter%3Dcanvas%7Bwidth%3D1280%2Cheight%3D720%2Caspect%3D16%3A9%7D%2Cacodec%3Dmp2a%2Cab%3D128%2Cchannels%3D2%2Csamplerate%3D32000%7D%3Astd%7Baccess%3Dhttp%2Cmux%3Dts%7Bpid-video%3D68%2Cpid-audio%3D69%7D%2Cdst%3D%2Fdream.ts%7D&option=%3Asout-all&option=%3Asout-keep"
            # url = self.url.replace(":", "%3a")
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.hostaddr, '', 'Admin')
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(handler)
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_stop")
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_empty")
            f = opener.open(cmd)
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_play")
            vurl = self.hostaddr + "/dream.ts"
            desc = " "
            self.session.open(Playgo, self.name, vurl, desc)

        elif idx == 6:
            pass  # print "In Playvid Download"
            if "#header#" in self.url:
                self.svfile, self.filetitle = self.getlocal_filename()
                cmd1 = "rm " + self.svfile
                os.system(cmd1)
                n1 = self.url.find("#header#", 0)
                header = self.url[(n1+8):]
                self.url = self.url[:n1]
                cmd = 'wget -O "' + self.svfile + '" --header="' + header + '" --user-agent="Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" "' + self.url + '" &'
                pass  # print "In Playvid cmd =", cmd
                os.system(cmd)
                self.icount = 1
                return

            if "plugin://plugin.video.youtube" in self.url or "youtube.com/" in self.url :
                file1 = "/tmp/vid.txt"
                f1 = open(file1, "r + ")
                txt1 = f1.read()
                pass  # print "In Playvid download youtube txt1 =", txt1
                self.url = txt1
                pass  # print "In Playvid download youtube self.url =", self.url
                self.svfile, self.filetitle = self.getlocal_filename()
                downloadPage(self.url, self.svfile).addErrback(self.showError)
                self.updateTimer.start(2000)

            elif ".m3u8" in self.url:
                ###############################
                pass  # print "In Playvid m3u8 download self.urlmain =", self.urlmain
                url1 = self.urlmain
                n1 = url1.find("|", 0)
                pass  # print "Here in hlsclient-py n1, url1 =", n1, url1
                if n1 > -1:
                    self.url = url1[:n1]
                    pass  # print "Here in hlsclient-py url =", url
                    header = url1[(n1+1):]
                    pass  # print "Here in hlsclient-py header = ", header
                else:
                    self.url = url1
                    header = ""
                ################################
                self.svfile, self.filetitle = self.getlocal_filename()
                # self.pop = 0
                cmd = 'python "%s/lib/hlsdownld.py" "%s" "1" "%s" "%s" + &' % (THISPLUG, self.url, self.svfile, header)
                pass  # print "In Playvid m3u8 download cmd =", cmd
                os.system(cmd)
                self.icount = 1
                # self.updateTimer.start(2000)

            elif self.url.startswith("https"):
                pass  # print "In Playvid Download https url like youtube"
                self.icount = 1
                self.svfile, self.filetitle = self.getlocal_filename()
                pass  # print "In Playvid Download https self.svfile,self.filetitle =", self.svfile, self.filetitle
                pass  # print "In Playvid Download https self.url =", self.url
                self.filetitle = self.filetitle.replace("-", "")
                if PY3:
                    urlretrieve(self.url, self.svfile, reporthook=self.download_progress_hook)
                    print("Done")
                else:
                    downloadPage(self.url, self.svfile).addErrback(self.showError)
                    self.updateTimer.start(2000)

            elif "rtmp" in self.url:
                params = self.url
                pass  # print "params A=", params
                params = "'" + params + "'"
                params = params.replace(" swfVfy=", "' --swfVfy '")
                params = params.replace(" playpath=", "' --playpath '")
                params = params.replace(" app=", "' --app '")
                params = params.replace(" pageUrl=", "' --pageUrl '")
                params = params.replace(" tcUrl=", "' --tcUrl '")
                params = params.replace(" swfUrl=", "' --swfUrl '")
                pass  # print "params B=", params

                self.svfile, self.filetitle = self.getlocal_filename()
                self.urtmp = "rtmpdump -r " + params + " -o '" + self.svfile + "'"
                self["info"].setText(_("Start downloading"))
                self.icount = 1
                cmd = "rm " + self.svfile
                pass  # print "rtmp cmd =", cmd
                os.system(cmd)
                JobManager.AddJob(downloadJob(self, self.urtmp, self.svfile, 'Title 1'))
                self.LastJobView()

            else:
                self.icount = 1
                self.svfile, self.filetitle = self.getlocal_filename()
                pass  # print "In Playvid Download https self.svfile,self.filetitle =", self.svfile, self.filetitle
                pass  # print "In Playvid Download https self.url =", self.url
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
            pass  # print 'add to favorite'
            try:
                from Plugins.Extensions.KodiLite.lib.favorites import addfavorite
            except:
                from favorites import addfavorite
            import sys

            try:
                addon_id = os.path.split(os.path.split(sys.argv[0])[0])[1]
                pass  # print "470add_id",addon_id
                result = addfavorite(addon_id, self.name, self.url)
            except:
                result = False
            if result is False:
                pass  # print "failed to add to favorites"
                self.session.open(MessageBox, _("Failed to add to favorites."), MessageBox.TYPE_ERROR, timeout=4)
            else:
                pass  # print "added to favorites"
                self.session.open(MessageBox, _("Item added successfully to favorites."), MessageBox.TYPE_INFO, timeout=4)
        elif idx == 9:
            # print("In Utils.py self.url =", self.url)
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
            Downloadpath = str(cfg.cachefold.value)
            # mkdir(Downloadpath)
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
            """
            print("In playChoice res =", res)
            url = res[1]
            name = res[0]
            desc = " "
            self.session.open(Playvid2, name, url, desc)
            self.close()
            """
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
            desc = " "
            self.session.open(Playgo, name, url, desc)
            self.close()
        else:
            cmd = "rm -rf " + res[1]
            os.system(cmd)
            self.close()

    def showError(self, error):
        pass  # print "DownloadPage error = ", error

    def updateStatus(self):
        # pass  # print "self.icount =", self.icount
        # pass  # print "In updateStatus self.pop =", self.pop
        if self.pop == 1:
            try:
                ptxt = self.p.read()
                # pass  # print "In updateStatus ptxt =", ptxt
                if "data B" in ptxt:
                    n1 = ptxt.find("data B", 0)
                    n2 = ptxt.find("&url", n1)
                    n3 = ptxt.find("\n", n2)
                    url = ptxt[(n2+5):n3]
                    url = url.replace("AxNxD", "&")
                    self.url = url.replace("ExQ", "=")
                    # pass  # print "In updateStatus url =", url
                    name = "Video"
                    desc = " "
                    self.session.open(Playgo, self.name, self.url, desc)
                    self.close()
                    self.updateTimer.stop()
                # else:
                    # self.openTest()
                    # return
            except:
                self.openTest()
            # return
        else:
            if not os.path.exists(self.svfile):
                pass  # print "No self.svfile =", self.svfile
                self.openTest()
                return

            if self.icount == 0:
                self.openTest()
                return
            # pass  # print "Exists self.svfile =", self.svfile
            b1 = os.path.getsize(self.svfile)
            pass  # print "b1 =", b1
            b = b1 / 1000
            if b == self.bLast:
                infotxt = _('Download Complete....') + str(b)
                self['info'].setText(infotxt)
                return
            self.bLast = b
            infotxt = _('Downloading....') + str(b) + ' kb'
            self['info'].setText(infotxt)

    def download_progress_hook(self, count, blockSize, totalSize):
        # print("count, blockSize, totalSize =", count, blockSize, totalSize)
        # b1 = os.path.getsize(self.svfile)
        b1 = count*blockSize
        # print("b1 =", b1)
        if (b1 > totalSize) or (b1 == totalSize):
            infotxt = _('Download Complete....') + str(totalSize)
            self['info'].setText(infotxt)
            # return
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
        pass  # print "Here in cancel"
        try:
            import urllib
            vlcip = cfg.vlcip.value
            self.hostaddr = "http://" + vlcip + ":8080"
            password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, self.hostaddr, '', 'Admin')
            handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
            opener = urllib.request.build_opener(handler)
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_stop")
            f = opener.open(self.hostaddr + "/requests/status.xml?command=pl_empty")
            # self.session.nav.stopService()
            # self.session.nav.playService(self.srefOld)
        except:
            pass
        if os.path.exists("/tmp/hls.avi"):
            os.remove("/tmp/hls.avi")
        self.close()

    def stopDL(self):
        cmd = "rm -f " + self.svfile
        os.system(cmd)
        self.session.nav.playService(self.srefOld)
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


if NOSS == 0:
    class Playgo(Screen, InfoBarMenu, InfoBarBase, SubsSupport, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
        STATE_PLAYING = 1
        STATE_PAUSED = 2

        def __init__(self, session, name, url, desc):

            Screen.__init__(self, session)
            self.skinName = "Playvid2"
            self.sref = None
            # title = PlugDescription
            # self["title"] = Button(title + Version)
            self['key_yellow'] = Button(_('Subtitles'))
            InfoBarMenu.__init__(self)
            InfoBarNotifications.__init__(self)
            InfoBarBase.__init__(self)
            InfoBarShowHide.__init__(self)
            # self.statusScreen = self.session.instantiateDialog(StatusScreen)
            # aspect ratio stuff
            try:
                self.init_aspect = int(self.getAspect())
            except:
                self.init_aspect = 0
            self.new_aspect = self.init_aspect
            # end aspect ratio
            self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarSeekActions", "InfobarActions"],
                                        {"leavePlayer": self.cancel,
                                         "back": self.cancel,
                                         "info": self.showinfo,
                                         "playpauseService": self.playpauseService,
                                         "yellow": self.subtitles,
                                         'down': self.av}, -1)
            self.allowPiP = False
            initSubsSettings()
            SubsSupport.__init__(self, embeddedSupport=True, searchSupport=True)
            self.subs = True
            InfoBarSeek.__init__(self, actionmap="MediaPlayerSeekActions")
            self.icount = 0
            self.name = name
            self.url = url
            self.desc = desc
            self.pcip = "None"
            self.state = self.STATE_PLAYING
            self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
            self.onLayoutFinish.append(self.openTest)

        def getAspect(self):
            return AVSwitch().getAspectRatioSetting()

        def getAspectString(self, aspectnum):
            return {0: _('4:3 Letterbox'),
                    1: _('4:3 PanScan'),
                    2: _('16:9'),
                    3: _('16:9 always'),
                    4: _('16:10 Letterbox'),
                    5: _('16:10 PanScan'),
                    6: _('16:9 Letterbox')}[aspectnum]

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
            pass  # print self.getAspectString(temp)
            temp = temp + 1
            if temp > 6:
                temp = 0
            self.new_aspect = temp
            self.setAspect(temp)
            pass  # print self.getAspectString(temp)
            # self.statusScreen.setStatus(self.getAspectString(temp))

        def showinfo(self):
            debug = True
            try:
                servicename, serviceurl = getserviceinfo(self.sref)
                if servicename is not None:
                    sTitle = servicename
                else:
                    sTitle = ''
                if serviceurl is not None:
                    sServiceref = serviceurl
                else:
                    sServiceref = ''
                currPlay = self.session.nav.getCurrentService()
                sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
                sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
                sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)
                # return str(sTitle)
                # message='remote keys help:\nmenu: subtitle player\nnumbers 1-6 seek back and forward\nleft and right:next and previous channel when playlist supported\ninfo:help\nup and cancel keys:exit to playlist'
                message = 'stitle:' + str(sTitle) + "\n" + 'sServiceref:' + str(sServiceref) + "\n" + 'sTagCodec:' + str(sTagCodec) + "\n" + 'sTagVideoCodec:' + str(sTagVideoCodec) + "\n" + 'sTagAudioCodec :' + str(sTagAudioCodec)
                from XBMCAddonsinfo import XBMCAddonsinfoScreen
                self.session.open(XBMCAddonsinfoScreen, None, 'XBMCAddonsPlayer', message)
            except:
                pass

        def playpauseService(self):
            pass  # print "playpauseService"
            if self.state == self.STATE_PLAYING:
                self.pause()
                self.state = self.STATE_PAUSED
            elif self.state == self.STATE_PAUSED:
                self.unpause()
                self.state = self.STATE_PLAYING

        def pause(self):
            self.session.nav.pause(True)

        def unpause(self):
            self.session.nav.pause(False)

        def openTest(self):
            if "5002" in self.url:
                pass  # print "In openTest streamlink self.url 2= ", self.url
                ref = self.url
                pass  # print "ref= ", ref
                sref = eServiceReference(ref)
                sref.setName(self.name)
                self.session.nav.stopService()
                self.session.nav.playService(sref)
            else:
                if "pcip" in self.url:
                    n1 = self.url.find("pcip")
                    urlA = self.url
                    self.url = self.url[:n1]
                    self.pcip = urlA[(n1+4):]
                url = self.url
                name = self.name
                pass  # print "Here in Playvid name A =", name
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace("›", "-")
                name = name.replace(",", "-")
                pass  # print "Here in Playvid name B2 =", name
                if url is not None:
                    url = str(url)
                    url = url.replace(":", "%3a")
                    url = url.replace("\\", "/")
                    pass  # print "url final= ", url
                    ref = "4097:0:1:0:0:0:0:0:0:0:" + url
                    pass  # print "ref= ", ref
                    sref = eServiceReference(ref)
                    sref.setName(self.name)
                    self.session.nav.stopService()
                    self.session.nav.playService(sref)
                else:
                    return

        def subtitles(self):
            try:
                self.subsMenu()
            except:
                self.session.open(MessageBox, _("Subtitle Player cannot be started."), MessageBox.TYPE_ERROR, timeout=10)

        def cancel(self):
            if os.path.exists("/tmp/hls.avi"):
                os.remove("/tmp/hls.avi")
            self.session.nav.stopService()
            pass  # print "Here in Playvid2 cancel SREF =", SREF
            self.session.nav.playService(self.srefOld)
            # try:
            if self.pcip != "None":
                url2 = "http://" + self.pcip + ":8080/requests/status.xml?command=pl_stop"
                pass  # print "In Playvid2 url2 =", url2
                resp = urlopen(url2)
            # except:
            # pass
            # aspect ratio
            if not self.new_aspect == self.init_aspect:
                try:
                    self.setAspect(self.init_aspect)
                except:
                    pass
            # aspect ratio
            self.close()


if NOSS == 1:
    class Playgo(Screen, InfoBarMenu, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
        STATE_PLAYING = 1
        STATE_PAUSED = 2

        def __init__(self, session, name, url, desc):

            Screen.__init__(self, session)
            self.skinName = "MoviePlayer"
            self.sref = None
            # title = PlugDescription
            # self["title"] = Button(title + Version)
            self['key_yellow'] = Button(_(' '))
            InfoBarMenu.__init__(self)
            InfoBarNotifications.__init__(self)
            InfoBarBase.__init__(self)
            InfoBarShowHide.__init__(self)
            # self.statusScreen = self.session.instantiateDialog(StatusScreen)
            # aspect ratio stuff
            try:
                self.init_aspect = int(self.getAspect())
            except:
                self.init_aspect = 0

            self.new_aspect = self.init_aspect
            # end aspect ratio
            self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarSeekActions", "InfobarActions"],
                                        {"leavePlayer": self.cancel,
                                         "back": self.cancel,
                                         "info": self.showinfo,
                                         "playpauseService": self.playpauseService,
                                         "yellow": self.subtitles,
                                         'down': self.av}, -1)
            self.allowPiP = False
            InfoBarSeek.__init__(self, actionmap="MediaPlayerSeekActions")
            self.icount = 0
            self.name = name
            self.url = url
            self.desc = desc
            self.pcip = "None"
            self.state = self.STATE_PLAYING
            self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
            self.onLayoutFinish.append(self.openTest)

        # aspect ratio stuff
        def getAspect(self):
            return AVSwitch().getAspectRatioSetting()

        def getAspectString(self, aspectnum):
            return {0: _('4:3 Letterbox'),
                    1: _('4:3 PanScan'),
                    2: _('16:9'),
                    3: _('16:9 always'),
                    4: _('16:10 Letterbox'),
                    5: _('16:10 PanScan'),
                    6: _('16:9 Letterbox')}[aspectnum]

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
            pass  # print self.getAspectString(temp)
            temp = temp + 1
            if temp > 6:
                temp = 0
            self.new_aspect = temp
            self.setAspect(temp)
            pass  # print self.getAspectString(temp)
            # self.statusScreen.setStatus(self.getAspectString(temp))

        def showinfo(self):
            debug = True
            try:
                servicename, serviceurl = getserviceinfo(self.sref)
                if servicename is not None:
                    sTitle = servicename
                else:
                    sTitle = ''
                if serviceurl is not None:
                    sServiceref = serviceurl
                else:
                    sServiceref = ''
                currPlay = self.session.nav.getCurrentService()
                sTagCodec = currPlay.info().getInfoString(iServiceInformation.sTagCodec)
                sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
                sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)
                # return str(sTitle)
                # message='remote keys help:\nmenu: subtitle player\nnumbers 1-6 seek back and forward\nleft and right:next and previous channel when playlist supported\ninfo:help\nup and cancel keys:exit to playlist'
                message = 'stitle:' + str(sTitle) + "\n" + 'sServiceref:' + str(sServiceref) + "\n" + 'sTagCodec:' + str(sTagCodec) + "\n" + 'sTagVideoCodec:' + str(sTagVideoCodec) + "\n" + 'sTagAudioCodec :' + str(sTagAudioCodec)
                from XBMCAddonsinfo import XBMCAddonsinfoScreen
                self.session.open(XBMCAddonsinfoScreen, None, 'XBMCAddonsPlayer', message)
            except:
                pass

        def playpauseService(self):
            pass  # print "playpauseService"
            if self.state == self.STATE_PLAYING:
                self.pause()
                self.state = self.STATE_PAUSED
            elif self.state == self.STATE_PAUSED:
                self.unpause()
                self.state = self.STATE_PLAYING

        def pause(self):
            self.session.nav.pause(True)

        def unpause(self):
            self.session.nav.pause(False)

        def openTest(self):
            if "5002" in self.url:
                pass  # print "In openTest streamlink self.url 2= ", self.url
                ref = self.url
                pass  # print "ref= ", ref
                sref = eServiceReference(ref)
                sref.setName(self.name)
                self.session.nav.stopService()
                self.session.nav.playService(sref)
            else:
                if "pcip" in self.url:
                    n1 = self.url.find("pcip")
                    urlA = self.url
                    self.url = self.url[:n1]
                    self.pcip = urlA[(n1+4):]
                url = self.url
                name = self.name
                pass  # print "Here in Playvid name A =", name
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace("›", "-")
                name = name.replace(",", "-")
                pass  # print "Here in Playvid name B2 =", name
                if url is not None:
                    url = str(url)
                    url = url.replace(":", "%3a")
                    url = url.replace("\\", "/")
                    pass  # print "url final= ", url
                    ref = "4097:0:1:0:0:0:0:0:0:0:" + url
                    pass  # print "ref= ", ref
                    sref = eServiceReference(ref)
                    sref.setName(self.name)
                    self.session.nav.stopService()
                    self.session.nav.playService(sref)

                else:
                    return

        def subtitles(self):
            self.session.open(MessageBox, _("Please install script.module.SubSupport."), MessageBox.TYPE_ERROR, timeout=10)

        def cancel(self):
            if os.path.exists("/tmp/hls.avi"):
                os.remove("/tmp/hls.avi")
            self.session.nav.stopService()
            pass  # print "Here in Playvid2 cancel SREF =", SREF
            self.session.nav.playService(self.srefOld)
            # try:
            if self.pcip != "None":
                url2 = "http://" + self.pcip + ":8080/requests/status.xml?command=pl_stop"
                pass  # print "In Playvid2 url2 =", url2
                resp = urlopen(url2)
            # except:
            # pass
            # aspect ratio
            if not self.new_aspect == self.init_aspect:
                try:
                    self.setAspect(self.init_aspect)
                except:
                    pass
            # aspect ratio
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
        self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
                                        {
                                        "red": self.close,
                                        "green": self.okClicked,
                                        "yellow": self.play,
                                        "blue": self.stopdl,
                                        "cancel": self.cancel,
                                        "ok": self.okClicked,
                                        }, -2)
        self.icount = 0
        self.name = name
        self.url = url
        txt = "Video stream rtmp.\n\n\nMust do (1) Download  (2) Play.\n\n"
        self["info"].setText(txt)
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.getrtmp)

    def getrtmp(self):
        pic = THISPLUG + "/images/default.png"
        if isFHD():
            pic = res_plugin_path + "defaultL.png"
        self["pixmap"].instance.setPixmapFromFile(pic)
        params = self.url
        pass  # print "params A=", params
        params = params.replace("-swfVfy", " --swfVfy")
        params = params.replace("-playpath", " --playpath")
        params = params.replace("-app", " --app")
        params = params.replace("-pageUrl", " --pageUrl")
        params = params.replace("-tcUrl", " --tcUrl")
        params = params.replace("-swfUrl", " --swfUrl")
        pass  # print "params B=", params
        fold = cfg.cachefold.value + "/xbmc/vid"
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
        fold = cfg.cachefold.value + "/xbmc/vid"
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
            desc = " "
            self.session.open(Playvid2, self.name, svfile, desc)
            # runKDplayer(self.session,name,svfile,desc)
        else:
            txt = "Download Video first."
            self["info"].setText(txt)

    def cancel(self):
        self.session.nav.playService(self.srefOld)
        self.close()

    def stopdl(self):
        svfile = self.svf
        cmd = "rm " + svfile
        os.system(cmd)
        self.session.nav.playService(self.srefOld)
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
        # pass  # print "pressed", number
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
                startpos = data.rfind("sec (")+5
                if startpos and startpos != -1:
                    self.progress = int(float(data[startpos:-4]))
            elif data.find('%') != -1:
                tmpvalue = data[:data.find("%")]
                tmpvalue = tmpvalue[tmpvalue.rfind(" "):].strip()
                tmpvalue = tmpvalue[tmpvalue.rfind("(")+1:].strip()
                self.progress = int(float(tmpvalue))
            else:
                Task.processOutput(self, data)
        except Exception as errormsg:
            Task.processOutput(self, data)

    def processOutputLine(self, line):
        self.error = self.ERROR_SERVER

    def afterRun(self):
        pass


class tvList(MenuList):
    def __init__(self, list):
        from enigma import eListboxPythonMultiContent
        from enigma import gFont
        MenuList.__init__(self, list, False, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 22))
        self.l.setFont(2, gFont('Regular', 24))
        self.l.setFont(3, gFont('Regular', 26))
        self.l.setFont(4, gFont('Regular', 28))
        self.l.setFont(5, gFont('Regular', 30))
        self.l.setFont(6, gFont('Regular', 32))
        self.l.setFont(7, gFont('Regular', 34))
        self.l.setFont(8, gFont('Regular', 36))
        self.l.setFont(9, gFont('Regular', 40))
        if isFHD():
            self.l.setItemHeight(50)
        else:
            self.l.setItemHeight(50)

def rvListEntry(name, idx):
    from Components.MultiContent import MultiContentEntryText
    from Components.MultiContent import MultiContentEntryPixmapAlphaTest
    from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER
    from enigma import loadPNG
    from Tools.Directories import SCOPE_PLUGINS
    from Tools.Directories import resolveFilename
    res = [name]
    if 'radio' in name.lower():
        pngs = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/radio.png".format('KodiLite'))
    elif 'webcam' in name.lower():
        pngs = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/webcam.png".format('KodiLite'))
    elif 'music' in name.lower():
        pngs = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/music.png".format('KodiLite'))
    elif 'sport' in name.lower():
        pngs = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/sport.png".format('KodiLite'))
    else:
        pngs = resolveFilename(SCOPE_PLUGINS, "Extensions/{}/res/pics/tv.png".format('KodiLite'))
    if isFHD():
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(50, 50), png=loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(90, 0), size=(1900, 50), font=7, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    else:
        res.append(MultiContentEntryPixmapAlphaTest(pos=(10, 0), size=(50, 50), png=loadPNG(pngs)))
        res.append(MultiContentEntryText(pos=(90, 0), size=(1000, 50), font=2, text=name, color=0xa6d1fe, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def showlist(data, list):
    idx = 0
    plist = []
    for line in data:
        name = data[idx]
        plist.append(rvListEntry(name, idx))
        idx = idx + 1
        list.setList(plist)


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

        self.delayTimerDelay = 1500
        self.shown = True
        self.skin = '\n            <screen name="StatusScreen" position="%s,%s" size="%s,90" zPosition="0" backgroundColor="transparent" flags="wfNoBorder">\n                    <widget name="status" position="0,0" size="%s,70" valign="center" halign="left" font="Regular;22" transparent="1" foregroundColor="yellow" shadowColor="#40101010" shadowOffset="3,3" />\n            </screen>' % (str(statusPositionX),
                str(statusPositionY),
                str(self.sc_width),
                str(self.sc_width))
        Screen.__init__(self, session)
        self.stand_alone = True
        pass  # print 'initializing status display'
        # title = PlugDescription
        # self["title"] = Button(title + Version)
        self['status'] = Label('')
        self.onClose.append(self.__onClose)

    def setStatus(self, text, color='yellow'):
        self['status'].setText(text)
        self['status'].instance.setForegroundColor(parseColor(color))
        self.show()
        self.delayTimer.start(self.delayTimerDelay, True)

    def hideStatus(self):
        self.hide()
        self['status'].setText('')

    def __onClose(self):
        self.delayTimer.stop()
        del self.delayTimer
