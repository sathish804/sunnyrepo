'''
DeccanDelight scraper plugin
Copyright (C) 2022 gujal

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
'''
from resources.lib.base import Scraper
from bs4 import BeautifulSoup, SoupStrainer
import re
import requests
import base64
import json
from six.moves import urllib_parse


class ibomma(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://ww11.ibomma.bar/' if self.mirror else 'https://www.ibomma.net/'
        self.icon = self.ipath + 'ibomma.png'
        country = 'in' if self.mirror else 'us'
        surl = 'https://cdueyzmieouheiq8aib-{0}.securi.link/?label=telugu&q='.format(country)
        self.list = {'01Telugu Movies': self.bu + 'telugu-movies/',
                     '99[COLOR yellow]** Search **[/COLOR]': surl}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []

        if url[-3:] == '&q=':
            search_text = self.get_SearchQuery('iBomma')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('article')
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        if len(items) > 1:
            for item in items:
                title = item.h2.a.text
                title = title.encode('utf8') if self.PY2 else title
                title += ' [COLOR yellow]({0})[/COLOR]'.format(item.h2.span.text)
                thumb = item.img.get('src')
                url = item.a.get('href')
                movies.append((title, thumb, url))
        else:
            items = re.findall(r'(?:data={},\s*)?data=\s*(.+?)</script>', html)[0]
            items = json.loads(items)
            items = items.get('hits', {}).get('hits', [])
            for item in items:
                item = item.get('_source')
                desc = item.get('description')
                desc = desc.split('\n')
                title = desc[0].strip()
                title = title.encode('utf8') if self.PY2 else title
                r = re.search(r'\d{4}', desc[1])
                if r:
                    title += ' [COLOR yellow][{0}][/COLOR]'.format(r.group(0))
                thumb = item.get('image_link')
                url = item.get('location')
                movies.append((title, thumb, url))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('button', {'class': 'server-button'})
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        urldiv = re.findall(r'const\s*urls\s*=\s*([^]]+])', html)[0]
        urls = re.findall(r"(http[^']+)", urldiv)
        for item in items:
            linkcode = int(item.get('data-index')) - 1
            ref, vurl = urls[linkcode].split('link=')
            ref = urllib_parse.urljoin(ref, '/')
            vurl = base64.b64decode(vurl).decode('utf-8')
            vidhost = self.get_vidhost(vurl)
            videos.append((vidhost, vurl + '|Referer={0}&verifypeer=false'.format(ref)))

        return videos
