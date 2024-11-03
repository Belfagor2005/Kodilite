#!/usr/bin/python
# -*- coding: utf-8 -*-

from twisted.web.client import downloadPage
import os
import re
import sys
from . import Utils

PY3 = sys.version_info.major >= 3
if PY3:
    PY3 = True
    from urllib.request import urlopen
else:
    from urllib2 import urlopen

THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite"
latest = " "


def findmax(match=[]):
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
                    # C.append(int(x[2]))
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
    try:
        url2 = "https://github.com/tvaddonsco/tva-resolvers-repo/tree/master/zips/script.module.urlresolver/"
        fpage = urlopen(url2).read()
        rx = name + '-(.*?).zip'
        match = re.compile(rx, re.DOTALL).findall(fpage)
        latest = findmax(match)
        return latest
    except:
        return " "


def checkvers4(name):
    try:
        url2 = "https://github.com/tvaddonsco/tva-resolvers-repo/tree/master/zips/script.module.resolveurl/"
        fpage = urlopen(url2).read()
        rx = name + '-(.*?).zip'
        match = re.compile(rx, re.DOTALL).findall(fpage)
        latest = findmax(match)
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
        n1 = txt.find('<addon', 0)
        n11 = txt.find('id', n1)
        n2 = txt.find("version", n11)
        n3 = txt.find('"', n2)
        n4 = txt.find('"', (n3 + 2))
        version = txt[(n3 + 1):n4]
        f.close()
        pass  # print "In main version urlresolver= ", version
        newvers = checkvers3("script.module.urlresolver")
        pass  # print "In main newvers urlresolver= ", newvers
        if newvers == " ":
            upd_done1()
        elif newvers != version:
            dest = "/tmp/urlresolver.zip"
            xfile = "https://github.com/tvaddonsco/tva-resolvers-repo/raw/master/zips/script.module.urlresolver/script.module.urlresolver-" + newvers + ".zip"
            downloadPage(xfile, dest).addCallback(uresolv).addErrback(showError)
        else:
            upd_done1()


def showError(error):
    upd_done1()


def uresolv(fplug):
    tfile = THISPLUG + "/scripts/script.module.urlresolver"
    cmd1 = "rm -rf " + tfile
    fdest = THISPLUG + "/scripts"
    cmd2 = "unzip -o -q '/tmp/urlresolver.zip' -d " + fdest
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
    tfile = THISPLUG + "/scripts/script.module.resolveurl/addon.xml"
    f = open(tfile, "r")
    txt = f.read()
    n1 = txt.find('<addon', 0)
    n11 = txt.find('id', n1)
    n2 = txt.find("version", n11)
    n3 = txt.find('"', n2)
    n4 = txt.find('"', (n3 + 2))
    version = txt[(n3 + 1):n4]
    f.close()
    newvers = latest
    if newvers == " ":
        upd_done()
    elif newvers != version:
        dest = "/tmp/resolveurl.zip"
        xfile = "https://github.com/tvaddonsco/tva-resolvers-repo/raw/master/zips/script.module.resolveurl/script.module.resolveurl-" + newvers + ".zip"
        downloadPage(xfile, dest).addCallback(upd_done6).addErrback(showError5)
    else:
        upd_done()


def showError5(error):
    upd_done()


def upd_done6(fplug):
    tfile = THISPLUG + "/scripts/script.module.resolveurl"
    cmd1 = "rm -rf " + tfile
    fdest = THISPLUG + "/scripts"
    cmd2 = "unzip -o -q '/tmp/resolveurl.zip' -d " + fdest
    cmd = cmd1 + " && " + cmd2
    os.system(cmd)
    upd_done()


def upd_done():
    print("In upd_done")
    dest = "/tmp/updates5.zip"
    xfile = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/updates5.zip"
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


def upd_last(fplug):
    fdest = "/usr"
    cmd = "unzip -o -q '/tmp/updates5.zip' -d " + fdest
    print("cmd A =", cmd)
    os.system(cmd)


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
    if os.path.exists(tf):
        cmd = "mv " + tf + " " + tf2
        os.system(cmd)
    tf = THISPLUG + "/scripts/script.module.lambdascrapers"
    if os.path.exists(tf):
        cmd = "cp -rf " + THISPLUG + "/lambda__init__.py " + THISPLUG + "/scripts/script.module.lambdascrapers/lib/lambdascrapers/__init__.py"
        os.system(cmd)
    upd_last3()


def upd_last3():
    dest = "/tmp/adlist.zip"
    xfile = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/adlist.zip"
    downloadPage(xfile, dest).addCallback(upd_last4).addErrback(showError7)


def showError7(error):
    upd_last5()


def upd_last4(fplug):
    fdest = THISPLUG
    cmd = "unzip -o -q '/tmp/adlist.zip' -d " + fdest
    os.system(cmd)
    upd_last5()


def upd_last5():
    dest = "/tmp/extractors.zip"
    xfile = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/KodiDirect/Fix/extractors.zip"
    downloadPage(xfile, dest).addCallback(upd_last6).addErrback(showError8)


def showError8(error):
    pass


def upd_last6(fplug):
    fd = THISPLUG + "/youtube_dl/control.py"
    if os.path.exists(fd):
        fdest = THISPLUG + "/youtube_dl/extractor"
        cmd = "unzip -o -q '/tmp/extractors.zip' -d " + fdest
        os.system(cmd)
    else:
        pass
