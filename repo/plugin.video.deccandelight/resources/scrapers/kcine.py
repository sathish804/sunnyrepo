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


class kcine(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.kannadacine.com/'
        self.icon = self.ipath + 'kcine.png'
        self.list = {'01By Year': 'menu-item-449',
                     '02By Genre': 'menu-item-92',
                     '03By Upload order': self.bu + 'MMMM7'
                     }

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        menus = []
        html = requests.get(self.bu, headers=self.hdr).text
        mlink = SoupStrainer('li', {'id': iurl})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)

        items = mdiv.ul.find_all('li')

        for item in items:
            title = item.text
            url = item.find('a')['href']
            menus.append((title, self.icon, url))

        return (menus, 7)

    def get_items(self, iurl):
        movies = []
        html = requests.get(iurl, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'article-container'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('ul', {'class': re.compile('^default-wp-page')})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('article')
        for item in items:
            title = self.unescape(item.h2.text).strip()
            title = title.encode('utf8') if self.PY2 else title
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['data-src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'Previous' in str(Paginator):
            pdiv = Paginator.find('li', {'class': 'previous'})
            purl = pdiv.find('a')['href']
            title = 'Next Page..'
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': re.compile('^article-content')})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                vidurl = link.get('src')
                if '.disabled' not in vidurl:
                    self.resolve_media(vidurl, videos)
        except:
            pass

        try:
            links = videoclass.find_all('video')
            for link in links:
                vidurl = link.find('source').get('src')
                if '.disabled' not in vidurl:
                    self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
