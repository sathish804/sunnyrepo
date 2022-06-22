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
from six.moves import urllib_parse
import re
import requests


class omg(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://kgb.capital/genre/' if self.mirror else 'https://www.onlinemoviesgold.net/genre/'
        self.icon = self.ipath + 'omg.png'
        self.list = {'01Tamil Movies': 'tamil',
                     '02Telugu Movies': 'telugu',
                     '03Malayalam Movies': 'malayalam',
                     '04Kannada Movies': self.bu + 'kannada-moviesMMMM7',
                     '05Hindi Movies': 'hindi',
                     '06English Movies': 'hollywood',
                     '07Punjabi Movies': self.bu + 'punjabi-moviesMMMM7',
                     '09Bengali Movies': self.bu + 'bengali-moviesMMMM7',
                     '98[COLOR cyan]Adult Movies[/COLOR]': self.bu + 'adult-moviesMMMM7',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-6] + '?s=MMMM7'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of categories.
        """
        cats = []
        page = requests.get(self.bu[:-6], headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'menu'})
        mdiv = BeautifulSoup(page, "html.parser", parse_only=mlink)
        submenus = mdiv.find_all('li', {'class': 'menu-item-has-children'})
        for submenu in submenus:
            if iurl in submenu.find('a').text.lower():
                break

        items = submenu.find_all('li')
        for item in items:
            title = item.text
            url = item.find('a')['href']
            url = url if url.startswith('http') else self.bu[:-7] + url
            cats.append((title, self.icon, url))

        return (cats, 7)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Online Movies Gold')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text
        if '?s=' in url:
            mlink = SoupStrainer('div', {'class': 'result-item'})
        else:
            mlink = SoupStrainer('div', {'class': re.compile('^items')})
        html = requests.get(url, headers=self.hdr).text
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        nlink = SoupStrainer('div', {'class': 'resppages'})
        npage = BeautifulSoup(html, "html.parser", parse_only=nlink)
        plink = SoupStrainer('div', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('article')

        for item in items:
            try:
                title = self.unescape(item.h3.text)
                title = self.clean_title(title)
            except:
                tdiv = item.find('div', {'class': 'title'})
                title = self.unescape(tdiv.a.text)
                title = title.encode('utf8') if self.PY2 else title
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'chevron-right' in str(npage):
            purl = Paginator.find('span', {'class': 'current'}).nextSibling.get('href')
            pgtxt = Paginator.find('span').text
            title = 'Next Page.. (Currently in {0})'.format(pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'id': 'info'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        url = mdiv.find('table').nextSibling.find('a')['href']
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'entry-content'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        links = mdiv.find_all('iframe')

        for link in links:
            try:
                vidurl = link.get('src')
                self.resolve_media(vidurl, videos)
            except:
                pass

        try:
            links = re.findall(r'<li><a\s*href="([^"]+)', html, re.IGNORECASE)
            for link in links:
                self.resolve_media(link, videos)
        except:
            pass

        try:
            links = re.findall(r'<a\s*href="(magnet[^"]+)', html, re.IGNORECASE)
            for link in links:
                self.resolve_media(link, videos)
        except:
            pass

        return videos
