'''
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
'''

from resources.lib.base import Scraper
from bs4 import BeautifulSoup, SoupStrainer
from six.moves import urllib_parse
import re
import requests


class bbt(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://bigtamilboss.net/'
        self.icon = self.ipath + 'bbt.png'

    def get_menu(self):
        html = requests.get(self.bu, headers=self.hdr).text
        items = re.findall(r'id="menu-item-[23](?!11195|299).+?href="([^"]+)">[^>]*>([^<]+)', html)
        mlist = {}
        ino = 1
        for url, title in items:
            if url.startswith('/'):
                url = self.bu[:-1] + url
            mlist.update({'{0:02d}{1}'.format(ino, title): url})
            ino += 1
        mlist.update({'99[COLOR yellow]** Search **[/COLOR]': '{0}?s=MMMM7'.format(self.bu)})
        return (mlist, 7, self.icon)

    def get_items(self, url):
        episodes = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('BigBoss Tamil')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('article')
        plink = SoupStrainer('div', {'class': 'nav-links'})
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        for item in items:
            title = self.unescape(item.h2.text)
            title = title.encode('utf8') if self.PY2 else title
            url = item.find('a')['href']
            if item.find('img'):
                thumb = item.find('img')['src']
            else:
                thumb = self.icon
            if 'data:image' in thumb:
                if 'data-srcset' in item.find('img'):
                    thumb = item.find('img')['data-srcset'].split(' ')[0]
                else:
                    thumb = item.find('img')['data-src']
            episodes.append((title, thumb, url))

        if 'next' in Paginator.text.lower():
            purl = Paginator.find('a', {'class': re.compile('next')}).get('href')
            currpg = Paginator.find('span', {'class': re.compile('current')}).text
            lastpg = Paginator.find_all('a', {'class': 'page-numbers'})[-2].text
            title = 'Next Page.. (Currently in Page {} of {})'.format(currpg, lastpg)
            episodes.append((title, self.nicon, purl))

        return (episodes, 8)

    def get_videos(self, url):
        videos = []
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('iframe')
        links = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            for link in links:
                vidurl = link.get('src')
                self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
