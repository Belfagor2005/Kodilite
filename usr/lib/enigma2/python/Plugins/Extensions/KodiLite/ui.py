#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.ConfigList import ConfigListScreen
from Components.FileList import FileList
from Components.Label import Label
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.config import ConfigSelection, ConfigYesNo
from Components.config import ConfigSubsection, ConfigInteger
from Components.config import config, ConfigText
from Components.config import getConfigListEntry
from Screens.Screen import Screen
from enigma import ePicLoad
from enigma import eSize
from enigma import eTimer
from enigma import gMainDC
from enigma import getDesktop
import skin
import sys

DM = False
try:
    from Tools.Directories import resolveFilename, pathExists, SCOPE_MEDIA, SCOPE_ACTIVE_SKIN
except:
    DM = True
    from Tools.Directories import resolveFilename, pathExists, SCOPE_MEDIA

if DM:
    from enigma import eRect
else:
    pass

PY3 = sys.version_info.major >= 3

if DM:
    from skin import componentSizes, TemplatedListFonts
else:
    pass


THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"


def getScale():
    return AVSwitch().getFramebufferScale()


def setPixmap(dest, ptr, scaleSize, aspectRatio):
    if scaleSize.isValid() and aspectRatio.isValid():
        pic_scale_size = ptr.size().scale(scaleSize, aspectRatio)
        dest_size = dest.getSize()
        dest_width = dest_size.width()
        dest_height = dest_size.height()
        pic_scale_width = pic_scale_size.width()
        pic_scale_height = pic_scale_size.height()

        if pic_scale_width == dest_width:
            dest_rect = eRect(0, (dest_height - pic_scale_height) / 2, pic_scale_width, pic_scale_height)
        else:
            dest_rect = eRect((dest_width - pic_scale_width) / 2, 0, pic_scale_width, pic_scale_height)
        dest.instance.setScale(1)
        dest.instance.setScaleDest(dest_rect)
    else:
        dest.instance.setScale(0)
    dest.instance.setPixmap(ptr)


config.pic = ConfigSubsection()
config.pic.framesize = ConfigInteger(default=30, limits=(5, 99))
config.pic.slidetime = ConfigInteger(default=10, limits=(1, 60))
config.pic.resize = ConfigSelection(default="1", choices=[("0", _("simple")), ("1", _("better"))])
config.pic.cache = ConfigYesNo(default=True)
config.pic.lastDir = ConfigText(default=resolveFilename(SCOPE_MEDIA))
config.pic.infoline = ConfigYesNo(default=True)
config.pic.loop = ConfigYesNo(default=True)
config.pic.bgcolor = ConfigSelection(default="#00000000", choices=[("#00000000", _("black")), ("#009eb9ff", _("blue")), ("#00ff5a51", _("red")), ("#00ffe875", _("yellow")), ("#0038FF48", _("green"))])
config.pic.textcolor = ConfigSelection(default="#0038FF48", choices=[("#00000000", _("black")), ("#009eb9ff", _("blue")), ("#00ff5a51", _("red")), ("#00ffe875", _("yellow")), ("#0038FF48", _("green"))])


class picscr(Screen):
    skin = """
        <screen name="picshow" position="center,center" size="560,440" title="WebMedia" >
                <ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
                <ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />
                <ePixmap pixmap="buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
                <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
                <widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
                <widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
                <widget source="label" render="Label" position="5,55" size="350,140" font="Regular;19" backgroundColor="#25062748" transparent="1"  />
                <widget name="thn" position="360,40" size="180,160" alphatest="on" />
                <widget name="filelist" position="5,205" zPosition="2" size="550,230" scrollbarMode="showOnDemand" />
        </screen>"""


class picscrdm(Screen):
    skin = """
            <screen name="picshow" position="center,80" size="1200,610" title="PicturePlayer">
                <ePixmap pixmap="skin_default/buttons/red.png" position="10,5" size="200,40"  />
                <ePixmap pixmap="skin_default/buttons/green.png" position="210,5" size="200,40"  />
                <ePixmap pixmap="skin_default/buttons/yellow.png" position="410,5" size="200,40"  />
                <ePixmap pixmap="skin_default/buttons/blue.png" position="610,5" size="200,40"  />
                <widget source="key_red" render="Label" position="10,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" />
                <widget source="key_green" render="Label" position="210,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" />
                <widget source="key_yellow" render="Label" position="410,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" />
                <widget source="key_blue" render="Label" position="610,5" size="200,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-2,-2" />
                <widget source="global.CurrentTime" render="Label" position="1130,12" size="60,25" font="Regular;22" halign="right">
                    <convert type="ClockToText">Default</convert>
                </widget>
                <widget source="global.CurrentTime" render="Label" position="820,12" size="300,25" font="Regular;22" halign="right">
                    <convert type="ClockToText">Format:%A %d. %B</convert>
                </widget>
                <eLabel position="10,50" size="1180,1" backgroundColor="grey" />
                <eLabel position="380,50" size="1,585" backgroundColor="grey" />
                <widget name="path" position="400,60" size="790,30" font="Regular;24"/>
                <eLabel position="380,90" size="810,1" backgroundColor="grey" />
                <widget source="label" render="Label" position="20,370" size="330,140" font="Regular;19"/>
                <widget name="thn" position="40,60" size="300,300" />
                <widget name="filelist" position="400,95" size="790,510" scrollbarMode="showOnDemand" />
            </screen>
            """


class picshow(Screen):

    def __init__(self, session, sname, mode, names, urls, picDir):
        Screen.__init__(self, session)
        if DM:
            self.skin = picscrdm.skin
        else:
            self.skin = picscr.skin
        self.sname = sname
        self.mode = mode
        self.names = names
        self.urls = urls
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MenuActions"],
                                    {
                                    "cancel": self.KeyExit,
                                    "red": self.KeyExit,
                                    "green": self.KeyGreen,
                                    "yellow": self.KeyYellow,
                                    "menu": self.KeyMenu,
                                    "ok": self.KeyOk
                                    }, -1)

        self["key_red"] = StaticText(_("Close"))
        self["key_green"] = StaticText(_("Thumbnails"))
        self["key_yellow"] = StaticText("")
        self["key_blue"] = StaticText(_("Setup"))
        self["label"] = StaticText("")
        self["thn"] = Pixmap()
        currDir = config.pic.lastDir.value
        if not pathExists(currDir):
            currDir = "/"
        print("In ui.py currDir = ", currDir)
        currDir = picDir + "/"
        print("In ui.py currDir 3 = ", currDir)
        self["path"] = Label(currDir)
        self.filelist = FileList(currDir, matchingPattern=r"(?i)^.*\.(jpeg|jpg|jpe|png|bmp|gif)")
        self["filelist"] = self.filelist
        self["filelist"].onSelectionChanged.append(self.selectionChanged)
        self.ThumbTimer = eTimer()
        try:
            self.ThumbTimer_conn = self.ThumbTimer.timeout.connect(self.showThumb)
        except AttributeError:
            self.ThumbTimer.callback.append(self.showThumb)
        self.picload = ePicLoad()
        try:
            self.picload_conn = self.picload.PictureData.connect(self.showPic)
        except:
            self.picload.PictureData.get().append(self.showPic)
        self.onLayoutFinish.append(self.setConf)

    def setConf1(self):
        self.setTitle(_("PicturePlayer"))
        sc = getScale()
        self._aspectRatio = eSize(sc[0], sc[1])
        self._scaleSize = self["thn"].instance.size()
        # 0=Width 1=Height 2=Aspect 3=use_cache 4=resize_type 5=Background(#AARRGGBB)
        params = (self._scaleSize.width(), self._scaleSize.height(), sc[0], sc[1], config.pic.cache.value, int(config.pic.resize.value), "#00000000")
        self.picload.setPara(params)

    def showPic(self, picInfo=""):
        ptr = self.picload.getData()
        if ptr is not None:
            self["thn"].instance.setPixmap(ptr.__deref__())
            self["thn"].show()

        text = picInfo.split('\n', 1)
        self["label"].setText(text[1])
        self["key_yellow"].setText(_("Exif"))

    def showThumb(self):
        if not self.filelist.canDescent():
            if self.filelist.getCurrentDirectory() and self.filelist.getFilename():
                if self.picload.getThumbnail(self.filelist.getCurrentDirectory() + self.filelist.getFilename()) == 1:
                    self.ThumbTimer.start(500, True)

    def selectionChanged(self):
        if not self.filelist.canDescent():
            self.ThumbTimer.start(500, True)
        else:
            self["label"].setText("")
            self["thn"].hide()
            self["key_yellow"].setText("")

    def KeyGreen(self):
        if PY3:
            return
        else:
            if DM:
                self.session.openWithCallback(self.callbackView, Pic_ThumbDM, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory(), self.sname, self.mode, self.names, self.urls)
            else:
                self.session.openWithCallback(self.callbackView, Pic_Thumb, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory(), self.sname, self.mode, self.names, self.urls)

    def KeyYellow(self):
        if not self.filelist.canDescent():
            self.session.open(Pic_Exif, self.picload.getInfo(self.filelist.getCurrentDirectory() + self.filelist.getFilename()))

    def KeyMenu(self):
        self.session.openWithCallback(self.setConf, Pic_Setup)

    def KeyOk(self):
        print("In ui.py self.filelist.getFileList() = ", self.filelist.getFileList())
        idx = self.filelist.getSelectionIndex()
        print("In ui.py idx = ", idx)
        print("In ui.py self.filelist.getFileList()[idx] = ", self.filelist.getFileList()[idx])
        name = self.filelist.getFileList()[idx][0][0]
        print("In ui.py name = ", name)
        n1 = name.rfind(".")
        name2 = name[:n1]
        print("In ui.py name2 = ", name2)
        np = len(self.names)
        i = 0
        idx2 = 0
        while i < np:
            if name2 in self.names[i]:
                idx2 = i
                break
            i += 1
        print("In ui.py idx2 = ", idx2)
        url = self.urls[idx2]

        if "adult" in self.sname.lower():
            tname = self.sname.replace("(Adult)", "")
            path = THISPLUG + "/plugins/Adult/" + tname + "/default.py"
        else:
            tname = self.sname
            path = THISPLUG + "/plugins/General/" + tname + "/default.py"
        print("ui.py path =", path)
        if PY3:
            modl = tname.lower()
            import importlib.util
            spec = importlib.util.spec_from_file_location(modl, path)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            foo.Main(self.session, self.sname, mode=self.mode, name=name2, url=url)
        else:
            modl = name.lower()
            import imp
            foo = imp.load_source(modl, path)
            foo.Main(self.session, self.sname, mode=self.mode, name=name2, url=url)

    def setConf(self, retval=None):
        self.setTitle(_("Picture player"))
        sc = getScale()
        # 0=Width 1=Height 2=Aspect 3=use_cache 4=resize_type 5=Background(#AARRGGBB)
        self.picload.setPara((self["thn"].instance.size().width(), self["thn"].instance.size().height(), sc[0], sc[1], config.pic.cache.value, int(config.pic.resize.value), "#00000000"))

    def callbackView(self, val=0):
        if val > 0:
            self.filelist.moveToIndex(val)

    def KeyExit(self):
        del self.picload
        if self.filelist.getCurrentDirectory() is None:
            config.pic.lastDir.setValue("/")
        else:
            config.pic.lastDir.setValue(self.filelist.getCurrentDirectory())
        config.pic.save()
        self.close()


class Pic_Setup(Screen, ConfigListScreen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.setTitle(_("PicturePlayer"))
        # for the skin: first try MediaPlayerSettings, then Setup, this allows individual skinning
        self.skinName = ["PicturePlayerSetup", "Setup"]
        self.setup_title = _("Settings")
        self.onChangedEntry = []
        self.session = session
        ConfigListScreen.__init__(self, [], session=session, on_change=self.changedEntry)
        self["actions"] = ActionMap(["SetupActions", "MenuActions"],
                                    {"cancel": self.keyCancel,
                                     "save": self.keySave,
                                     "ok": self.keySave,
                                     "menu": self.closeRecursive}, -2)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("OK"))
        self["HelpWindow"] = Pixmap()
        self["HelpWindow"].hide()
        self["footnote"] = StaticText("")
        self["description"] = StaticText("")
        self.createSetup()
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(self.setup_title)

    def createSetup(self):
        setup_list = [getConfigListEntry(_("Slide show interval (sec.)"), config.pic.slidetime),
                      getConfigListEntry(_("Scaling mode"), config.pic.resize),
                      getConfigListEntry(_("Cache thumbnails"), config.pic.cache),
                      getConfigListEntry(_("Show info line"), config.pic.infoline),
                      getConfigListEntry(_("Frame size in full view"), config.pic.framesize),
                      getConfigListEntry(_("Slide picture in loop"), config.pic.loop),
                      getConfigListEntry(_("Background color"), config.pic.bgcolor),
                      getConfigListEntry(_("Text color"), config.pic.textcolor),
                      getConfigListEntry(_("Fulview resulution"), config.usage.pic_resolution)]
        self["config"].list = setup_list
        self["config"].l.setList(setup_list)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)

    def keyRight(self):
        ConfigListScreen.keyRight(self)

    def keyCancel(self):
        self.close()

    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    def getCurrentEntry(self):
        return self["config"].getCurrent()[0]

    def getCurrentValue(self):
        return str(self["config"].getCurrent()[1].getText())

    def createSummary(self):
        from Screens.Setup import SetupSummary
        return SetupSummary


class Pic_Exif(Screen):
    skin = """
            <screen name="Pic_Exif" position="center,center" size="560,360" title="Info" >
                <ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
                <widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
                <widget source="menu" render="Listbox" position="5,50" size="550,310" scrollbarMode="showOnDemand" selectionDisabled="1" >
                    <convert type="TemplatedMultiContent">
                    {
                    "template": [  MultiContentEntryText(pos = (5, 5), size = (250, 30), flags = RT_HALIGN_LEFT, text = 0), MultiContentEntryText(pos = (260, 5), size = (290, 30), flags = RT_HALIGN_LEFT, text = 1)],
                    "fonts": [gFont("Regular", 20)],
                    "itemHeight": 30
                    }
                    </convert>
                </widget>
            </screen>"""

    def __init__(self, session, exiflist):
        Screen.__init__(self, session)
        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
                                    {"cancel": self.close}, -1)
        self["key_red"] = StaticText(_("Close"))
        exifdesc = [_("filename") + ':', "EXIF-Version:", "Make:", "Camera:", "Date/Time:", "Width / Height:", "Flash used:", "Orientation:", "User Comments:", "Metering Mode:", "Exposure Program:", "Light Source:", "CompressedBitsPerPixel:", "ISO Speed Rating:", "X-Resolution:", "Y-Resolution:", "Resolution Unit:", "Brightness:", "Exposure Time:", "Exposure Bias:", "Distance:", "CCD-Width:", "ApertureFNumber:"]
        list = []

        for x in list(range(len(exiflist))):
            if x > 0:
                list.append((exifdesc[x], exiflist[x]))
            else:
                name = exiflist[x].split('/')[-1]
                list.append((exifdesc[x], name))
        self["menu"] = List(list)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle(_("Info"))


T_INDEX = 0
T_FRAME_POS = 1
T_PAGE = 2
T_NAME = 3
T_FULL = 4


class Pic_ThumbDM(Screen):
    SKIN_COMPONENT_KEY = "PicturePlayer"
    SKIN_COMPONENT_DESCRIPTION_SIZE = "thumbDescriptionSize"
    SKIN_COMPONENT_MARGIN = "thumpMargin"
    SKIN_COMPONENT_SPACE_X = "thumbSpaceX"
    SKIN_COMPONENT_SPACE_Y = "thumbSpaceY"
    SKIN_COMPONENT_THUMP_X = "thumbX"
    SKIN_COMPONENT_THUMP_Y = "thumbY"

    def __init__(self, session, piclist, lastindex, path, sname, mode, names, urls):
        self.sname = sname
        self.mode = mode
        self.names = names
        self.urls = urls

        self.textcolor = config.pic.textcolor.value
        self.color = config.pic.bgcolor.value

        tlf = TemplatedListFonts()
        self._labelFontSize = tlf.size(tlf.SMALLER)
        self._labelFontFace = tlf.face(tlf.SMALLER)

        sizes = componentSizes[Pic_ThumbDM.SKIN_COMPONENT_KEY]
        self._descSize = sizes.get(Pic_ThumbDM.SKIN_COMPONENT_DESCRIPTION_SIZE, 35)
        self._margin = sizes.get(Pic_ThumbDM.SKIN_COMPONENT_MARGIN, 10)
        self._spaceX = sizes.get(Pic_ThumbDM.SKIN_COMPONENT_SPACE_X, 55)
        self._spaceY = sizes.get(Pic_ThumbDM.SKIN_COMPONENT_SPACE_Y, 30)
        self._thumbX = sizes.get(Pic_ThumbDM.SKIN_COMPONENT_THUMP_X, 190)
        self._thumbY = sizes.get(Pic_ThumbDM.SKIN_COMPONENT_THUMP_Y, 200)

        size_w = getDesktop(0).size().width()
        size_h = getDesktop(0).size().height()
        self.thumbsX = size_w / (self._spaceX + self._thumbX)  # thumbnails in X
        self.thumbsY = size_h / (self._spaceY + self._thumbY)  # thumbnails in Y
        self.thumbsC = self.thumbsX * self.thumbsY  # all thumbnails

        self.positionlist = []
        skincontent = ""

        posX = -1
        for x in range(self.thumbsC):
            posY = x / self.thumbsX
            posX += 1
            if posX >= self.thumbsX:
                posX = 0

            absX = self._spaceX + (posX * (self._spaceX + self._thumbX))
            absY = self._spaceY + (posY * (self._spaceY + self._thumbY))
            self.positionlist.append((absX, absY))
            absX += self._margin
            absY += self._margin
            skincontent += '<widget source="label%s" render="Label" position="%s,%s" size="%s,%s" font="%s;%s" valign="top" halign="center" zPosition="2" transparent="1" foregroundColor="%s"/>' % (x, absX, absY + self._thumbY - self._descSize, self._thumbX, self._descSize, self._labelFontFace, self._labelFontSize, self.textcolor)
            skincontent += '<widget name="thumb%s" position="%s,%s" size="%s,%s" zPosition="2" transparent="1" />' % (x, absX, absY, self._thumbX, self._thumbY - self._descSize - self._margin)

        self.doubleMargin = self._margin * 2
        self.skin = """<screen position="0,0" size="{0},{1}" flags="wfNoBorder" >
                        <eLabel position="0,0" zPosition="0" size="{0},{1}" backgroundColor="{2}" /> \
                        <widget name="frame" position="35,30" size="{3},{4}" pixmap="pic_frame.png" zPosition="1" alphatest="on" />{5}
                        </screen>""".format(size_w, size_h, self.color, self._thumbX + self.doubleMargin, self._thumbY + self.doubleMargin, skincontent)

        Screen.__init__(self, session)

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"],
                                    {"cancel": self.Exit,
                                     "ok": self.KeyOk,
                                     "left": self.key_left,
                                     "right": self.key_right,
                                     "up": self.key_up,
                                     "down": self.key_down,
                                     "showEventInfo": self.StartExif}, -1)

        self["frame"] = MovingPixmap()
        for x in range(self.thumbsC):
            self["label" + str(x)] = StaticText()
            self["thumb" + str(x)] = Pixmap()

        self.Thumbnaillist = []
        self.filelist = []
        self.currPage = -1
        self.dirlistcount = 0
        self.path = path

        index = 0
        framePos = 0
        Page = 0
        for x in piclist:
            if x[0][1] is False:
                self.filelist.append((index, framePos, Page, x[0][0],  path + x[0][0]))
                index += 1
                framePos += 1
                if framePos > (self.thumbsC - 1):
                    framePos = 0
                    Page += 1
            else:
                self.dirlistcount += 1

        self.maxentry = len(self.filelist) - 1
        self.index = lastindex - self.dirlistcount
        if self.index < 0:
            self.index = 0
        self.picload = ePicLoad()
        self.picload_conn = self.picload.PictureData.connect(self.showPic)
        self.onLayoutFinish.append(self.setPicloadConf)
        self.ThumbTimer = eTimer()
        self.ThumbTimer_conn = self.ThumbTimer.timeout.connect(self.showPic)

    def setPicloadConf(self):
        sc = getScale()
        self._aspectRatio = eSize(sc[0], sc[1])
        self._scaleSize = self["thumb0"].instance.size()
        self.picload.setPara([self._scaleSize.width(), self._scaleSize.height(), sc[0], sc[1], config.pic.cache.value, int(config.pic.resize.value), self.color])
        self.paintFrame()

    def paintFrame(self):
        # print "index=" + str(self.index)
        if self.maxentry < self.index or self.index < 0:
            return
        pos = self.positionlist[self.filelist[self.index][T_FRAME_POS]]
        self["frame"].moveTo(pos[0], pos[1], 1)
        self["frame"].startMoving()
        if self.currPage != self.filelist[self.index][T_PAGE]:
            self.currPage = self.filelist[self.index][T_PAGE]
            self.newPage()

    def newPage(self):
        self.Thumbnaillist = []
        # clear Labels and Thumbnail
        for x in range(self.thumbsC):
            self["label" + str(x)].setText("")
            self["thumb" + str(x)].hide()
        for x in self.filelist:
            if x[T_PAGE] == self.currPage:
                self["label" + str(x[T_FRAME_POS])].setText("(" + str(x[T_INDEX] + 1) + ") " + x[T_NAME])
                self.Thumbnaillist.append([0, x[T_FRAME_POS], x[T_FULL]])
        self.showPic()

    def showPic(self, picInfo=""):
        for x in range(len(self.Thumbnaillist)):
            if self.Thumbnaillist[x][0] == 0:
                if self.picload.getThumbnail(self.Thumbnaillist[x][2]) == 1:  # zu tun probier noch mal
                    self.ThumbTimer.start(config.pic.thumbDelay.value, True)
                else:
                    self.Thumbnaillist[x][0] = 1
                break
            elif self.Thumbnaillist[x][0] == 1:
                self.Thumbnaillist[x][0] = 2
                ptr = self.picload.getData()
                if ptr is not None:
                    setPixmap(self["thumb" + str(self.Thumbnaillist[x][1])], ptr, self._scaleSize, self._aspectRatio)
                    self["thumb" + str(self.Thumbnaillist[x][1])].show()

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_right(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def key_up(self):
        self.index -= self.thumbsX
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_down(self):
        self.index += self.thumbsX
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def StartExif(self):
        if self.maxentry < 0:
            return
        self.session.open(Pic_Exif, self.picload.getInfo(self.filelist[self.index][T_FULL]))

    def KeyOkX(self):
        if self.maxentry < 0:
            return
        self.old_index = self.index
        self.session.openWithCallback(self.callbackView, Pic_Full_View, self.filelist, self.index, self.path)

    def KeyOk(self):
        idx = self.index
        print("In ui.py idx = ", idx)
        print("In ui.py self.filelist[idx] = ", self.filelist[idx])
        name = self.filelist[idx][3]
        print("In ui.py name = ", name)
        n1 = name.rfind(".")
        name2 = name[:n1]
        print("In ui.py name2 = ", name2)
        np = len(self.names)
        i = 0
        idx2 = 0
        while i < np:
            if name2 in self.names[i]:
                idx2 = i
                break
            i += 1
        print("In ui.py idx2 = ", idx2)
        url = self.urls[idx2]

        if "adult" in self.sname.lower():
            tname = self.sname.replace("(Adult)", "")
            path = THISPLUG + "/plugins/Adult/" + tname + "/default.py"
        else:
            tname = self.sname
            path = THISPLUG + "/plugins/General/" + tname + "/default.py"
        print("Mainscreen2 path =", path)
        if PY3:
            modl = tname.lower()
            import importlib.util
            spec = importlib.util.spec_from_file_location(modl, path)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            foo.Main(self.session, self.sname, mode=self.mode, name=name2, url=url)
        else:
            modl = name.lower()
            import imp
            foo = imp.load_source(modl, path)
            foo.Main(self.session, self.sname, mode=self.mode, name=name2, url=url)

    def callbackView(self, val=0):
        self.index = val
        if self.old_index != self.index:
            self.paintFrame()

    def Exit(self):
        del self.picload_conn
        del self.picload
        self.close(self.index + self.dirlistcount)


class Pic_Thumb(Screen):
    def __init__(self, session, piclist, lastindex, path, sname, mode, names, urls):
        print("In pitureplayer piclist = ", piclist)
        print("In pitureplayer lastindex = ", lastindex)
        print("In pitureplayer path = ", path)
        print("In pitureplayer 9 ")

        self.sname = sname
        self.mode = mode
        self.names = names
        self.urls = urls

#        def __init__(self, session, piclist, lastindex, path):

        self.textcolor = config.pic.textcolor.value
        self.color = config.pic.bgcolor.value
        self.spaceX, self.picX, self.spaceY, self.picY, textsize, thumtxt = skin.parameters.get("PicturePlayerThumb", (35, 190, 30, 200, 20, 14))
        try:
            pic_frame = resolveFilename(SCOPE_ACTIVE_SKIN, "icons/pic_frame.png")
        except:
            pic_frame = None

        self.size_w = getDesktop(0).size().width()
        self.size_h = getDesktop(0).size().height()
        self.thumbsX = self.size_w / (self.spaceX + self.picX)  # thumbnails in X
        print("KD self.thumbsX =", self.thumbsX)
        self.thumbsY = self.size_h / (self.spaceY + self.picY)  # thumbnails in Y
        print("KD self.thumbsY =", self.thumbsY)
        self.thumbsC = self.thumbsX * self.thumbsY  # all thumbnails
        self.thumbsC = int(self.thumbsC)
        print("KD self.thumbsC =", self.thumbsC)
        self.positionlist = []
        skincontent = ""
        posX = -1
#                self.thumbsC = 17
        r = range(self.thumbsC)
        print("KodIlite r =", r)
        l = list(range(self.thumbsC))
        print("KodIlite l =", l)
        for x in list(range(self.thumbsC)):
            posY = x / self.thumbsX
            posX += 1
            if posX >= self.thumbsX:
                posX = 0
            absX = self.spaceX + (posX * (self.spaceX + self.picX))
            absY = self.spaceY + (posY * (self.spaceY + self.picY))
            self.positionlist.append((absX, absY))
            skincontent += "<widget source=\"label" + str(x) + "\" render=\"Label\" position=\"" + str(absX + 5) + "," + str(absY + self.picY - textsize) + "\" size=\"" + str(self.picX - 10) + "," + str(textsize) \
                + "\" font=\"Regular;" + str(thumtxt) + "\" zPosition=\"2\" transparent=\"1\" noWrap=\"1\" foregroundColor=\"" + self.textcolor + "\" />"
            skincontent += "<widget name=\"thumb" + str(x) + "\" position=\"" + str(absX + 5) + "," + str(absY + 5) + "\" size=\"" + str(self.picX - 10) + "," + str(self.picY - (textsize * 2)) + "\" zPosition=\"2\" transparent=\"1\" alphatest=\"on\" />"
        # Screen, backgroundlabel and MovingPixmap
        if pic_frame:
            self.skin = "<screen position=\"0,0\" size=\"" + str(self.size_w) + "," + str(self.size_h) + "\" flags=\"wfNoBorder\" > \
                <eLabel position=\"0,0\" zPosition=\"0\" size=\"" + str(self.size_w) + "," + str(self.size_h) + "\" backgroundColor=\"" + self.color + "\" />" \
                + "<widget name=\"frame\" position=\"" + str(self.spaceX) + "," + str(self.spaceY) + "\" size=\"" + str(self.picX) + "," + str(self.picY) + "\" pixmap=\"" + pic_frame + "\" zPosition=\"1\" alphatest=\"on\" />" \
                + skincontent + "</screen>"
        else:
            self.skin = """<screen position="0,0" size="{0},{1}" flags="wfNoBorder" >
                <eLabel position="0,0" zPosition="0" size="{0},{1}" backgroundColor="{2}" /> \
                <widget name="frame" position="35,30" size="{3},{4}" pixmap="pic_frame.png" zPosition="1" alphatest="on" />{5}</screen>""".format(self.size_w, self.size_h, self.color, self._thumbX + self.doubleMargin, self._thumbY + self.doubleMargin, skincontent)

        Screen.__init__(self, session)
        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"],
                                    {"cancel": self.Exit,
                                     "ok": self.KeyOk,
                                     "left": self.key_left,
                                     "right": self.key_right,
                                     "up": self.key_up,
                                     "down": self.key_down,
                                     "showEventInfo": self.StartExif}, -1)
        self["frame"] = MovingPixmap()
        for x in list(range(self.thumbsC)):
            self["label" + str(x)] = StaticText()
            self["thumb" + str(x)] = Pixmap()

        self.Thumbnaillist = []
        self.filelist = []
        self.currPage = -1
        self.dirlistcount = 0
        self.path = path
        index = 0
        framePos = 0
        Page = 0
        for x in piclist:
            if not x[0][1]:
                self.filelist.append((index, framePos, Page, x[0][0], path + x[0][0]))
                index += 1
                framePos += 1
                if framePos > (self.thumbsC - 1):
                    framePos = 0
                    Page += 1
            else:
                self.dirlistcount += 1

        self.maxentry = len(self.filelist) - 1
        self.index = lastindex - self.dirlistcount
        if self.index < 0:
            self.index = 0

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showPic)

        if DM:
            self.onLayoutFinish.append(self.setConf)
        else:
            self.onLayoutFinish.append(self.setPicloadConf)
        self.ThumbTimer = eTimer()
        self.ThumbTimer.callback.append(self.showPic)

    def setConf(self):
        self.setTitle(_("PicturePlayer"))
        sc = getScale()
        self._aspectRatio = eSize(sc[0], sc[1])
        self._scaleSize = self["thn"].instance.size()
        # 0=Width 1=Height 2=Aspect 3=use_cache 4=resize_type 5=Background(#AARRGGBB)
        params = (self._scaleSize.width(), self._scaleSize.height(), sc[0], sc[1], config.pic.cache.value, int(config.pic.resize.value), "#00000000")
        self.picload.setPara(params)

    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara([self["thumb0"].instance.size().width(), self["thumb0"].instance.size().height(), sc[0], sc[1], config.pic.cache.value, int(config.pic.resize.value), self.color])
        self.paintFrame()

    def paintFrame(self):
        # print "index=" + str(self.index)
        if self.maxentry < self.index or self.index < 0:
            return
        pos = self.positionlist[self.filelist[self.index][T_FRAME_POS]]
        self["frame"].moveTo(pos[0], pos[1], 1)
        self["frame"].startMoving()
        if self.currPage != self.filelist[self.index][T_PAGE]:
            self.currPage = self.filelist[self.index][T_PAGE]
            self.newPage()

    def newPage(self):
        self.Thumbnaillist = []
        for x in list(range(self.thumbsC)):
            self["label" + str(x)].setText("")
            self["thumb" + str(x)].hide()
        for x in self.filelist:
            if x[T_PAGE] == self.currPage:
                self["label" + str(x[T_FRAME_POS])].setText("(" + str(x[T_INDEX] + 1) + ") " + x[T_NAME])
                self.Thumbnaillist.append([0, x[T_FRAME_POS], x[T_FULL]])
        self.showPic()

    def showPic(self, picInfo=""):
        for x in list(range(len(self.Thumbnaillist))):
            if self.Thumbnaillist[x][0] == 0:
                if self.picload.getThumbnail(self.Thumbnaillist[x][2]) == 1:  # zu tun probier noch mal
                    self.ThumbTimer.start(500, True)
                else:
                    self.Thumbnaillist[x][0] = 1
                break
            elif self.Thumbnaillist[x][0] == 1:
                self.Thumbnaillist[x][0] = 2
                ptr = self.picload.getData()
                if ptr is not None:
                    self["thumb" + str(self.Thumbnaillist[x][1])].instance.setPixmap(ptr.__deref__())
                    self["thumb" + str(self.Thumbnaillist[x][1])].show()

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_right(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def key_up(self):
        self.index -= self.thumbsX
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_down(self):
        self.index += self.thumbsX
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def StartExif(self):
        if self.maxentry < 0:
            return
        self.session.open(Pic_Exif, self.picload.getInfo(self.filelist[self.index][T_FULL]))

    def KeyOkX(self):
        if self.maxentry < 0:
            return
        self.old_index = self.index
        self.session.openWithCallback(self.callbackView, Pic_Full_View, self.filelist, self.index, self.path)

    def KeyOk(self):
        idx = self.index
        print("In ui.py idx = ", idx)
        print("In ui.py self.filelist[idx] = ", self.filelist[idx])
        name = self.filelist[idx][3]
        print("In ui.py name = ", name)
        n1 = name.rfind(".")
        name2 = name[:n1]
        print("In ui.py name2 = ", name2)
        np = len(self.names)
        i = 0
        idx2 = 0
        while i < np:
            if name2 in self.names[i]:
                idx2 = i
                break
            i += 1
        print("In ui.py idx2 = ", idx2)
        url = self.urls[idx2]
        if "adult" in self.sname.lower():
            tname = self.sname.replace("(Adult)", "")
            path = THISPLUG + "/plugins/Adult/" + tname + "/default.py"
        else:
            tname = self.sname
            path = THISPLUG + "/plugins/General/" + tname + "/default.py"
        print("Mainscreen2 path =", path)
        if PY3:
            modl = tname.lower()
            import importlib.util
            spec = importlib.util.spec_from_file_location(modl, path)
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            foo.Main(self.session, self.sname, mode=self.mode, name=name2, url=url)
        else:
            modl = name.lower()
            import imp
            foo = imp.load_source(modl, path)
            foo.Main(self.session, self.sname, mode=self.mode, name=name2, url=url)

    def callbackView(self, val=0):
        self.index = val
        if self.old_index != self.index:
            self.paintFrame()

    def Exit(self):
        del self.picload
        self.close(self.index + self.dirlistcount)

# ---------------------------------------------------------------------------


class Pic_Full_View(Screen):
    def __init__(self, session, filelist, index, path):

        self.textcolor = config.pic.textcolor.value
        self.bgcolor = config.pic.bgcolor.value
        space = config.pic.framesize.value

        self.size_w = size_w = getDesktop(0).size().width()
        self.size_h = size_h = getDesktop(0).size().height()

        if config.usage.pic_resolution.value and (size_w, size_h) != eval(config.usage.pic_resolution.value):
            (size_w, size_h) = eval(config.usage.pic_resolution.value)
            gMainDC.getInstance().setResolution(size_w, size_h)
            getDesktop(0).resize(eSize(size_w, size_h))

        self.skin = "<screen position=\"0,0\" size=\"" + str(size_w) + "," + str(size_h) + "\" flags=\"wfNoBorder\" > \
                <eLabel position=\"0,0\" zPosition=\"0\" size=\"" + str(size_w) + "," + str(size_h) + "\" backgroundColor=\"" + self.bgcolor + "\" /><widget name=\"pic\" position=\"" + str(space) + "," + str(space) + "\" size=\"" + str(size_w - (space * 2)) + "," + str(size_h - (space * 2)) + "\" zPosition=\"1\" alphatest=\"on\" /> \
                <widget name=\"point\" position=\"" + str(space + 5) + "," + str(space + 2) + "\" size=\"20,20\" zPosition=\"2\" pixmap=\"skin_default/icons/record.png\" alphatest=\"on\" /> \
                <widget name=\"play_icon\" position=\"" + str(space + 25) + "," + str(space + 2) + "\" size=\"20,20\" zPosition=\"2\" pixmap=\"skin_default/icons/ico_mp_play.png\"  alphatest=\"on\" /> \
                <widget source=\"file\" render=\"Label\" position=\"" + str(space + 45) + "," + str(space) + "\" size=\"" + str(size_w - (space * 2) - 50) + ",25\" font=\"Regular;20\" borderWidth=\"1\" borderColor=\"#000000\" halign=\"left\" foregroundColor=\"" + self.textcolor + "\" zPosition=\"2\" noWrap=\"1\" transparent=\"1\" /></screen>"

        Screen.__init__(self, session)

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"],
                                    {"cancel": self.Exit,
                                     "green": self.PlayPause,
                                     "yellow": self.PlayPause,
                                     "blue": self.nextPic,
                                     "red": self.prevPic,
                                     "left": self.prevPic,
                                     "right": self.nextPic,
                                     "showEventInfo": self.StartExif}, -1)
        self["point"] = Pixmap()
        self["pic"] = Pixmap()
        self["play_icon"] = Pixmap()
        self["file"] = StaticText(_("please wait, loading picture..."))
        self.old_index = 0
        self.filelist = []
        self.lastindex = index
        self.currPic = []
        self.shownow = True
        self.dirlistcount = 0

        for x in filelist:
            if len(filelist[0]) == 3:  # orig. filelist
                if not x[0][1]:
                    self.filelist.append(path + x[0][0])
                else:
                    self.dirlistcount += 1
            elif len(filelist[0]) == 2:  # scanlist
                if not x[0][1]:
                    self.filelist.append(x[0][0])
                else:
                    self.dirlistcount += 1
            else:  # thumbnaillist
                self.filelist.append(x[T_FULL])

        self.maxentry = len(self.filelist) - 1
        self.index = index - self.dirlistcount
        if self.index < 0:
            self.index = 0

        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.finish_decode)

        self.slideTimer = eTimer()
        self.slideTimer.callback.append(self.slidePic)

        if self.maxentry >= 0:
            self.onLayoutFinish.append(self.setPicloadConf)

    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara([self["pic"].instance.size().width(), self["pic"].instance.size().height(), sc[0], sc[1], 0, int(config.pic.resize.value), self.bgcolor])

        self["play_icon"].hide()
        if not config.pic.infoline.value:
            self["file"].setText("")
        self.start_decode()

    def ShowPicture(self):
        if self.shownow and len(self.currPic):
            self.shownow = False
            if config.pic.infoline.value:
                self["file"].setText(self.currPic[0])
            else:
                self["file"].setText("")
            self.lastindex = self.currPic[1]
            self["pic"].instance.setPixmap(self.currPic[2].__deref__())
            self.currPic = []

            self.next()
            self.start_decode()

    def finish_decode(self, picInfo=""):
        self["point"].hide()
        ptr = self.picload.getData()
        if ptr is not None:
            text = ""
            try:
                text = picInfo.split('\n', 1)
                text = "(" + str(self.index + 1) + "/" + str(self.maxentry + 1) + ") " + text[0].split('/')[-1]
            except:
                pass
            self.currPic = []
            self.currPic.append(text)
            self.currPic.append(self.index)
            self.currPic.append(ptr)
            self.ShowPicture()

    def start_decode(self):
        self.picload.startDecode(self.filelist[self.index])
        self["point"].show()

    def next(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry

    def slidePic(self):
        print("slide to next Picture index=" + str(self.lastindex))
        if config.pic.loop.value is False and self.lastindex == self.maxentry:
            self.PlayPause()
        self.shownow = True
        self.ShowPicture()

    def PlayPause(self):
        if self.slideTimer.isActive():
            self.slideTimer.stop()
            self["play_icon"].hide()
        else:
            self.slideTimer.start(config.pic.slidetime.value * 1000)
            self["play_icon"].show()
            self.nextPic()

    def prevPic(self):
        self.currPic = []
        self.index = self.lastindex
        self.prev()
        self.start_decode()
        self.shownow = True

    def nextPic(self):
        self.shownow = True
        self.ShowPicture()

    def StartExif(self):
        if self.maxentry < 0:
            return
        self.session.open(Pic_Exif, self.picload.getInfo(self.filelist[self.lastindex]))

    def Exit(self):
        del self.picload
        if config.usage.pic_resolution.value and (self.size_w, self.size_h) != eval(config.usage.pic_resolution.value):
            gMainDC.getInstance().setResolution(self.size_w, self.size_h)
            getDesktop(0).resize(eSize(self.size_w, self.size_h))
        self.close(self.lastindex + self.dirlistcount)
