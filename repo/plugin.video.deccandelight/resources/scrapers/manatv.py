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
import re
import requests
import base64


class manatv(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://manatelugumovies.cc/'
        self.icon = self.ipath + 'manatv.png'
        self.list = {'01ETV Serials': 'ETV Serials',
                     '02ETV Shows': 'ETV Shows',
                     '03Gemini TV Serials': 'Gemini Serials',
                     '04Gemini TV Shows': 'Gemini TV Shows',
                     '05MAA TV Serials': 'MAA Serials',
                     '06MAA TV Shows': 'MAA TV Shows',
                     '07Zee Telugu Serials': 'Zee Telugu Serials',
                     '08Zee Telugu Shows': 'Zee Telugu Shows'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        html = requests.get(self.bu, headers=self.hdr).content
        mlink = SoupStrainer('ul', {'class': 'mega-nav'})
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        menu = {}
        for item in items:
            for eachitem in item.find_all('ul'):
                cat = eachitem.findParent('li').a.text
                cat_items = []
                for li in eachitem.find_all('li'):
                    title = li.text
                    url = li.find('a')['href']
                    cat_items.append((title, url))
                menu[cat] = cat_items

        categories = []
        for title, url in menu[iurl]:
            categories.append((title, self.icon, url))

        return (categories, 7)

    def get_items(self, url):
        movies = []
        html = requests.get(url, headers=self.hdr).text
        html = html.replace('<br />', '</p><p>')
        mlink = SoupStrainer('div', {'class': re.compile('^entry-content')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        pdiv = mdiv.find('div', {'class': 'eppage'})
        ilink = SoupStrainer('div', {'class': 'post-thumbnail'})
        idiv = BeautifulSoup(html, "html.parser", parse_only=ilink)

        try:
            thumb = idiv.find('img')['src']
        except:
            thumb = self.icon

        items = mdiv.find_all('p')
        for item in items:
            if 'href' in str(item):
                itxt = (item.text).replace('Click ', 'Click').replace('Here ', 'Here').replace(' OR', '')
                itxt = (self.unescape(itxt))
                itxt = itxt.encode('utf8') if self.PY2 else itxt
                itxt = re.search(r'(E\d+)?.+?\s(\d.*)', itxt)
                if itxt:
                    ep = '[COLOR lime]{}[/COLOR] - '.format(itxt.group(1)) if itxt.group(1) else ''
                    title = '{}[COLOR yellow]{}[/COLOR]'.format(ep, itxt.group(2))
                    item = str(item).encode('base64') if self.PY2 else base64.b64encode(str(item).encode('utf-8'))
                    movies.append((title, thumb, item))

        try:
            if 'next page' in (pdiv.text).lower():
                pdiv = pdiv.find_all('a')[-1]
                purl = pdiv.get('href')
                movies.append(('Next Page..', self.nicon, purl))
        except:
            pass

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = base64.b64decode(url).decode('utf8')
        links = re.findall('(<a.+?a>)', html)
        for link in links:
            vidurl = re.findall('href="([^"]+)', link)[0]
            vidtxt = re.findall('">([^<]+)', link)[0]
            if 'source=vidfy' in vidurl:
                url = 'http://vidfy.me/player.php?vid=' + re.findall(r'\?url=([^&]+)', vidurl)[0]
                headers = self.hdr
                headers['Referer'] = 'http://desitelugu.com/'
                html = requests.get(url, headers=self.hdr).text
                if 'video is not available' not in html:
                    try:
                        vidurl = re.findall('<source.+?src="([^"]+)', html)[0]
                    except:
                        vidurl = re.findall(r'src:\s*"([^"]+)', html)[0]
                    vidurl += '|Referer={}&User-Agent={}'.format(url, self.hdr['User-Agent'])
                    videos.append(('vidfy | {}'.format(vidtxt), vidurl))
            elif 'source=youtube' in vidurl:
                vidurl = 'https://www.youtube.com/embed/' + re.findall(r'\?url=([^&]+)', vidurl)[0]
                self.resolve_media(vidurl, videos, vidtxt)

        return videos
