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
from bs4 import BeautifulSoup, SoupStrainer
from six.moves import urllib_parse
import requests


class tdhool(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.tamildhool.net/'
        self.icon = self.ipath + 'tdhool.png'
        self.list = {'01Sun TV': self.bu + 'sun-tv-programs/MMMM5',
                     '02Vijay TV': self.bu + 'vijay-tv-programs/MMMM5',
                     '03Zee Tamil TV': self.bu + 'zee-tamil-programs/MMMM5',
                     '04Colors Tamil TV': self.bu + 'colors-tamil/',
                     #  '05Raj TV': self.bu + 'raj-tv/',
                     #  '06Polimer TV': self.bu + 'polimer-tv/',
                     #  '07Jaya TV': self.bu + 'jaya-tv/',
                     '08News & Gossips': self.bu + 'news-gossips/',
                     '09Tamil TV Programs': self.bu + 'tamil-tv/',
                     '10Recent Posts': self.bu,
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = requests.get(iurl, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'content-area'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = mdiv.find_all('figure', {'class': 'wp-block-image'})
        for item in items:
            title = self.unescape(item.text)
            if title.endswith('Streaming'):
                continue
            url = item.find('a')['href']
            if url.endswith('bigg-boss-ultimate-season-1/'):
                url += 'MMMM5'
            try:
                icon = item.find('img')['src']
                if icon.startswith('data'):
                    icon = item.find('img')['data-lazy-src']
                icon = 'https:' + icon if icon.startswith('//') else icon
            except:
                icon = self.icon

            shows.append((title, icon, url))

        return (shows, 7)

    def get_items(self, url):
        episodes = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Tamil Dhool')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('main', {'id': 'main'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'navigation'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('article')
        if len(items) == 1:
            items = items.find_all('div', {'class': 'gallery-item-inner'})

        for item in items:
            if item.h3:
                title = self.unescape(item.h3.text)
            elif item.h5:
                title = self.unescape(item.h5.text)
            else:
                title = self.unescape(item.find('a').get('title'))
            title = self.clean_title(title)
            try:
                iurl = item.h3.find('a')['href']
            except:
                iurl = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
                if thumb.startswith('data'):
                    thumb = item.find('img')['data-lazy-src']
                thumb = 'https:' + thumb if thumb.startswith('//') else thumb
            except:
                thumb = self.icon
            episodes.append((title, thumb, iurl))

        if 'next' in str(Paginator):
            nextli = Paginator.find('a', {'class': 'next'})
            purl = nextli.get('href')
            currpg = Paginator.find('span').text
            lastpg = Paginator.find_all('a', {'class': 'page-numbers'})[-2].text
            title = 'Next Page.. (Currently in Page %s of %s)' % (currpg, lastpg)
            episodes.append((title, self.nicon, purl))

        return (episodes, 8)

    def get_videos(self, url):
        videos = []
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'content-area'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('video')
            for link in links:
                vidurl = link.find('source')['src']
                self.resolve_media(vidurl, videos)
        except:
            pass

        try:
            links = videoclass.find_all('noscript')
            for link in links:
                vidurl = link.find('iframe')['src'].strip()
                self.resolve_media(vidurl, videos)
        except:
            pass

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                vidurl = link.get('src').strip() + '|Referer={}'.format(self.bu)
                self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
