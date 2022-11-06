#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Simple HTTP Live Streaming client.

References:
    http://tools.ietf.org/html/draft-pantos-http-live-streaming-08

This program is free software. It comes without any warranty, to
the extent permitted by applicable law. You can redistribute it
and/or modify it under the terms of the Do What The Fuck You Want
To Public License, Version 2, as published by Sam Hocevar. See
http://sam.zoy.org/wtfpl/COPYING for more details.

Last updated: July 22, 2012

Original Code From:
    http://nneonneo.blogspot.gr/2010/08/http-live-streaming-client.html

Depends on python-crypto (for secure stream)
Modified for OpenPli enigma2 usage by athoik
Modified for KodiDirect and IPTVworld by pcd
"""
import os
import re
import sys
import threading
import time
import Queue
import operator


if PY3:
    from urllib.request import urlopen, Request
    from urllib.parse import urlparse
    from urllib.parse import urljoin
else:
    from urllib2 import urlopen, Request
    from urlparse import urlparse
    from urlparse import urljoin


SUPPORTED_VERSION = 3
STREAM_PFILE = ''


def getUrl2(url, referer):
    req = Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Referer', referer)
    response = urlopen(req)
    link = response.read()
    response.close()
    return link


class hlsclient(threading.Thread):

    def __init__(self):
        self._stop = False
        self.thread = None
        self._downLoading = False
        threading.Thread.__init__(self)

    def setUrl(self, url):
        self.url = url
        self._stop = False
        self.thread = None
        self._downLoading = False

    def isDownloading(self):
        return self._downLoading

    def run(self):
        self.play()

    def download_chunks(self, downloadUrl, chunk_size=4096):
        req = Request(downloadUrl)
        hdr = 'User-Agent=ONLINETVCLIENT_X60000_X25000_X4000MEGA_V1770'
        req.add_header('User-Agent', 'User-Agent=ONLINETVCLIENT_X60000_X25000_X4000MEGA_V1770')
        conn = urlopen(req)
        while 1:
            data = conn.read(chunk_size)
            if not data:
                return
            yield data

    def download_file(self, downloadUrl):
        return ''.join(self.download_chunks(downloadUrl))

    def validate_m3u(self, conn):
        ''' make sure file is an m3u, and returns the encoding to use. '''
        mime = conn.headers.get('Content-Type', '').split(';')[0].lower()
        if mime == 'application/vnd.apple.mpegurl':
            enc = 'utf8'
        elif mime == 'audio/mpegurl':
            enc = 'iso-8859-1'
        elif conn.url.endswith('.m3u8'):
            enc = 'utf8'
        elif conn.url.endswith('.m3u'):
            enc = 'iso-8859-1'
        else:
            os.remove(STREAM_PFILE)
            self.stop()
        if conn.readline().rstrip('\r\n') != '#EXTM3U':
            os.remove(STREAM_PFILE)
            self.stop()
        return enc

    def gen_m3u(self, url, skip_comments=True):
        req = Request(url)
        if self.header != "":
            req.add_header('User-Agent', str(self.header))
        conn = urlopen(req)
        enc = 'utf8'
        for line in conn:
            line = line.rstrip('\r\n').decode(enc)
            if not line:
                # blank line
                continue
            elif line.startswith('#EXT'):
                # tag
                yield line
            elif line.startswith('#'):
                # comment
                if skip_comments:
                    continue
                else:
                    yield line
            else:
                # media file
                yield line

    def parse_m3u_tag(self, line):
        if ':' not in line:
            return line, []
        tag, attribstr = line.split(':', 1)
        attribs = []
        last = 0
        quote = False
        for i, c in enumerate(attribstr + ','):
            if c == '"':
                quote = not quote
            if quote:
                continue
            if c == ',':
                attribs.append(attribstr[last:i])
                last = i+1
        return tag, attribs

    def parse_kv(self, attribs, known_keys=None):
        d = {}
        for item in attribs:
            k, v = item.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"')
            if known_keys is not None and k not in known_keys:
                os.remove(STREAM_PFILE)
                self.stop()
            d[k] = v
        return d

    def handle_basic_m3uX(self, hlsUrl):
        # http://l3md.shahid.net/media/l3/2fda1d3fd7ab453cad983544e8ed70e4/3be7afa11f5a4037bb0b1163d378c444/4df816395413420488af72856246b027/kormebra_s01_e27.mpegts/playlist-f01309a9eaa9e824e1b65430ddecf7f592cdfd76.m3u8
        # line = re.sub('foo','bar', line.rstrip())
        base_key_url = re.sub('playlist-.*?.m3u8', '', hlsUrl)
        seq = 1
        enc = None
        nextlen = 5
        duration = 5
        for line in self.gen_m3u(hlsUrl):
            if line.startswith('#EXT'):
                tag, attribs = self.parse_m3u_tag(line)
                if tag == '#EXTINF':
                    duration = float(attribs[0])
                elif tag == '#EXT-X-TARGETDURATION':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-TARGETDURATION'
                    targetduration = int(attribs[0])
                    pass
                elif tag == '#EXT-X-MEDIA-SEQUENCE':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-MEDIA-SEQUENCE'
                    seq = int(attribs[0])
                elif tag == '#EXT-X-KEY':
                    attribs = self.parse_kv(attribs, ('METHOD', 'URI', 'IV'))
                    assert 'METHOD' in attribs, '[hlsclient::handle_basic_m3u] expected METHOD in EXT-X-KEY'
                    if attribs['METHOD'] == 'NONE':
                        assert 'URI' not in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=NONE, but URI found'
                        assert 'IV' not in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=NONE, but IV found'
                        enc = None
                    elif attribs['METHOD'] == 'AES-128':
                        from Crypto.Cipher import AES
                        assert 'URI' in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=AES-128, but no URI found'
                        if 'https://' in attribs['URI']:
                            key = self.download_file(attribs['URI'].strip('"'))  # key = self.download_file(base_key_url+attribs['URI'].strip('"'))
                            print(attribs['URI'].strip('"'))
                        else:
                            key = self.download_file('m3u8http://hls.fra.rtlnow.de/hls-vod-enc-key/vodkey.bin')
                        assert len(key) == 16, '[hlsclient::handle_basic_m3u] EXT-X-KEY: downloaded key file has bad length'
                        if 'IV' in attribs:
                            assert attribs['IV'].lower().startswith('0x'), '[hlsclient::handle_basic_m3u] EXT-X-KEY: IV attribute has bad format'
                            iv = attribs['IV'][2:].zfill(32).decode('hex')
                            assert len(iv) == 16, '[hlsclient::handle_basic_m3u] EXT-X-KEY: IV attribute has bad length'
                        else:
                            iv = '\0'*8 + struct.pack('>Q', seq)
                        enc = AES.new(key, AES.MODE_CBC, iv)
                    else:
                        assert False, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=%s unknown' % attribs['METHOD']
                elif tag == '#EXT-X-PROGRAM-DATE-TIME':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-PROGRAM-DATE-TIME'
                    pass
                elif tag == '#EXT-X-ALLOW-CACHE':
                    pass
                elif tag == '#EXT-X-ENDLIST':
                    assert not attribs
                    yield None
                    return
                elif tag == '#EXT-X-STREAM-INF':
                    os.remove(STREAM_PFILE)
                    self.stop()
                elif tag == '#EXT-X-DISCONTINUITY':
                    assert not attribs
                    pass
                elif tag == '#EXT-X-VERSION':
                    assert len(attribs) == 1
                    if int(attribs[0]) > SUPPORTED_VERSION:
                        pass
                else:
                    pass
                    os.remove(STREAM_PFILE)
                    self.stop()
            else:
                yield (seq, enc, duration, targetduration, line)
                seq += 1

    def handle_basic_m3u(self, hlsUrl):
        seq = 1
        enc = None
        nextlen = 5
        duration = 5
        for line in self.gen_m3u(hlsUrl):
            if "#EXT-X-PLAYLIST-TYPE:VOD" in line:
                line.replace("#EXT-X-PLAYLIST-TYPE:VOD", "")
                continue
            if line.startswith('#EXT'):
                tag, attribs = self.parse_m3u_tag(line)
                if tag == '#EXTINF':
                    duration = float(attribs[0])
                elif tag == '#EXT-X-TARGETDURATION':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-TARGETDURATION'
                    targetduration = int(attribs[0])
                    pass
                elif tag == '#EXT-X-MEDIA-SEQUENCE':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-MEDIA-SEQUENCE'
                    seq = int(attribs[0])
                elif tag == '#EXT-X-KEY':
                    attribs = self.parse_kv(attribs, ('METHOD', 'URI', 'IV'))
                    assert 'METHOD' in attribs, '[hlsclient::handle_basic_m3u] expected METHOD in EXT-X-KEY'
                    if attribs['METHOD'] == 'NONE':
                        assert 'URI' not in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=NONE, but URI found'
                        assert 'IV' not in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=NONE, but IV found'
                        enc = None
                    elif attribs['METHOD'] == 'AES-128':
                        from Crypto.Cipher import AES
                        assert 'URI' in attribs, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=AES-128, but no URI found'
                        key = self.download_file(attribs['URI'].strip('"'))
                        assert len(key) == 16, '[hlsclient::handle_basic_m3u] EXT-X-KEY: downloaded key file has bad length'
                        if 'IV' in attribs:
                            assert attribs['IV'].lower().startswith('0x'), '[hlsclient::handle_basic_m3u] EXT-X-KEY: IV attribute has bad format'
                            iv = attribs['IV'][2:].zfill(32).decode('hex')
                            assert len(iv) == 16, '[hlsclient::handle_basic_m3u] EXT-X-KEY: IV attribute has bad length'
                        else:
                            iv = '\0'*8 + struct.pack('>Q', seq)
                        enc = AES.new(key, AES.MODE_CBC, iv)
                    else:
                        assert False, '[hlsclient::handle_basic_m3u] EXT-X-KEY: METHOD=%s unknown' % attribs['METHOD']
                elif tag == '#EXT-X-PROGRAM-DATE-TIME':
                    assert len(attribs) == 1, '[hlsclient::handle_basic_m3u] too many attribs in EXT-X-PROGRAM-DATE-TIME'
                    pass
                elif tag == '#EXT-X-ALLOW-CACHE':
                    pass
                elif tag == '#EXT-X-ENDLIST':
                    assert not attribs
                    yield None
                    return
                elif tag == '#EXT-X-STREAM-INF':
                    os.remove(STREAM_PFILE)
                    self.stop()
                elif tag == '#EXT-X-DISCONTINUITY':
                    assert not attribs
                elif tag == '#EXT-X-VERSION':
                    assert len(attribs) == 1
                    if int(attribs[0]) > SUPPORTED_VERSION:
                        pass  # print '[hlsclient::handle_basic_m3u] file version %s exceeds supported version %d; some things might be broken' % (attribs[0], SUPPORTED_VERSION)
                else:
                    pass
            else:
                pass
                yield (seq, enc, duration, targetduration, line)
                seq += 1

    def player_pipe(self, queue, videopipe):
        while not self._stop:
            block = queue.get(block=True)
            if block is None:
                return
            videopipe.write(block)
            if not self._downLoading:
                pass
                self._downLoading = True

    def play(self, header):
        self.header = header
        if os.path.exists(STREAM_PFILE):
            os.remove(STREAM_PFILE)
        videopipe = open(STREAM_PFILE, "w+b")
        variants = []
        variant = None
        for line in self.gen_m3u(self.url):
            if line.startswith('#EXT'):
                tag, attribs = self.parse_m3u_tag(line)
                if tag == '#EXT-X-STREAM-INF':
                    variant = attribs
            elif variant:
                variants.append((line, variant))
                variant = None
        if len(variants) == 1:
            self.url = urljoin(self.url, variants[0][0])
        elif len(variants) >= 2:
            autoChoice = {}
            for i, (vurl, vattrs) in enumerate(variants):
                for attr in vattrs:
                    key, value = attr.split('=')
                    key = key.strip()
                    value = value.strip().strip('"')
                    if key == 'BANDWIDTH':
                        autoChoice[i] = int(value)
                    elif key == 'PROGRAM-ID':
                        pass  # print 'program %s' % value,
                    elif key == 'CODECS':
                        pass  # print 'codec %s' % value,
                    elif key == 'RESOLUTION':
                        pass  # print 'resolution %s' % value,
                    else:
                        pass
            choice = max(autoChoice.iteritems(), key=operator.itemgetter(1))[0]
            self.url = urljoin(self.url, variants[choice][0])
        queue = Queue.Queue(1024)  # 1024 blocks of 4K each ~ 4MB buffer
        self.thread = threading.Thread(target=self.player_pipe, args=(queue, videopipe))
        self.thread.start()
        last_seq = -1
        targetduration = 5
        changed = 0
#        try:
        while self.thread.isAlive():
            if self._stop:
                self.hread._Thread__stop()
            medialist = list(self.handle_basic_m3u(self.url))
            if None in medialist:
                # choose to start playback at the start, since this is a VOD stream
                pass
            else:
                # choose to start playback three files from the end, since this is a live stream
                medialist = medialist[-3:]
            for media in medialist:
                try:
                    if media is None:
                        queue.put(None, block=True)
                        return
                    seq, enc, duration, targetduration, media_url = media
                    if seq > last_seq:
                        for chunk in self.download_chunks(urljoin(self.url, media_url)):
                            if enc:
                                chunk = enc.decrypt(chunk)
                            queue.put(chunk, block=True)
                        last_seq = seq
                        changed = 1
                except:
                    pass

            self._sleeping = True
            if changed == 1:
                # initial minimum reload delay
                time.sleep(duration)
            elif changed == 0:
                # first attempt
                time.sleep(targetduration*0.5)
            elif changed == -1:
                # second attempt
                time.sleep(targetduration*1.5)
            else:
                # third attempt and beyond
                time.sleep(targetduration*3.0)
            self._sleeping = False
            changed -= 1

    def stop(self):
        self._stop = True
        self._downLoading = False
        if self.thread:
            self.thread._Thread__stop()
        pass  # print '[hlsclient::stop] Stopping Main hlsclient thread'
        self._Thread__stop()


if __name__ == '__main__':
    try:
        h = hlsclient()
        h.setUrl(sys.argv[1])
        header = ""
        global STREAM_PFILE
        STREAM_PFILE = sys.argv[3]
        if (sys.argv[2]) == '1':
            pass  # print "Here in going in play"
            h.play(header)
    except:
        pass
        h.stop()
