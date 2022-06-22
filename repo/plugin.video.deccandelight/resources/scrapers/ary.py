'''
DeccanDelight scraper plugin
Copyright (C) 2019 gujal

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


class ary(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.arydigital.tv/videos/'
        self.icon = self.ipath + 'ary.png'
        self.list = {'01Current Dramas': self.bu,
                     '02Finished Dramas': self.bu[:-7] + 'ary-digital-old-dramas/'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        """
        shows = []
        html = requests.get(iurl, headers=self.hdr).text

        if 'old-dramas' in iurl:
            mlink = SoupStrainer('main', {'id': 'content'})
            mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
            items = mdiv.find_all('div', {'class': 'drama-gallery'})
        else:
            mlink = SoupStrainer('li', {'id': 'menu-item-139134'})
            mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
            items = mdiv.find('ul').find_all('li')
            shows.append(('Bulbulay Season 2', self.icon, self.bu + 'category/bulbulay-season-2/'))
        for item in items:
            title = self.unescape(item.text)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['data-src']
            except:
                thumb = self.icon
            shows.append((title, thumb, url))
        return (shows, 7)

    def get_items(self, url):
        movies = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': re.compile('^tabs-panel')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('link', {'rel': 'next'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': re.compile('^item')})

        for item in items:
            title = self.unescape(item.h6.text.strip())
            title = title.encode('utf8') if self.PY2 else title
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if len(Paginator) > 0:
            purl = Paginator.link.get('href')
            title = 'Next Page..'
            movies.append((title, self.nicon, purl))

        return (movies, 9)

    def get_video(self, url):
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('iframe')
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        vidurl = videoclass.find('iframe')['src']
        return vidurl
