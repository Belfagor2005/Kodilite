
import urllib2  
from urllib import unquote_plus
import re
#202003..-ashemaletube, anyporn, shemalestube , sheshaft, xhamster, drtuber

#ytdl - bravotube, redtrube, pornxs, fantasti.cc, eporner,xtube 

import ssl
import urllib2
def getUrl(url):
        print "Here in getUrl url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
              response = urllib2.urlopen(req)
        except:      
              gcontext = ssl._create_unverified_context()
	      response = urllib2.urlopen(req, context=gcontext)
	link=response.read()
	response.close()
	return link      
	
def getUrl2(url, referer):
        print "Here in getUrl2 url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        req.add_header('Referer', referer)
        try:
              response = urllib2.urlopen(req)
        except:      
              gcontext = ssl._create_unverified_context()
	      response = urllib2.urlopen(req, context=gcontext)
	link=response.read()
	response.close()
	return link	

	
def getUrl3(url):
        print "Here in getUrl3 url =", url
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        try:
              response = urllib2.urlopen(req)
        except:      
              gcontext = ssl._create_unverified_context()
	      response = urllib2.urlopen(req, context=gcontext)
	link=response.geturl()
	response.close()
	return link


def getVideo(name, url):
     name = name.lower()
     print "In getVideo name =", name
     print "In getVideo url =", url
     if "motherless" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage 1 =", fpage
           regexvideo = "__fileurl = '(.*?)'"
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           url = match[0]

     elif "shemalemovie" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "shemalemovie fpage 1 =", fpage
	   regexvideo = 'contentUrl" href="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
	   url = match[0]
           print "shemalemovie url =", url


     elif "pornhub" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "pornhub fpage 1 =", fpage
	   regexvideo = 'defaultQuality.*?http(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           url = "http" + match[0].replace("\\", "")
           print "pornhub url =", url

     elif "drtuber" in name:
           print "Here in drtuber url =", url
           fpage = getUrl(url)
	   print "drtuber fpage 1 =", fpage
	   regexvideo = 'defaultQuality.*?http(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
#           url = "http" + match[0].replace("\\", "")
           print "drtuber url =", url

     elif "shemalestube" in name:
           print "Here in shemalestube url =", url
           fpage = getUrl(url)
	   print "shemalestube fpage 1 =", fpage
	   regexvideo = "var filename = '(.*?)'"
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
	   print "shemalestube match =", match
	   indic = 0
	   for url1 in match:
	           print "shemalestube url1 =", url1
	           if "playlist" in url1:
	                    url = url1
	                    indic = 1 
	                    break
	   print "shemalestube indic =", indic         
	   if indic == 0:
	           url = match[0]
           print "shemalestube url =", url

     elif "anyporn" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "anyporn fpage 1 =", fpage
	   regexvideo = 'source src="(.*?)".*?title="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
	   print "anyporn match =", match
	   for url1, name in match:
	         if "hq" in name.lower():
	                 url = url1
	                 break
           print "anyporn url =", url
           
     elif 'empflix' in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage 1 =", fpage
	   url = re.compile('<meta itemprop="contentUrl" content="(.+?)" />').findall(fpage)[0]
           print "empflix url =", url


     elif 'tnaflix' in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage 1 =", fpage
	   url = re.compile('<meta itemprop="contentUrl" content="([^"]+)" />').findall(fpage)[0]
           print "tnaflix url =", url
           
     elif 'upornia' in url:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage 1 =", fpage
	   url = re.compile('file: \'(.+?)\',').findall(fpage)[0]
           print "upornia url =", url
           

     elif "shemaletubevideos" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage 2 =", fpage
           n1 = fpage.find("mp4", 0)
           n2 = fpage.rfind("http", 0, n1)
           url = fpage[n2:(n1+3)]
           print "vidurl =", url
#     elif ("" in name) or ("" in url.lower()):
     elif ("xnxx" in name) or ("xnxx" in url.lower()):
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage 3 =", fpage
           regexvideo = "setVideoUrlHigh\('(.*?)'"
           match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print "getVideos match 3=", match
           url1 = match[0]
	   url = unquote_plus(url1)
           print "vidurl =", url

#     elif "luxuretv" in name:
     elif ("luxuretv" in name) or ("luxuretv" in url.lower()):
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage 4 =", fpage
	   regexvideo = '<source src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print "getVideos match 4=", match
	   url = match[0]
           print "vidurl 4=", url

     elif "hotgoo" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = 'video controls src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           url = match[0]
           print "vidurl 4=", url

     elif "heavy-r" in name:
           print "Here in playVideo url =", url
           content = getUrl(url)
	   print  "content C =", content
	   regexvideo = '"video/mp4" src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(content)
	   url = match[0]
           print "vidurl =", url

     elif ("xhamster" in name) or ("xhamster" in url):
        fpage = getUrl(url)
	print "xhamster fpage C =", fpage
        start = 0
        if "file:" in fpage:
                  regexvideo = "file\:.*?http(.*?)'"
	          match = re.compile(regexvideo,re.DOTALL).findall(fpage) 
	          print "Here in xhamster match =", match
	          url = "http" + match[0]
                  print "xhamster url 1 =", url
        elif '.mp4"' in fpage:
                  pos1 = fpage.find('.mp4"', start)
                  if (pos1 < 0):
                           return
  	          pos2 = fpage.rfind("http", 0, pos1)
 	          if (pos2 < 0):
                           return
                  url = fpage[(pos2):pos1] + ".mp4"
                  url = url.replace("\\", "")
                  print "xhamster url 2 =", url
        else:
           print "Here in xhamster url 3 =", url
           fpage = getUrl(url)
	   print "xhamster fpage 2=", fpage
           start = 0
           pos1 = fpage.find(".flv", start)
           if (pos1 < 0):
                           return
  	   pos2 = fpage.find("a href", pos1)
 	   if (pos2 < 0):
                           return
           pos3 = fpage.find('"', (pos2+10))
 	   if (pos3 < 0):
                           return                
           url = fpage[(pos2+8):pos3]
           url = url.replace("\\", "")         
           print "Here in xhamster url 4=", url
           
     elif "spicytranny" in name:
           print "Here in playVideo url =", url
           fpage = getUrl(url)
	   print "fpage C =", fpage
           start = 0
           if "video_url" in fpage:
#           regexvideo = "http://anysex.com/ge.*?le(.*?)'"
                  regexvideo = "video_ur.*?'(.*?)'"
	          match = re.compile(regexvideo,re.DOTALL).findall(fpage) 
	          print "Here in playVideo match =", match
                  url1 = match[0]
                  print "Here in playVideo url1 =", url1
      #           url1 = "http://anysex.com/get_file/1/53a3597298cde104bf87d5d84c866ee1/90000/90981/90981.mp4/"
                  
           elif '.mp4"' in fpage:
                  pos1 = fpage.find('.mp4"', start)
                  if (pos1 < 0):
                           return
  	          pos2 = fpage.rfind("http", 0, pos1)
 	          if (pos2 < 0):
                           return
                  url1 = fpage[(pos2):pos1] + ".mp4"
           elif "source src" in fpage:
                  regexvideo = 'source src="(.*?)"'
	          match = re.compile(regexvideo,re.DOTALL).findall(fpage) 
                  url1 = match[0]  
                  
           elif ".flv" in fpage:       
                  pos1 = fpage.find(".flv", start)
  	          pos2 = fpage.find("a href", pos1)
                  pos3 = fpage.find('"', (pos2+10))
                  url1 = fpage[(pos2+8):pos3]
           else:
                  print "None possible"       
                       
           url = url1
           print "Here in playVideo url =", url

     elif "deviantclip" in name:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           start = 0
           pos1 = fpage.find("source src", start)
           if (pos1 < 0):
                           return
  	   pos2 = fpage.find("http", pos1)
 	   if (pos2 < 0):
                           return
           pos3 = fpage.find("'", (pos2+5))
 	   if (pos3 < 0):
                           return                

           url = fpage[(pos2):(pos3)]
           print "vidurl 4=", url


     elif "xvideos" in name:
           print "Here in getVideo url 2=", url
           fpage = getUrl(url)
	   print "fpage 3 =", fpage
           regexvideo = "setVideoUrlHigh\('(.*?)'"
           match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print "getVideos match 3=", match
           url1 = match[0]
	   url = unquote_plus(url1)
           print "vidurl =", url

     elif "txxx" in url:
        print "Here in txxx url =", url
        fpage = getUrl(url)
	print "fpage C =", fpage
	try:
           regexvideo = 'div class="download-link.*?href="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In xvideos match =", match
           url = match[0]
           print  "Here in txxx url =", url
        except:   
           regexvideo = 'a class="btn btn-default btn-close js--wat.*?href="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In xvideos match =", match
           url = match[0]
           print  "Here in txxx url =", url
           

     elif "befuck" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = '<source src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In xvideos match =", match
           url = match[0]
           url = url.replace("&amp;", "&")
           print  "Here in befuck url =", url

     elif "pornxs" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = 'config-final-url="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In pornxs match =", match
           url = match[0]
           url = url.replace("&amp;", "&")
           print  "Here in pornxs url =", url
           
     elif "sheshaft" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = 'div class="download-link.*?href="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In sheshaft match =", match
           url = match[0]
           print  "Here in sheshaft url =", url

     elif "ashemaletube" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = '<source src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In ashemaletube match =", match
           url = match[0]
           url = url.replace("\\", "")
           print  "Here in ashemaletube url =", url



     elif "sunporno" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = '<video src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In sunporno =", match
           url = match[0]
           print  "Here in sunporno url =", url

     elif "jizzbunker" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = "type:'video/.*?src:'(.*?)'"
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In jizzbunker =", match
           url = match[0]
           print  "Here in jizzbunker url =", url

     elif "pornoxo" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = '<video id=.*?source src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In pornoxo =", match
           url = match[0]
           print  "Here in pornoxo url =", url

     elif "youporn" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = '"videoUrl"\:"(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In youporn =", match
           url = match[0]
           url = url.replace("\\", "")
           print  "Here in pornoxo url =", url

     elif "vporn" in url:
           fpage = getUrl(url)
	   print "fpage C =", fpage
           regexvideo = '<source src="(.*?)"'
	   match = re.compile(regexvideo,re.DOTALL).findall(fpage)
           print  "In vporn =", match
           url = match[0]
           print  "Here in vporn url =", url




     else:  #youtube-dl
           name, url
     return name, url






















































