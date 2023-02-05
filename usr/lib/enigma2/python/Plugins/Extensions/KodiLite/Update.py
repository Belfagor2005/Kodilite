#!/usr/bin/python
# -*- coding: utf-8 -*-

from twisted.web.client import downloadPage
import os
import re
import sys
from . import Utils

PY3 = sys.version_info.major >= 3
if PY3:
    # Python 3
    PY3 = True
    # unicode = str
    # unichr = chr
    # long = int
    # xrange = range
    from urllib.request import urlopen
else:
    # Python 2
    from urllib2 import urlopen

THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
latest = " "

# print "Starting Update-py"
# fontpath = THISPLUG
# addFont('%s/font_default.otf' % fontpath, 'TSmediaFont', 100, 1)


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
        pass  # print "In findmax x =", x
        A.append(int(x[0]))
    # A.append((x[0]))
    lx = len(x)
    pass  # print "In findmax A =", A
    Amax = max(A)
    pass  # print "In findmax Amax =", Amax

    i1 = 0
    for a in A:
        if a == Amax:
            imax = i1
            break
            i1 = i1+1
    # maxitem = str(Amax)
    pass  # print "In findnax imax A=", imax
    maxitem = str(Amax)
    if lx > 1:
        for item in match:
            x = item.split(".")
            if int(x[0]) == int(Amax):
                B.append(x[1])
            else:
                # continue
                B.append(int('0'))
        pass  # print "In findmax B =", B
        Bmax = max(B)
        pass  # print "In findnax Bmax =", Bmax
        i2 = 0
        for b in B:
            if b == Bmax:
                imax = i2
                break
            i2 = i2+1
        maxitem = str(Amax) + "." + str(Bmax)
        pass  # print "In findnax imax B=", imax
        if lx > 2:
            for item in match:
                x = item.split(".")
                if (int(x[0]) == int(Amax)) and (int(x[1]) == int(Bmax)):
                    # C.append(int(x[2]))
                    C.append(x[2])
                else:
                    C.append(int('0'))
            pass  # print "In findmax C =", C
            Cmax = max(C)
            pass  # print "In findnax Cmax =", Cmax
            i3 = 0
            for c in C:
                if c == Cmax:
                    imax = i3
                    break
                i3 = i3+1
            maxitem = str(Amax) + "." + str(Bmax) + "." + str(Cmax)
        if lx > 3:
            for item in match:
                x = item.split(".")
            if (int(x[0]) == int(Amax)) and (int(x[1]) == int(Bmax)) and ((x[2]) == Cmax):
                # C.append(int(x[2]))
                D.append(x[3])
            else:
                D.append(int('0'))
            pass  # print "In findmax D =", D
            Dmax = max(D)
            pass  # print "In findnax Dmax =", Dmax
            i4 = 0
            for d in D:
                if d == Dmax:
                    imax = i4
                    break
            i4 = i4+1
            maxitem = str(Amax) + "." + str(Bmax) + "." + str(Cmax) + "." + str(Dmax)
    # pass  # print "In findnax imax C=", imax
    # pass  # print "In findnax imax final =", imax
    # maxitem = match[imax]
    pass  # print "maxitem =", maxitem
    return maxitem


def checkvers3(name):
    # name = "script.module.urlresolver"
    try:
        url2 = "https://github.com/tvaddonsco/tva-resolvers-repo/tree/master/zips/script.module.urlresolver/"
        fpage = urlopen(url2).read()
        pass  # print "In newvers fpage =", fpage
        rx = name + '-(.*?).zip'
        match = re.compile(rx, re.DOTALL).findall(fpage)
        pass  # print  "match =", match
        latest = findmax(match)
        pass  # print  "latest =", latest
        return latest
    except:
        return " "


def checkvers4(name):
    try:
        url2 = "https://github.com/tvaddonsco/tva-resolvers-repo/tree/master/zips/script.module.resolveurl/"
        fpage = urlopen(url2).read()
        pass  # print "In newvers fpage =", fpage
        rx = name + '-(.*?).zip'
        match = re.compile(rx, re.DOTALL).findall(fpage)
        pass  # print  "match =", match
        latest = findmax(match)
        pass  # print  "latest =", latest
        return latest
    except:
        return " "


def updstart():
    upd_done()


def updsXtart():
    tfile = THISPLUG + "/scripts/script.module.urlresolver/addon.xml"
    if not os.path.exists(tfile):
        upd_done1()
    else:
        f = open(tfile, "r")
        txt = f.read()
        pass  # print "In main txt = ", txt
        n1 = txt.find('<addon', 0)
        n11 = txt.find('id', n1)
        n2 = txt.find("version", n11)
        n3 = txt.find('"', n2)
        n4 = txt.find('"', (n3+2))
        version = txt[(n3+1):n4]
        f.close()
        pass  # print "In main version urlresolver= ", version
        newvers = checkvers3("script.module.urlresolver")
        pass  # print "In main newvers urlresolver= ", newvers
        if newvers == " ":
            upd_done1()
        elif newvers != version:
            # plug = "urlresolver.zip"
            # fdest = THISPLUG + "/scripts"
            dest = "/tmp/urlresolver.zip"
            xfile = "https://github.com/tvaddonsco/tva-resolvers-repo/raw/master/zips/script.module.urlresolver/script.module.urlresolver-" + newvers + ".zip"
            pass  # print "xfile =", xfile
            downloadPage(xfile, dest).addCallback(uresolv).addErrback(showError)
        else:
            upd_done1()


def showError(error):
    pass  # print "ERROR :", error
    upd_done1()


def uresolv(fplug):
    tfile = THISPLUG + "/scripts/script.module.urlresolver"
    cmd1 = "rm -rf " + tfile
    fdest = THISPLUG + "/scripts"
    cmd2 = "unzip -o -q '/tmp/urlresolver.zip' -d " + fdest
    pass  # print "In main cmd urlresolver=", cmd2
    # title = _("Installing script urlresolver")
    cmd = cmd1 + " && " + cmd2
    os.system(cmd)
    upd_done1()


def upd_done1():
    tfile = THISPLUG + "/scripts/script.module.resolveurl/addon.xml"
    if not os.path.exists(tfile):
        upd_done()
    else:
        newvers = checkvers4("script.module.resolveurl")
        latest = newvers
        pass  # print  "latest =", latest
    tfile = THISPLUG + "/scripts/script.module.resolveurl/addon.xml"
    f = open(tfile, "r")
    txt = f.read()
    pass  # print "In main txt = ", txt
    n1 = txt.find('<addon', 0)
    n11 = txt.find('id', n1)
    n2 = txt.find("version", n11)
    n3 = txt.find('"', n2)
    n4 = txt.find('"', (n3+2))
    version = txt[(n3+1):n4]
    f.close()
    pass  # print "In resolveurl version = ", version
    newvers = latest
    pass  # print "In resolveurl newvers= ", newvers
    if newvers == " ":
        upd_done()
    elif newvers != version:
        # plug = "resolveurl.zip"
        # fdest = THISPLUG + "/scripts"
        dest = "/tmp/resolveurl.zip"
        xfile = "https://github.com/tvaddonsco/tva-resolvers-repo/raw/master/zips/script.module.resolveurl/script.module.resolveurl-" + newvers + ".zip"
        pass  # print "In main version resolveurl xfile= ", xfile
        downloadPage(xfile, dest).addCallback(upd_done6).addErrback(showError5)
    else:
        upd_done()


def showError5(error):
    pass  # print "ERROR :", error
    upd_done()


def upd_done6(fplug):
    pass  # print "In upd_done6"
    tfile = THISPLUG + "/scripts/script.module.resolveurl"
    cmd1 = "rm -rf " + tfile
    fdest = THISPLUG + "/scripts"
    cmd2 = "unzip -o -q '/tmp/resolveurl.zip' -d " + fdest
    pass  # print "In main cmd resolveurl=", cmd2
    # title = _("Installing script resolveurl")
    cmd = cmd1 + " && " + cmd2
    pass  # print "In main cmd =", cmd
    os.system(cmd)
    upd_done()


def upd_done():
    print("In upd_done")
    dest = "/tmp/updates5.zip"
    xfile = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/updates5.zip"
    print("upd_done xfile =", xfile)
    # downloadPage(xfile, dest).addCallback(upd_last).addErrback(showError6)
    # downloadPage(xfile, dest).addCallback(upd_last)
    f = Utils.getUrlresp(xfile)
    print("f =", f)
    p = f.read()
    f1 = open(dest, "wb")
    f1.write(p)
    f1.close()
    fplug = ""
    upd_last(fplug)


def showError6(error):
    print("ERROR :", error)
    # upd_last2()


def upd_last(fplug):
    fdest = "/usr"
    cmd = "unzip -o -q '/tmp/updates5.zip' -d " + fdest
    print("cmd A =", cmd)
    os.system(cmd)
    # upd_last2()
    pass


def upd_last2():
    if not os.path.exists("/usr/lib/python2.7/site-packages/requests"):
        cmd = "opkg install python-requests"
        os.system(cmd)
    if not os.path.exists("/usr/lib/python2.7/site-packages/Crypto"):
        cmd = "opkg install python-pycrypto"
        os.system(cmd)
    if not os.path.exists("/usr/lib/python2.7/lib-dynload/mmap.so"):
        cmd = "opkg install python-mmap"
        os.system(cmd)
    if not os.path.exists("/usr/lib/python2.7/sqlite3"):
        cmd = "opkg install python-sqlite3"
        os.system(cmd)
    if not os.path.exists("/usr/lib/python2.7/cProfile.pyo"):  # needed by exodus
        cmd = "opkg install python-profile"
        os.system(cmd)
    if not os.path.exists("/usr/lib/python2.7/email"):  # needed by youtube
        cmd = "opkg install python-email"
        os.system(cmd)
    try:
        import Image
    except:
        try:
            from PIL import Image
        except:
            cmd = "opkg install python-image"
            os.system(cmd)
    try:
        import Image
    except:
        try:
            from PIL import Image
        except:
            cmd = "opkg install python-imaging"
            os.system(cmd)

    tf = THISPLUG + "/scripts/script.module.covenant/lib/resources/lib/sources/en/123netflix.py"
    tf2 = THISPLUG + "/scripts/script.module.covenant/lib/resources/lib/sources/en/netflix.py"
    pass  # print "Renaming 123netflix.py"
    if os.path.exists(tf):
        cmd = "mv " + tf + " " + tf2
        pass  # print "Rename cmd =", cmd
        os.system(cmd)
    tf = THISPLUG + "/scripts/script.module.lambdascrapers"
    pass  # print "fix script.module.lambdascrapers"
    if os.path.exists(tf):
        cmd = "cp -rf " + THISPLUG + "/lambda__init__.py " + THISPLUG + "/scripts/script.module.lambdascrapers/lib/lambdascrapers/__init__.py"
        os.system(cmd)
    pass  # print "In upd_done 2"
    # ###################
    upd_last3()


def upd_last3():
    # ################
    pass  # print "In upd_last3"
    # ################
    dest = "/tmp/adlist.zip"
    xfile = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/adlist.zip"
    pass  # print "upd_done xfile =", xfile
    downloadPage(xfile, dest).addCallback(upd_last4).addErrback(showError7)


def showError7(error):
    pass  # print "ERROR :", error
    upd_last5()


def upd_last4(fplug):
    fdest = THISPLUG
    cmd = "unzip -o -q '/tmp/adlist.zip' -d " + fdest
    pass  # print "cmd A =", cmd
    os.system(cmd)
    upd_last5()


def upd_last5():
    # ################
    pass  # print "In upd_last3"
    # ################
    dest = "/tmp/extractors.zip"
    xfile = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/extractors.zip"
    pass  # print "upd_done xfile =", xfile
    downloadPage(xfile, dest).addCallback(upd_last6).addErrback(showError8)


def showError8(error):
    pass  # print "ERROR :", error


def upd_last6(fplug):
    fd = THISPLUG + "/youtube_dl/control.py"
    if os.path.exists(fd):
        fdest = THISPLUG + "/youtube_dl/extractor"
        cmd = "unzip -o -q '/tmp/extractors.zip' -d " + fdest
        pass  # print "cmd A =", cmd
        os.system(cmd)
    else:
        pass
