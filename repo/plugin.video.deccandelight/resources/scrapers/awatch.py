'''
DeccanDelight scraper plugin
Copyright (C) 2017 gujal

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


class awatch(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'http://www.andhrawatch.com/'
        self.icon = self.ipath + 'awatch.png'
        self.list = {'01Movies': self.bu + 'telugu-movies/',
                     '02Trailers': self.bu + 'movie-trailers/',
                     '03Short Films': self.bu + 'short-films/'}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': re.compile('^row ')})
        plink = SoupStrainer('nav', {'class': 'herald-pagination'})

        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('article')

        for item in items:
            title = self.unescape(item.text)
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src'].split('?')[0]
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        if 'Next' in str(Paginator):
            currpg = Paginator.find('span', {'class': re.compile('current')}).text
            purl = Paginator.find('a', {'class': re.compile('next')}).get('href')
            pages = Paginator.find_all('a', {'class': 'page-numbers'})
            lastpg = pages[-2].text
            title = 'Next Page.. (Currently in {} of {})'.format(currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 9)

    def get_video(self, url):
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('iframe')
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            vidurl = videoclass.find('iframe')['src'].split('?')[0]
        except:
            vidurl = None

        return vidurl
