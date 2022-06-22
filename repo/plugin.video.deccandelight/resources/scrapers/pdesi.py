'''
DeccanDelight scraper plugin
Copyright (C) 2021 gujal

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
from kodi_six import xbmcgui


class pdesi(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://playdesi.net/'
        self.icon = self.ipath + 'pdesi.png'

    def get_menu(self):
        html = requests.get(self.bu, headers=self.hdr).text
        mlink = SoupStrainer('div', {'id': 'main-menu'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('li', {'class': 'menu-item-object-page'})
        mlist = {}
        ino = 1
        for item in items:
            mlist.update({'{0:02d}{1}'.format(ino, item.text): item.find('a').get('href')})
            ino += 1
        mlist.update({'99[COLOR yellow]** Search **[/COLOR]': '{0}?s=MMMM7'.format(self.bu)})
        return (mlist, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = requests.get(iurl, headers=self.hdr).text
        mlink = SoupStrainer('section', {'id': 'innerTop'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        r = mdiv.find('h4', {'class': 'heading-tag'})
        if r:
            items = r.text.split('|')
            mode = 6
            for item in items:
                shows.append((item, self.icon, '{0}ZZZZ{1}'.format(iurl, items.index(item))))
        else:
            items = mdiv.find_all('div', {'class': 'vc_column_container col-md-3'})
            mode = 7
            for item in items:
                title = '{0} [COLOR cyan][I]{1}[/I][/COLOR]'.format(item.h4.text, item.p.text)
                thumb = item.find('img').get('src')
                url = item.find('a').get('href')
                shows.append((title, thumb, url))
        return (shows, mode)

    def get_third(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        iurl, sect = iurl.split('ZZZZ')
        shows = []
        html = requests.get(iurl, headers=self.hdr).text
        mlink = SoupStrainer('section', {'id': 'innerTop'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        sdiv = mdiv.contents[int(sect)]
        items = sdiv.find_all('div', {'class': 'vc_column_container col-md-3'})
        mode = sdiv.find('h4', {'class': 'heading-tag'}).text
        if '|' in mode:
            mode = mode.split('|')[0]
        mode = 8 if 'Original' in mode else 7
        for item in items:
            title = '{0} [COLOR cyan][I]{1}[/I][/COLOR]'.format(item.h4.text, item.p.text)
            thumb = item.find('img').get('src')
            url = item.find('a').get('href')
            shows.append((title, thumb, url))
        return (shows, mode)

    def get_items(self, url):
        episodes = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Play Desi')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('article')
        plink = SoupStrainer('div', {'class': 'pagination'})
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
            purl = Paginator.find('a', {'class': 'next'}).get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            lastpg = Paginator.find_all('a', {'class': 'page-numbers'})[-2].text
            title = 'Next Page.. (Currently in Page {} of {})'.format(currpg, lastpg)
            episodes.append((title, self.nicon, purl))

        return (episodes, 8)

    def get_videos(self, url):
        videos = []
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': re.compile('entry-content')})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                vidurl = link.get('src')
                self.resolve_media(vidurl, videos)
        except:
            pass

        try:
            pDialog = xbmcgui.DialogProgress()
            pDialog.create('Deccan Delight', 'Processing Links...')
            prog_per = 0
            videoclass.find('div', {'class': 'post-share'}).decompose()
            links = videoclass.find_all('a', {'target': '_blank'})
            for link in links:
                vidurl = link.get('href')
                self.resolve_media(vidurl, videos)
                prog_per += int(100 / len(links))
                if (pDialog.iscanceled()):
                    return videos
                pDialog.update(prog_per, 'Collected Links... {0} from {1}'.format(len(videos), len(links)))
        except:
            import traceback
            traceback.print_exc()
            pass

        return videos
