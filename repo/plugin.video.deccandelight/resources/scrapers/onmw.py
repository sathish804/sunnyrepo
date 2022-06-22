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
requests.packages.urllib3.disable_warnings()


class onmw(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.onlinemoviewatch.org/movies/'
        self.icon = self.ipath + 'onmw.png'
        self.list = {'01Tamil Movies': self.bu + 'online-tamil-movies',
                     '02Telugu Movies': self.bu + 'telugu-movies-online',
                     '03Malayalam Movies': self.bu + 'malayalam',
                     '04Kannada Movies': self.bu + 'kannada-movie-2018',
                     '04Hindi Movies': self.bu + 'bollywood-movies',
                     '05English Movies': self.bu + 'hollywood-movies-atoz',
                     '06Dubbed Movies': self.bu + 'dubbed-movies',
                     '07Punjabi Movies': self.bu + 'punjabi-movies',
                     '08Marathi Movies': self.bu + 'new-marathi-film',
                     '09Bengali Movies': self.bu + 'bengali-2017',
                     '10Urdu Movies': self.bu + 'pakistani',
                     '11South in Hindi Movies': self.bu + 'south-movie-in-hindi',
                     '98[COLOR cyan]Adult Movies[/COLOR]': self.bu + 'adult-movies',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-7] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Online Movie Watch')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr, verify=False).text
        mlink = SoupStrainer('div', {'class': 'postcont'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'class': 'postbox'})

        for item in items:
            title = self.unescape(item.h2.text)
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['data-lazy-src'] + '|verifypeer=false'
            except:
                thumb = self.icon
            movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            purl = Paginator.find('a', {'class': 'nextpostslink'}).get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            title = 'Next Page.. (Currently in Page {0})'.format(currpg)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = requests.get(url, headers=self.hdr, verify=False).text

        try:
            mlink = SoupStrainer('div', {'class': re.compile('^videosection')})
            videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
            links = videoclass.find_all('iframe')
            for link in links:
                try:
                    vidurl = link.get('src')
                    self.resolve_media(vidurl, videos)
                except:
                    pass
        except:
            pass

        try:
            mlink = SoupStrainer('ul', {'class': re.compile(r'^dropdown-menu\s')})
            videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
            links = videoclass.find_all('li', {'id': re.compile(r'^episode-\d')})
            for link in links:
                for key in link.attrs.keys():
                    if 'data-ply' in key:
                        vidurl = link.get(key)
                        self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
