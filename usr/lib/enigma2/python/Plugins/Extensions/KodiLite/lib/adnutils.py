#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys

try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError

PY2 = False
PY3 = False

print("sys.version_info =", sys.version_info)
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
PY34 = sys.version_info[0:2] >= (3, 4)

f1 = open("/tmp/py.txt","a")
msg = "adnutils PY3 = " + str(PY3) + " adnutils PY2 = " + str(PY2)
f1.write(msg)
f1.close()

# ammend  this command is in /kodilite/Utils.py   ;)
# if possible remove this file py adnutils

if PY3:
    def getUrl(url):
#        print(  "Here in getUrl url =", url)
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
            response = urlopen(req)
            link=response.read().decode(errors='ignore')
            response.close()
            return link
        except:
            import ssl
            gcontext = ssl._create_unverified_context()
            response = urlopen(req, context=gcontext)
            link=response.read().decode(errors='ignore')
            response.close()
            return link

    def getUrl2(url, referer):
        # print  "Here in  getUrl2 url =", url
        # print  "Here in  getUrl2 referer =", referer
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Referer', referer)
        try:
            response = urlopen(req)
            link=response.read().decode()
            response.close()
            return link
        except:
            import ssl
            gcontext = ssl._create_unverified_context()
            response = urlopen(req, context=gcontext)
            link=response.read().decode()
            response.close()
            return link


    def getUrl3(url):
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
            response = urlopen(req)
            link=response.geturl()
            response.close()
            return link
        except:
            import ssl
            gcontext = ssl._create_unverified_context()
            response = urlopen(req, context=gcontext)
            link=response.geturl()
            response.close()
            return link

    def getUrlresp(url):
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
            response = urlopen(req)
            return response
        except:
            import ssl
            gcontext = ssl._create_unverified_context()
            response = urlopen(req, context=gcontext)
            return response
else:
    def getUrl(url):
        pass#print "Here in getUrl url =", url
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
            response = urlopen(req)
            pass#print "Here in getUrl response =", response
            link=response.read()
            response.close()
            return link
        except:
            import ssl
            gcontext = ssl._create_unverified_context()
            response = urlopen(req, context=gcontext)
            pass#print "Here in getUrl response 2=", response
            link=response.read()
            response.close()
            return link

    def getUrl2(url, referer):
        pass#print "Here in  getUrl2 url =", url
        pass#print "Here in  getUrl2 referer =", referer
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Referer', referer)
        try:
            response = urlopen(req)
            link=response.read()
            response.close()
            return link
        except:
            import ssl
            gcontext = ssl._create_unverified_context()
            response = urlopen(req, context=gcontext)
            link=response.read()
            response.close()
            return link

    def getUrl3(url):
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
            response = urlopen(req)
            link=response.geturl()
            response.close()
            return link
        except:
            import ssl
            gcontext = ssl._create_unverified_context()
            response = urlopen(req, context=gcontext)
            link=response.geturl()
            response.close()
            return link

    def getUrlresp(url):
        pass#print "Here in getUrl url =", url
        req = Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
            response = urlopen(req)
            return response
        except:
            import ssl
            gcontext = ssl._create_unverified_context()
            response = urlopen(req, context=gcontext)
            return response


std_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
}
