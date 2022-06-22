"""
DeccanDelight scraper plugin
Copyright (C) 2018 gujal

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
from resources.lib.base import Scraper
from bs4 import BeautifulSoup, SoupStrainer
from six.moves import urllib_parse
import re
import requests
import json
import base64
import random
import time
from kodi_six import xbmc

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer
cache = StorageServer.StorageServer('deccandelight', 8)


class einthusan(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://einthusan.tv/'
        self.icon = self.ipath + 'einthusan.png'
        self.list = {'01Tamil': self.bu + 'launcher/?lang=tamil',
                     '02Telugu': self.bu + 'launcher/?lang=telugu',
                     '03Malayalam': self.bu + 'launcher/?lang=malayalam',
                     '04Kannada': self.bu + 'launcher/?lang=kannada',
                     '05Hindi': self.bu + 'launcher/?lang=hindi',
                     '06Bengali': self.bu + 'launcher/?lang=bengali',
                     '07Marathi': self.bu + 'launcher/?lang=marathi',
                     '08Punjabi': self.bu + 'launcher/?lang=punjabi'}
        self.hdr.update({'Referer': self.bu, 'Origin': self.bu[:-1]})

    def decrypt(self, e):
        t = 10
        i = e[0:t] + e[-1] + e[t + 2:-1]
        i = base64.b64decode(i).decode('utf-8')
        return json.loads(i)

    def encrypt(self, t):
        e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        n = 10
        a = json.dumps(t).encode('utf-8')
        a = base64.b64encode(a).decode('utf-8')
        a = a[0:n] + random.choice(e) + random.choice(e) + a[n + 1:] + a[n]
        return a

    def get_sort_cdn(self, slist):
        ejo = []
        for server in slist:
            params = {'_': int(time.time() * 1000)}
            response = requests.get(server, headers=self.hdr, params=params)
            ejo.append((response.elapsed, server))
        ejo = self.encrypt([x for _, x in sorted(ejo)])
        return ejo

    def get_menu(self):
        return (self.list, 4, self.icon)

    def get_top(self, iurl):
        """
        Get the list of categories.
        """
        cats = []
        html = requests.get(iurl, headers=self.hdr).text
        mlink = SoupStrainer('section', {'id': 'UILaunchPad'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('li')
        thumb = 'http://s3.amazonaws.com/einthusanthunderbolt/etc/img/{}.jpg'.format(iurl.split('=')[1])
        for item in items:
            if 'input' not in str(item) and 'data-disabled' not in str(item):
                title = item.p.text
                if title not in ['Feed', 'Contact', 'Go Premium']:
                    url = self.bu[:-1] + item.find('a')['href']
                    cats.append((title, thumb, url))
        surl = '{0}movie/results/?lang={1}&query=MMMM7'.format(self.bu, iurl.split('=')[1])
        cats.append(('[COLOR yellow]** Search Movies **[/COLOR]', thumb, surl))
        return cats, 5

    def get_second(self, iurl):
        """
        Get the list of types.
        """
        thumb = 'http://s3.amazonaws.com/einthusanthunderbolt/etc/img/{}.jpg'.format(iurl.split('=')[1])
        cats = [('Alphabets', thumb, iurl + 'XXXXAlphabets|Numbers'),
                ('Years', thumb, iurl + 'XXXXYear')]
        return cats, 6

    def get_third(self, iurl):
        """
        Get the list of types.
        """
        cats = []
        iurl, sterm = iurl.split('XXXX')
        html = requests.get(iurl, headers=self.hdr).text
        if sterm == 'Year':
            spat = 'href="([^"]+(?:{})[^"]+)">([^<]+)'.format(sterm)
        else:
            spat = r'href="([^"]+(?:{})[^"]+)"\s*data-disabled="">([^<]+)'.format(sterm)
        items = re.findall(spat, html)
        thumb = 'http://s3.amazonaws.com/einthusanthunderbolt/etc/img/{}.jpg'.format(iurl.split('=')[1])
        for url, title in items:
            url = self.bu[:-1] + url.replace('&amp;', '&')
            if '/playlist/' in url:
                title += '  [COLOR cyan][I]Playlists[/I][/COLOR]'
            cats.append((title, thumb, url))

        return cats, 7

    def get_items(self, iurl):
        clips = []
        if iurl.endswith('='):
            search_text = self.get_SearchQuery('Einthusan')
            search_text = urllib_parse.quote_plus(search_text)
            iurl += search_text
        nextpg = True
        nmode = 9
        while nextpg and len(clips) < 18:
            html = requests.get(iurl, headers=self.hdr).text
            if '/movie-clip/' in iurl:
                items = re.findall(r'data-disabled="false"\s*href="([^"]+)">\s*<img\s*src="([^"]+).+?>([^<]+)</h3.+?info">(.+?)</div', html)
            else:
                items = re.findall(r'data-disabled="false"\s*href="([^"]+)"><img\s*src="([^"]+).+?h3>([^<]+).+?info">(.+?)</div', html)
            for url, thumb, title, info in items:
                title = self.unescape(title)
                title = title.encode('utf8') if self.PY2 else title
                r = re.search(r'<p>(\d{4})', info)
                if r:
                    title += ' ({0})'.format(r.group(1))
                if 'Subtitle' in info:
                    title += '  [COLOR cyan][I]with subtitles[/I][/COLOR]'
                elif '/movie-clip/' in iurl and '/playlist/' not in url:
                    mtitle = self.unescape(re.findall('title="([^"]+)', info)[0])
                    mtitle = mtitle.encode('utf8') if self.PY2 else mtitle
                    title = '[COLOR cyan]{}[/COLOR] - [COLOR yellow]{}[/COLOR]'.format(mtitle, title)
                url = self.bu[:-1] + url
                if not thumb.startswith('http'):
                    thumb = 'http:' + thumb
                clips.append((title, thumb, url))
            if len(clips) > 0 and '/playlist/' in url:
                nmode = 7

            paginator = re.search(r'>(Page[^<]+).+?data-disabled=""\s*href="([^"]+)"><i>&#xe956;</i><p>Next<', html, re.DOTALL)
            if paginator:
                iurl = self.bu[:-1] + paginator.group(2).replace('&amp;', '&')
            else:
                nextpg = False

            xbmc.sleep(3000)

        if nextpg:
            title = 'Next Page.. (Currently in {})'.format(paginator.group(1))
            clips.append((title, self.nicon, iurl))

        return clips, nmode

    def get_video(self, iurl):
        headers = self.hdr
        r = requests.get(iurl, headers=headers)
        token = self.unescape(re.findall('data-pageid="([^"]+)', r.text)[0])
        ej = re.findall('data-ejpingables="([^"]+)', r.text)[0]
        ej = self.decrypt(ej)
        xj = {"EJOutcomes": cache.cacheFunction(self.get_sort_cdn, ej),
              "NativeHLS": False}
        pdata = {'xEvent': 'UIVideoPlayer.PingOutcome',
                 'xJson': json.dumps(xj).replace(' ', ''),
                 'gorilla.csrf.Token': token}
        headers.update({'X-Requested-With': 'XMLHttpRequest'})
        aurl = iurl.replace('/movie', '/ajax/movie')
        r2 = requests.post(aurl, data=pdata, headers=headers, cookies=r.cookies)
        stream_url = self.decrypt(r2.json()['Data']['EJLinks'])['MP4Link']

        return stream_url
