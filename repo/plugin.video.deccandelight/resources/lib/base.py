"""
Base deccandelight Scraper class
Copyright (C) 2016 Gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import json
import re
import requests
import base64
import six
from six.moves import urllib_parse
from bs4 import BeautifulSoup, SoupStrainer
from kodi_six import xbmc, xbmcaddon, xbmcvfs
from resources.lib import jsunpack
import resolveurl

_addon = xbmcaddon.Addon()
_addonname = _addon.getAddonInfo('name')
_version = _addon.getAddonInfo('version')
_addonID = _addon.getAddonInfo('id')
_icon = _addon.getAddonInfo('icon')
_fanart = _addon.getAddonInfo('fanart')
_path = _addon.getAddonInfo('path')
_ipath = _path + '/resources/images/'
_settings = _addon.getSetting
_timeout = _settings('timeout')
PY2 = six.PY2
LOGINFO = xbmc.LOGNOTICE if PY2 else xbmc.LOGINFO

mozhdr = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'}
ioshdr = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0_1 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A402 Safari/604.1'}
droidhdr = {'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G610F Build/LMY48Z)'}
jiohdr = {'User-Agent': 'ExoPlayerDemo/5.2.0 (Linux;Android 6.0.1) ExoPlayerLib/2.3.0'}

if PY2:
    import HTMLParser
    _html_parser = HTMLParser.HTMLParser()
else:
    import html
    _html_parser = html


class Scraper(object):

    def __init__(self):
        self.ipath = _ipath
        self.hdr = mozhdr
        self.dhdr = droidhdr
        self.jhdr = jiohdr
        self.ihdr = ioshdr
        self.PY2 = PY2
        self.parser = _html_parser
        self.settings = _settings
        self.adult = _settings('adult') == 'true'
        self.mirror = _settings('mirror') == 'true'
        self.nicon = self.ipath + 'next.png'

    def get_nicon(self):
        return self.nicon

    def log(self, text, caption=None):
        if not caption:
            caption = '@@@@DeccanDelight log'
        xbmc.log('{} = {}'.format(caption, text), LOGINFO)

    def get_SearchQuery(self, sitename):
        keyboard = xbmc.Keyboard()
        keyboard.setHeading('Search ' + sitename)
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_text = keyboard.getText()

        return search_text

    def get_vidhost(self, url):
        """
        Trim the url to get the video hoster
        :return vidhost
        """
        parts = url.split('/')[2].split('.')
        vidhost = '{}.{}'.format(parts[len(parts) - 2], parts[len(parts) - 1])
        return vidhost

    def resolve_media(self, url, videos, vidtxt=''):
        non_str_list = ['olangal.', 'desihome.', 'thiruttuvcd', '.filmlinks4u', '#', '/t.me/',
                        'cineview', 'bollyheaven', 'videolinkz', 'moviefk.co', 'goo.gl', '/ads/',
                        'imdb.', 'mgid.', 'atemda.', 'movierulz.ht', 'facebook.', 'twitter.',
                        'm2pub', 'abcmalayalam', 'india4movie.co', 'embedupload.', 'bit.ly',
                        'tamilraja.', 'multiup.', 'filesupload.', 'fileorbs.', 'tamil.ws',
                        'insurance-donate.', '.blogspot.', 'yodesi.net', 'desi-tashan.',
                        'yomasti.co/ads', 'ads.yodesi', 'mylifeads.', 'yaartv.', '/cdn-cgi/'
                        'steepto.', '/movierulztv', '/email-protection', 'oneload.xyz']

        dhoolembed = ['thiraione.com', 'thiraitwo.com', 'thiraithree.com', 'thiraifour.com',
                      'thiraifive.com', 'thiraisix.com', 'tamilalpha.com', 'tamilbeta.com',
                      'tamilbliss.com', 'thirailight.com', 'malarnaal.com']

        embed_list = ['cineview', 'bollyheaven', 'videolinkz', 'vidzcode', 'escr.',
                      'embedzone', 'embedsr', 'fullmovie-hd', 'links4.pw', 'esr.',
                      'embedscr', 'embedrip', 'movembed', 'power4link.us', 'adly.biz',
                      'watchmoviesonline4u', 'nobuffer.info', 'yomasti.co', 'hd-rulez.',
                      'techking.me', 'onlinemoviesworld.xyz', 'cinebix.com', 'vids.xyz',
                      'desihome.', 'loan-', 'filmshowonline.', 'hinditwostop.', 'media.php',
                      'hindistoponline', 'telly-news.', 'tellytimes.', 'tellynews.', 'tvcine.',
                      'business-', 'businessvoip.', 'toptencar.', 'serialinsurance.',
                      'youpdates', 'loanadvisor.', 'tamilray.', 'embedrip.', 'xpressvids.',
                      'beststopapne.', 'bestinforoom.', '?trembed=', 'tamilserene.',
                      'tvnation.', 'techking.', 'etcscrs.', 'etcsr1.', 'etcrips.', 'etcsrs.']

        headers = {}
        if '|' in url:
            url, hdrs = url.split('|')
            hitems = hdrs.split('&')
            for hitem in hitems:
                hdr, value = hitem.split('=')
                headers.update({hdr: value})

        if url.startswith('magnet:'):
            if resolveurl.HostedMediaFile(url):
                vidhost = '[COLOR red]Magnet[/COLOR]'
                r = re.search(r'(\d+(?:p|mb|gb))', url.replace('%20', ' '), re.I)
                if r:
                    vidhost = '{0} [COLOR gold]{1}[/COLOR]'.format(vidhost, r.group(1))
                if vidtxt != '':
                    vidhost += ' | %s' % vidtxt
                if (vidhost, url) not in videos:
                    videos.append((vidhost, url))

        elif 'filmshowonline.net/media/' in url:
            try:
                headers.update(self.hdr)
                r = requests.get(url, headers=headers)
                clink = r.text
                cookies = r.cookies
                eurl = re.findall(r"var\s*height.+?url:\s*'([^']+)", clink, re.DOTALL)[0]
                if not eurl.startswith('http'):
                    eurl = 'https:' + eurl
                enonce = re.findall(r"var\s*height.+?nonce.+?'([^']+)", clink, re.DOTALL)[0]
                evid = re.findall(r"var\s*height.+?link_id:\s*([^\s]+)", clink, re.DOTALL)[0]
                values = {'echo': 'true',
                          'nonce': enonce,
                          'width': '848',
                          'height': '480',
                          'link_id': evid}
                headers = self.hdr
                headers.update({'Referer': url, 'X-Requested-With': 'XMLHttpRequest'})
                emdiv = requests.post(eurl, data=values, headers=headers, cookies=cookies).json()['embed']
                strurl = re.findall('(http[^"]+)', emdiv)[0]
                if resolveurl.HostedMediaFile(strurl):
                    vidhost = self.get_vidhost(strurl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
            except:
                pass

        elif 'cdn.jwplayer.com' in url:
            headers.update(self.hdr)
            media_id = url.split('/')[-1].split('-')[0]
            jurl = 'https://content.jwplatform.com/v2/media/{0}'.format(media_id)
            r = requests.get(jurl, headers=headers)
            if r.status_code < 400:
                vlink = r.json().get('playlist')[0].get('sources')[0].get('file')
                if vlink:
                    vidhost = self.get_vidhost(vlink)
                    if (vidhost, vlink) not in videos:
                        videos.append((vidhost, vlink))
                else:
                    self.log('Cannot resolve : {0}'.format(url))

        elif any([x in url for x in dhoolembed]):
            strurl = url.replace('/p/', '/v/') + '.m3u8|Referer={0}&User-Agent=iPad'.format(url)
            vidhost = self.get_vidhost(strurl)
            if vidtxt != '':
                vidhost += ' | %s' % vidtxt
            if (vidhost, strurl) not in videos:
                videos.append((vidhost, strurl))

        elif 'justmoviesonline.com' in url:
            headers.update(self.hdr)
            html = requests.get(url, headers=headers).text
            src = re.search(r"atob\('(.*?)'", html)
            if src:
                src = src.group(1)
                src = base64.b64decode(src).decode('utf-8')
                try:
                    strurl = re.findall('file":"(.*?)"', src)[0]
                    vidhost = 'GVideo'
                    strurl = urllib_parse.quote_plus(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                except:
                    pass
                try:
                    strurl = re.findall('''source src=["'](.*?)['"]''', src)[0]
                    vidhost = self.get_vidhost(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                except:
                    pass
            elif '?id=' in url:
                src = eval(re.findall('Loading.+?var.+?=([^;]+)', html, re.DOTALL)[0])
                for item in src:
                    if 'http' in item and 'justmovies' not in item:
                        strurl = item
                strurl += url.split('?id=')[1]
                strurl += '.mp4|User-Agent={}'.format(mozhdr['User-Agent'])
                vidhost = 'GVideo'
                strurl = urllib_parse.quote_plus(strurl)
                if (vidhost, strurl) not in videos:
                    videos.append((vidhost, strurl))

        elif 'videohost.site' in url or 'videohost1.com' in url:
            try:
                headers.update(self.hdr)
                html = requests.get(url, headers=headers).text
                pdata = eval(re.findall(r'Run\((.*?)\)', html)[0])
                pdata = base64.b64decode(pdata).decode('utf-8')
                linkcode = jsunpack.unpack(pdata).replace('\\', '')
                sources = json.loads(re.findall(r'sources:(.*?\}\])', linkcode)[0])
                for source in sources:
                    strurl = source['file'] + '|Referer={}'.format(url)
                    vidhost = self.get_vidhost(url) + ' | GVideo | {}'.format(source['label'])
                    strurl = urllib_parse.quote_plus(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
            except:
                pass

        elif 'akamaihd.' in url:
            vidhost = self.get_vidhost(url)
            if (vidhost, url) not in videos:
                videos.append((vidhost, url))

        elif 'articlesnew.' in url or 'newscurrent.co' in url:
            url = 'https://articlesnew.com/medium/?' + url.split('?')[-1]
            headers.update(self.hdr)
            html = requests.get(url, headers=headers).text
            r = re.findall(r'''<form.+?action="([^"]+).+?name='([^']+)'\s*value='([^']+)''', html, re.DOTALL)
            if r:
                purl, name, value = r[0]
                html = requests.post(purl, data={name: value}, headers=headers).text
                s = re.findall(r"<iframe.+?src='([^']+)", html)
                if s:
                    strurl = s[0]
                    if 'articlesnew.com' in strurl:
                        strurl = strurl.split('url=')[-1]
                    if 'hls' in strurl and 'videoapne' in strurl:
                        strurl = strurl.replace('hls/,', '')
                        strurl = strurl.replace(',.urlset/master.m3u8', '/v.mp4')
                    vidhost = self.get_vidhost(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))

        elif 'videohost2.com' in url:
            headers.update(self.hdr)
            html = requests.get(url, headers=headers).text

            try:
                pdata = eval(re.findall(r'Loading video.+?(\[.+?\]);', html, re.DOTALL)[0])
                if 'id=' in url:
                    strurl = pdata[7] + url.split('=')[1] + pdata[9]
                else:
                    strurl = pdata[7]
                vidhost = self.get_vidhost(url) + ' | GVideo'
                strurl = urllib_parse.quote_plus(strurl + '|Referer={}'.format(url))
                if (vidhost, strurl) not in videos:
                    videos.append((vidhost, strurl))
            except:
                pass

            try:
                pdata = re.findall(r"atob\('([^']+)", html)[0]
                pdata = base64.b64decode(pdata).decode('utf-8')
                strurl = re.findall(r"source\ssrc='([^']+)", pdata)[0] + '|Referer={}'.format(url)
                vidhost = self.get_vidhost(url)
                strurl = urllib_parse.quote_plus(strurl)
                if (vidhost, strurl) not in videos:
                    videos.append((vidhost, strurl))
            except:
                pass

        elif 'hindistoponline' in url or 'hindigostop' in url:
            headers.update(self.hdr)
            url = url.replace('www.hindistoponline.com', 'hindigostop.com')
            html = requests.get(url, headers=headers).text

            try:
                strurl = re.findall(r'source:\s*"([^"]+)', html)[0]
                vidhost = self.get_vidhost(strurl)
                strurl = urllib_parse.quote_plus(strurl + '|User-Agent={}&Referer={}'.format(mozhdr['User-Agent'], url))
                if (vidhost, strurl) not in videos:
                    videos.append((vidhost, strurl))
            except:
                pass

            try:
                strurl = re.findall('''(?i)<iframe.+?src=["']([^'"]+)''', html)[0]
                if resolveurl.HostedMediaFile(strurl):
                    vidhost = self.get_vidhost(strurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                else:
                    self.log('ResolveUrl cannot resolve : {}'.format(url))
            except:
                pass

        elif 'arivakam.' in url:
            headers.update(self.hdr)
            html = requests.get(url, headers=headers, verify=False).text
            rurl = urllib_parse.urljoin(url, '/')
            strurl = re.search(r'"file":"([^"]+)', html)
            if strurl:
                embedurl = strurl.group(1)
                if 'playallu' in embedurl:
                    vidhost, strurl = self.playallu(embedurl, rurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                else:
                    vidhost = self.get_vidhost(embedurl)
                    if (vidhost, embedurl) not in videos:
                        videos.append((vidhost, embedurl))
            else:
                embedurl = re.search(r'<iframe.+?src="([^"]+)', html)
                if embedurl:
                    embedurl = embedurl.group(1)
                    if 'playallu' in embedurl:
                        vidhost, strurl = self.playallu(embedurl, rurl)
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                    else:
                        vidhost = self.get_vidhost(embedurl)
                        if (vidhost, embedurl) not in videos:
                            videos.append((vidhost, embedurl))
            sources = re.findall(r'"linkserver".+?video="([^"]+)', html)
            for embedurl in sources:
                headers.update({'Referer': url})
                if 'playallu' in embedurl:
                    vidhost, strurl = self.playallu(embedurl, rurl)
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                elif embedurl.startswith('api_player') and 'type=default' not in embedurl:
                    ehtml = requests.get(rurl + 'player/' + embedurl, headers=headers, verify=False).text
                    linkcode = jsunpack.unpack(ehtml).replace('\\', '')
                    elink = re.findall(r'''file"\s*:\s*"([^"]+)''', linkcode)
                    if elink:
                        strurl = elink[0]
                        vidhost = self.get_vidhost(strurl)
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))

        elif 'tamildbox' in url or 'tamilhdbox' in url:
            if 'embed' in url:
                thdr = mozhdr
                thdr['Referer'] = url
                r = requests.get(url, headers=thdr).text
                match = re.search(r"domainStream\s*=\s*([^;]+)", r)
                if match:
                    surl = re.findall('file":"([^"]+)', match.group(1))[0]

                    if 'vidyard' in surl:
                        surl += '|Referer=https://play.vidyard.com/'
                    else:
                        surl = surl.replace('/hls/', '/own1hls/2020/')
                        surl += '|Referer=https://embed1.tamildbox.tips/'

                    surl += '&User-Agent={}'.format(mozhdr['User-Agent'])
                else:
                    surl = url.replace('hls_vast', 'hls').replace('.tamildbox.tips', '.tamilgun.tv')
                    if '.m3u8' not in surl:
                        surl += '/playlist.m3u8'
                vidhost = self.get_vidhost(surl)
                if (vidhost, surl) not in videos:
                    videos.append((vidhost, surl))
            else:
                link = requests.get(url, headers=mozhdr).text

                try:
                    mlink = SoupStrainer('div', {'class': re.compile('^video-player-content')})
                    videoclass = BeautifulSoup(link, "html.parser", parse_only=mlink)
                    vlinks = videoclass.find_all('iframe')
                    for vlink in vlinks:
                        iurl = vlink.get('src')
                        if iurl.startswith('//'):
                            iurl = 'https:' + iurl
                        if 'playallu.' in iurl:
                            vidhost, strlink = self.playallu(iurl, url)
                            if (vidhost, strlink) not in videos:
                                videos.append((vidhost, strlink))
                        else:
                            if resolveurl.HostedMediaFile(iurl):
                                vidhost = self.get_vidhost(iurl)
                                if (vidhost, iurl) not in videos:
                                    videos.append((vidhost, iurl))
                except:
                    import traceback
                    traceback.print_exc()
                    pass

                try:
                    mlink = SoupStrainer('div', {'class': 'player-api'})
                    videoclass = BeautifulSoup(link, "html.parser", parse_only=mlink)
                    vlinks = videoclass.find_all('iframe')
                    for item in vlinks:
                        blink = item.get('src')
                        if 'cdn.jwplayer.com' in blink:
                            headers.update(self.hdr)
                            media_id = blink.split('/')[-1].split('-')[0]
                            jurl = 'https://content.jwplatform.com/v2/media/{0}'.format(media_id)
                            jd = requests.get(jurl, headers=headers).json()
                            vlink = jd.get('playlist')[0].get('sources')[0].get('file')
                            if vlink:
                                vidhost = self.get_vidhost(vlink)
                                if (vidhost, vlink) not in videos:
                                    videos.append((vidhost, vlink))
                        else:
                            self.log('Cannot resolve : {0}'.format(blink))
                except:
                    pass

                try:
                    etext = re.search(r'var\s*vidorev_jav_js_object\s*=\s*([^;]+)', link, re.DOTALL)
                    if etext:
                        glink = json.loads(etext.group(1)).get('single_video_url')
                        vidhost = self.get_vidhost(glink)
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    etext = re.search(r'file:\s*"([^"]+).+?type:\s*"([^"]+)', link, re.DOTALL)
                    if etext:
                        glink = etext.group(1)
                        vidhost = self.get_vidhost(glink) + ' | {}'.format(etext.group(2))
                        if 'http' not in glink:
                            glink = 'http:' + glink
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                    etext = re.search(r'file":\s*"([^"]+).+?label":\s*"([^"]+)', link, re.DOTALL)
                    if etext:
                        glink = etext.group(1)
                        vidhost = self.get_vidhost(glink) + ' | {}'.format(etext.group(2))
                        if 'http' not in glink:
                            glink = 'http:' + glink
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    mlink = SoupStrainer('div', {'id': 'player-embed'})
                    dclass = BeautifulSoup(link, "html.parser", parse_only=mlink)
                    if 'unescape' in str(dclass):
                        etext = re.findall("unescape.'[^']*", str(dclass))[0]
                        etext = urllib_parse.unquote(etext)
                        dclass = BeautifulSoup(etext, "html.parser")
                    glink = dclass.iframe.get('src')
                    if resolveurl.HostedMediaFile(glink):
                        vidhost = self.get_vidhost(glink)
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    mlink = SoupStrainer('div', {'class': re.compile('^item-content')})
                    dclass = BeautifulSoup(link, "html.parser", parse_only=mlink)
                    glink = dclass.p.iframe.get('src')
                    if resolveurl.HostedMediaFile(glink):
                        vidhost = self.get_vidhost(glink)
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    if 'p,a,c,k,e,d' in link:
                        linkcode = jsunpack.unpack(link).replace('\\', '')
                        glink = re.findall(r"file\s*:\s*'(.*?)'", linkcode)[0]
                    if 'youtu.be' in glink:
                        glink = 'https://docs.google.com/vt?id=' + glink[16:]
                    if resolveurl.HostedMediaFile(glink):
                        vidhost = self.get_vidhost(glink)
                        if (vidhost, glink) not in videos:
                            videos.append((vidhost, glink))
                except:
                    pass

                try:
                    codes = re.findall(r'"return loadEP.([^,]*),(\d*)', link)
                    for ep_id, server_id in codes:
                        burl = 'https://{}/actions.php?case=loadEP&ep_id={}&server_id={}'.format(url.split('/')[2], ep_id, server_id)
                        bhtml = requests.get(burl, headers=mozhdr).text
                        blink = re.findall('<iframe.+?src="([^"]+)', bhtml, re.IGNORECASE)[0]
                        if blink.startswith('//'):
                            blink = 'https:' + blink
                        if 'googleapis' in blink:
                            blink = 'https://drive.google.com/open?id=' + re.findall('docid=([^&]*)', blink)[0]
                            vidhost = 'GVideo'
                            if (vidhost, blink) not in videos:
                                videos.append((vidhost, blink))
                        elif 'cdn.jwplayer.com' in blink:
                            headers.update(self.hdr)
                            media_id = blink.split('/')[-1].split('-')[0]
                            jurl = 'https://content.jwplatform.com/v2/media/{0}'.format(media_id)
                            jd = requests.get(jurl, headers=headers).json()
                            vlink = jd.get('playlist')[0].get('sources')[0].get('file')
                            if vlink:
                                vidhost = self.get_vidhost(vlink)
                                if (vidhost, vlink) not in videos:
                                    videos.append((vidhost, vlink))
                            else:
                                self.log('Cannot resolve : {0}'.format(blink))
                        elif 'tamildbox.' in blink:
                            if 'embed' in blink:
                                thdr = mozhdr
                                thdr['Referer'] = blink
                                r = requests.get(blink, headers=thdr).text
                                match = re.search(r"domainStream\s*=\s*'([^']+)", r)
                                if match:
                                    surl = match.group(1)
                                    if 'vidyard' in surl:
                                        surl += '|Referer=https://play.vidyard.com/'
                                    else:
                                        if '.php' not in surl:
                                            if '.m3u8' not in surl:
                                                surl += '/playlist.m3u8'
                                        surl = surl.replace('/hls/', '/hls1mp4/2020/')
                                        surl += '|Referer=https://embed1.tamildbox.tips/'
                                    surl += '&User-Agent={}'.format(mozhdr['User-Agent'])
                                else:
                                    surl = blink.replace('hls_vast', 'hls')
                                    surl = surl.replace('.tamildbox.tips', '.tamilgun.tv')
                                    if '.m3u8' not in surl:
                                        surl += '/playlist.m3u8'
                                vidhost = self.get_vidhost(surl)
                                if (vidhost, surl) not in videos:
                                    videos.append((vidhost, surl))
                            else:
                                link = requests.get(blink, headers=mozhdr).text
                                etext = re.search(r'file:\s*"([^"]+).+?type:\s*"([^"]+)', link, re.DOTALL)
                                if etext:
                                    glink = etext.group(1)
                                    vidhost = self.get_vidhost(glink) + ' | {}'.format(etext.group(2))
                                    if glink.startswith('//'):
                                        glink = 'https:' + glink
                                    if (vidhost, glink) not in videos:
                                        videos.append((vidhost, glink))
                                etext = re.search(r'file":\s*"([^"]+).+?label":\s*"([^"]+)', link, re.DOTALL)
                                if etext:
                                    glink = etext.group(1)
                                    vidhost = self.get_vidhost(glink) + ' | {}'.format(etext.group(2))
                                    if glink.startswith('//'):
                                        glink = 'https:' + glink
                                    if (vidhost, glink) not in videos:
                                        videos.append((vidhost, glink))
                        else:
                            if resolveurl.HostedMediaFile(blink):
                                vidhost = self.get_vidhost(blink)
                                if (vidhost, blink) not in videos:
                                    videos.append((vidhost, blink))
                            else:
                                self.log('Resolveurl cannot resolve : {}'.format(blink))
                except:
                    pass

        elif 'tamilthee.' in url:
            vidhost = self.get_vidhost(url)
            vidurl = url.replace('/p/', '/v/') + '.m3u8'
            if (vidhost, vidurl) not in videos:
                videos.append((vidhost, vidurl))

        elif 'vidnext.net' in url:
            if 'streaming.php' in url:
                headers.update(self.hdr)
                url = 'https:' + url if url.startswith('//') else url
                chtml = requests.get(url, headers=headers).text
                clink = SoupStrainer('ul', {'class': 'list-server-items'})
                csoup = BeautifulSoup(chtml, "html.parser", parse_only=clink)
                citems = csoup.find_all('li')
                for citem in citems:
                    link = citem.get('data-video')
                    if link and 'vidnext.net' not in link:
                        if resolveurl.HostedMediaFile(link):
                            vidhost = self.get_vidhost(link)
                            if vidtxt != '':
                                vidhost += ' | %s' % vidtxt
                            if (vidhost, link) not in videos:
                                videos.append((vidhost, link))
                        else:
                            self.log('ResolveUrl cannot resolve : {}'.format(link))

        elif '.box.' in url and '.mp4' in url:
            vidhost = self.get_vidhost(url)
            if (vidhost, url) not in videos:
                videos.append((vidhost, url))

        elif 'files.' in url and url.endswith('.mp4'):
            vidhost = self.get_vidhost(url)
            if (vidhost, url) not in videos:
                videos.append((vidhost, url))

        elif any([x in url for x in embed_list]):
            url = url.replace('hd-rulez.info/', 'business-mortgage.biz/')
            vidcount = 0
            headers.update(self.hdr)
            clink = requests.get(url, headers=headers).text
            csoup = BeautifulSoup(clink, "html.parser")

            try:
                url2 = csoup.find('meta', {'http-equiv': 'refresh'}).get('content').split('URL=')[-1]
                if any([x in url2 for x in embed_list]):
                    clink = requests.get(url2, headers=headers).text
                    csoup = BeautifulSoup(clink, "html.parser")
                else:
                    self.log('Cannot Process : {}'.format(url2))
            except:
                pass

            try:
                links = csoup.find_all('iframe')
                headers.update({'Referer': url})
                for link in links:
                    strurl = link.get('src')
                    if 'about:' in strurl:
                        strurl = link.get('data-phast-src')
                    # self.log('-------> Scraped link : %s' % strurl)
                    if any([x in strurl for x in ['apnevideotwo', 'player.business']]):
                        vidhost = 'CDN Direct'
                        if vidtxt:
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    elif 'apnevideoone' in strurl:
                        shtml = requests.get(strurl, headers=headers).text
                        vidurl = re.findall(r'link_play\s*=\s*\[{"file":"([^"]+)', shtml)[0]
                        vidurl = vidurl.encode('utf8') if PY2 else vidurl
                        vhdr = {'Origin': 'https://apnevideoone.co'}
                        vidurl = '{0}|{1}'.format(vidurl, urllib_parse.urlencode(vhdr))
                        vidhost = 'CDN Apne'
                        if vidtxt:
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, vidurl) not in videos:
                            videos.append((vidhost, vidurl))
                        vidcount += 1
                    elif 'flow.' in strurl:
                        shtml = requests.get(strurl, headers=headers).text
                        vidurl = re.findall(r'"(?:file|src)":"([^"]+m3u8)', shtml)[0]
                        vidurl = vidurl.encode('utf8') if PY2 else vidurl
                        vhdr = {'Referer': strurl}
                        vidurl += '|{}'.format(urllib_parse.urlencode(vhdr))
                        vidhost = 'CDN'
                        if vidtxt:
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, vidurl) not in videos:
                            videos.append((vidhost, vidurl))
                        vidcount += 1
                    elif 'drivewire.' in strurl:
                        vid = strurl.split('id=')[-1]
                        parts = urllib_parse.urlparse(strurl)
                        vidurl = '{0}://{1}/hls/{2}/{2}.m3u8'.format(parts.scheme, parts.netloc, vid)
                        vidhost = 'DriveWire'
                        if vidtxt:
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, vidurl) not in videos:
                            videos.append((vidhost, vidurl))
                        vidcount += 1
                    elif not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                        # self.log('-------> sending to resolveurl for checking : %s' % strurl)
                        if resolveurl.HostedMediaFile(strurl):
                            vidhost = self.get_vidhost(strurl)
                            if vidtxt != '':
                                vidhost += ' | %s' % vidtxt
                            if (vidhost, strurl) not in videos:
                                videos.append((vidhost, strurl))
                            vidcount += 1
                        else:
                            self.log('Resolveurl cannot resolve : {}'.format(strurl))
            except Exception as e:
                # import traceback
                # traceback.print_exc()
                self.log(e)
                pass

            try:
                sources = re.findall(r'sources:\s*([^\]]+)', clink, re.DOTALL)[0]
                links = re.findall(r'''src:\s*['"]([^"']+)''', sources)
                for strurl in links:
                    # self.log('-------> Scraped link : %s' % strurl)
                    vidhost = self.get_vidhost(strurl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                    vidcount += 1
            except:
                pass

            try:
                r = re.search(r'jwplayer\("container"\).setup\({\s*\n\s*file:\s*"([^"]+)', clink)
                if r:
                    strurl = r.group(1)
                    vidhost = self.get_vidhost(strurl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                    vidcount += 1
            except:
                pass

            try:
                plink = csoup.find('a', {'class': 'main-button dlbutton'})
                strurl = plink.get('href')
                if not any([x in strurl for x in non_str_list]):
                    if resolveurl.HostedMediaFile(strurl):
                        vidhost = self.get_vidhost(strurl)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve : {}'.format(strurl))
            except:
                pass

            try:
                plink = csoup.find('div', {'class': 'aio-pulse'})
                strurl = plink.find('a')['href']
                if not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                    if resolveurl.HostedMediaFile(strurl):
                        vidhost = self.get_vidhost(strurl)
                        if vidtxt != '':
                            vidhost += ' | {}'.format(vidtxt)
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve : {}'.format(strurl))
            except:
                pass

            try:
                plink = csoup.find('div', {'class': re.compile('entry-content')})
                strurl = plink.find('a')['href']
                if not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                    if resolveurl.HostedMediaFile(strurl):
                        vidhost = self.get_vidhost(strurl)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve : {}'.format(strurl))
            except:
                pass

            try:
                for linksSection in csoup.find_all('embed'):
                    strurl = linksSection.get('src')
                    if not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                        if resolveurl.HostedMediaFile(strurl):
                            vidhost = self.get_vidhost(strurl)
                            if vidtxt != '':
                                vidhost += ' | %s' % vidtxt
                            if (vidhost, strurl) not in videos:
                                videos.append((vidhost, strurl))
                            vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve : {}'.format(strurl))
            except:
                pass

            try:
                plink = csoup.find('div', {'id': 'Proceed'})
                strurl = plink.find('a')['href']
                if not any([x in strurl for x in non_str_list]) and not any([x in strurl for x in embed_list]):
                    if resolveurl.HostedMediaFile(strurl):
                        vidhost = self.get_vidhost(strurl)
                        if vidtxt != '':
                            vidhost += ' | %s' % vidtxt
                        if (vidhost, strurl) not in videos:
                            videos.append((vidhost, strurl))
                        vidcount += 1
                    else:
                        self.log('Resolveurl cannot resolve : {}'.format(strurl))
            except:
                pass

            try:
                vid = re.findall(r'tune\.pk[^?]+\?vid=([^&]+)', clink)[0]
                strurl = 'https://tune.pk/video/{vid}/'.format(vid=vid)
                if resolveurl.HostedMediaFile(strurl):
                    vidhost = self.get_vidhost(strurl)
                    if vidtxt != '':
                        vidhost += ' | %s' % vidtxt
                    if (vidhost, strurl) not in videos:
                        videos.append((vidhost, strurl))
                    vidcount += 1
                else:
                    self.log('Resolveurl cannot resolve : {}'.format(strurl))
            except:
                pass

            try:
                vidurl = re.search(r'file\s*:\s*"([^"]+)', clink)
                if vidurl:
                    vidurl = vidurl.group(1)
                    vidhost = self.get_vidhost(vidurl)
                    if (vidhost, vidurl) not in videos:
                        videos.append((vidhost, vidurl))
                    vidcount += 1
            except:
                pass

            if vidcount == 0:
                self.log('Could not process link : {}'.format(url))

        elif not any([x in url for x in non_str_list]):
            if resolveurl.HostedMediaFile(url):
                vidhost = self.get_vidhost(url)
                if 'Referer' in headers.keys():
                    url = '{0}$${1}'.format(url, headers.get('Referer'))
                if vidtxt != '':
                    vidhost += ' | %s' % vidtxt
                if (vidhost, url) not in videos:
                    videos.append((vidhost, url))
            else:
                self.log('ResolveUrl cannot resolve : {}'.format(url))

        return

    def clean_title(self, title):
        cleanup = ['Watch Online Movie', 'Watch Onilne', 'Tamil Movie ', 'Tamil Dubbed', 'WAtch ', 'Online Free',
                   'Full Length', 'Latest Telugu', 'RIp', 'DvDRip', 'DvDScr', 'Full Movie Online Free', 'Uncensored',
                   'Full Movie Online', 'Watch Online ', 'Free HD', 'Online Full Movie', 'Downlaod', 'Bluray',
                   'Full Free', 'Malayalam Movie', ' Malayalam ', 'Full Movies', 'Full Movie', 'Free Online',
                   'Movie Online', 'Watch ', 'movie online', 'Wach ', 'Movie Songs Online', 'Full Hindi', 'Korean',
                   'tamil movie songs online', 'tamil movie songs', 'movie songs online', 'Tamil Movie', ' Hindi',
                   'Hilarious Comedy Scenes', 'Super Comedy Scenes', 'Ultimate Comedy Scenes', 'Watch...', 'BDRip',
                   'Super comedy Scenes', 'Comedy Scenes', 'hilarious comedy Scenes', '...', 'Telugu Movie',
                   'Sun TV Show', 'Vijay TV Show', 'Vijay Tv Show', 'Vijay TV Comedy Show', 'Hindi Movie', 'Film',
                   'Vijay Tv Comedy Show', 'Vijay TV', 'Vijay Tv', 'Sun Tv Show', 'Download', 'Starring', u'\u2013',
                   'Tamil Full Movie', 'Tamil Horror Movie', 'Tamil Dubbed Movie', '|', '-', ' Full ', u'\u2019',
                   '/', 'Pre HDRip', '(DVDScr Audio)', 'PDVDRip', 'DVDSCR', '(HQ Audio)', 'HQ', ' Telugu', 'BRRip',
                   'DVDScr', 'DVDscr', 'PreDVDRip', 'DVDRip', 'DVDRIP', 'WEBRip', 'WebRip', 'Movie ', ' Punjabi',
                   'TCRip', 'HDRip', 'HDTVRip', 'HD-TC', 'HDTV', 'TVRip', '720p', 'DVD', 'HD', ' Dubbed', '( )',
                   '720p', '(UNCUT)', 'UNCUT', '(Clear Audio)', 'DTHRip', '(Line Audio)', ' Kannada', ' Hollywood',
                   'TS', 'CAM', 'Online Full', '[+18]', 'Streaming Free', 'Permalink to ', 'And Download', '()',
                   'Full English', ' English', 'Online', ' Tamil', ' Bengali', ' Bhojpuri', 'Print Free', 'Free']

        for word in cleanup:
            if word in title:
                title = title.replace(word, '')

        title = title.strip()
        title = title.encode('utf8') if PY2 else title
        return title

    def unescape(self, title):
        return self.parser.unescape(title)

    def playallu(self, eurl, referer):
        headers = self.hdr
        headers.update({'Referer': referer})
        epage = requests.get(eurl, headers=headers).text
        idfile = re.findall(r'var\s*idfile\s*=\s*"([^"]+)', epage)[0]
        iduser = re.findall(r'var\s*idUser\s*=\s*"([^"]+)', epage)[0]
        apiurl = re.findall(r"var\s*DOMAIN_API\s*=\s*'([^']+)", epage)[0]
        servers = eval(re.findall(r"var\s*DOMAIN_LIST_RD\s*=\s*([^;]+)", epage)[0])
        headers.update({'Referer': 'https://play.playallu.xyz/', 'Origin': 'https://play.playallu.xyz'})
        referer = urllib_parse.urljoin(referer, '/')
        data = {'referrer': referer[:-1], 'typeend': 'html'}
        jd = requests.post(apiurl + '{0}/{1}'.format(iduser, idfile), headers=headers, data=data).json()
        durs = jd.get('data')[0]
        playlist = jd.get('data')[1]
        v = jd.get('v')
        vod = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:{0}\n#EXT-X-PLAYLIST-TYPE:VOD\n".format(jd.get('tgdr'))
        server = 0
        for seg in range(len(playlist)):
            vod += "#EXTINF:{0},\n".format(durs[seg])
            vod += "https://{0}/stream/v{1}/{2}.html\n".format(servers[server], v, playlist[seg])
            server += 1
            if server == len(servers):
                server = 0
        vod += "#EXT-X-ENDLIST\n"
        vodfile = 'special://temp/__temp_{0}_playallu_vod__.m3u8'.format(self.get_vidhost(referer).split('.')[0])
        if xbmcvfs.exists(vodfile):
            xbmcvfs.delete(vodfile)
        f = xbmcvfs.File(vodfile, 'w')
        f.write(vod)
        f.close()
        vodfile = xbmc.translatePath(vodfile) if self.PY2 else xbmcvfs.translatePath(vodfile)
        master = '#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-STREAM-INF:PROGRAM-ID=1\n{0}'.format(vodfile)
        mfile = 'special://temp/__temp_{0}_playallu_master.m3u8'.format(self.get_vidhost(referer).split('.')[0])
        if xbmcvfs.exists(mfile):
            xbmcvfs.delete(mfile)
        f = xbmcvfs.File(mfile, 'w')
        f.write(master)
        f.close()
        mfile = xbmc.translatePath(mfile) if self.PY2 else xbmcvfs.translatePath(mfile)
        vidhost = 'Playallu | {0}p'.format(jd.get('quaity'))
        return vidhost, mfile
