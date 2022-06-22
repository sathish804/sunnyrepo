'''
DeccanDelight scraper plugin
Copyright (C) 2016 gujal

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
import re
import requests


class bmov(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://bharat-movies.com/'
        self.icon = self.ipath + 'bmov.png'
        self.list = {'01Hindi': 'hindi',
                     '02Telugu': 'telugu',
                     '03Tamil': 'tamil',
                     '04Malayalam': 'malayalam',
                     '05Kannada': 'kannada',
                     '06Bengali': 'bengali'
                     }

    def get_menu(self):
        return (self.list, 4, self.icon)

    def get_top(self, iurl):
        menus = []

        title = 'Movies by Name'
        url = '{}{}/movies/list.htm'.format(self.bu, iurl)
        menus.append((title, self.icon, url))

        if 'bengali' not in iurl:
            title = 'Movies by Year'
            url = '{}{}/movies/{}-newrelease-movies-new.htm'.format(self.bu, iurl, iurl)
            menus.append((title, self.icon, url))

        return (menus, 5)

    def get_second(self, iurl):
        menus = []

        html = requests.get(iurl, headers=self.hdr, verify=False).text
        items = re.findall('id=ila.+?href=([^>]+)>([^<]+)', html)
        burl = re.findall('(.+/)', iurl)[0]
        for item in items:
            title = item[1]
            url = burl + item[0]
            menus.append((title, self.icon, url))

        return (menus, 7)

    def get_items(self, iurl):
        movies = []
        html = requests.get(iurl, headers=self.hdr, verify=False).text
        items = re.findall('id=L[12].+?href=([^>]+)>([^<]+)', html)
        burl = re.findall('(.+/)', iurl)[0]
        for item in items:
            title = self.unescape(item[1])
            title = title.strip()
            title = title.encode('utf8') if self.PY2 else title
            url = burl + item[0]
            movies.append((title, self.icon, url))

        return (movies, 9)

    def get_video(self, url):
        html = requests.get(url, headers=self.hdr, verify=False).text

        try:
            vidurl = re.findall('<iframe.+?src="([^"]+)', html)[0]
        except:
            vidurl = ''

        return vidurl
