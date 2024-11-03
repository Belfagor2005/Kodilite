#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
from . import Utils
# from Plugins.Extensions.KodiLite.adnutils import *
# ###########20220115#########################

THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
LATEST = " "


def updstart2():
    url2 = "https://ytdl-org.github.io/youtube-dl/download.html"
    xdest = "/tmp/down.txt"
    f = Utils.getUrlresp(url2)
    p = f.read()
    f1 = open(xdest, "wb")
    f1.write(p)
    f1.close()
    fplug = ""
    getdown(fplug)


def getdown(fplug):
    fpage = open("/tmp/down.txt", "r").read()
    txt = fpage
    n1 = txt.find('<h2><a href=', 0)
    n2 = txt.find('">', (n1 + 15))
    n3 = txt.find('</a>', (n2 + 4))
    latest = txt[(n2 + 2):n3]
    global LATEST
    LATEST = latest
    tfile = THISPLUG + "/scripts/script.module.ytdl/lib/youtube_dl/version.py"
    f = open(tfile, "r")
    txt = f.read()
    n1 = txt.find('__version__ = ', 0)
    n2 = txt.find("'", (n1 + 18))
    version = txt[(n1 + 15):n2]
    f.close()
    newvers = latest
    if newvers == " ":
        upd_done()
    elif newvers != version:
        dest = "/tmp/youtube-dl.zip"
        xfile = "https://yt-dl.org/downloads/latest/youtube-dl"
        f = Utils.getUrlresp(xfile)
        p = f.read()
        f1 = open(dest, "wb")
        f1.write(p)
        f1.close()
        fplug = ""
        ytdl(fplug)
    else:
        upd_done()


def showError(error):
    cmd = "wget https://yt-dl.org/downloads/" + LATEST + "/youtube-dl -O /tmp/youtube-dl.zip"
    os.system(cmd)
    ytdl()


def ytdl(fplug=" "):
    try:
        fdest = THISPLUG + "/scripts/script.module.ytdl/lib"
        import zipfile
        zip_ref = zipfile.ZipFile('/tmp/youtube-dl.zip', 'r')
        zip_ref.extractall(fdest)
        zip_ref.close()
        upd_done()
    except:
        upd_done()


def findmax(items=[]):
    maxitem = max(items)
    return maxitem


def findmaxX(match=[]):
    A = []
    B = []
    C = []
    D = []
    # imax = 0
    for item in match:
        item = item.replace("%7E", "~")
        x = item.split(".")
        A.append(int(x[0]))
    lx = len(x)
    Amax = max(A)
    i1 = 0
    for a in A:
        if a == Amax:
            # imax = i1
            break
        i1 += 1

    maxitem = str(Amax)
    if lx > 1:
        for item in match:
            x = item.split(".")
            if int(x[0]) == int(Amax):
                B.append(x[1])
            else:
                B.append(int('0'))
        Bmax = max(B)
        i2 = 0
        for b in B:
            if b == Bmax:
                # imax = i2
                break
            i2 += 1
        maxitem = str(Amax) + "." + str(Bmax)
    if lx > 2:
        for item in match:
            x = item.split(".")
            if (int(x[0]) == int(Amax)) and (int(x[1]) == int(Bmax)):
                C.append(x[2])
            else:
                C.append(int('0'))
        Cmax = max(C)
        i3 = 0
        for c in C:
            if c == Cmax:
                # imax = i3
                break
            i3 += 1
        maxitem = str(Amax) + "." + str(Bmax) + "." + str(Cmax)
    if lx > 3:
        for item in match:
            x = item.split(".")
            if (int(x[0]) == int(Amax)) and (int(x[1]) == int(Bmax)) and ((x[2]) == Cmax):
                D.append(x[3])
            else:
                D.append(int('0'))
        Dmax = max(D)
        i4 = 0
        for d in D:
            if d == Dmax:
                # imax = i4
                break
            i4 += 1
        maxitem = str(Amax) + "." + str(Bmax) + "." + str(Cmax) + "." + str(Dmax)
    return maxitem


def checkvers3(name):
    url2 = "https://raw.githubusercontent.com/Gujal00/smrzips/master/addons.xml"  # repository.gujal-2.0.0.zip
    fpage = Utils.getUrl(url2)
    rx = 'addon id="script.module.resolveurl".*?version="(.*?)"'
    match = re.compile(rx, re.DOTALL).findall(fpage)
    latest = match[0]
    return latest


def checkvers4(name):
    try:
        url2 = "https://github.com/host505/repository.host505/tree/master/script.module.oathscrapers/"
        fpage = Utils.getUrl(url2)
        rx = name + '-(.*?).zip'
        match = re.compile(rx, re.DOTALL).findall(fpage)
        latest = findmax(match)
        return latest
    except:
        return " "


def upd_done():
    tfile = THISPLUG + "/scripts/script.module.resolveurl/addon.xml"
    if not os.path.exists(tfile):
        upd_done1()
    else:
        f = open(tfile, "r")
        txt = f.read()
        n1 = txt.find('<addon', 0)
        n11 = txt.find('id', n1)
        n2 = txt.find("version", n11)
        n3 = txt.find('"', n2)
        n4 = txt.find('"', (n3 + 2))
        version = txt[(n3 + 1):n4]
        f.close()
        newvers = checkvers3("script.module.resolveurl")
        if newvers == " ":
            upd_done1()
        if newvers != version:
            dest = "/tmp/resolveurl.zip"
            xfile = "https://raw.githubusercontent.com/Gujal00/smrzips/master/zips/script.module.resolveurl/script.module.resolveurl-" + newvers + ".zip"
            f = Utils.getUrlresp(xfile)
            p = f.read()
            f1 = open(dest, "wb")
            f1.write(p)
            f1.close()
            fplug = ""
            uresolv(fplug)
        else:
            upd_done1()


def uresolv(fplug):
    tfile = THISPLUG + "/scripts/script.module.resolveurl"
    cmd1 = "rm -rf " + tfile
    fdest = THISPLUG + "/scripts"
    cmd2 = "unzip -o -q '/tmp/resolveurl.zip' -d " + fdest
    cmd = cmd1 + " && " + cmd2
    os.system(cmd)
    tfile2 = THISPLUG + "/scripts/script.module.resolveurl-master"
    try:
        cmd3 = "mv -f " + tfile2 + " " + tfile
        os.system(cmd3)
    except:
        pass
    tfile3A = THISPLUG + "/script.module.resolveurl.zip"
    cmd3 = "unzip -o -q '" + tfile3A + "' -d " + fdest
    os.system(cmd3)
    tfile3 = tfile + "/lib/oathscrapers/sources_oathscrapers/en/123movies.py"
    tfile4 = tfile + "/lib/oathscrapers/sources_oathscrapers/en/one23movies.py"
    try:
        cmd4 = "mv -f " + tfile3 + " " + tfile4
        os.system(cmd4)
    except:
        pass

    upd_done1()


def upd_done1():
    fdest = THISPLUG + "/scripts"
    tfile3A = THISPLUG + "/script.module.resolveurl.zip"
    cmd3 = "unzip -o -q '" + tfile3A + "' -d " + fdest
    os.system(cmd3)
    upd_done2()


def uresolv2(fplug):
    tfile = THISPLUG + "/scripts/script.module.oathscrapers"
    cmd1 = "rm -rf " + tfile
    fdest = THISPLUG + "/scripts"
    cmd2 = "unzip -o -q '/tmp/oathscrapers.zip' -d " + fdest
    cmd = cmd1 + " && " + cmd2
    os.system(cmd)

    tfile3 = tfile + "/lib/oathscrapers/sources_oathscrapers/en/123movies.py"
    tfile4 = tfile + "/lib/oathscrapers/sources_oathscrapers/en/one23movies.py"
    try:
        cmd4 = "cp -rf " + tfile3 + " " + tfile4
        os.system(cmd4)
    except:
        pass
    upd_done2()


def upd_done2():
    pass
