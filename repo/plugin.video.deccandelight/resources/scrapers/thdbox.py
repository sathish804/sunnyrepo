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
import re
import requests


class thdbox(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://tamilhdbox.com/'
        self.icon = self.ipath + 'thdbox.png'
        self.list = {'01Sun TV': self.bu + 'channel/sun-tv/',
                     '02Vijay TV': self.bu + 'channel/vijay-tv-programs/',
                     '03Zee Tamil TV': self.bu + 'channel/zee-tamil-programs/',
                     '04Colors Tamil TV': self.bu + 'channel/colors-tamil-programs/'}

    def get_menu(self):
        return (self.list, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = requests.get(iurl, headers=self.hdr).text
        soup = BeautifulSoup(html, "html.parser")
        items = soup.find_all('article')

        for item in items:
            title = item.h3.text.strip()
            if 'tv live' not in title.lower():
                url = item.find('a').get('href').split('#')[0]
                if self.bu in url:
                    thumb = item.find('img').get('src')
                    shows.append((title, thumb, url))

        return (shows, 7)

    def get_items(self, url):
        movies = []
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('article', {'class': re.compile('video')})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)

        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

        for item in mdiv:
            i = item.h3.find('a')
            i.find('div').decompose()
            i.find('span').decompose()
            title = self.unescape(i.text)
            title = title.encode('utf8') if self.PY2 else title
            url = i.get('href')
            try:
                thumb = item.find('img').get('src').strip()
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            purl = Paginator.find('a', {'rel': 'next'}).get('href')
            pgtxt = Paginator.find('span', {'class': 'pages'}).text
            title = 'Next Page.. (Currently in {0})'.format(pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': re.compile('^video-player-content')})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                iurl = link.get('src')
                if iurl.startswith('//'):
                    iurl = 'https:' + iurl
                if 'playallu.' in iurl:
                    vidhost, strlink = self.playallu(iurl, url)
                    videos.append((vidhost, strlink))
                else:
                    self.resolve_media(iurl, videos)
        except:
            pass

        yt = re.search('"youtube","single_video_source":"([^"]+)', html)
        if yt:
            iurl = 'https://www.youtube.com/watch?v={0}'.format(yt.group(1))
            self.resolve_media(iurl, videos)

        return videos
