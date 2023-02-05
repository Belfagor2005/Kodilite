#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
"""
    This file is part of Plugin KodiLite pcd@xtrend-alliance.com
    Copyright (C) 2014

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
'''
20220730 v9.0 py3
20221030 v9.1 recoded by Lululla
20230128 v9.1r2 updates getpics - trhead - minor fix by Lululla
20230205 v9.1r3 recoded getpics - spinner removed - minor fix by Lululla
'''

from . import _
from Components.AVSwitch import AVSwitch
from Components.ActionMap import NumberActionMap
from Components.Button import Button
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.config import ConfigSubsection, ConfigSelection
from Components.config import ConfigText, ConfigDirectory
from Components.config import NoSave, ConfigYesNo
from Components.config import config
from Components.config import getConfigListEntry
from PIL import Image, ImageChops
from Plugins.Plugin import PluginDescriptor
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.InfoBar import MoviePlayer
from Screens.InfoBarGenerics import InfoBarMenu, InfoBarSeek, InfoBarAudioSelection, \
    InfoBarSubtitleSupport, InfoBarSummarySupport, InfoBarServiceErrorPopupSupport, InfoBarNotifications
from Screens.InputBox import PinInput
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools.Directories import SCOPE_PLUGINS
from Tools.Directories import fileExists, copyfile
from Tools.Directories import resolveFilename
from Tools.LoadPixmap import LoadPixmap
from enigma import eConsoleAppContainer, gPixmapPtr
from enigma import eListboxPythonMultiContent
from enigma import eServiceReference
from enigma import eTimer
from enigma import gFont
from enigma import iPlayableService
from keymapparser import readKeymap
from twisted.web.client import downloadPage
from twisted.web.client import getPage
import os
import re
import sys
import xml.etree.cElementTree

global subsx
subsx = False


from . import Utils
from . import html_conv
from .lib.xUtils import Getvid, Getvid2, Playoptions
from .lib.SkinLoader import loadPluginSkin

PY3 = sys.version_info.major >= 3


if PY3:
    from http.client import HTTPConnection
    PY3 = True
else:
    from httplib import HTTPConnection


HTTPConnection.debuglevel = 1
PlugDescription = 'KODILITE '
Version = 'V.9.1r3'
Credits = " Linuxsat-Support Forum"
select_file = "/tmp/select.txt"
THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
res_plugin_path = os.path.join(THISPLUG, 'skin/images/')
res_pic_path = os.path.join(THISPLUG, 'res/')
THISADDON = ""
HANDLE = 1
DEBUG = 1
NOSS = 0
SELECT = []
newstext = " "
date = " "
NewUpdate = " "
dtext1 = " "
LAST = ""
ADDONCAT = ""
plug = ""
NEWDEFPY = ""
ARG = " "
PICPOS = []
F4MCMD = ""
# HOST = "http://mirrors.kodi.tv/addons/jarvis/"
# HOST = "https://github.com/hadynz/repository.arabic.xbmc-addons/tree/master/repo"
HOST = ""
HOST1 = "http://mirrors.kodi.tv/addons/matrix/"


if Utils.isFHD():
    defpic = os.path.join(res_plugin_path, 'defaultL.png')
    dblank = os.path.join(res_plugin_path, 'blankL.png')
    exitz = os.path.join(res_plugin_path, 'ExitL.png')

else:
    defpic = os.path.join(res_plugin_path, 'default.png')
    dblank = os.path.join(res_plugin_path, 'blank.png')
    exitz = os.path.join(res_plugin_path, 'Exit.png')


config.plugins.kodiplug = ConfigSubsection()
cfg = config.plugins.kodiplug
cfg.tempdel = ConfigYesNo(False)
cfg.picdel = ConfigYesNo(False)
cfg.subtitle = ConfigYesNo(False)
cfg.elog = ConfigYesNo(True)
cfg.update = ConfigYesNo(False)
# cfg.cachefold = ConfigText("/media/hdd", False)
cfg.cachefold = ConfigDirectory("/media/hdd")
cfg.vlcip = ConfigText("192.168.1.1", False)
cfg.mmenu = ConfigYesNo(True)
# cfg.debug = ConfigYesNo(False)
cfg.thumb = ConfigSelection(default="False", choices=[("True", _("yes")), ("False", _("no")), ("Single", _("single"))])
cfg.backup = ConfigYesNo(False)
cfg.directpl = ConfigYesNo(False)
cfg.textcol = NoSave(ConfigSelection(default="0xffffff", choices=[("0xffffff", _("white")), ("0xb3b3b9", _("grey"))]))
cfg.textsel = NoSave(ConfigSelection(default="0xf07655", choices=[("0xf07655", _("red")), ("0xe5b243", _("yellow")), ("0xffffff", _("white"))]))
cfg.textfont = ConfigSelection(default="22", choices=[("25", _("medium")), ("35", _("large")), ("22", _("small"))])
# cfg.skinres = ConfigSelection(default="hd", choices=[("fullhd", _("Full-HD 1920x1080")), ("hd", _("HD 1280x720"))])
cfg.wait = ConfigSelection(default="10", choices=[("10", _("10sec")), ("20", _("20sec")), ("30", _("30sec")), ("40", _("40sec")), ("60", _("60sec")), ("120", _("120sec")), ("180", _("180sec")), ("240", _("240sec")), ("300", _("300sec"))])
cfg.listcol = NoSave(ConfigSelection(default="0x000000", choices=[("0x40000000", _("black")), ("0x40002d39", _("blue"))]))
cfg.mainback = NoSave(ConfigSelection(default="default", choices=[("default", _("default")), ("skin2", _("skin2"))]))
cfg.viewdownloads = NoSave(ConfigSelection(default="disabled", choices=[("disabled", _("Not assigned")), ("help", _("Key help"))]))
cfg.youtubequal = NoSave(ConfigSelection(default="2", choices=[("1", _("SD")), ("2", _("720p")), ("3", _("1080p"))]))


if cfg.subtitle.getValue() is True:
    try:
        from Plugins.Extensions.SubsSupport import SubsSupport, SubsSupportStatus
        subsx = True
    except ImportError:
        class SubsSupport(object):
            def __init__(self, *args, **kwargs):
                pass

        class SubsSupportStatus(object):
            def __init__(self, *args, **kwargs):
                pass
        NOSS = 1
        subsx = False
else:
    class SubsSupport(object):
        def __init__(self, *args, **kwargs):
            pass

    class SubsSupportStatus(object):
        def __init__(self, *args, **kwargs):
            pass
    subsx = False


def returnIMDB(text_clear):
    if Utils.is_tmdb:
        try:
            from Plugins.Extensions.TMBD.plugin import TMBD
            text = html_conv.html_unescape(text_clear)
            _session.open(TMBD.tmdbScreen, text, 0)
        except Exception as ex:
            print("[XCF] Tmdb: ", str(ex))
        return True
    elif Utils.is_imdb:
        try:
            from Plugins.Extensions.IMDb.plugin import main as imdb
            text = html_conv.html_unescape(text_clear)
            imdb(_session, text)
        except Exception as ex:
            print("[XCF] imdb: ", str(ex))
        return True
    else:
        text_clear = html_conv.html_unescape(text_clear)
        _session.open(MessageBox, text_clear, MessageBox.TYPE_INFO)
        return True
    return


import requests
from requests import get, exceptions
from requests.exceptions import HTTPError
from twisted.internet.reactor import callInThread


def threadGetPage(url=None, file=None, key=None, success=None, fail=None, *args, **kwargs):
    print('[kodilite][threadGetPage] url, file, key, args, kwargs', url, "   ", file, "   ", key, "   ", args, "   ", kwargs)
    try:
        # from requests import get, exceptions
        # from requests.exceptions import HTTPError
        # from twisted.internet.reactor import callInThread
        response = get(url)
        response.raise_for_status()
        if file is None:
            success(response.content)
        elif key is not None:
            success(response.content, file, key)
        else:
            success(response.content, file)
    except HTTPError as httperror:
        print('[kodilite][threadGetPage] Http error: ', httperror)
        fail(error)  # E0602 undefined name 'error'
    except exceptions.RequestException as error:
        print(error)


def findmax(match=[]):
    A = []
    B = []
    C = []
    D = []
    E = []
    imax = 0
    for item in match:
        item = item.replace("%7E", "~")
        x = item.split(".")
        print("In findmax x =", x)
        A.append(int(x[0]))
    lx = len(x)
    print("In findmax A =", A)
    Amax = max(A)
    print("In findmax Amax =", Amax)
    i1 = 0
    for a in A:
        if a == Amax:
            imax = i1
            break
        i1 += 1
    print("In findnax imax A=", imax)
    maxitem = str(Amax)
    if lx > 1:
        for item in match:
            x = item.split(".")
            if int(x[0]) == int(Amax):
                B.append(x[1])
            else:
                # continue
                B.append(int('0'))
        print("In findmax B =", B)
        Bmax = max(B)
        print("In findnax Bmax =", Bmax)
        i2 = 0
        for b in B:
            if b == Bmax:
                imax = i2
                break
            i2 += 1
        maxitem = str(Amax) + "." + str(Bmax)
        print("In findnax imax B=", imax)
        if lx > 2:
            for item in match:
                x = item.split(".")
                if (int(x[0]) == int(Amax)) and (int(x[1]) == int(Bmax)):
                    # C.append(int(x[2]))
                    C.append(x[2])
                else:
                    C.append(int('0'))
            print("In findmax C =", C)
            Cmax = max(C)
            print("In findnax Cmax =", Cmax)
            i3 = 0
            for c in C:
                if c == Cmax:
                    imax = i3
                    break
                i3 += 1
            maxitem = str(Amax) + "." + str(Bmax) + "." + str(Cmax)
        if lx > 3:
            for item in match:
                x = item.split(".")
                if (int(x[0]) == int(Amax)) and (int(x[1]) == int(Bmax)) and ((x[2]) == Cmax):
                    # C.append(int(x[2]))
                    D.append(x[3])
                else:
                    D.append(int('0'))
        print("In findmax D =", D)
        Dmax = max(D)
        print("In findnax Dmax =", Dmax)
        i4 = 0
        for d in D:
            if d == Dmax:
                imax = i4
                break
            i4 += 1

        maxitem = str(Amax) + "." + str(Bmax) + "." + str(Cmax) + "." + str(Dmax)
        # print  "In findnax imax C=", imax
    # print  "In findnax imax final =", imax
    # maxitem = match[imax]
    print("maxitem =", maxitem)
    return maxitem


def dellog():  # to clear log files
    import os
    if os.path.exists("/tmp/e.log"):
        os.remove("/tmp/e.log")
    if os.path.exists("/tmp/xbmc_log"):
        os.remove("/tmp/xbmc_log")
    if os.path.exists("/tmp/KodiLite_log"):
        os.remove("/tmp/KodiLite_log")
    if os.path.exists("/tmp/KodiLite_error"):
        os.remove("/tmp/KodiLite_error")
    if os.path.exists("/tmp/data.txt"):
        os.remove("/tmp/data.txt")
    if os.path.exists("/tmp/vidinfo.txt"):
        os.remove("/tmp/vidinfo.txt")
    if os.path.exists("/tmp/vidinfo.txt"):
        os.remove("/tmp/type.txt")


dellog()  # del log to open plugin


def jointext(file1, file2):
    f1 = open(file1, "r+")
    txt1 = f1.read()
    f2 = open(file2, "r")
    txt2 = f2.read()
    txt = txt1 + txt2
    f1.write(txt)
    f1.close()
    f2.close()


def parameters_string_to_dict(parameters):
    paramDict = {}
    # print  "Here in parameters =", parameters
    if parameters:
        paramPairs = parameters.split("&")
        for paramsPair in paramPairs:
            # print  "Here in paramPairs =", paramPairs
            if "=" not in paramsPair:
                continue
            paramSplits = paramsPair.split('=')
            if paramSplits[0] == "?url":
                paramSplits[0] = 'url'
            paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def getpics(names, pics, tmpfold, picfold):
    global defpic
    defpic = defpic
    pix = []

    if cfg.thumb.value == "False":
        npic = len(pics)
        i = 0
        while i < npic:
            pix.append(defpic)
            i += 1
        return pix

    cmd = "rm " + tmpfold + "/*"
    os.system(cmd)

    npic = len(pics)
    j = 0

    while j < npic:
        name = names[j]
        if name is None or name == '':
            name = "Video"
        url = pics[j]
        ext = str(os.path.splitext(url)[-1])
        picf = os.path.join(picfold, str(name + ext))
        tpicf = os.path.join(tmpfold, str(name + ext))

        if os.path.exists(picf):
            if ('stagione') in str(name.lower()):
                cmd = "rm " + picf
                os.system(cmd)
            cmd = "cp " + picf + " " + tmpfold
            print("In getpics fileExists(picf) cmd =", cmd)
            os.system(cmd)

        # test remove this
        # if os.path.exists(tpicf):
            # cmd = "rm " + tpicf
            # os.system(cmd)

        if not os.path.exists(picf):
            if THISPLUG in url:
                try:
                    cmd = "cp " + url + " " + tpicf
                    print("In getpics not fileExists(picf) cmd =", cmd)
                    os.system(cmd)
                except:
                    pass
            else:
                # now download image
                try:
                    url = url.replace(" ", "%20").replace("ExQ", "=").replace("AxNxD", "&")
                    poster = Utils.checkRedirect(url)
                    if poster:

                        if "|" in url:
                            n3 = url.find("|", 0)
                            n1 = url.find("Referer", n3)
                            n2 = url.find("=", n1)
                            url = url[:n3]
                            referer = url[n2:]
                            p = Utils.getUrl2(url, referer)
                            with open(tpicf, 'wb') as f1:
                                f1.write(p)
                        else:
                            try:
                                # print("Going in urlopen url =", url)
                                # p = Utils.gettUrl(url)
                                # with open(tpicf, 'wb') as f1:
                                    # f1.write(p)
                                try:
                                    with open(tpicf, 'wb') as f:
                                        f.write(requests.get(url, stream=True, allow_redirects=True).content)
                                    print('=============11111111=================\n')
                                except Exception as e:
                                    print("Error: Exception")
                                    print('===========2222222222=================\n')
                                    if PY3:
                                        poster = poster.encode()
                                    callInThread(threadGetPage, url=poster, file=tpicf, success=downloadPic, fail=downloadError)
                                '''
                                print(str(e))
                                open(tpicf, 'wb').write(requests.get(poster, stream=True, allow_redirects=True).content)
                                '''
                            except Exception as e:
                                print("Error: Exception 2")
                                print(str(e))

                except:
                    cmd = "cp " + defpic + " " + tpicf
                    os.system(cmd)

        if not fileExists(tpicf):
            cmd = "cp " + defpic + " " + tpicf
            os.system(cmd)

        if os.path.exists(tpicf):
            try:
                size = [150, 220]
                if Utils.isFHD():
                    size = [220, 330]

                file_name, file_extension = os.path.splitext(tpicf)
                try:
                    im = Image.open(tpicf).convert("RGBA")

                    # shrink if larger
                    try:
                        im.thumbnail(size, Image.Resampling.LANCZOS)
                    except:
                        im.thumbnail(size, Image.ANTIALIAS)
                    imagew, imageh = im.size

                    # enlarge if smaller
                    try:
                        if imagew < size[0]:
                            ratio = size[0] / imagew

                            try:
                                im = im.resize((int(imagew * ratio), int(imageh * ratio)), Image.Resampling.LANCZOS)
                            except:
                                im = im.resize((int(imagew * ratio), int(imageh * ratio)), Image.ANTIALIAS)

                            imagew, imageh = im.size
                    except Exception as e:
                        print(e)

                    # crop and center image
                    bg = Image.new("RGBA", size, (255, 255, 255, 0))

                    im_alpha = im.convert("RGBA").split()[-1]
                    bgwidth, bgheight = bg.size
                    bg_alpha = bg.convert("RGBA").split()[-1]
                    temp = Image.new("L", (bgwidth, bgheight), 0)
                    temp.paste(im_alpha, (int((bgwidth - imagew) / 2), int((bgheight - imageh) / 2)), im_alpha)
                    bg_alpha = ImageChops.screen(bg_alpha, temp)
                    bg.paste(im, (int((bgwidth - imagew) / 2), int((bgheight - imageh) / 2)))
                    im = bg

                    im.save(file_name + ".png", "PNG")

                except Exception as e:
                    print(e)
                    im = Image.open(tpicf)

                    try:
                        im.thumbnail(size, Image.Resampling.LANCZOS)
                    except:
                        im.thumbnail(size, Image.ANTIALIAS)

                    im.save(tpicf)

            except Exception as e:
                print("******* picon resize failed *******")
                print(e)
        else:
            print("******* make picon failed *******")
            tpicf = defpic

        pix.append(j)
        pix[j] = picf
        j += 1

    cmd1 = "cp " + tmpfold + "/* " + picfold
    os.system(cmd1)

    cmd1 = "rm " + tmpfold + "/* &"
    os.system(cmd1)
    return pix


def downloadPic(output, poster):
    try:
        if output is not None:
            f = open(poster, 'wb')
            f.write(output)
            f.close()
    except Exception as e:
        print('error ', str(e))
    return


def downloadError(output):
    print('output error ', output)
    pass


def savePoster(dwn_poster, url_poster):
    with open(dwn_poster, 'wb') as f:
        f.write(requests.get(url_poster, stream=True, allow_redirects=True).content)
        f.close()


def up(names, tmppics, pos, menu, pixmap):
    menu.up()
    pos = pos - 1
    num = len(names)
    if pos == -1:
        pos = num - 1
        menu.moveToIndex(pos)
    name = names[pos]
    if name == "Exit":
        pixmap.instance.setPixmapFromFile(exitz)
    else:
        try:
            pic = tmppics[pos]
            pixmap.instance.setPixmapFromFile(pic)
        except:
            pass
    return pos


def down(names, tmppics, pos, menu, pixmap):
    print("In def down tmppics =", tmppics)
    menu.down()
    pos = pos + 1
    num = len(names)
    if pos == num:
        pos = 0
        menu.moveToIndex(pos)
    name = names[pos]
    if name == "Exit":
        pixmap.instance.setPixmapFromFile(exitz)
    else:
        try:
            pic = tmppics[pos]
            print("In def down pic =", pic)
            pixmap.instance.setPixmapFromFile(pic)
        except:
            pass
    return pos


def left(names, tmppics, pos, menu, pixmap):
    menu.pageUp()
    pos = menu.getSelectionIndex()
    name = names[pos]
    if name != "Exit":
        pic = tmppics[pos]
        pixmap.instance.setPixmapFromFile(pic)
    else:
        try:
            pixmap.instance.setPixmapFromFile(exitz)
        except:
            pass
    return pos


def right(names, tmppics, pos, menu, pixmap):
    menu.pageDown()
    pos = menu.getSelectionIndex()
    name = names[pos]
    if name != "Exit":
        pic = tmppics[pos]
        pixmap.instance.setPixmapFromFile(pic)
    else:
        try:
            pixmap.instance.setPixmapFromFile(exitz)
        except:
            pass
    return pos


def update_xbmc_text(addon_id):  # #mfaraj to update the file from xbmc client to be used by xbmc library files
    if addon_id is None:
        return
    try:
        cachefolder = cfg.cachefold.value
    except:
        cachefolder = "/media/hdd"
    afile = open("/etc/xbmc.txt", 'w')
    afile.write(cachefolder)
    afile.close()


class Rundefault(Screen):
    def __init__(self, session, name, url, nextrun, progressCallBack=None):
        Screen.__init__(self, session)
        self.name = name
        self.session = session
        # lululla added
        global _session
        _session = session
        # end
        self.url = url
        self.nextrun = nextrun
        self.onShown.append(self.start)
        self.error = None
        self.data1 = ''
        self.updateTimer = eTimer()
        try:
            self.updateTimer_conn = self.updateTimer.timeout.connect(self.updateStatus)
        except AttributeError:
            self.updateTimer.callback.append(self.updateStatus)
        self.timecount = 0
        ncount = cfg.wait.value
        self.timeint = 1000
        self.nct = int(ncount)
        self.error = ''
        self.progressCallBack = progressCallBack
        self.progress = (_('Please wait...\n'))
        if os.path.exists("/tmp/stopaddon"):
            os.remove("/tmp/stopaddon")

    def start(self):
        url = self.url
        name = self.name
        if DEBUG == 1:
            print("In Rundefault name =", name)
            print("In Rundefault url =", url)
            print("In Rundefault self.nextrun =", self.nextrun)
#                print  "In Rundefault url B=", url
        if (THISPLUG not in url):
            desc = " "
            self.progressCallBack("Finished")
            self.updateTimer.stop()
            self.session.open(Playoptions, name, url, desc)
            self.close()

        else:
            # pictures?###########
            n1 = url.find("default.py?", 0)
            urla = url[(n1+11):]
            print("In Rundefault urla =", urla)
            plugin_id = os.path.split(THISADDON)[1]
            if ("plugin.image" in plugin_id) or ("plugin.picture" in plugin_id) and ("url=" not in urla) and ("plugin://" not in urla):
                print("In Rundefault going in picshow")
                self.picshow(urla)
            else:
                global HANDLE
                hdl = int(HANDLE)
                hdl = hdl + 1
                HANDLE = str(hdl)
                n1 = url.find('?', 0)
                if n1 < 0:
                    return
                url1 = url[:n1]
                url2 = url[n1:]
                url2 = url2.replace(" ", "%20")
                if "plugin://plugin.video.youtube/" in url:
                    url1 = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/" + ADDONCAT + "/plugin.video.youtube/default.py"
                    url2 = url2.replace("plugin://plugin.video.youtube/?", "path=/root/video&")
                    # url2 = url[n1:]
                    # url2 = url2.replace(" ", "%20")
                arg = url1 + " " + HANDLE + " '" + url2 + "'"
                if DEBUG == 1:
                    print("Rundefault arg =", arg)
                self.arg = arg
                self.stream()

    def picshow(self, urla):
        xurl = urla
        xdest = "/tmp/picture.png"
        downloadPage(xurl, xdest).addCallback(self.picture).addErrback(self.showError)

    def showError(self, error):
        print("ERROR :", error)

    def picture(self, fplug):
        pic = "/tmp/picture.png"
        self.session.open(Splash3, pic)  # Splash3 ???

    def stoprun(self):
        self.close()
        try:
            self.container.appClosed.remove(self.runFinished)
            self.container.dataAvail.remove(self.dataAvail)
            self.progressCallBack("Finished")
        except:
            pass

    def dataAvail(self, rstr):
        if os.path.exists("/tmp/stopaddon"):
            self.stoprun()
            return
        if rstr:
            self.data1 = self.data1+rstr
            if self.progressCallBack is not None:
                self.progress = self.progress + "..."
                self.progressCallBack(self.progress)

    def stream(self):
        self.picfold = cfg.cachefold.value + "/xbmc/pic"
        self.tmpfold = cfg.cachefold.value + "/xbmc/tmp"
        # cmd = "rm -rf " + self.tmpfold
        # os.system(cmd)
        if os.path.exists("/tmp/stopaddon"):
            self.stoprun()
            return
        if DEBUG == 1:
            print("In rundef self.arg =", self.arg)
        cmd = "python " + self.arg
        print("In rundef cmd A=", cmd)
        afile = open("/tmp/test.txt", "w")
        afile.write("going in default.py")
        afile.write(cmd)
        fdef = 'default'  # NEWDEFPY[:-3]
        args = cmd.split(" ")
        arg1 = args[1]
        arg2 = args[2]
        arg3 = args[3]
        arg4 = cfg.cachefold.value
        sys.argv = [arg1, arg2, arg3, arg4]
        self.plugin_id = os.path.split(THISADDON)[1]
        print("539arg3 =", arg3)
        if 'select=true' in arg3:
            f = open("/tmp/result.txt", "w")
            line = arg3.replace("'?", "")
            params = parameters_string_to_dict(line)
            print("Here in select writing result.txt params =", params)
            for key in list(params.keys()):
                if "url" in key:
                    url = params[key]
                    break
            # url = params.get("url","0")
            text = url + "\n"
            print("Here in select writing result.txt text =", text)
            f.write(text)
            f.close()
            myfile = file(r"/tmp/arg1.txt")
            icount = 0
            for line in myfile.readlines():
                sysarg = line
                sysarg = sysarg.replace("\n", "")
                icount += 1
                if icount > 0:
                    break
            print("sysarg =", sysarg)
            args = sysarg.split(" ")
            cmd = "python '" + args[0] + "' '1' '" + args[2] + "'"
        else:
            print("In rundef cmd B=", cmd)
            print("In rundef cmd C=", cmd)
        # cmd='python '+xpath_file+' 1 '+arg3
        self.container = eConsoleAppContainer()

        self.data1 = ''
        if os.path.exists("/tmp/data.txt"):
            os.remove("/tmp/data.txt")
        # if DEBUG == 1:
        self.lastcmd = cmd
        global LAST
        LAST = self.lastcmd
        cmd = cmd + " &"
        print("In Rundefault cmd =", cmd)
        self.dtext = " "
        print("cmd 2=", cmd)
        self.p = os.popen(cmd)
        self.timecount = 0
        self.updateTimer.start(self.timeint)

    def showback(self):
        myfile = file(r"/tmp/arg1.txt")
        icount = 0
        for line in myfile.readlines():
            sysarg = line
            sysarg = sysarg.replace("\n", "")
            icount += 1
            if icount > 0:
                break
        print("sysarg =", sysarg)
        args = sysarg.split(" ")
        cmd = "python '" + args[0] + "' '1' '" + args[2] + "' &"
        os.system(cmd)

    def updateStatus(self):
        ncount = cfg.wait.value
        self.timecount = self.timecount + 1
        print("In rundef updateStatus self.timecount =", self.timecount)
        self.dtext = self.p.read()
        print("In rundef updateStatus self.dtext =", self.dtext)
        global dtext1
        if len(self.dtext) > 0:
            dtext1 = dtext1 + self.dtext
        if "data B" in self.dtext:
            self.updateTimer.stop()
            self.action(" ")
        """
        if os.path.exists(self.dfile):
        b1 = os.path.getsize(self.dfile)
        if b1 > 0:
          print   "In rundef b1 =", b1
          b = b1 / 1000
          print   "In rundef b =", b
          try:
              print   "In rundef self.bLast =", self.bLast
              if b == self.bLast:
                 self.updateTimer.stop()
                 self.action(" ")
          except:
               pass
          self.bLast = b
        """
        print("In rundef self.timecount =", self.timecount)
        if self.timecount > self.nct:
            self.updateTimer.stop()
        f1 = open("/tmp/e.log", "a")
        # f1.write(dtext1)
        f1.close()
        self.action(" ")

    def callback(self, result):
        if result:
            self.stream()

    def action(self, retval):
        print("In Rundefault action 1")
        if os.path.exists("/tmp/stopaddon"):
            self.stoprun()
            return
        # str = self.data1
        print("In Rundefault action 2")
        self.data = []
        self.names = []
        self.urls = []
        self.pics = []
        self.names.append("Exit")
        self.urls.append(" ")
        self.pics.append(exitz)
        self.tmppics = []
        self.lines = []
        self.vidinfo = []
        afile = open("/tmp/test.txt", "w")
        afile.write("\nin action=")
        # datain = ""
        parameters = []
        print("In Rundefault action 3")
        self.data = []
        # dtext = self.p.read()
        data = self.dtext.splitlines()
        for line in data:
            print("In Rundefault line =", line)
            if "data B" not in line:
                continue
            else:
                i1 = line.find("&", 0)
                line1 = line[i1:]
                self.data.append(line1)
        print("In Rundefault self.data =", self.data)
        ln = len(self.data)
        if ln == 0:
            cmd = LAST + " > /tmp/error.log 2>&1 &"
            os.system(cmd)
            self.error = (_("Error! Try another item OR exit and submit log /tmp/e.log and /tmp/error.log"))
            self.progressCallBack((_("Error! Try another item OR exit and submit log /tmp/e.log and /tmp/error.log")))
            return

        n1 = 0
        if n1 == 0:
            inum = len(self.data)
            i = 0
            while i < inum:
                name = " "
                url = " "
                line = self.data[i]
                if DEBUG == 1:
                    print("In rundef line B=", line)
                if line.startswith("&"):
                    line = line[1:]
                    # print   "In rundef line C=", line
                params = parameters_string_to_dict(line)
                if DEBUG == 1:
                    print("Rundefault params=", params)
                self.lines.append(line)
                try:
                    name = params.get("name")
                    name = name.replace("AxNxD", "&")
                    name = name.replace("ExQ", "=")
                    if DEBUG == 1:
                        print("Rundefault name=", name)
                except:
                    pass
                try:
                    url = params.get("url")
                    url = url.replace("AxNxD", "&")
                    url = url.replace("ExQ", "=")
                    if DEBUG == 1:
                        print("Rundefault url=", url)
                except:
                    pass

                thumbnailImage = params.get("thumbnailImage")
                iconImage = params.get("iconImage")
                try:
                    if thumbnailImage.startswith("http"):
                        pic = thumbnailImage
                        print("Rundefault pic A=", pic)
                    elif iconImage.startswith("http"):
                        pic = iconImage
                        print("Rundefault pic B=", pic)
                    else:
                        pic = defpic

                except:
                    pic = defpic

                if DEBUG == 1:
                    print("Rundefault pic=", pic)
                self.names.append(name)
                self.urls.append(url)
                self.pics.append(pic)
                i += 1

            if DEBUG == 1:
                print("Rundefault self.names=", self.names)
                print("Rundefault self.urls=", self.urls)
                print("Rundefault self.pics=", self.pics)
        picindic = 0
        ipc = 4
        plen = len(self.pics)
        if plen < 10:
            ipcn = plen
        else:
            ipcn = 10
        if plen > 3:
            while ipc < ipcn:
                print("Here in Rundefault self.pics[ipc] =", self.pics[ipc])
                if ("default.png" not in self.pics[ipc]) and ("defaultL.png" not in self.pics[ipc]):
                    print("Here in Rundefault default not in self.pics[ipc]")
                    picindic = 1
                ipc += 1

        if 'showtext' in self.urls[1]:
            f = open("/tmp/show.txt", "r")
            fpage = f.read()
            self.session.openWithCallback(self.close, ShowPage2, fpage)

        elif (len(self.names) == 2) and (self.urls[1] is None) and (THISPLUG not in self.names[1]):
            if "*download*" in self.names[1]:
                url = self.names[1].replace("*download*", "")
                name = self.name
                desc = " "
                self.progressCallBack("Finished")
                self.updateTimer.stop()
                self.session.open(Getvid, name, url, desc)
                self.close()
            elif "*download2*" in self.names[1]:
                url = self.names[1].replace("*download2*", "")
                name = self.name
                desc = " "
                self.progressCallBack("Finished")
                self.updateTimer.stop()
                self.session.open(Getvid2, name, url, desc)
                self.close()
            elif ("stack://" in self.names[1]):
                stkurl = self.names[1]
                self.playstack(stkurl)

            elif ("rtmp" in self.names[1]):
                if "live" in name:
                    name = self.name
                    desc = " "
                    url = self.names[1]
                    # self.session.open(Showrtmp2, name, url, desc)
                    self.progressCallBack("Finished")
                    self.updateTimer.stop()
                    self.session.open(Playoptions, name, url, desc)
                    self.close()

                else:
                    name = self.name
                    desc = " "
                    url = self.names[1]
                    # self.session.open(Showrtmp, name, url, desc)
                    self.progressCallBack("Finished")
                    self.updateTimer.stop()
                    self.session.open(Playoptions, name, url, desc)
                    self.close()

            else:
                name = self.name
                desc = " "
                url = self.names[1]
                self.progressCallBack("Finished")
                self.updateTimer.stop()
                self.session.open(Playoptions, name, url, desc)
                self.close()
        elif (len(self.names) == 2) and (self.urls[1] is not None) and (THISPLUG not in self.urls[1]):
            url = self.urls[1]
            if "*download*" in url:
                url = url.replace("*download*", "")
                name = self.name
                desc = " "
                self.progressCallBack("Finished")
                self.updateTimer.stop()
                self.session.open(Getvid, name, url, desc)
                self.close()
            elif "*download2*" in url:
                url = url.replace("*download2*", "")
                name = self.name
                desc = " "
                self.progressCallBack("")
                self.updateTimer.stop()
                self.session.open(Getvid2, name, url, desc)
                self.close()

            else:
                name = self.name
                desc = " "
                self.progressCallBack("Finished")
                self.updateTimer.stop()
                self.session.open(Playoptions, name, url, desc)
                self.close()

        else:
            inm = 0
            for name in self.names:
                if name is None:
                    self.names[inm] = "Video"
                self.names[inm] = self.names[inm].replace(":", "-")
                self.names[inm] = self.names[inm].replace("&", "-")
                self.names[inm] = self.names[inm].replace("'", "-")
                self.names[inm] = self.names[inm].replace("?", "-")
                self.names[inm] = self.names[inm].replace("/", "-")
                self.names[inm] = self.names[inm].replace("#", "-")
                self.names[inm] = self.names[inm].replace("|", "-")
                self.names[inm] = self.names[inm].replace("*", "")
                self.names[inm] = Utils.cleanName(self.names[inm])
                inm += 1
            ipic = 2
            npic = len(self.pics)
            cpic = self.pics[1]
            print("cpic =", cpic)
            print("self.pics A=", self.pics)
            while ipic < npic:
                pic = self.pics[ipic]
                if pic == cpic:
                    self.pics[ipic] = defpic
                ipic += 1
            print("self.pics B=", self.pics)
            print("In rundefault picindic =", picindic)
            if cfg.thumb.value == "True":
                if picindic == 1:
                    self.tmppics = getpics(self.names, self.pics, self.tmpfold, self.picfold)
                    self.session.open(XbmcPluginPics, self.name, self.names, self.urls, self.tmppics, self.nextrun)
                else:
                    self.tmppics = getpics(self.names, self.pics, self.tmpfold, self.picfold)
                    self.session.open(XbmcPluginScreen, self.name, self.names, self.urls, self.tmppics, self.nextrun, picindic)

            else:
                self.tmppics = getpics(self.names, self.pics, self.tmpfold, self.picfold)
                self.session.open(XbmcPluginScreen, self.name, self.names, self.urls, self.tmppics, self.nextrun, picindic)

    def playstack(self, urlFull):
        if DEBUG == 1:
            print("urlFull =", urlFull)
        playlist = []
        names = []
        i = 0
        start = 0
        while i < 20:
            n1 = urlFull.find("http", start)
            if n1 < 0:
                break
            n2 = urlFull.find("http", (n1+4))
            if n2 < 0:
                n2 = len(urlFull)
            url1 = urlFull[n1:n2]
            # print   "url1 =", url1
            n3 = url1.find(".mp4", 0)
            if n3 < 0:
                n3 = url1.find(".flv", 0)
                if n3 < 0:
                    break
            url1 = url1[0:(n3 + 4)]
            name = "Video" + str(i)
            playlist.append(url1)
            names.append(name)
            start = n2 - 1
            i += 1
        idx = 0
        self.session.open(Playlist, idx, names, playlist)  # playlist not exist ???


class XbmcPluginPics(Screen):

    def __init__(self, session, name, names, urls, tmppics, curr_run):
        self.skinName = "XbmcPluginPics"
        Screen.__init__(self, session)
        title = PlugDescription
        self.session = session
        # lululla added
        global _session
        _session = session
        # end
        self["title"] = Button(title + Version)
        # self["bild"] = startspinner()
        self.curr_run = curr_run
        self.nextrun = self.curr_run+1
        self.pos = []

        if Utils.isFHD():
            self.pos.append([122, 42])
            self.pos.append([478, 42])
            self.pos.append([834, 42])
            self.pos.append([1190, 42])
            self.pos.append([1546, 42])
            self.pos.append([122, 522])
            self.pos.append([478, 522])
            self.pos.append([834, 522])
            self.pos.append([1190, 522])
            self.pos.append([1546, 522])
        else:
            self.pos.append([81, 28])
            self.pos.append([319, 28])
            self.pos.append([556, 28])
            self.pos.append([793, 28])
            self.pos.append([1031, 28])
            self.pos.append([81, 348])
            self.pos.append([319, 348])
            self.pos.append([556, 348])
            self.pos.append([793, 348])
            self.pos.append([1031, 348])

        print(" self.pos =", self.pos)
        list = []
        self.name = name
        self.pics = tmppics
        self.mlist = names
        self.urls1 = urls
        self.names1 = names
        self["info"] = Label()
        self.curr_run = curr_run
        txt = str(SELECT[self.curr_run])
        print("In XbmcPluginScreen SELECT[self.curr_run] A=", SELECT[self.curr_run])
        self.nextrun = self.curr_run+1
        print("2028", txt)
        self.select = txt
        self.rundef = None
        self.plug = ''
        self.keylock = False
        # self.spinner_running = False
        print("self.mlist =", self.mlist)
        list = names
        self["menu"] = List(list)
        for x in list:
            print("x in list =", x)
        ip = 0
        print("self.pics = ", self.pics)
        self["frame"] = MovingPixmap()
        i = 0
        while i < 20:
            self["label" + str(i + 1)] = StaticText()
            self["pixmap" + str(i + 1)] = Pixmap()
            i += 1

        i = 0
        self["actions"] = NumberActionMap(["OkCancelActions", "MenuActions", "DirectionActions", "NumberActions"],
                                          {"ok": self.okClicked,
                                           "cancel": self.cancel,
                                           "left": self.key_left,
                                           "right": self.key_right,
                                           "up": self.key_up,
                                           "info": self.showIMDB,
                                           "epg": self.showIMDB,
                                           "down": self.key_down})

        self.index = 0
        ln = len(self.names1)
        self.npage = int(float(ln / 10)) + 1
        print("self.npage =", self.npage)
        self.ipage = 1
        self.icount = 0
        print("Going in openTest")
        self.onLayoutFinish.append(self.openTest)

    def cancel(self):
        self.close()

    def showIMDB(self):
        itype = self.index
        text_clear = self.names1[itype]
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def exit(self):
        # if self.spinner_running is True:
        # self.stopSpinner()
        self.keylock = False
        afile = open("/tmp/stopaddon", "w")
        afile.write("stop execution")
        afile.close()
        self.progressCallBack("Finished")
        try:
            self.rundef.stoprun()
        except:
            pass
        # else:
            # self.stopSpinner()
        self.close()

    def progressCallBack(self, progress):
        try:
            if progress is not None:
                if progress.startswith("Error"):
                    self.keylock = False
                    self["info"].setText(progress)
                    return
                if progress == "Finished":
                    self.keylock = False
                    self.selection_changed()
                    return
            self["info"].setText(progress)
        except:
            pass

    def selection_changed(self):
        self.keylock = False
        try:
            self["info"].setText(self.select)
        except:
            pass

    def info(self):
        itype = self.index
        self.inf = self.infos[itype]
        self.inf = ''
        try:
            self.inf = self.infos[itype]
        except:
            pass
        if self.inf:
            try:
                self["info"].setText(self.inf)
            except:
                self["info"].setText('')
        print("In GridMain infos =", self.inf)

    def paintFrame(self):
        # print("In paintFrame self.index, self.minentry, self.maxentry =", self.index, self.minentry, self.maxentry)
        # print("In paintFrame self.ipage = ", self.ipage)
        try:
            ifr = self.index - (10 * (self.ipage - 1))
            # print("ifr =", ifr)
            ipos = self.pos[ifr]
            # print("ipos =", ipos)
            self["frame"].moveTo(ipos[0], ipos[1], 1)
            self["frame"].startMoving()
            self.info()
        except Exception as e:
            print('error  in paintframe: ', str(e))

    def openTest(self):
        print("self.index, openTest self.ipage, self.npage =", self.index, self.ipage, self.npage)
        if self.ipage < self.npage:
            self.maxentry = (10*self.ipage)-1
            self.minentry = (self.ipage-1)*10
            print("self.ipage , self.minentry, self.maxentry =", self.ipage, self.minentry, self.maxentry)

        elif self.ipage == self.npage:
            print("self.ipage , len(self.pics) =", self.ipage, len(self.pics))
            self.maxentry = len(self.pics) - 1
            self.minentry = (self.ipage-1)*10
            print("self.ipage , self.minentry, self.maxentry B=", self.ipage, self.minentry, self.maxentry)
            i1 = 0
            blpic = dblank
            while i1 < 10:
                self["label" + str(i1+1)].setText(" ")
                self["pixmap" + str(i1+1)].instance.setPixmapFromFile(blpic)
                i1 += 1
        print("len(self.pics), self.minentry, self.maxentry =", len(self.pics), self.minentry, self.maxentry)
        self.npics = len(self.pics)
        i = 0
        i1 = 0
        self.picnum = 0
        print("doing pixmap")
        ln = self.maxentry - (self.minentry-1)
        while i < ln:
            idx = self.minentry + i
            print("i, idx =", i, idx)
            print("self.names1[idx] B=", self.names1[idx])
            self["label" + str(i+1)].setText(self.names1[idx])
            print("idx, self.pics[idx]", idx, self.pics[idx])
            pic = self.pics[idx]
            print("pic =", pic)
            if os.path.exists(pic):
                print("pic path exists")
            else:
                print("pic path exists not")
            picd = defpic
            try:
                self["pixmap" + str(i+1)].instance.setPixmapFromFile(pic)  # ok
            except:
                self["pixmap" + str(i+1)].instance.setPixmapFromFile(picd)
            i += 1
        self.index = self.minentry
        print("self.minentry, self.index =", self.minentry, self.index)
        self.paintFrame()

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
            self.key_up()
        else:
            self.paintFrame()

    def key_right(self):
        i = self.npics - 1
        if self.index == i:
            self.index = 0
            self.ipage = 1
            self.openTest()
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
            self.key_down()
        else:
            self.paintFrame()

    def key_up(self):
        print("keyup self.index, self.minentry = ", self.index, self.minentry)
        self.index = self.index - 5
        print("keyup self.index, self.minentry 2 = ", self.index, self.minentry)
        print("keyup self.ipage = ", self.ipage)
        if self.index < (self.minentry):
            if self.ipage > 1:
                self.ipage = self.ipage - 1
                self.openTest()
            elif self.ipage == 1:
                return
            else:
                self.index = 0
            self.paintFrame()
        else:
            self.paintFrame()

    def key_down(self):
        # print("keydown self.index, self.maxentry = ", self.index, self.maxentry)
        self.index = self.index + 5
        # print("keydown self.index, self.maxentry 2= ", self.index, self.maxentry)
        # print("keydown self.ipage = ", self.ipage)
        if self.index > (self.maxentry):
            if self.ipage < self.npage:
                self.ipage = self.ipage + 1
                self.openTest()
            elif self.ipage == self.npage:
                self.index = 0
                self.ipage = 1
                self.openTest()
            else:
                # print("keydown self.index, self.maxentry 3= ", self.index, self.maxentry)
                self.index = 0
            self.paintFrame()
        else:
            self.paintFrame()

    def okClicked(self):
        if self.keylock:
            return
        if DEBUG == 1:
            print("screen number" + str(self.curr_run) + "okClicked")
        itype = self.index
        url = self.urls1[itype]
        name = self.names1[itype]
        self.name = name
        global SELECT
        # SELECT.append(self.name)
        # print("screen number" + str(self.curr_run)+"okClicked SELECT[0]=", SELECT[0])
        # SELECT[self.curr_run] = SELECT[self.curr_run-1] + " -> " + self.name
        SELECT.append(SELECT[self.curr_run] + " -> " + self.name)
        self.next_select = SELECT[self.curr_run]
        self.url = url
        print("In XbmcPluginScreen self.name =", self.name)
        if ('search' in self.name.lower()) or ('insert' in self.name.lower()):
            # ShowSearchDialog(self.session)
            print("In XbmcPluginScreen search")
            ebuf = []
            ebuf.append((_("New"), ""))
            f = file(r"/etc/history")
            fileslist = []
            icount = 0
            for line in f.readlines():
                fileslist.append(icount)
                fileslist[icount] = (_(line[:-1]), line)
                if icount > 0:
                    ebuf.append(fileslist[icount])
                icount += 1
            self.session.openWithCallback(self.Searchtest, ChoiceBox, title="Please Select", list=ebuf)

        else:
            if itype == 0:
                self.cancel()
            elif itype == 1 and self.curr_run == 1:
                if name == "Setup":  # ##to generate e2 e2sett.py
                    d = THISPLUG + "/plugins/" + self.plug
                    settings_file = d + "/resources/settings.xml"
                    import os
                    if not os.path.exists(settings_file):
                        self['info'].setText(_("No settings available"))
                        return
                    try:
                        from Plugins.Extensions.KodiLite.lib.XBMCAddonsSetup import AddonsettScreen
                    except:
                        from .lib.XBMCAddonsSetup import AddonsettScreen
                    self.session.open(AddonsettScreen, self.plug)
                    return
            elif itype == 2 and self.name == "Favorites":
                favorites_xml = "/etc/KodiLite/favorites.xml"
                import os
                if not os.path.exists(favorites_xml):
                    try:
                        if not os.path.exists("/etc/KodiLite"):
                            os.makedirs("/etc/KodiLite")
                        copyfile(THISPLUG + "/lib/defaults/favorites.xml", favorites_xml)
                    except:
                        return
                try:
                    from Plugins.Extensions.KodiLite.lib.favorites import getfavorites
                except:
                    from .lib.favorites import getfavorites
                favlist = getfavorites(self.plug)
                names2 = []
                urls2 = []
                names2.append("Exit")
                urls2.append("")
                for fav in favlist:
                    names2.append(fav[0])
                    urls2.append(fav[1])
                self.session.open(Favorites, names2, urls2)
                return
            else:
                self["info"].setText("Please wait ...")
                self.rundef = Rundefault(self.session, name, url, self.nextrun, self.progressCallBack)
                self.rundef.start()
        self["info"].setText("Select")

# plugin://plugin.video.youtube/kodion/search/query/?q=adele
    def Searchtest(self, res):
        if res is None:
            self.close()
        else:
            txt = " "
            if "Delete history" in res[0]:
                f = open("/etc/history", "w")
                f.write(" ")
                txt = " "
            elif "New text" in res[0]:
                txt = " "
            else:
                txt = res[0]
            print("In XbmcPluginScreen Searchtest txt=", txt)
            self.session.openWithCallback(self.searchCallback, VirtualKeyBoard, title=(_("Enter your search term(s)")), text=txt)

    def searchCallback(self, search_txt):
        if search_txt:
            print("In XbmcPluginScreen self.url 2=", self.url)
            print("In XbmcPluginScreen search_txt 1=", search_txt)
            n1 = self.url.find("?", 0)
            file = open("/tmp/xbmc_search.txt", 'w')
            file.write(search_txt)
            file.close()
            if os.path.exists("/etc/history"):
                f = open("/etc/history", 'a+')
                hist = f.read()
                print("In XbmcPluginScreen search_txt hist =", hist)
            else:
                hist = " "
                f = open("/etc/history", 'a+')
            if search_txt not in hist:
                newtxt = search_txt + "\n"
                f.write(newtxt)
                f.close()
            else:
                f.close()
            self["info"].setText(_("Please wait.."))
            # self.keylock=True
            rundef = Rundefault(self.session, self.name, self.url, 2, self.progressCallBack)
            rundef.start()
            if rundef.error:
                self["info"].setText(_("Error:") + rundef.error)


class XbmcPluginScreen(Screen):

    def __init__(self, session, name, names, urls, tmppics, curr_run, picindic):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        print("Here in XbmcPluginScreen picindic =", picindic)
        if picindic == 0:
            self.skinName = "XbmcPluginScreenF"
        else:
            if cfg.thumb.value == "Single":
                self.skinName = "XbmcPluginScreenS"
            else:
                self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.curr_run = curr_run
        self.nextrun = self.curr_run + 1
        self.rundef = None
        self.plug = ''
        self.keylock = False
        name1 = name.replace("plugin.video.", "")
        name1 = name1.replace("plugin.audio.", "")
        name1 = name1.replace("plugin.image.", "")
        name1 = name1.replace("plugin.picture.", "")
        print("name1 =", name1)
        self.select = name1
        self["info"].setText(self.select)
        self["pixmap1"] = Pixmap()
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self["actions"] = NumberActionMap(["OkCancelActions", "DirectionActions", "ColorActions", "EPGSelectActions"], {
                                           "upRepeated": self.up,
                                           "downRepeated": self.down,
                                           "up": self.up,
                                           "down": self.down,
                                           "info": self.showIMDB,
                                           "epg": self.showIMDB,
                                           "left": self.left,
                                           "right": self.right,
                                           "red": self.cancel,
                                           "green": self.okClicked,
                                           "ok": self.okClicked,
                                           "cancel": self.cancel}, -1)
        self.plug = name
        self.handle = 1
        self.names1 = []
        for nam in names:
            if nam is None:
                nam = "Video"
            self.names1.append(nam)
            # self.names1 = names
        self.urls1 = urls
        self.tmppics1 = tmppics
        if DEBUG == 1:
            print("screen number" + str(self.curr_run) + "self.names1 =", self.names1)
            print("screen number" + str(self.curr_run) + "self.urls1 =", self.urls1)
            print("screen number" + str(self.curr_run) + "self.tmppics1 =", self.tmppics1)
        if "showtext=true" in self.urls1[1]:
            """
            f = open("/tmp/show.txt", "r")
            fpage = f.read()
            # self.session.openWithCallback(self.showback, ShowPage2, fpage)
            self.onShown.append(ShowPage2, fpage)
            """
            pass
        self.names = []
        self.urls = []
        self.pics = []
        self.tmppics = []
        self.sett = []
        self.lines = []
        self.vidinfo = []
        self.data = []
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        os.system("rm /tmp/data.txt")
        self.pos = 0
        self.missed = " "
        self.shlist = " "
        self["menu"].onSelectionChanged.append(self.selection_changed)
        self.onShown.append(self.selection_changed)
        self.onLayoutFinish.append(self.action)

    def cancel(self):
        self.close()

    def showIMDB(self):
        itype = self.index
        text_clear = self.names1[itype]
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def exit(self):
        # if self.spinner_running is True:
        # self.stopSpinner()
        self.keylock = False
        afile = open("/tmp/stopaddon", "w")
        afile.write("stop execution")
        afile.close()
        self.progressCallBack("Finished")
        try:
            self.rundef.stoprun()
        except:
            pass
        # else:
            # self.stopSpinner()
        self.close()

    def progressCallBack(self, progress):
        try:
            if progress is not None:
                if progress.startswith("Error"):
                    self.keylock = False
                    self["info"].setText(progress)
                    return
                if progress == "Finished":
                    self.keylock = False
                    self.selection_changed()
                    return
            self["info"].setText(progress)
        except:
            pass

    def selection_changed(self):
        self.keylock = False
        try:
            self["info"].setText(self.select)
        except:
            pass

    def showerror(self):
        try:
            from Plugins.Extensions.KodiLite.lib.XBMCAddonsinfo import XBMCAddonsinfoScreen
        except:
            from .lib.XBMCAddonsinfo import XBMCAddonsinfoScreen
        self.session.open(XBMCAddonsinfoScreen, None)

    def home(self):
        self.session.open(StartPlugin)  # not exist this ??
        self.close()

    def action(self):
        try:
            if os.path.exists("/tmp/netstat.txt"):
                os.remove("/tmp/netstat.txt")
            os.system("netstat -np > /tmp/netstat.txt && sleep 1")
            f1 = open('/tmp/netstat.txt', "r+")
            for line in f1.readlines():
                if '55333' in line:
                    n1 = line.find("/", 0)
                    if n1 < 0:
                        continue
                    n2 = line.rfind(" ", 0, n1)
                    pid = line[(n2+1):n1]
                    print("In Rundefault pid =", pid)
                    cmdnet = "kill " + str(pid)
                    self.container = eConsoleAppContainer()
                    self.container.execute(cmdnet)
        except:
            pass

        if cfg.thumb.value == "False":
            picthumb = defpic
            self["pixmap1"].instance.setPixmapFromFile(picthumb)
        # print   "In XbmcPluginScreen self.names1 =", self.names1
        Utils.showlist(self.names1, self["menu"])

    def up(self):
        if self.keylock:
            return
        self.pos = up(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap1"])

    def down(self):
        if self.keylock:
            return
        self.pos = down(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap1"])

    def left(self):
        if self.keylock:
            return
        self.pos = left(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap1"])

    def right(self):
        if self.keylock:
            return
        self.pos = right(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap1"])

    def keyRight(self):
        if self.keylock:
            return
        self["menu"].right()

    def vidError(self, reply):
        return

    def okClicked(self):
        # self["bild"] = startspinner()
        if self.keylock:
            return
        if DEBUG == 1:
            print("screen number"+str(self.curr_run) + "okClicked")
        itype = self["menu"].getSelectionIndex()
        url = self.urls1[itype]
        name = self.names1[itype]
        self.name = name
        global SELECT
        # SELECT.append(self.name)
        print("screen number"+str(self.curr_run)+"okClicked SELECT[0]=", SELECT[0])
        # SELECT[self.curr_run] = SELECT[self.curr_run-1] + " -> " + self.name
        SELECT.append(SELECT[self.curr_run] + " -> " + self.name)
        self.next_select = SELECT[self.curr_run]
        print("In XbmcPluginScreen self.curr_run =", self.curr_run)
        print("In XbmcPluginScreen SELECT[self.curr_run] =", SELECT[self.curr_run])
        print("In XbmcPluginScreen SELECT =", SELECT)
        self.url = url
        self.url = url
        print("In XbmcPluginScreen self.name =", self.name)
        if ('search' in self.name.lower()) or ('insert' in self.name.lower()):
            # ShowSearchDialog(self.session)
            print("In XbmcPluginScreen search")
            ebuf = []
            ebuf.append((_("Delete history"), ""))
            ebuf.append((_("New text"), ""))
            import os
            if not os.path.exists("/etc/history"):
                f = open("/etc/history", 'w+')
            else:
                f = open("/etc/history", 'r')
            # fileslist = []
            icount = 0
            for line in f.readlines():
                print("icount =", icount)
                print("line =", line)
                # fileslist.append(icount)
                # fileslist[icount] = (_(line[:-1]), "")
                # if icount>0:
                item = (_(line[:-1]), "")
                ebuf.append(item)
                icount = icount + 1
            self.session.openWithCallback(self.Searchtest, ChoiceBox, title="Please Select", list=ebuf)

        else:
            if itype == 0:
                self.cancel()
            elif itype == 1 and self.curr_run == 1:
                if name == "Setup":  # ##to generate e2 e2sett.py
                    d = THISPLUG + "/plugins/" + self.plug
                    settings_file = d + "/resources/settings.xml"
                    import os
                    if not os.path.exists(settings_file):
                        self['info'].setText(_("No settings available"))
                        return

                    try:
                        from Plugins.Extensions.KodiLite.lib.XBMCAddonsSetup import AddonsettScreen
                    except:
                        from .lib.XBMCAddonsSetup import AddonsettScreen
                    self.session.open(AddonsettScreen, self.plug)

                    return
            elif itype == 2 and self.name == "Favorites":
                # elif itype == 1 and self.name == "Favorites":
                favorites_xml = "/etc/KodiLite/favorites.xml"
                import os
                if not os.path.exists(favorites_xml):
                    try:
                        if not os.path.exists("/etc/KodiLite"):
                            os.makedirs("/etc/KodiLite")
                        copyfile(THISPLUG+"/lib/defaults/favorites.xml", favorites_xml)
                    except:
                        return
                try:
                    from Plugins.Extensions.KodiLite.lib.favorites import getfavorites
                except:
                    from .lib.favorites import getfavorites
                favlist = getfavorites(self.plug)
                names2 = []
                urls2 = []
                names2.append("Exit")
                urls2.append("")
                for fav in favlist:
                    names2.append(fav[0])
                    urls2.append(fav[1])
                self.session.open(Favorites, names2, urls2)
                return
            else:
                self["info"].setText("Please wait..")
                self.keylock = True
                # self.startSpinner()
                # dellog()
                self.rundef = Rundefault(self.session, name, url, self.nextrun, self.progressCallBack)
                self.rundef.start()
        self["info"].setText("Please Select")

#    plugin://plugin.video.youtube/kodion/search/query/?q=adele
    def Searchtest(self, res):
        if res is None:
            self.close()
        else:
            txt = " "
            if "Delete history" in res[0]:
                f = open("/etc/history", "w")
                f.write(" ")
                txt = " "
            elif "New text" in res[0]:
                txt = " "
            else:
                txt = res[0]
            print("In XbmcPluginScreen Searchtest txt=", txt)
            self.session.openWithCallback(self.searchCallback, VirtualKeyBoard, title=(_("Enter your search term(s)")), text=txt)

    def searchCallback(self, search_txt):
        if search_txt:
            print("In XbmcPluginScreen self.url 2=", self.url)
            print("In XbmcPluginScreen search_txt 1=", search_txt)
            n1 = self.url.find("?", 0)
            file = open("/tmp/xbmc_search.txt", 'w')
            file.write(search_txt)
            file.close()

            if os.path.exists("/etc/history"):
                f = open("/etc/history", 'a+')
                hist = f.read()
                print("In XbmcPluginScreen search_txt hist =", hist)
            else:
                hist = " "
                f = open("/etc/history", 'a+')
            if search_txt not in hist:
                newtxt = search_txt + "\n"
                f.write(newtxt)
                f.close()
            else:
                f.close()
            self["info"].setText(_("Please wait.."))
            self.keylock = True
            rundef = Rundefault(self.session, self.name, self.url, 2, self.progressCallBack)
            rundef.start()
            if rundef.error:
                self["info"].setText(_("Error:")+rundef.error)


class Favorites(Screen):

    def __init__(self, session, names, urls):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "Fav"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self["info"] = Label()
        self["pixmap1"] = Pixmap()
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button(_("Select"))
        self["key_yellow"] = Button(_("Delete favorite"))
        # self["key_blue"] = Button(_("More addons"))
        self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions"], {
                                           "red": self.close,
                                           "green": self.okClicked,
                                           "yellow": self.delete,
                                           # "blue": self.addon,
                                           "ok": self.okClicked,
                                           "cancel": self.close}, -1)
        self.names = names
        self.urls = urls
        self.onLayoutFinish.append(self.source)

    def source(self):
        pic = defpic
        self["pixmap1"].instance.setPixmapFromFile(pic)
        Utils.showlist(self.names, self["menu"])

    def okClicked(self):
        try:
            idx = self["menu"].getSelectionIndex()
            desc = " "
            name = self.names[idx]
            url = self.urls[idx]
            self.session.open(Playoptions, name, url, desc)
        except:
            self["info"].setText(_("No item selected !"))

    def delete(self):
        import xml.etree.ElementTree as ET
        xmlfile = "/etc/KodiLite/favorites.xml"
        tree = ET.parse(xmlfile)
        idx = self["menu"].getSelectionIndex()
        name = self.names[idx]
        root = tree.getroot()
        for addon in root.iter('addon'):
            for media in addon.iter('media'):
                title = media.get('title')
                if title == name:
                    addon.remove(media)
                tree.write(xmlfile)
        self.close()


class Start_mainmenu(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = "xbmc4A"
        self.session = session
        global _session
        _session = session
        # end
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["label1"] = StaticText("")
        self["label2"] = StaticText("")
        self["label3"] = StaticText("")
        self["label4"] = StaticText("")
        self["label20"] = StaticText("")
        self["label30"] = StaticText("")
        self["info"] = Label()
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        global newstext
        news = newstext
        self.cancel = False
        self.data1 = ''
        self.keylock = False
        self.progress = (" ")
        # print  "In StartPlugin_mainmenu newstext =", newstext
        self["info"].setText("Addons")
        self["pixmap1"] = Pixmap()
        self["menu"] = Utils.tvList([])
        self.progress = (" ")
        self["key_red"] = Button(_("Delete addon"))
        self["key_green"] = Button(_("Install addon"))
        self["key_yellow"] = Button(_("Config"))
        self["key_blue"] = Button(_("Show Error"))
        self["key_blue"].hide()
        user_log = '/tmp/error.log'
        if fileExists(user_log):
            self["key_blue"].show()
        os.system("rm /tmp/select.txt")
        self["menu"].onSelectionChanged.append(self.selection_changed)
        self.onShown.append(self.selection_changed)
        self["actions"] = NumberActionMap(["OkCancelActions",
                                           "ColorActions",
                                           "DirectionActions",
                                           "EPGSelectActions",
                                           "MenuActions"], {"upRepeated": self.up,
                                                            "downRepeated": self.down,
                                                            "up": self.up,
                                                            "down": self.down,
                                                            "left": self.left,
                                                            "right": self.right,
                                                            "red": self.delete,
                                                            "green": self.addon,
                                                            "yellow": self.conf,
                                                            "menu": self.conf,
                                                            "blue": self.openVi,
                                                            "ok": self.okClicked,
                                                            "epg": self.showIMDB,
                                                            "info": self.showIMDB,
                                                            "cancel": self.exit}, -1)
        self.updateTimer = eTimer()
        try:
            self.updateTimer_conn = self.updateTimer.timeout.connect(self.updateStatus)
        except AttributeError:
            self.updateTimer.callback.append(self.updateStatus)
        self.timecount = 0
        ncount = cfg.wait.value
        nc = int(ncount) * 1000
        timeint = int(float(nc/120))
        print("timeint =", timeint)
        self.timeint = 1000
        self.nct = int(float(nc/self.timeint))
        print("self.nct =", self.nct)
        self.pos = 0
        self.num = 0
        self.urls = []
        self.names = []
        self.shortnms = []
        self.data = []
        self.missed = " "
        self.shlist = " "
        try:
            self.fixscripts()
        except:
            pass
        print("StartPlugin_mainmenu 2")
        self.onLayoutFinish.append(self.listplugs)
        self.onLayoutFinish.append(self.showhide)

    def openVi(self):
        from .lib.type_utils import vEditor
        user_log = '/tmp/error.log'
        if fileExists(user_log):
            self.session.open(vEditor, user_log)

    def cancel(self):
        self.close()

    def exit(self):
        self.close()

    def fixscripts(self):
        url = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/list.txt"
        self.fixlist = Utils.getUrl(url)
        print("self.fixlist =", self.fixlist)
        pathsh = THISPLUG + "/scripts"
        for name in os.listdir(pathsh):
            self.name = name
            self.checkfixsh()
        return

    def delete(self):
        global ADDONCAT
        ADDONCAT = "plugins"
        self.session.openWithCallback(self.listplugs, DelAdd)

    def addon(self):
        global ADDONCAT
        ADDONCAT = "plugins"
        print("going to Getadds")
        self.session.openWithCallback(self.listplugs, Getadds)

    def conf(self):
        # self.session.open(XbmcConfigScreen)
        from . import settings
        self.session.openWithCallback(self.showhide, settings.XbmcConfigScreen)

    def selection_changed(self):
        self.keylock = False
        try:
            self.pos = self["menu"].getSelectionIndex()
            self.name = self.names[self.pos]
        except:
            pass

    def showIMDB(self):
        itype = self.index
        text_clear = self.names1[itype]
        if returnIMDB(text_clear):
            print('show imdb/tmdb')

    def showhide(self):
        self.pos = self["menu"].getSelectionIndex()
        num = len(self.names)
        name = self.names[self.pos]
        # print('2 self.pos ', self.pos)
        pname = PlugDescription
        version = Version
        provider = "Provider:"
        self["label30"].setText("Thank's to: ")
        prov = 'Lululla & Pcd'
        desc = 'Copyright (C) 2014'
        pic = defpic

        if self.pos == 0:
            pic = exitz
            provider = "Thank's to :"
            print('sel pos is == 0')

        if self.pos < -1:
            self.pos = num - 1
            self["menu"].moveToIndex(self.pos)
            name = self.names[self.pos]
            print('sel pos is < 0')

        if self.pos > 0:
            pic = THISPLUG + "/" + ADDONCAT + "/" + name + "/icon.png"
            self["pixmap1"].instance.setPixmapFromFile(pic)
            pname, version, prov, desc = self.getinfo(name)
            self["label1"].setText(pname)
            self["label20"].setText("Version:")
            self["label2"].setText(version)
            self["label30"].setText(provider)
            self["label3"].setText(prov)
            self["label4"].setText(desc)
            print('sel pos is > 0')

        if not fileExists(pic):
            pic = defpic
            self["pixmap1"].instance.setPixmapFromFile(pic)
            print('sel pos not exist')
        self["label1"].setText(pname)
        self["label20"].setText("Version:")
        self["label2"].setText(version)
        self["label30"].setText(provider)
        self["label3"].setText(prov)
        self["label4"].setText(desc)
        self["pixmap1"].instance.setPixmapFromFile(pic)
        user_log = '/tmp/error.log'
        if fileExists(user_log):
            self["key_blue"].show()

    def up(self):
        if self.keylock:
            return
        self["menu"].up()
        self.showhide()

    def down(self):
        if self.keylock:
            return
        self["menu"].down()
        self.showhide()

    def left(self):
        if self.keylock:
            return
        self["menu"].pageUp()
        self.showhide()

    def right(self):
        if self.keylock:
            return
        self["menu"].pageDown()
        self.showhide()

    def getinfo(self, name):
        xfile = THISPLUG + "/" + ADDONCAT + "/" + name + "/addon.xml"
        dedesc = ' '
        endesc = ' '
        itdesc = ' '
        try:
            tree = xml.etree.cElementTree.parse(xfile)
        except:
            return "", "", "", ""
        root = tree.getroot()
        pname = str(root.get('name'))
        version = str(root.get('version'))
        prov = str(root.get('provider-name'))
        try:
            for description in root.iter('description'):
                lang = description.get('lang')
                desc = str(description.text)
                if lang == "de":
                    dedesc = desc
                elif lang == "it":
                    itdesc = desc
                else:
                    endesc = desc
        except:
            for description in root.getiterator('description'):
                lang = description.get('lang')
                desc = str(description.text)
                if lang == "de":
                    dedesc = desc
                elif lang == "it":
                    itdesc = desc
                else:
                    endesc = desc

        if config.osd.language.value == "de_DE":
            desc2 = dedesc
        elif config.osd.language.value == "it_IT":
            desc2 = itdesc
        else:
            desc2 = endesc
        if desc2 == ' ':
            desc2 = endesc
        return pname, version, prov, desc2

    def listplugs(self):
        print("In listplugs 1")
        self.urls = []
        self.names = []
        self.shortnms = []
        path = THISPLUG + "/" + ADDONCAT
        self.names.append("Exit")
        self.shortnms.append("Exit")
        self.urls.append("0")
        i = 1

        for name in os.listdir(path):
            if "E2" in name:
                self.names.append(name)
                self.shortnms.append(name)
                self.urls.append(i)
                i += 1

            if "__init__" in name:
                continue
            if "plugin." not in name:
                continue
            elif "plugin.video.select" in name:
                continue
            else:
                try:
                    pic = THISPLUG + "/" + ADDONCAT + "/" + name + "/icon.png"
                    im = Image.open(pic)
                    if Utils.isFHD():
                        x = 200
                        y = 200
                    else:
                        x = 120
                        y = 120
                    im = im.resize((x, y), Image.ANTIALIAS)
                    im.save(pic)
                except:
                    pass

                print("config.ParentalControl.configured.value =", config.ParentalControl.configured.value)
                print("In listplugs 2")
                self.names.append(name)
                # name1 = name[13:]
                print("In listplugs name =", name)
                if "plugin.video." in name:
                    name1 = name.replace("plugin.video.", "")
                elif "plugin.audio." in name:
                    name1 = name.replace("plugin.audio.", "")
                elif "plugin.image." in name:
                    name1 = name.replace("plugin.image.", "")
                elif "plugin.picture." in name:
                    name1 = name.replace("plugin.picture.", "")
                print("In listplugs name1 =", name1)
                self.shortnms.append(name1)
                self.urls.append(i)
                i += 1
        self.num = i
        print("Here in listplugs going in Utils.showlist self.shortnms =", self.shortnms)
        Utils.showlist(self.shortnms, self["menu"])

    def checkfixsh(self):
        print("self.name =", self.name)
        if self.name not in self.fixlist:
            return
        else:
            plug = self.name + "-fix.1.0.0.zip"
            xurl = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/" + plug
            print("xurl =", xurl)
            xdest = "/tmp/plug.zip"
            cmd1 = "wget -O " + xdest + " " + xurl
            fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/scripts"
            cmd2 = "unzip -o -q '/tmp/plug.zip' -d " + fdest
            cmd = cmd1 + " && " + cmd2
            print("In checkfixsh cmd =", cmd)
            # title = (_("Installing addon fix"))
            os.system(cmd)
            return

    def checkUpd(self):
        ltxt = "In checkUpd self.name = " + self.name
        print(ltxt)
        tfile = THISPLUG + "/" + ADDONCAT + "/" + self.name + "/addon.xml"
        f = open(tfile, "r")
        txt = f.read()
        print("In checkUpd txt = ", txt)
        n1 = txt.find('<addon', 0)
        n11 = txt.find('id', n1)
        n2 = txt.find("version", n11)
        n3 = txt.find('"', n2)
        n31 = txt.find("'", n2)
        if n31 > -1:
            if n31 < n3:
                n4 = txt.find("'", (n31+2))
                version = txt[(n31+1):n4]
            else:
                n4 = txt.find('"', (n3+2))
                version = txt[(n3+1):n4]
        else:
            n4 = txt.find('"', (n3+2))
            version = txt[(n3+1):n4]
        print("In checkUpd version = ", version)
        f.close()
        try:
            file1 = THISPLUG + "/adlist.txt"
            f1 = open(file1, "r+")
            fpage = f1.read()
        except:
            fpage = " "

        lines = fpage.splitlines()
        nlist = 0
        for line in lines:

            if line.startswith("#####"):
                continue
            elif "###" not in line:
                continue
            elif self.name not in line:
                continue
            else:
                nlist = 1  # addon in adlist.txt
                print("In checkUpd line B=", line)
                print("In checkUpd self.name c=", self.name)
                items = line.split("###")
                # n = len(items)
                print("In checkUpd items =", items)
                # name = items[0]
                # url1 = items[1]
                if items[2] != '':
                    # url2 = items[2]
                    self.checkLine(line, version)
                    break
                else:
                    print("In checkUpd going in self.okClicked2 ")
                    self.okClicked2()
        if nlist == 0:  # user added addon
            self.okClicked2()

    def checkLine(self, line, version):
        print("In checkLine line =", line)
        items = line.split("###")
        print("In checkLine items =", items)
        name = items[0]
        url1 = items[1]
        url2 = items[2]
        if url2 == '':
            self.okClicked2()
        else:
            url2 = items[2]
            n2 = url1.find(".zip", 0)
            n3 = url1.rfind(name, 0, n2)
            n4 = n3 + len(name) + 1
            url0 = url1[:n4]
            print("url0 =", url0)
            xurl = url2
            xdest = "/tmp/down.txt"
            self.line = line
            self.version = version
            self.name = name
            self.url1 = url1
            self.url2 = url2
            self.url0 = url0
            downloadPage(xurl, xdest).addCallback(self.getdown).addErrback(self.showError)

    def showError(self, error):
        print("ERROR :", error)

    def getdown(self, fplug):
        fpage = open("/tmp/down.txt", "r").read()
        if self.url2.endswith(".xml"):
            rx = 'addo.*?id="' + self.name + '".*?version="(.*?)"'
        else:
            rx = self.name + '-(.*?).zip'
        match = re.compile(rx, re.DOTALL).findall(fpage)
        print("match =", match)
        if len(match) == 0:
            rx = self.name + '_(.*?).zip'
            match = re.compile(rx, re.DOTALL).findall(fpage)
            print("match 2=", match)
        try:
            latest = findmax(match)
        except:
            latest = max(match)
        latest = latest.replace("%7E", "~")
        print("latest =", latest)
        print("self.version =", self.version)
        if latest != self.version:
            self.xurl = self.url0 + latest + ".zip"
            print("self.xurl =", self.xurl)
            txt = _("New version ") + latest + _(" is available. Update Now ?")
            print(txt)
            self.session.openWithCallback(self.do_update, MessageBox, txt, type=0)
        else:
            self.okClicked2()

    def do_update(self, answer):
        if answer is None:
            self.okClicked2()
        else:
            if answer is False:
                self.okClicked2()
            else:
                xurl = self.xurl
                print("self.xurl=", self.xurl)
                xdest = "/tmp/plug.zip"
                downloadPage(xurl, xdest).addCallback(self.install).addErrback(self.showError)

    def install(self, fplug):
        fdest = THISPLUG + "/" + ADDONCAT + ""
        addon = THISPLUG + "/" + ADDONCAT + "/" + self.name
        cmd1 = "rm -rf '" + addon + "'"
        cmd2 = " unzip -o -q '/tmp/plug.zip' -d '" + fdest + "'"
        cmd3 = " cp -f '" + THISPLUG + "/xpath.py' " + addon
        cmd = cmd1 + " && " + cmd2 + " && " + cmd3
        print("cmd =", cmd)
        title = _("Installing ") + self.name
        print("self.session 1=", self.session)
        self.session.openWithCallback(self.checkName, Console, _(title), [cmd])

    def checkName(self):
        path = THISPLUG + "/" + ADDONCAT
        for name in os.listdir(path):
            print("name =", name)
            if "plugin" not in name:
                if "__init" in name:
                    continue
                elif "E2" in name:
                    self.close()
                else:
                    newname = "plugin.video." + name
                    cmd = "mv " + path + "/" + name + " " + path + "/" + newname + " &"
                    os.system(cmd)
            if "-master" in name:
                newname = name.replace("-master", "")
                cmd = "mv " + path + "/" + name + " " + path + "/" + newname + " &"
                os.system(cmd)
            if ("pelisalacarta" in name) or ("tvalacarta" in name):
                cmd = "rm '" + path + "/" + name + "/fixed2'"
                os.system(cmd)

        self.close()
        # self.checkfix() Not necessary as okclick2 calls it.

    def checkfix(self):
        url = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/list.txt"
        self.fixlist = Utils.getUrl(url)
        print("In checkfix self.fixlist =", self.fixlist)
        print("In checkfix self.name =", self.name)
        if self.name in self.fixlist:
            plug = self.name + "-fix.1.0.0.zip"
            xurl = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/" + plug
            print("xurl =", xurl)
            ucode = "UTF-8"
            xurl = xurl.encode(ucode)
            xdest = "/tmp/plug.zip"
            downloadPage(xurl, xdest).addCallback(self.installB).addErrback(self.showError)
        else:
            print("No fix to install")
            self.stream()

    def installB(self, fplug):
        fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/" + ADDONCAT
        cmd = "unzip -o -q '/tmp/plug.zip' -d " + fdest
        print("In installB cmd =", cmd)
        # title = (_("Installing addon fix"))
        os.system(cmd)
        self.stream()

# #nnnnn
    def checkImports(self):
        self["info"].setText("Please wait...")
        """
        xmfile = THISPLUG+"/" + ADDONCAT + "/"+self.id+"/resources/settings.xml"
        tmpfile = THISPLUG+"/ofile.xml"
        if os.path.exists(xmfile):
               f = open(xmfile, "r")
               f1 = open(tmpfile, "w")
               ftxt = f.read()
               ftxt = ftxt.decode("ISO-8859-1")
               f1.write(ftxt)
               f.close()
               f1.close()
               print  "Here in checkImports copying tmpfile to ", xmfile
               cmd = "cp -f " + tmpfile + " " + xmfile + " && rm " + tmpfile
               print  "Here in checkImports cmd ", cmd
               os.system(cmd)
        """
# ##########
        print("In checkImports 1")
        self.shlist = " "
        self.plugins = " "
        scripts = THISPLUG + "/scripts"
        for name in os.listdir(scripts):
            self.shlist = self.shlist + name + " "
        plugins = THISPLUG + "/" + ADDONCAT
        for name in os.listdir(plugins):
            self.plugins = self.plugins + name + " "
        print("In checkImports 2")
        import xbmcaddon
        try:
            sys.argv[0] = THISPLUG + "/" + ADDONCAT + "/" + self.id + "/default.py"
        except:
            import sys
            sys.argv = []
            sys.argv.append(THISPLUG + "/" + ADDONCAT + "/" + self.id + "/default.py")
        update_xbmc_text(self.id)
        print("In checkImports 3")
        addon = xbmcaddon.Addon(self.id)
        path = addon.getAddonInfo("path")
        print("In checkImports self.id =", self.id)
        print("In checkImports path =", path)
        xfile = path + "/addon.xml"
        tree = xml.etree.cElementTree.parse(xfile)
        root = tree.getroot()
        self.missed = ""
        i = 0
        try:
            for x in root.iter('import'):
                addon = x.get('addon') + " "  # to get xbmcswift not xbmcswift2
                if "xbmc.python" in addon:
                    continue
                if "xbmc.addon" in addon:
                    continue
                if "repository." in addon:
                    continue
                if "artwork" in addon:
                    continue
                if addon in self.shlist or addon in self.plugins:
                    continue
                self.missed = self.missed + " " + addon
                i = 1
        except:
            for x in root.getiterator('import'):
                addon = x.get('addon') + " "
                if "xbmc.python" in addon:
                    continue
                if "xbmc.addon" in addon:
                    continue
                if "repository." in addon:
                    continue
                if "artwork" in addon:
                    continue
                if addon in self.shlist or addon in self.plugins:
                    continue
                self.missed = self.missed + " " + addon
                i = 1
        if i == 0:
            arg = "'" + THISPLUG.strip() + "/" + ADDONCAT + "/" + self.name.strip() + "/default.py' '1' ''"
            self.arg = arg
            # ###pcd1234
            self.stream()
            # self.checkfix()
        else:
            txt = "Missing (Install from KodiLite list):-\n" + self.missed
            print("In checkimports not in matrix", txt)
            self["info"].setText(txt)

    def okClicked(self):
        if self.keylock:
            return
        print("In StartPlugin_mainmenu okClicked")
        idx = self["menu"].getSelectionIndex()
        if DEBUG == 1:
            print("idx =", idx)
        if idx == 0:
            self.exit()
        # elif "Get more" in self.names[idx]:
        # self.addon()
        else:
            self.name = self.names[idx]
            self.nameplug = self.name
            print("In StartPlugin_mainmenu okClicked B self.name =", self.name)
            print("In StartPlugin_mainmenu okClicked B ADDONCAT =", ADDONCAT)
            if ADDONCAT == "plugins":
                if self.name.endswith("E2"):
                    self.runE2plug(self.name)
                else:
                    # self.checkUpd()
                    self.okClicked2()
            else:
                self.okClicked2()
        self.showhide()

    def runE2plug(self, name):
        try:
            from Plugins.Extensions.KodiLite.Execlist import Execlist
            Execlist(self.session, name)
        except:
            from .Execlist import Execlist
            Execlist(self.session, name)

    def okClicked2(self):
        global SELECT
        SELECT = []
        SELECT.append(self.name)
        SELECT.append("1")
        SELECT[1] = self.name
        print("In StartPlugin_mainmenu SELECT[0] =", SELECT[1])
        self.id = self.nameplug
        self.name = self.nameplug
        f = open("/tmp/kodiplug.txt", "w")
        tplug = self.id + "\n"
        f.write(tplug)
        f.close()
        if ADDONCAT == "plugins":
            self.defaultpy()
            # self.changepy()
            self.checkImports()
        else:
            arg = "'" + THISPLUG.strip() + "/plugins/" + self.name.strip() + "/default.py' '1' ''"
            self.arg = arg
            self.stream()
        self.showhide()

    def defaultpy(self):
        global THISADDON
        THISADDON = THISPLUG + "/plugins/" + self.id
        print("In defaultpy THISADDON =", THISADDON)
        dpath = THISADDON + "/default.py"
        if not os.path.exists(dpath):
            fmod = self.findmod()
            cmd = "mv " + THISADDON + "/" + fmod + " " + THISADDON + "/default.py"
            print("cmd =", cmd)
            os.system(cmd)
        tfile = THISPLUG + "/added.txt"
        f = open(tfile, 'r')
        addtxt = f.read()
        f.close()
        fpath1 = THISPLUG + "/plugins/" + self.id
        fpath2 = fpath1 + "/fixed2"
        fpathf = fpath1 + "/default.py"
        f = open(fpathf, 'r')
        f.close()
        if fileExists(fpath2):
            addtxt2 = "\nf = file('/tmp/e.log', 'a')\nsys.stdout = f\n"
            fpath = fpath1 + "/default.py"
            f = open(fpath, 'r')
            deftxt = f.read()
            f.close()
            if addtxt2 in deftxt:
                f1 = open('/tmp/default.txt', 'w')
                icount = 0
                deftxt3 = deftxt.replace(addtxt2, "\n")
                f1.write(deftxt3)
                f.close()
                f1.close()
                cmd = "rm " + fpath + " && cp /tmp/default.txt " + fpath
                os.system(cmd)
            else:
                pass

        else:
            fpath = fpath1 + "/default.py"
            f = open(fpath, 'r')
            deftxt = f.read()
            print("In defaultpy deftxt =", deftxt)
            x = ord(deftxt[0])
            x1 = ord(deftxt[1])
            x2 = ord(deftxt[2])
            x3 = ord(deftxt[3])
            xm = max([x, x1, x2, x3])
            print("In defaultpy nonasci xm =",  xm)
            if xm > 127:
                n1 = deftxt.find("#", 0)
                if n1 == -1:
                    n1 = 1000
                n2 = deftxt.find("import", 0)
                if n2 == -1:
                    n2 = 1000
                n3 = deftxt.find("from", 0)
                if n3 == -1:
                    n3 = 1000
                nmin = min(n1, n2, n3)
                print("nmin =", nmin)
                deftxt = deftxt[nmin:]

            print("In defaultpy deftxt B=", deftxt)
            data = []
            data = deftxt.splitlines()
            f.close()
            if addtxt not in deftxt:
                cmdrm = "rm " + fpath1 + "/xpath.py"
                os.system(cmdrm)
                f1 = open('/tmp/default.txt', 'w')
                icount = 0
                for line in data:
                    # line = line.decode("ISO-8859-1")
                    line = line + "\n"
                    if not (line.startswith("#")):
                        if icount == 0:
                            f1.write(addtxt)
                            icount = 1
                        else:
                            pass
                    f1.write(line)
                f.close()
                f1.close()
                cmd = "rm " + fpath + " && cp /tmp/default.txt " + fpath
                os.system(cmd)
            cmd1 = "touch " + fpath2
            os.system(cmd1)

    def findmod(self):
        xfile = os.path.join(THISADDON, 'addon.xml')
        print("In plugin-py findmod xfile =", xfile)
        f = open(xfile, "r")
        ftext = f.read()
        n1 = ftext.find("<extension", 0)
        n2 = ftext.find("library", n1)
        n3 = ftext.find('"', n2)
        n4 = ftext.find('"', (n3+1))
        fmod = ftext[(n3+1):n4]
        print("Newmod =", fmod)
        return fmod

    def stream(self):
        self.picfold = cfg.cachefold.value + "/xbmc/pic"
        self.tmpfold = cfg.cachefold.value + "/xbmc/tmp"
        cmd = "rm " + self.tmpfold + "/*"
        os.system(cmd)
        os.system("rm /tmp/data.txt")
        os.system("rm /tmp/data.txt")
        os.system("rm /tmp/vidinfo.txt")
        os.system("rm /tmp/type.txt")
        if DEBUG == 1:
            print("DEBUG =", DEBUG)
        fdef = 'default'
        arg1 = THISPLUG + "/" + ADDONCAT + "/" + self.name + "/default.py"
        arg2 = "1"
        arg3 = ""
        arg4 = cfg.cachefold.value
        sys.argv = [arg1, arg2, arg3, arg4]
        d = THISPLUG + "/" + ADDONCAT + "/" + self.name
        global THISADDON
        THISADDON = d
        self.plugin_id = self.name
        sys.argv = [arg1, arg2, arg3, arg4]
        d = THISADDON
        # dellog()
        # ########
        xpath_file = THISPLUG + "/" + ADDONCAT + "/" + self.name + "/xpath.py"
        # fixed2_file = THISPLUG + "/" + ADDONCAT + "/" + self.name + "/fixed2"
        default_file = THISPLUG + "/" + ADDONCAT + "/" + self.name + "/default.py"
        # if not os.path.exists(xpath_file):
        os.system("cp -f " + THISPLUG + "/lib/xpath.py " + xpath_file)
        cmd = 'python ' + default_file + ' 1 ' + "'"+arg3 + "'"
        print(cmd)

        if os.path.exists("/tmp/data.txt"):
            os.remove("/tmp/data.txt")
        self.dtext = " "
        self.lastcmd = cmd
        global LAST
        LAST = self.lastcmd
        # print("cmd = ", cmd)
        self.p = os.popen(cmd)
        self.timecount = 0
        self.updateTimer.start(self.timeint)

    def updateStatus(self):
        ncount = cfg.wait.value
        # nct = int(ncount)/4
        self.timecount += 1
        print("In StartPlugin_mainmenu updateStatus self.timecount =", self.timecount)
        self.dtext = self.p.read()
        print("In StartPlugin_mainmenu updateStatus self.dtext =", self.dtext)
        global dtext1
        if len(self.dtext) > 0:
            dtext1 = dtext1 + self.dtext
        if "data B" in self.dtext:
            self.updateTimer.stop()
            self.action(" ")
        print("In StartPlugin_mainmenu self.timecount =", self.timecount)
        if self.timecount > self.nct:
            self.updateTimer.stop()
            f1 = open("/tmp/e.log", "a")
            # f1.write(dtext1)
            f1.close()
        self.action(" ")

    def action(self, retval):
        self.keylock = False
        self.names2 = []
        self.urls2 = []
        self.pics2 = []
        self.names2.append("Exit")
        self.urls2.append(" ")
        self.pics2.append(" ")
        self.names2.append("Setup")
        self.urls2.append(" ")
        self.pics2.append(" ")
        self.names2.append("Favorites")
        self.urls2.append(" ")
        self.pics2.append(" ")
        self.tmppics2 = []
        self.lines = []
        self.vidinfo = []
        afile = open("/tmp/test.txt", "w")
        afile.write("\nin action=")
        datain = " "
        parameters = []
        self.data = []
        print("StartPlugin_mainmenu self.dtext =", self.dtext)
        data = self.dtext.splitlines()
        for line in data:
            print("StartPlugin_mainmenu line =", line)
            if "data B" not in line:
                continue
            else:
                i1 = line.find("&", 0)
                line1 = line[i1:]
                self.data.append(line1)
        print("StartPlugin_mainmenu self.data =", self.data)
        if len(self.data) == 0:
            cmd = LAST + " > /tmp/error.log 2>&1 &"
            os.system(cmd)
            self.error = (_("Error! Submit logs /tmp/e.log and /tmp/error.log."))
            self["info"].setText(self.error)
            return
        inum = len(self.data)
        print("StartPlugin_mainmenu inum =", inum)
        n1 = 0
        if n1 == 0:
            i = 0
            while i < inum:
                name = " "
                url = " "
                line = self.data[i]
                print("StartPlugin_mainmenu line =", line)
                params = parameters_string_to_dict(line)
                self.lines.append(line)
                try:
                    name = params.get("name")
                    name = name.replace("AxNxD", "&")
                    name = name.replace("ExQ", "=")
                except:
                    pass
                try:
                    url = params.get("url")
                    url = url.replace("AxNxD", "&")
                    url = url.replace("ExQ", "=")
                except:
                    pass
                try:
                    pic = params.get("thumbnailImage")
                    if (pic == "DefaultFolder.png") or (pic is None):
                        pic = defpic
                    print("StartPlugin_mainmenu pic 1 =", pic)
                except:
                    pic = defpic
                print("StartPlugin_mainmenu pic 2 =", pic)
                self.name = name
                self.names2.append(name)
                self.urls2.append(url)
                self.pics2.append(pic)
                i += 1
            if (len(self.names2) == 2) and (self.urls2[1] is None) and (THISPLUG not in self.names2[1]):
                if ("rtmp" in self.names2[1]):
                    if "live" in name:
                        name = self.name
                        desc = " "
                        url = self.names2[1]
                        # self.session.open(Showrtmp2, name, url, desc)
                        self.progressCallBack("Finished")
                        self.session.open(Playoptions, name, url, desc)
                        self.close()

                    else:
                        name = self.name
                        desc = " "
                        url = self.names[1]
                        # self.session.open(Showrtmp, name, url, desc)
                        self.progressCallBack("Finished")
                        self.session.open(Playoptions, name, url, desc)
                        self.close()

                else:
                    name = self.name
                    desc = " "
                    url = self.names2[1]
                    self.progressCallBack("Finished")
                    self.session.open(Playoptions, name, url, desc)
                    self.close()
            elif (len(self.names2) == 2) and (self.urls2[1] is not None) and (THISPLUG not in self.urls2[1]):
                name = self.name
                desc = " "
                url = self.urls2[1]
                self.progressCallBack("Finished")
                self.session.open(Playoptions, name, url, desc)  # Playoptions defin
                self.close()
            else:
                if DEBUG == 1:
                    print("StartPlugin_mainmenu self.names2 =", self.names2)
                    print("StartPlugin_mainmenu self.urls2 =", self.urls2)
                    print("StartPlugin_mainmenu self.pics2 =", self.pics2)
                self.tmppics2 = self.pics2
                if self.cancel is True:
                    return

                if ("plugin.image" in self.id) or ("plugin.picture" in self.id):
                    print("StartPlugin_mainmenu going in XbmcPluginScreenP")
                    from picture import XbmcPluginScreenP
                    self.session.open(XbmcPluginScreenP, self.id, self.names2, self.urls2, self.tmppics2, 1, SELECT)
                else:
                    print("StartPlugin_mainmenu going in XbmcPluginScreen")
                    picindic = 0
                    self.session.open(XbmcPluginScreen, self.id, self.names2, self.urls2, self.tmppics2, 1, picindic)


class DelAdd(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("Please select addon type"))
        self["info"].setText(self.info)
        # self["bild"] = startspinner()
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Delete.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DeleteL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        methods = []
        methods.append(_("Delete plugin"))
        methods.append(_("Delete script"))
        methods.append(_("Delete repository"))
        Utils.showlist(methods, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        if sel is None:
            self.close()
        elif sel == 0:
            self.session.open(DelAdd1, 'plugins')
        elif sel == 1:
            self.session.open(DelAdd1, 'scripts')
        elif sel == 2:
            self.session.open(DelAdd1, 'repos')

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class DelAdd1(Screen):

    def __init__(self, session, type):
        Screen.__init__(self, session)
        self.skinName = "XbmcPluginScreenF"
        self.session = session
        global _session
        _session = session
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = " "
        self["info"].setText(self.info)
        # self["bild"] = startspinner()
        self.type = type
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {
                                            "ok": self.okClicked,
                                            "back": self.close,
                                            "red": self.close,
                                            "green": self.okClicked,
                                          }, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.addlist = []
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Delete.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DeleteL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        type = str(self.type)
        adds = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/%s" % type
        for name in os.listdir(adds):
            if "plugin.video.select" in name:
                continue
            elif "script.module.extras" in name:
                continue
            elif "script.module.main" in name:
                continue
            elif "script.module" in name:
                continue
            elif "__init" in name:
                continue
            self.addlist.append(name)
        Utils.showlist(self.addlist, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        plug = self.addlist[sel]
        type = str(self.type)
        cmd = "rm -rf '/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/%s/%s'" % (type, plug)  # + "'" % type
        title = _("Removing %s" % (plug))
        self.session.open(Console, _(title), [cmd])
        self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        self["menu"].number(number)


class Getadds(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("Please select install method"))
        self["info"].setText(self.info)
        # self["bild"] = startspinner()
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        methods = []
        methods.append(_("Install from zip"))
        methods.append(_("Install from KodiLite list"))
        methods.append(_("Install from Kodi repositories"))
        """
        methods.append(_("Install from User list (/KodiLite/useradlist.txt"))
        methods.append(_("Install from Kodi official repositories"))
        methods.append(_("Install from User repositories"))
        methods.append(_("Install from Fusion"))
        """
        Utils.showlist(methods, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        if sel is None:
            self.close()
        elif sel == 0:
            self.session.open(Getadds1)
        elif sel == 1:
            self.session.open(Getaddons)
        elif sel == 2:
            # self.session.open(Getaddons2)
            self.session.open(Getadds3)
        # elif sel == 3:
            # # self.session.open(Getadds3)
            # pass
        # elif sel == 4:
            # self.session.open(Getadds4)
        # else:
            # self.session.open(Fusion)

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Getadds1(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("Please put zip files in folders /tmp, /media/hdd or /media/usb."))
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        methods = []
        self.urls = []
        methods.append("/tmp")
        self.urls.append("/tmp")
        methods.append("/media/hdd")
        self.urls.append("/media/hdd")
        methods.append("/media/usb")
        self.urls.append("/media/usb")
        Utils.showlist(methods, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        url = self.urls[sel]
        if sel is None:
            self.close()
        else:
            self.session.open(Getadds7, url)

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Getadds7(Screen):

    def __init__(self, session, url):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("Please select"))
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        print("In Getadds7 url =", url)
        self.url = url
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        self.names = []
        path = self.url
        print("In Getadds7 path =", path)
        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(".zip"):
                    self.names.append(name)
                else:
                    continue
        print("In Getadds7 self.names =", self.names)
        Utils.showlist(self.names, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        self.name = self.names[sel]
        if sel is None:
            self.close()
        else:
            xurl = self.url + "/" + self.name
            print("xurl=", xurl)
            if self.name.startswith("repo"):
                fdest = THISPLUG + "/repos"
            elif self.name.startswith("plugin."):
                fdest = THISPLUG + "/plugins"
            elif self.name.startswith("script."):
                fdest = THISPLUG + "/scripts"

            adn = fdest + "/" + self.name
            if os.path.exists(adn):
                os.remove(adn)
            cmd = "unzip -o -q '" + xurl + "' -d '" + fdest + "'"
            print("cmd =", cmd)
            title = _("Installing ...")
            self.session.open(Console, _(title), [cmd])
            self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Getaddons(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("Any errors - report in www.linuxsat-support.com KodiLite thread"))
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        print("In Getaddons openTest")
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        self.data = []
        cats = []
        try:
            import base64
            thost = 'aHR0cDovL3BhdGJ1d2ViLmNvbQ=='
            ServerS1 = base64.b64decode(thost)
            print("In install ServerS1 =", ServerS1)
            try:
                fpage = Utils.getUrl(ServerS1.decode() + '/Newkodilite/adlist3.txt')
            except:
                fpage = Utils.getUrl(ServerS1 + '/Newkodilite/adlist3.txt')
            print("In install fpage =", fpage)
            icount = 0
            lines = fpage.split("\n")
            for line in lines:
                print("In Getaddons openTest line =", line)
                if line.startswith("#####"):
                    cat = line.replace("#####", "")
                    cat = cat.replace("####", "")
                    if "fix" in cat:
                        continue
                    cats.append(cat)
                    line = line
                    self.data.append(line)
        except:
            pass
        Utils.showlist(cats, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        if sel is None:
            self.close()
        else:
            name = self.data[sel]
            if "Adult" in name:
                self.catname = name
                self.allow()
            else:
                self.session.open(GetaddonsA2, name)
                self.close()

    def allow(self):
        if config.ParentalControl.configured.value:
            # ####print  "Here Ad 1"
            # from Screens.InputBox import InputBox, PinInput
            self.session.openWithCallback(self.pinEntered, PinInput, pinList=[config.ParentalControl.setuppin.value], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the parental control pin code"), windowtitle=_("Enter pin code"))
        else:
            # ####print  "Here Ad 2"
            self.pinEntered(True)
        # return

    def pinEntered(self, result):
        # ####print  "Here Ad 3 result =", result
        if result:
            self.session.open(GetaddonsA2, self.catname)
            self.close()
        else:
            self.session.openWithCallback(self.close, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)
            self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class GetaddonsA2(Screen):

    def __init__(self, session, cat):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.cat = cat
        self.info = (_("     Please select addon to install"))
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.names = []
        self.urls = []
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        print("In GetaddonsA2 openTest")
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        self.data = []
        xn = 0
        if xn == 0:
            import base64
            thost = 'aHR0cDovL3BhdGJ1d2ViLmNvbQ=='
            ServerS1 = base64.b64decode(thost)
            try:
                url = ServerS1.decode() + '/Newkodilite/adlist3.txt'
                fpage = Utils.getUrl(url)
            except:
                url = ServerS1 + '/Newkodilite/adlist3.txt'
                fpage = Utils.getUrl(url)
            print("In install fpage =", fpage)
        print("In install fpage 2=", fpage)
        self.fpage = fpage
        print("In GetaddonsA2 self.cat =", self.cat)
        # self.cat = self.cat.encode("UTF-8")
        n1 = fpage.find(self.cat)
        n2 = fpage.find("#####", (n1+10))
        fpage2 = fpage[n1:n2]
        lines = fpage2.splitlines()
        print("In install lines =", lines)
        nms = []
        for line in lines:
            print("In install line =", line)
            if line.startswith("#####"):
                continue
            elif "---" in line:
                nms.append(line)
                self.names.append(" ")
                self.urls.append(" ")
            elif "###" not in line:
                nms.append(line)
                self.names.append(" ")
                self.urls.append(" ")
            else:
                print("In GetaddonsA2 line =", line)
                items = line.split("###")
                # print  "In GetaddonsA2 items =", items
                nm = items[0]
                nms.append(nm)
                self.names.append(items[0])
                self.urls.append(line)
        Utils.showlist(nms, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        if sel is None:
            self.close()
        else:
            line = self.urls[sel]
            self.name = self.names[sel]
            self.checkLine(line)

    def checkLine(self, line):
        print("In GetaddonsA2 checkLine line =", line)
        items = line.split("###")
        print("In GetaddonsA2 checkLine items =", items)
        name = items[0]
        url1 = items[1]
        url2 = items[2]
        if url2 == '':
            xurl = url1
            xdest = "/tmp/plug.zip"
            # downloadPage(xurl, xdest).addCallback(self.install).addErrback(self.showError)
            f = Utils.getUrlresp(xurl)
            print("f =", f)
            fpage = f.read()
            print("fpage 2 =", fpage)
            f1 = open(xdest, "wb")
            f1.write(fpage)
            f1.close()
            self.install()
        elif not items[1].endswith(".zip"):  # datadirectory zip false
            self.session.open(GetaddonsA3, line)
            self.close()
        else:
            url2 = items[2]
            n2 = url1.find(".zip", 0)
            n3 = url1.rfind("-", 0, n2)
            if n3 < 0:
                n3 = url1.rfind("_", 0, n2)
            n4 = n3 + 1
            url0 = url1[:n4]
            print("url0 =", url0)
            # fpage = urlopen(url2).read()
            xurl = url2
            xdest = "/tmp/down.txt"
            self.line = line
            self.name = name
            self.url1 = url1
            self.url2 = url2
            self.url0 = url0
            # fpage = urlopen(url2).read()
            xurl = xurl
            print("xurl =", xurl)
            # downloadPage(xurl, xdest).addCallback(self.getdown).addErrback(self.showError)
            f = Utils.getUrlresp(xurl)
            print("f =", f)
            fpage = f.read().decode()
            print("fpage 2 =", fpage)
            f1 = open(xdest, "w")
            f1.write(fpage)
            f1.close()
            self.getdown()

    def showError(self, error):
        print("ERROR :", error)

    def getdown(self):
        fpage = open("/tmp/down.txt", "r").read()
        print("GetaddonsA2 In checkLine fpage =", fpage)
        if self.url2.endswith(".xml"):
            # rx = self.name + '.*?version="(.*?)"'
            rx = 'addo.*?id="' + self.name + '".*?version="(.*?)"'
        else:
            rx = self.name + '-(.*?).zip'
        print("rx =", rx)
        match = re.compile(rx, re.DOTALL).findall(fpage)
        print("match =", match)
        if len(match) == 0:
            rx = self.name + '_(.*?).zip'
            match = re.compile(rx, re.DOTALL).findall(fpage)
            print("match 2=", match)
        elif len(match) == 1:
            latest = match[0]
        else:
            latest = findmax(match)
        if latest is not None:
            xurl = self.url0 + latest + ".zip"
            print("xurl =", xurl)
            xdest = "/tmp/plug.zip"
            f = Utils.getUrlresp(xurl)
            print("f =", f)
            fpage = f.read()
            print("fpage 2 =", fpage)
            f1 = open(xdest, "wb")
            f1.write(fpage)
            f1.close()
            fplug = ""
            self.install()

        else:
            return

    def install(self):
        if "script." in self.name:
            fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/scripts"
        elif "repository" in self.name:
            fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/repos"
        else:
            fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins"
        addon = THISPLUG + "/plugins/" + self.name
        cmd1 = "rm -rf '" + addon + "'"
        cmd2 = "unzip -o -q '/tmp/plug.zip' -d " + fdest
        cmd = []
        cmd.append(cmd1)
        cmd.append(cmd2)
        print("cmd =", cmd)
        txt = "Installing addon " + self.name
        title = txt
        self.session.openWithCallback(self.checkName, Console, _(title), cmd)

    def checkName(self):
        path = THISPLUG + "/plugins"
        for name in os.listdir(path):
            print("name =", name)
            if "plugin" not in name:
                if "__init" in name:
                    continue
                elif "E2" in name:
                    self.close()
                else:
                    newname = "plugin.video." + name
                    cmd = "mv " + path + "/" + name + " " + path + "/" + newname + " &"
                    os.system(cmd)
            if "-master" in name:
                newname = name.replace("-master", "")
                cmd = "mv " + path + "/" + name + " " + path + "/" + newname + " &"
                os.system(cmd)
            if ("pelisalacarta" in name) or ("tvalacarta" in name):
                cmd = "rm '" + path + "/" + name + "/fixed2'"
                os.system(cmd)

        self.close()
        # self.checkfix()

    def checkfix(self):
        url = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/list.txt"
        self.fixlist = Utils.getUrl(url)
        self.fixlist = self.fixlist.decode()
        print("self.fixlist =", self.fixlist)
        print("self.name =", self.name)
        if self.name in self.fixlist:
            plug = self.name + "-fix.1.0.0.zip"
            xurl = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/" + plug
            print("xurl =", xurl)
            xdest = "/tmp/plug.zip"
            downloadPage(xurl, xdest).addCallback(self.installB).addErrback(self.showError)
        else:
            print("No fix to install")
            self.close()

    def showError(self, error):
        print("ERROR :", error)

    def installB(self, fplug):
        fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins"
        cmd = "unzip -o -q '/tmp/plug.zip' -d " + fdest
        print("In installB cmd =", cmd)
        os.system(cmd)
        self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Getadds3(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("WARNING ! Many repository addons may not work. This may be because they are not updated. \nIf you want this addon - please post your request."))
        self["info"].setText(self.info)
        # self["bild"] = startspinner()
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        methods = []
        self.urls = []
        methods.append("Matrix")
        self.urls.append("http://mirrors.kodi.tv/addons/matrix/")
        # methods.append("Matrix Script")
        # self.urls.append("http://mirrors.kodi.tv/addons/matrix/")
        Utils.showlist(methods, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        url = self.urls[sel]
        if sel is None:
            self.close()
        else:
            self.session.open(Getadds5, url)

    def keyLeft(self):
        self["text"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class GetaddonsA3(Screen):

    def __init__(self, session, line):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self.line = line
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (" ")
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onShown.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        items = self.line.split("###")
        print("In openTest items =", items)
        name = items[0]
        url1 = items[1]
        # url2 = items[2]
        fdest = THISPLUG + "/plugins/" + name
        cmd = "mkdir -p " + fdest
        os.system(cmd)
        self.getfolder(name, url1, fdest)

    def getfolder(self, name, url, xdest):
        fpage = Utils.getUrl(url)
        print("In Repo2 getfolder name, url C=", name, url)
        print("In Repo2 getfolder xdest=", xdest)
        print("In Repo2 getfolder fpage =", fpage)
        regexcat = '<li><a href="(.*?)">.*?</a><'
        match = re.compile(regexcat, re.DOTALL).findall(fpage)
        for url1 in match:
            if "../" in url1:
                continue
            if url1.endswith("/"):
                url2 = url + url1
                xdest4 = xdest + "/" + url1
                print("In Repo2 getfolder name, url D=", name, url)
                print("In Repo2 getfolder xdest4 D=", xdest4)
                if not os.path.exists(xdest4):
                    cmd = "mkdir " + xdest4
                    os.system(cmd)
                self.foldback(name, url2, xdest4)
            else:
                url2 = url + url1
                print("In Repo2 getfolder url2 =", url2)
                fpage2 = Utils.getUrl(url2)
                xdest3 = xdest + "/" + url1
                f3 = open(xdest3, "w")
                f3.write(fpage2)
                # f2.close()
                f3.close()
                self.close()
        return

    def foldback(self, name, url, xdest):
        self.getfolder(name, url, xdest)

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        if sel is None:
            self.close()
        else:
            name = self.data[sel]
            if "Adult" in name:
                self.catname = name
                self.allow()
            else:
                self.session.open(GetaddonsA2, name)
                self.close()

    def allow(self):
        if config.ParentalControl.configured.value:
            # ####print  "Here Ad 1"
            # from Screens.InputBox import InputBox, PinInput
            self.session.openWithCallback(self.pinEntered, PinInput, pinList=[config.ParentalControl.setuppin.value], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the parental control pin code"), windowtitle=_("Enter pin code"))
        else:
            # ####print  "Here Ad 2"
            self.pinEntered(True)
        # return

    def pinEntered(self, result):
        # ####print  "Here Ad 3 result =", result
        if result:
            self.session.open(GetaddonsA2, self.catname)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)
            self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Getadds4(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("WARNING ! Many repository addons may not work. This may be because they are not updated. \nIf you want this addon - please post your request.."))
        self["info"].setText(self.info)
        # self["bild"] = startspinner()
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        self.names = []
        self.urls = []
        path = THISPLUG + "/repos"
        print("In Getadds4 path", path)
        for name in os.listdir(path):
            if "repository." not in name:
                continue
            else:
                url = path + "/" + name + "/"
            self.names.append(name)
            self.urls.append(url)
        print("In Getadds4 self.urls =", self.urls)
        Utils.showlist(self.names, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        if sel is None:
            self.close()
        else:
            url = self.urls[sel]
            tfile = url + "addon.xml"
            print("In Getadds4 tfile =", tfile)
            f = open(tfile, "r")
            for line in f.readlines():
                print("In Repo line =", line)
                if "<info" in line:
                    n1 = line.find(">", 0)
                    n2 = line.find('<', n1)
                    infourl = line[(n1+1):n2]
                    print("In Repo infourl A=", infourl)
                if "<datadir" in line:
                    n1 = line.find(">", 0)
                    n2 = line.find('<', n1)
                    plugurl = line[(n1+1):n2]
                    print("In Repo plugurl =", plugurl)
                    if "false" in line:
                        zipcode = "false"
                    else:
                        zipcode = "true"
                    break
                print("In Repo infourl =", infourl)
                print("In Repo plugurl =", plugurl)
                print("In Repo zipcode =", zipcode)
            self.session.open(Repo2, infourl, plugurl, zipcode)

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Getadds5(Screen):

    def __init__(self, session, url):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        print("Addons url =", url)
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = " "
        self.url = url
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        xurl = self.url
        print("In Getadds5 xurl =", xurl)
        # getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)
        html = Utils.getUrl(xurl)
        self.gotPage(html)

    def gotPage(self, html):
        if DEBUG == 1:
            print("In Getadds5 html = ", html)
        self.html = html
        self.names = []
        self.urls = []
        regexcat = '<tr><td><a href="plugin(.*?)" title="(.*?)".*?</td><td>202(.*?)<'
        match = re.compile(regexcat, re.DOTALL).findall(html)
        print("In Addons match =", match)
        for url, name, rev in match:
            if ("plugin.video" not in name) and ("plugin.audio" not in name) and ("plugin.image" not in name) and ("plugin.picture" not in name):
                continue
            rev = rev.replace(" ", "")
            rev = rev.replace("\n", "")
            rev1 = "2" + rev
            name = name + " (" + rev1 + ")"
            url1 = self.url + "plugin" + url
            name = name.replace("/", "")
            name = name.replace("()", "")
            print("In Getadds5 name = ", name)
            print("In Getadds5 url1 = ", url1)
            self.names.append(name)
            self.urls.append(url1)
        Utils.showlist(self.names, self["menu"])

    def getfeedError(self, error=""):
        error = str(error)
        print("Download error =", error)

    def okClicked(self):
        if self.errcount == 1:
            self.close()
        else:
            sel = self["menu"].getSelectionIndex()
            name = self.names[sel]
            url = self.urls[sel]
            print("In Getadds5 url = ", url)
            self.session.open(Getadds6, name, url)

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Getadds6(Screen):

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = " "
        self.name = name
        print("In Getadds6 url =", url)
        self.url = url
        print("In Getadds6 self.url =", self.url)
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        xurl = self.url
        print("xurl 2=", xurl)
        # getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)
        html = Utils.getUrl(xurl)
        self.gotPage(html)

    def gotPage(self, html):
        # try:
        if DEBUG == 1:
            print("html 2= ", html)
        self.html = html
        self.names = []
        self.urls = []
        if "plugin.video" in self.name:
            regexcat = '<tr><td><a href="plugin.video(.*?)" title="(.*?)".*?td><td>20(.*?)<'
            match = re.compile(regexcat, re.DOTALL).findall(html)
            for url, name, rev in match:
                name = name + " :" + "20" + rev
                name = name.replace("plugin.video.", "")
                self.names.append(name)
                self.urls.append(url)
        elif "plugin.audio" in self.name:
            regexcat = '<<tr><td><a href="plugin.audio(.*?)" title="(.*?)".*?</td><td>20(.*?)<'
            match = re.compile(regexcat, re.DOTALL).findall(html)
            for url, name, rev in match:
                name = name + " :" + "20" + rev
                name = name.replace("plugin.audio.", "")
                self.names.append(name)
                self.urls.append(url)
        if "plugin.image" in self.name:
            regexcat = '<tr><td><a href="plugin.image(.*?)" title="(.*?)".*?</td><td>20(.*?)<'
            match = re.compile(regexcat, re.DOTALL).findall(html)
            for url, name, rev in match:
                name = name + " :" + "20" + rev
                name = name.replace("plugin.image.", "")
                self.names.append(name)
                self.urls.append(url)
        if "plugin.picture" in self.name:
            regexcat = '<tr><td><a href="plugin.picture(.*?)" title="(.*?)".*?</td><td>20(.*?)<'
            match = re.compile(regexcat, re.DOTALL).findall(html)
            for url, name, rev in match:
                name = name + " :" + "20" + rev
                name = name.replace("plugin.picture.", "")
                self.names.append(name)
                self.urls.append(url)
        Utils.showlist(self.names, self["menu"])

    def getfeedError(self, error=""):
        error = str(error)
        print("Download error =", error)

    def okClicked(self):
        if self.errcount == 1:
            self.close()
        else:
            sel = self["menu"].getSelectionIndex()
            name = self.names[sel]
            url = self.urls[sel]
            # http://mirrors.kodi.tv/addons/krypton/plugin.video.dailymotion_com/plugin.video.dailymotion_com-2.4.1.zip
            print("In getadds6 self.url =", self.url)
            if "plugin.video" in self.name:
                url = self.url + "plugin.video" + url
            if "plugin.audio" in self.name:
                url = self.url + "plugin.audio" + url
            if "plugin.image" in self.name:
                url = self.url + "plugin.image" + url
            if "plugin.picture" in self.name:
                url = self.url + "plugin.picture" + url
            print("Here in Getadds6 name, url =", name, url)
            self.session.open(Addons3, self.name, url)

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Fusion(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)

        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("Please select repository type"))
        self["info"].setText(self.info)
        # self["bild"] = startspinner()
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        self.methods = []
        self.urls = []
        # self.methods.append("superrepo")
        # self.urls.append("https://cdimage.debian.org/mirror/addons.superrepo.org/v7/addons/")
        self.methods.append("English")
        self.urls.append("http://fusion.tvaddons.co/kodi-repos/english/")
        self.methods.append("International")
        self.urls.append("http://fusion.tvaddons.co/kodi-repos/international/")
        self.methods.append("XXX-Adult")
        self.urls.append("http://fusion.tvaddons.co/kodi-repos/xxx-adult/")
        Utils.showlist(self.methods, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        url = self.urls[sel]
        name = self.methods[sel]
        self.selname = name
        self.selurl = url
        if sel is None:
            self.close()
        elif "adult" in name.lower():
            self.allow()
        else:
            self.session.open(Fusion2, name, url)

    def allow(self):
        # perm = config.ParentalControl.configured.value
        # ####print  "perm =", perm
        if config.ParentalControl.configured.value:
            # ####print  "Here Ad 1"
            # from Screens.InputBox import InputBox, PinInput
            self.session.openWithCallback(self.pinEntered, PinInput, pinList=[config.ParentalControl.setuppin.value], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the parental control pin code"), windowtitle=_("Enter pin code"))

        else:
            # ####print  "Here Ad 2"
            self.pinEntered(True)
        # return

    def pinEntered(self, result):
        # ####print  "Here Ad 3 result =", result
        if result:
            self.session.open(Fusion2, self.selname, self.selurl)
        else:
            self.session.openWithCallback(self.close, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)
            self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Fusion2(Screen):

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (_("Please select repository type"))
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.name = name
        self.url = url
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        self.names = []
        self.urls = []
        try:
            fpage = Utils.getUrl(self.url)
        except:
            fpage = " "
        # http://fusion.tvaddons.co/kodi-repos/english/repository.BludhavenGrayson-1.0.0.zip
        regexcat = 'a href="(.*?)">(.*?)<'
        match = re.compile(regexcat, re.DOTALL).findall(fpage)
        print("In Repo2 match =", match)
        # http://fusion.tvaddons.co/kodi-repos/english/repository.nextup-0.0.1.zip
        for url, name in match:
            name = name.replace("&gt", "")
            name = name.replace("..", "")
            name = name.replace(";", "")
            self.names.append(name)
            url1 = self.url + url
            self.urls.append(url1)
        Utils.showlist(self.names, self["menu"])

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        url = self.urls[sel]
        if sel is None:
            self.close()
        else:
            xurl = url
            print("xurl =", xurl)
            xdest = "/tmp/plug.zip"
            # downloadPage(xurl, xdest).addCallback(self.install).addErrback(self.showError)
            fpage = Utils.getUrl(xurl)
            f = open(xdest, 'w')
            f.write(fpage)
            f.close()
            self.install()

    def showError(self, error):
        print("ERROR :", error)

    def install(self):
        fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/repos"
        cmd = "unzip -o -q '/tmp/plug.zip' -d " + fdest
        title = (_("Installing repo"))
        self.session.openWithCallback(self.doneinst, Console, _(title), [cmd])

    def doneinst(self):
        self.session.open(Getadds4)

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Repo2(Screen):

    def __init__(self, session, infourl, plugurl, zipcode):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = "Please select"
        self.infourl = infourl
        self.plugurl = plugurl
        self.zipcode = zipcode
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        xurl = self.infourl
        print("In Repo2 xurl =", xurl)
        # getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)
        html = Utils.getUrl(xurl)
        self.gotPage(html)

    def gotPage(self, html):
        if DEBUG == 1:
            print("In Repo2 html = ", html)
        self.html = html
        self.names = []
        self.urls = []
        regexcat = '<add.*?id="(.*?)".*?version="(.*?)"'
        match = re.compile(regexcat, re.DOTALL).findall(html)
        print("In Repo2 match =", match)
        for name, url in match:
            self.names.append(name)
            self.urls.append(url)
        Utils.showlist(self.names, self["menu"])
        # except Exception, error:
        # print  "[plugins]: Could not download HTTP Page\n" + str(error)

    def getfeedError(self, error=""):
        error = str(error)
        print("Download error =", error)

    def okClicked(self):
        if self.zipcode == "false":
            sel = self["menu"].getSelectionIndex()
            if sel is None:
                self.close()
            name = self.names[sel]
            url1 = self.plugurl + name + "/"
            url2 = self.infourl
            line = name + "###" + url1 + "###" + url2 + "###"
            print("In Repo2 line =", line)
            """
            adpath = THISPLUG + "/useradlist.txt"
            f1 = open(adpath,"a")
            f1.write(line)
            f1.close()
            """
            self.session.open(GetaddonsA3, line)
        else:
            sel = self["menu"].getSelectionIndex()
            if sel is None:
                self.close()
            name = self.names[sel]
            url = self.urls[sel]
            if self.plugurl.endswith("/"):
                # url = self.plugurl + name + "/" + name + "-" + url + ".zip?raw=true"
                url = self.plugurl + name + "/" + name + "-" + url + ".zip"
            else:
                # url = self.plugurl + "/" + name + "/" + name + "-" + url + ".zip?raw=true"
                url = self.plugurl + "/" + name + "/" + name + "-" + url + ".zip"
            print("In Repo2 url B= ", url)
            url2 = self.infourl
            line = name + "###" + url + "###" + url2 + "###\n"
            print("In Repo2 line 2 =", line)
            adpath = THISPLUG + "/useradlist.txt"
            f1 = open(adpath, "a")
            f1.write(line)
            f1.close()
            self.session.open(Addons3, name, url)

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        # print  "pressed", number
        self["menu"].number(number)


class Repo3(Screen):

    def __init__(self, session, url, plugurl, zipcode):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = " "
        print("In Repo3 url =", url)
        self.url = plugurl + url
        self.zipcode = zipcode
        print("In Addons2 self.url =", self.url)
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        xurl = self.url
        print("Repo3 xurl=", xurl)
        getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)

    def gotPage(self, html):
        if DEBUG == 1:
            print("Repo3 html = ", html)
        self.html = html
        self.names = []
        self.urls = []
        regexcat = '<a href="plugin.video(.*?)">(.*?)</a><'
        match = re.compile(regexcat, re.DOTALL).findall(html)
        for url, name in match:
            name = name.replace("plugin.video.", "")
            self.names.append(name)
            self.urls.append(url)
        Utils.showlist(self.names, self["menu"])

    def getfeedError(self, error=""):
        error = str(error)
        print("Download error =", error)

    def okClicked(self):
        if self.errcount == 1:
            self.close()
        else:
            sel = self["menu"].getSelectionIndex()
            name = self.names[sel]
            url = self.urls[sel]
            url = self.url + "/plugin.video" + url
            print("Here in Repo3 name, url =", name, url)
            self.session.open(Addons3, name, url)

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        self["menu"].number(number)


# no used
class Addons(Screen):

    def __init__(self, session, url):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        print("Addons url =", url)
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = " "
        self.url = url
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        xurl = self.url
        print("In Addons xurl =", xurl)
        getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)

    def gotPage(self, html):
        if DEBUG == 1:
            print("In Addons html = ", html)
        file1 = THISPLUG + "/adlist.txt"
        f1 = open(file1, "r+")
        fpage = f1.read()
        n1 = fpage.find("Frodo")
        n2 = fpage.find("#####", (n1+10))
        fpage2 = fpage[n1:n2]
        self.html = html
        self.names = []
        self.urls = []
        print("In Addons HOST = ", HOST)
        regexcat = '<a href="plugin.video(.*?)">(.*?)/<'
        match = re.compile(regexcat, re.DOTALL).findall(html)
        print("In Addons match =", match)
        for url, name in match:
            if name not in fpage2:
                continue
            if "plugin.video" not in name:
                continue
            self.names.append(name)
            self.urls.append(url)
        Utils.showlist(self.names, self["menu"])

    def getfeedError(self, error=""):
        error = str(error)
        print("Download error =", error)

    def okClicked(self):
        sel = self["menu"].getSelectionIndex()
        name = self.names[sel]
        url = self.urls[sel]
        print("In Addons url = ", url)
        self.session.open(Addons2, name, url)
        self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        self["menu"].number(number)


# depends from Addons  # no used
class Addons2(Screen):

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = " "
        self.name = name
        print("In Addons2 url =", url)
        self.url = HOST + "plugin.video" + url
        print("In Addons2 self.url =", self.url)
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        xurl = self.url
        print("xurl 2=", xurl)
        getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)

    def gotPage(self, html):
        if DEBUG == 1:
            print("html 2= ", html)
        self.html = html
        self.names = []
        self.urls = []
        regexcat = '<a href="plugin.video(.*?)">(.*?)</a>(.*?)<'
        match = re.compile(regexcat, re.DOTALL).findall(html)
        for url, name, rev in match:
            name = name + " :" + rev
            name = name.replace("plugin.video.", "")
            self.names.append(name)
            self.urls.append(url)
        Utils.showlist(self.names, self["menu"])

    def getfeedError(self, error=""):
        error = str(error)
        print("Download error =", error)

    def okClicked(self):
        if self.errcount == 1:
            self.close()
        else:
            sel = self["menu"].getSelectionIndex()
            name = self.names[sel]
            url = self.urls[sel]
            url = self.url + "plugin.video" + url
            print("Here in Addons2 name, url =", name, url)
            self.session.open(Addons3, name, url)
            self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        self["menu"].number(number)


class Addons3(Screen):

    def __init__(self, session, name, url):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "XbmcPluginScreenF"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = " "
        self.name = name
        self.url = url
        print("In Addons3 self.name =", self.name)
        print("In Addons3 self.url =", self.url)
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.close,
                                           "red": self.close,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Select"))
        self.icount = 0
        self.errcount = 0
        self.onShown.append(self.openTest)

    def okClicked(self):
        pass

    def openTest(self):
        pic = res_plugin_path + "Download.png"
        if Utils.isFHD():
            pic = res_plugin_path + "DownloadL.png"
        self["pixmap1"].instance.setPixmapFromFile(pic)
        name = self.name.split(" : ")
        self.plug = name[0]
        xdest = "/tmp/" + self.plug
        xurl = self.url
        f = Utils.getUrlresp(xurl)
        print("f =", f)
        fpage = f.read()
        print("fpage 2 =", fpage)
        f1 = open(xdest, "wb")
        f1.write(fpage)
        f1.close()
        self.install()

    def showError(self, error):
        print("ERROR :", error)

    def install(self):
        print("In Addons3 self.plug =", self.plug)
        if "plugin." in self.plug:
            fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins"
        if "script." in self.plug:
            fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/scripts"
        if "repository." in self.plug:
            fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/repos"
        cmd = "unzip -o -q '/tmp/" + self.plug + "' -d " + fdest
        print("cmd =", cmd)
        title = _("Installing addons %s" % (self.plug))
        self.session.open(Console, _(title), [cmd])
        self["info"].setText(_("Done."))
        self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        self["menu"].number(number)


class ShowPage2(Screen):

    def __init__(self, session, newstext):
        Screen.__init__(self, session)
        self.session = session
        global _session
        _session = session
        self.skinName = "ShowPage"
        title = PlugDescription
        self["title"] = Button(title + Version)
        self.ftext = newstext  # global
        self["menu"] = Utils.tvList([])
        self['infoc'] = Label(_('Info'))
        self['infoc2'] = Label('%s' % Credits)
        self['info'] = Label()
        self.info = (" ")
        self["info"].setText(self.info)
        self["pixmap1"] = Pixmap()
        self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          {"ok": self.okClicked,
                                           "back": self.cancel,
                                           "red": self.cancel,
                                           "green": self.okClicked}, -1)
        self["key_red"] = Button(_("Exit"))
        self["key_green"] = Button(_("OK"))
        self.icount = 0
        self.errcount = 0
        print("In showPage 1")
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        print("In showPage 2")
        pic = defpic
        self["pixmap1"].instance.setPixmapFromFile(pic)
        self.data = []
        self.data = self.ftext.splitlines()
        print("In showPage self.data =", self.data)
        Utils.showlist(self.data, self["menu"])

    def cancel(self):
        self.close()

    def okClicked(self):
        self.close()

    def keyLeft(self):
        self["menu"].left()

    def keyRight(self):
        self["menu"].right()

    def keyNumberGlobal(self, number):
        self["menu"].number(number)


'''
# class Getaddons2(Screen):

    # def __init__(self, session):
        # Screen.__init__(self, session)
        # self.session = session
        # # lululla added
        # global _session
        # _session = session
        # # end
        # self.skinName = "XbmcPluginScreenF"
        # title = PlugDescription
        # self["title"] = Button(title + Version)

        # self["menu"] = Utils.tvList([])
        # self['infoc'] = Label(_('Info'))
        # self['infoc2'] = Label('%s' % Credits)
        # self['info'] = Label()
        # self.info = (_("Please select category"))
        # self["info"].setText(self.info)
        # self["pixmap1"] = Pixmap()
        # self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          # {"ok": self.okClicked,
                                           # "back": self.close,
                                           # "red": self.close,
                                           # "green": self.okClicked}, -1)
        # self["key_red"] = Button(_("Cancel"))
        # self["key_green"] = Button(_("Select"))
        # self.icount = 0
        # self.errcount = 0
        # self.onLayoutFinish.append(self.openTest)

    # def openTest(self):
        # pic = res_plugin_path + "Download.png"
        # if Utils.isFHD():
            # pic = res_plugin_path + "DownloadL.png"
        # self["pixmap1"].instance.setPixmapFromFile(pic)
        # self.data = []
        # cats = []
        # file1 = THISPLUG + "/useradlist.txt"
        # myfile = open(file1, "r+")
        # icount = 0
        # for line in myfile.readlines():
            # if line.startswith("#####"):
                # cat = line.replace("#####", "")
                # cat = cat.replace("####", "")
                # if "fix" in cat:
                    # continue
                # cats.append(cat)
                # self.data.append(line)
        # Utils.showlist(cats, self["menu"])

    # def okClicked(self):
        # sel = self["menu"].getSelectionIndex()
        # if sel is None:
            # self.close()
        # else:
            # name = self.data[sel]
            # if "Adult" in name:
                # self.catname = name
                # self.allow()
            # else:
                # self.session.open(GetaddonsA2B, name)
                # self.close()

    # def allow(self):
        # # perm = config.ParentalControl.configured.value
        # # ####print  "perm =", perm
        # if config.ParentalControl.configured.value:
            # # print  "Here Ad 1"
            # # from Screens.InputBox import InputBox, PinInput
            # self.session.openWithCallback(self.pinEntered, PinInput, pinList=[config.ParentalControl.setuppin.value], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the parental control pin code"), windowtitle=_("Enter pin code"))
        # else:
            # # ####print  "Here Ad 2"
            # self.pinEntered(True)
        # # return

    # def pinEntered(self, result):
        # # ####print  "Here Ad 3 result =", result
        # if result:
            # self.session.open(GetaddonsA2B, self.catname)
            # self.close()
        # else:
            # self.session.openWithCallback(self.close, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)
            # self.close()

    # def keyLeft(self):
        # self["menu"].left()

    # def keyRight(self):
        # self["menu"].right()

    # def keyNumberGlobal(self, number):
        # # print  "pressed", number
        # self["menu"].number(number)


# class GetaddonsA2B(Screen):

    # def __init__(self, session, cat):
        # Screen.__init__(self, session)
        # # if config.plugins.polar.menutype.value == "icons1":
            # # self.skinName = "Downloads"
        # # else:
        # self.session = session
        # self.skinName = "XbmcPluginScreenF"
        # title = PlugDescription
        # self["title"] = Button(title + Version)

        # self["menu"] = Utils.tvList([])
        # self['infoc'] = Label(_('Info'))
        # self['infoc2'] = Label('%s' % Credits)
        # self['info'] = Label()
        # self.cat = cat
        # self.info = (_("     Please select addon to install"))
        # self["info"].setText(self.info)
        # self["pixmap1"] = Pixmap()
        # self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                          # {"ok": self.okClicked,
                                           # "back": self.close,
                                           # "red": self.close,
                                           # "green": self.okClicked}, -1)
        # self["key_red"] = Button(_("Cancel"))
        # self["key_green"] = Button(_("Select"))
        # self.icount = 0
        # self.errcount = 0
        # self.names = []
        # self.urls = []
        # self.onLayoutFinish.append(self.openTest)

    # def openTest(self):
        # pic = res_plugin_path + "Download.png"
        # if Utils.isFHD():
            # pic = res_plugin_path + "DownloadL.png"
        # self["pixmap1"].instance.setPixmapFromFile(pic)
        # self.data = []
        # try:
            # file1 = THISPLUG + "/useradlist.txt"
            # f1 = open(file1, "r+")
            # fpage = f1.read()
        # except:
            # fpage = " "
        # self.fpage = fpage
        # n1 = fpage.find(self.cat)
        # n2 = fpage.find("#####", (n1+10))
        # fpage2 = fpage[n1:n2]
        # lines = fpage2.splitlines()
        # nms = []
        # for line in lines:
            # if line.startswith("#####"):
                # continue
            # elif "---" in line:
                # nms.append(line)
                # self.names.append(" ")
                # self.urls.append(" ")
            # elif "###" not in line:
                # nms.append(line)
                # self.names.append(" ")
                # self.urls.append(" ")
            # else:
                # # print  "In GetaddonsA2 line =", line
                # items = line.split("###")
                # # print  "In GetaddonsA2 items =", items
                # nm = items[0]
                # nms.append(nm)
                # self.names.append(items[0])
                # self.urls.append(line)
        # Utils.showlist(nms, self["menu"])

    # def okClicked(self):
        # sel = self["menu"].getSelectionIndex()
        # if sel is None:
            # self.close()
        # else:
            # line = self.urls[sel]
            # self.name = self.names[sel]
            # self.checkLine(line)

    # def checkLine(self, line):
        # print("In checkLine line =", line)
        # items = line.split("###")
        # print("In checkLine items =", items)
        # name = items[0]
        # url1 = items[1]
        # url2 = items[2]
        # if url2 == '':
            # xurl = url1
            # xdest = "/tmp/plug.zip"
            # downloadPage(xurl, xdest).addCallback(self.install).addErrback(self.showError)
        # elif not items[1].endswith(".zip"):  # datadirectory zip false
            # self.session.open(GetaddonsA3, line)
            # self.close()
        # else:
            # url2 = items[2]
            # n2 = url1.find(".zip", 0)
            # n3 = url1.rfind("-", 0, n2)
            # if n3 < 0:
                # n3 = url1.rfind("_", 0, n2)
            # n4 = n3 + 1
            # url0 = url1[:n4]
            # print("url0 =", url0)
            # # fpage = urlopen(url2).read()
            # xurl = url2
            # xdest = "/tmp/down.txt"
            # self.line = line
            # self.name = name
            # self.url1 = url1
            # self.url2 = url2
            # self.url0 = url0
            # # fpage = urlopen(url2).read()
            # downloadPage(xurl, xdest).addCallback(self.getdown).addErrback(self.showError)

    # def getdown(self, fplug):
        # fpage = open("/tmp/down.txt", "r").read()
        # print("In checkLine fpage =", fpage)
        # if self.url2.endswith(".xml"):
            # # rx = self.name + '.*?version="(.*?)"'
            # rx = 'addo.*?id="' + self.name + '".*?version="(.*?)"'
        # else:
            # rx = self.name + '-(.*?).zip'
        # print("rx =", rx)
        # match = re.compile(rx, re.DOTALL).findall(fpage)
        # print("match =", match)
        # if len(match) == 0:
            # rx = self.name + '_(.*?).zip'
            # match = re.compile(rx, re.DOTALL).findall(fpage)
            # print("match 2=", match)
        # elif len(match) == 1:
            # latest = match[0]
        # else:
            # latest = findmax(match)
        # if latest is not None:
            # xurl = self.url0 + latest + ".zip"
            # print("xurl =", xurl)
            # xdest = "/tmp/plug.zip"
            # downloadPage(xurl, xdest).addCallback(self.install).addErrback(self.showError)
        # else:
            # return

    # def showError(self, error):
        # print("ERROR :", error)

    # def install(self, fplug):
        # if "script." in self.name:
            # fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/scripts"
        # elif "repository" in self.name:
            # fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/repos"
        # else:
            # fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins"
        # addon = THISPLUG + "/plugins/" + self.name
        # cmd1 = "rm -rf '" + addon + "'"
        # cmd2 = "unzip -o -q '/tmp/plug.zip' -d " + fdest
        # cmd = []
        # cmd.append(cmd1)
        # cmd.append(cmd2)
        # print("cmd =", cmd)
        # title = (_("Installing addon"))
        # self.session.openWithCallback(self.checkName, Console, _(title), cmd)
        # # self.close()

    # def checkName(self):
        # if "repository" in self.name:
            # self.session.open(Getadds4)
        # else:
            # path = THISPLUG + "/plugins"
            # for name in os.listdir(path):
                # print("name =", name)
                # if "plugin" not in name:
                    # if "__init" in name:
                        # continue
                    # elif "E2" in name:
                        # self.close()
                    # else:
                        # newname = "plugin.video." + name
                        # cmd = "mv " + path + "/" + name + " " + path + "/" + newname + " &"
                        # os.system(cmd)
                # if "-master" in name:
                    # newname = name.replace("-master", "")
                    # cmd = "mv " + path + "/" + name + " " + path + "/" + newname + " &"
                    # os.system(cmd)
                # if ("pelisalacarta" in name) or ("tvalacarta" in name):
                    # cmd = "rm '" + path + "/" + name + "/fixed2'"
                    # os.system(cmd)
            # self.close()
            # self.checkfix()

    # def checkfix(self):
        # self.close()

    # def installB(self, fplug):
        # fdest = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/plugins"
        # cmd = "unzip -o -q '/tmp/plug.zip' -d " + fdest
        # print("In installB cmd =", cmd)
        # # title = (_("Installing addon fix"))
        # os.system(cmd)
        # self.close()

    # def keyLeft(self):
        # self["menu"].left()

    # def keyRight(self):
        # self["menu"].right()

    # def keyNumberGlobal(self, number):
        # # print  "pressed", number
        # self["menu"].number(number)


# class ShowPage(Screen):

    # def __init__(self, session, newstext):
        # Screen.__init__(self, session)
        # self.session = session
        # # self.skinName = "XbmcPluginScreenF"
        # title = PlugDescription
        # self["title"] = Button(title + Version)
        # self.skinName = "ShowPage"
        # # self["list"] = MenuList([])
        # self.ftext = newstext  # global

        # self["menu"] = Utils.tvList([])
        # self['infoc'] = Label(_('Info'))
        # self['infoc2'] = Label('%s' % Credits)
        # self['info'] = Label()
        # self.info = (_("Press OK if you want to see this message again."))
        # self["info"].setText(self.info)
        # self["pixmap"] = Pixmap()
        # self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                        # {
                                                # "ok": self.okClicked,
                                                # "back": self.cancel,
                                                # "red": self.cancel,
                                                # "green": self.okClicked,
                                        # }, -1)
        # self["key_red"] = Button(_("Exit"))
        # self["key_green"] = Button(_("OK"))
        # self.icount = 0
        # self.errcount = 0
        # print("In showPage 1")
        # self.onLayoutFinish.append(self.openTest)

    # def openTest(self):
        # print("In showPage 2")
        # if Utils.isFHD():
            # pic = res_plugin_path + "defaultL.png"
        # else:
            # pic = res_plugin_path + "default.png"
        # self["pixmap"].instance.setPixmapFromFile(pic)
        # self.data = []
        # self.data = self.ftext.splitlines()
        # print("In showPage self.data =", self.data)
        # Utils.showlist(self.data, self["menu"])

    # def cancel(self):
        # file = open("/etc/kodinodl", "w")
        # file.write(date)
        # file.write("\n")
        # file.close()
        # self.close()

    # def okClicked(self):
        # os.system("rm /etc/kodinodl &")
        # self.close()

    # def keyLeft(self):
        # self["menu"].left()

    # def keyRight(self):
        # self["menu"].right()

    # def keyNumberGlobal(self, number):
        # # print  "pressed", number
        # self["menu"].number(number)


# class Getcats(Screen):

    # def __init__(self, session):
        # Screen.__init__(self, session)
        # self.session = session
        # self.skinName = "Getcats2"
        # # self.list = []
        # # self["menu"] = List(self.list)
        # self["menu"] = Utils.tvList([])
        # self['infoc'] = Label(_('Info'))
        # self['infoc2'] = Label('%s' % Credits)
        # self['info'] = Label()
        # self.info = (_("Addon Categories"))
        # self["info"].setText(self.info)
        # self["pixmap1"] = Pixmap()
        # self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"],
                                             # {"ok": self.okClicked,
                                             # "back": self.close,
                                             # "red": self.close,
                                             # "green": self.okClicked,
                                             # "yellow": self.conf}, -1)
        # self["key_red"] = Button(_("Exit"))
        # self["key_green"] = Button(_("Select"))
        # self["key_yellow"] = Button(_("Config"))
        # title = _("Install methods")
        # self["title"] = Button(title)
        # self.icount = 0
        # self.errcount = 0
        # self.onLayoutFinish.append(self.openTest)

    # def fixscripts(self):
        # url = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/list.txt"
        # self.fixlist = Utils.getUrl(url)
        # print("self.fixlist =", self.fixlist)
        # pathsh = THISPLUG + "/scripts"
        # for name in os.listdir(pathsh):
            # self.name = name
            # self.checkfixsh()
        # return

    # def delete(self):
        # self.session.openWithCallback(self.listplugs, DelAdd)

    # def addon(self):
        # self.session.openWithCallback(self.listplugs, Getadds)

    # def conf(self):
        # self.session.open(XbmcConfigScreen)

    # def openTest(self):
        # picthumb = res_plugin_path + "default.png"
        # self["pixmap1"].instance.setPixmapFromFile(picthumb)
        # methods = []
        # methods.append(_("Showtime"))
        # methods.append(_("IPTV"))
        # methods.append(_("Youtube & Co"))
        # methods.append(_("Albanian"))
        # methods.append(_("Italian"))
        # methods.append(_("Turkish"))
        # methods.append(_("User Addons"))
        # methods.append(_("Adult 18+"))
        # Utils.showlist(methods, self["menu"])

    # def okClicked(self):
        # sel = self["menu"].getSelectionIndex()
        # global ADDONCAT
        # if sel is None:
            # self.close()
        # elif sel == 0:
            # ADDONCAT = "MOVIES"
        # elif sel == 1:
            # ADDONCAT = "IPTV"
        # elif sel == 2:
            # ADDONCAT = "YT"
        # elif sel == 3:
            # ADDONCAT = "ALB"
        # elif sel == 4:
            # ADDONCAT = "ITAL"
        # elif sel == 5:
            # ADDONCAT = "TURK"
        # elif sel == 6:
            # ADDONCAT = "plugins"
        # else:
            # ADDONCAT = "ADULT"

        # if ADDONCAT == "ADULT":
            # print("Here in else (adult) going to allow")
            # self.allow()
        # else:
            # f1 = open("/tmp/addoncat.txt", "w")
            # f1.write(ADDONCAT)
            # f1.close()
            # self.session.open(StartPlugin_mainmenu)

    # def allow(self):
        # perm = config.ParentalControl.configured.value
        # print("Here in allow perm =", perm)
        # if config.ParentalControl.configured.value:
            # print("Here in allow 1")
            # self.session.openWithCallback(self.pinEntered, PinInput, pinList=[config.ParentalControl.setuppin.value], triesEntry=config.ParentalControl.retries.servicepin, title=_("Please enter the parental control pin code"), windowtitle=_("Enter pin code"))

        # else:
            # print("Here in allow 2")
            # self.pinEntered(True)
        # # return

    # def pinEntered(self, result):
        # print("Here in allow result =", result)
        # if result:
            # global ADDONCAT
            # ADDONCAT = "ADULT"
            # f1 = open("/tmp/addoncat.txt", "w")
            # f1.write(ADDONCAT)
            # f1.close()
            # print("Here in allow 3")
            # self.session.open(StartPlugin_mainmenu)
        # else:
            # print("Here in allow 4")
            # self.session.openWithCallback(self.close, MessageBox, _("The pin code you entered is wrong."), MessageBox.TYPE_ERROR)
            # self.close()

    # def keyLeft(self):
        # self["menu"].left()

    # def keyRight(self):
        # self["menu"].right()

    # def keyNumberGlobal(self, number):
        # # print  "pressed", number
        # self["menu"].number(number)
'''

"""
    ######################################
    fyt = THISPLUG + "/scripts/script.module.youtube.dl/control.py"
    fyt1 = THISPLUG + "/scripts/script.module.youtube.dl"
    if not os.path.exists(fyt):
        cmd = "rm -rf " + fyt1
        print("fyt cmd =", cmd)
        os.system(cmd)

    fyt = THISPLUG + "/scripts/script.module.urlresolver/lib/urlresolver/plugins"
    fyt1 = THISPLUG + "/scripts/script.module.urlresolver"
    fyt2 = THISPLUG + "/kodi.py"

    if not os.path.exists(fyt):
        cmd = "rm -rf " + fyt1
        print("fyt cmd =", cmd)
        os.system(cmd)

    else:
        cmd = "cp rf " + fyt2 + " " + fyt1 + "/lib/urlresolver/lib/"
        os.system(cmd)

    fyt = THISPLUG + "/scripts/script.module.future/libs"
    fyt1 = THISPLUG + "/scripts/script.module.future/lib"
    if os.path.exists(fyt):
        cmd = "mv " + fyt + " " + fyt1
        print("fyt cmd =", cmd)
        os.system(cmd)
    print("In def main 71")
    ######################################
    #mmmmmmmmmmmmmmmmmmmmmmmmm
    xurl = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/kodi-news2.txt"
    ucode = "UTF-8"
    xurl = xurl.encode(ucode)
    xdest = "/tmp/kodi-news.txt"
    downloadPage(xurl, xdest).addCallback(gotNews).addErrback(showNewsError)

    def showNewsError(error):
       print("In def main 6 error =", error)
       start()

    def gotNews(txt=" "):
        print("In def main 7")
        global date
        session = _session
        indic = 0
        date = ""
        olddate = ""
        if not os.path.exists("/tmp/kodi-news.txt"):
            indic = 0
        else:
            myfile = file(r"/tmp/kodi-news.txt")
            icount = 0
            for line in myfile.readlines():
                if icount == 0:
                    date = line
                    break
                icount += 1
            myfile.close()
            myfile = file(r"/tmp/kodi-news.txt")
            global newstext
            newstext = myfile.read()
            print("In gotNews newstext =", newstext)
            myfile.close()
            news = newstext
            n1 = news.find("update2", 0)
            if n1 > -1:
                upd = news[n1:(n1+14)]
            else:
                upd = "None"
            global NewUpdate
            NewUpdate = upd
            if fileExists("/etc/kodiupd"):
                myfile = file(r"/etc/kodiupd")
                icount = 0
                for line in myfile.readlines():
                    if icount == 0:
                        upd1 = line
                        break
                    icount += 1
                myfile.close()
            else:
                upd1 = "None"
            n2 = upd1.find(".", 0)
            if n2 > -1:
                upd1 = upd1[:n2]
            print("upd =", upd)
            print("upd1 =", upd1)
            if upd != "None":
                if upd1 != upd:
                    txt = _("New ") + upd + _(" is available. \nAfter update - gui will restart.\nUpdate Now ?")
                    session.openWithCallback(do_upd, MessageBox, txt, type = 0)
                else:
                    check_news()
            else:
                check_news()

    def do_upd(answer):
        print("In def main 8")
        session = _session
        if answer is None:
            check_news()
        else:
        if answer is False:
            check_news()
        else:
            picfold = cfg.cachefold.value+"/xbmc/pic"
            cmd = "rm -rf " + picfold
            os.system(cmd)
            global plug
            plug = NewUpdate + ".zip"
            if "update" in plug:
                    f=open("/etc/kodiupd", 'w')
                    txt = plug + "\n"
                    f.write(txt)
            xdest = "/tmp/" + plug
            # cmd1 = "wget -O '" + dest + "' 'http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Software/" + plug + "'"
            # cmd1 = "wget -O '" + dest + "' 'http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Software2/" + plug + "'"
            ##############################################
            xurl = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Software/" + plug
            downloadPage(xurl, xdest).addCallback(gotUpd).addErrback(showNewsError)

    def gotUpd(answer):
        ##############################################
        session = _session
        if ".ipk" in plug:
            cmd2 = "opkg install --force-overwrite '/tmp/" + plug + "'"
        elif ".deb" in plug:
            cmd2 = "dpkg --install '/tmp/" + plug + "'"

        elif ".zip" in plug:
            cmd2 = "unzip -o -q '/tmp/" + plug + "' -d /"
        title = _("Installing %s" % (plug))
        session.openWithCallback(done_upd,Console, _(title),[cmd2])

    def done_upd():
        print("In def main 9")
        from .Restart import Restart
        session = _session
        Restart(session)

    def check_news():
        print("In check_news")
        session = _session
        olddate = " "
        if not os.path.exists("/etc/kodinodl"):
            indic = 1
        else:
            myfile2 = file(r"/etc/kodinodl")
            icount = 0
            for line in myfile2.readlines():
                if icount == 0:
                    olddate = line
                    break
                icount += 1
            if olddate != date :
                indic = 1
            else:
                indic = 0
            myfile2.close()
        print("In check_news indic =", indic)
        if indic == 0:
            start()
        else:
            session.openWithCallback(start, ShowPage, newstext)
        """


_session = ""
plug = ""


def main(session, **kwargs):
    global _session
    _session = session
    log = cfg.elog.value
    if log is True:
        logf = open('/tmp/e.log', 'w')
        sys.stdout = logf
    else:
        if os.path.exists("/tmp/e.log"):
            os.remove("/tmp/e.log")
    if not os.path.exists("/etc/KodiLite"):
        try:
            os.mkdir(os.path.join('/etc', "KodiLite"))
        except:
            pass
        # os.system("mkdir -p /etc/KodiLite")
    if not os.path.exists("/etc/KodiLite/favorites.xml"):
        cmd = "cp " + THISPLUG + "/lib/defaults/favorites.xml /etc/KodiLite/"
        os.system(cmd)
    print("In def main 4")

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc"))
    except:
        pass

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc/vid"))
    except:
        pass

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc/pic"))
    except:
        pass

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc/home"))
    except:
        pass

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc/database"))
    except:
        pass

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc/userdata"))
    except:
        pass

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc/userdata/Database"))
    except:
        pass

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc/home/addons"))
    except:
        pass

    try:
        os.mkdir(os.path.join(str(cfg.cachefold.value), "xbmc/home/addons/packages"))
    except:
        pass

    print("In def main 5")
    try:
        cachefolder = cfg.cachefold.value
    except:
        cachefolder = "/media/hdd"
    afile = open("/etc/xbmc.txt", 'w')
    afile.write(cachefolder)
    afile.close()
    print("In def main 6")
    # start()
    # if cfg.update.getValue() is True:
    try:
        from Plugins.Extensions.KodiLite.Update2 import updstart2
        updstart2()
    except:
        print("\nError 2 updating some scripts")
    try:
        from Plugins.Extensions.KodiLite.Update import updstart
        updstart()
    except:
        print("\nError updating some scripts")
    start()
    print("In def main 7")


def start():
    print("Going into StartPlugin_mainmenu")
    gpath = os.path.join(THISPLUG, 'greet')
    if os.path.exists(gpath):
        cmd = "rm -rf " + gpath
        os.system(cmd)
    #  _session.open(Getcats)
    global ADDONCAT
    ADDONCAT = "plugins"
    f1 = open("/tmp/addoncat.txt", "w")
    f1.write(ADDONCAT)
    f1.close()
    _session.open(Start_mainmenu)


def mpanel(menuid, **kwargs):
    if menuid == "mainmenu":
        return [("KodiLite", main, "xbmc_addons", 12)]
    else:
        return []


def Plugins(**kwargs):
    loadPluginSkin(kwargs["path"])
    try:
        viewdownloads = cfg.viewdownloads.value
        mmenu = cfg.mmenu.value
    except:
        viewdownloads = 'disabled'
        mmenu = False
    list = []
    list.append(PluginDescriptor(icon="plugin.png", name="KodiLite", description="Kodi Addons for enigma2", where=PluginDescriptor.WHERE_MENU, fnc=mpanel))
    list.append(PluginDescriptor(icon="plugin.png", name="KodiLite", description="Kodi Addons for enigma2", where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main))
    list.append(PluginDescriptor(icon="plugin.png", name="KodiLite", description="Kodi Addons for enigma2", where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main))
    if not viewdownloads == "disabled":
        list.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=showjobviews))
    return list


def showjobviews(reason, **kwargs):
    if reason == 0:
        try:
            pjopviews.gotSession(kwargs["session"])
        except:
            pass


class classJobManagerViews():

    def __init__(self):
        self.dialog = None

    def gotSession(self, session):
        global _session
        _session = session
        try:
            jobmanagerviews_keymap = THISPLUG+"/lib/jobs_keymap.xml"
            self.session = session
            global globalActionMap
            readKeymap(jobmanagerviews_keymap)
            # self.dialog = session.instantiateDialog(ScreenGrabber.ScreenGrabberView)
            # self.dialog.show()
            globalActionMap.actions['JobManagerView'] = self.ShowHide
            # self.ShowHide()
        except:
            return

    def ShowHide(self):
        # from  Plugins.Extensions.KodiLite.lib.download import viewdownloads
        # viewdownloads(self.session,THISPLUG)
        try:
            from Plugins.Extensions.KodiLite.lib.XBMCAddonsMediaExplorer import XBMCAddonsMediaExplorer
        except:
            from .lib.XBMCAddonsMediaExplorer import XBMCAddonsMediaExplorer
        _session.open(XBMCAddonsMediaExplorer)


pjopviews = classJobManagerViews()
