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
import re
import requests
from kodi_six import xbmcgui


class flinks(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www2.filmlinks4u.is/category/'
        self.icon = self.ipath + 'flinks.png'
        self.list = {'01Tamil Movies': self.bu + 'tamil',
                     '02Telugu Movies': self.bu + 'telugu',
                     '03Malayalam Movies': self.bu + 'malayalam',
                     '04Kannada Movies': self.bu + 'kannada',
                     '05Hindi Movies': self.bu + 'hindi',
                     '06Web Series': self.bu + 'web-series',
                     '11English Movies': self.bu + 'hollywood',
                     '12Animation Movies': self.bu + 'animation',
                     '13Biography Movies': self.bu + 'biography',
                     '14Documentary Movies': self.bu + 'documentary',
                     '21English Movies dubbed into Tamil': self.bu + 'hollywood-movies-dubbed-in-tamil',
                     '22English Movies dubbed into Telugu': self.bu + 'hollywood-movies-dubbed-in-telugu',
                     '23English Mobies dubbed into Hindi': self.bu + 'hollywood-movies-dubbed-in-hindi',
                     '24Hindi Movies dubbed into Tamil': self.bu + 'hindi-movies-dubbed-in-tamil',
                     '25Hindi Movies dubbed into Telugu': self.bu + 'hindi-movies-dubbed-in-telugu',
                     '26Tamil Movies dubbed into Hindi': self.bu + 'tamil-movies-dubbed-in-hindi',
                     '27Telugu Movies dubbed into Hindi': self.bu + 'telugu-movies-dubbed-in-hindi',
                     '30Web Series': self.bu + 'web-series',
                     '31Bengali Movies': self.bu + 'bengali',
                     '32Bhojpuri Movies': self.bu + 'bhojpuri',
                     '33Gujarati Movies': self.bu + 'gujarati',
                     '34Marathi Movies': self.bu + 'marathi',
                     '35Oriya Movies': self.bu + 'oriya',
                     '36Punjabi Movies': self.bu + 'punjabi',
                     '37Rajasthani Movies': self.bu + 'rajasthani',
                     '38Urdu Movies': self.bu + 'urdu',
                     '39Nepali Movies': self.bu + 'nepali',
                     '97[COLOR cyan]Hindi Adult Softcore[/COLOR]': self.bu + 'adult-hindi-short-films',
                     '98[COLOR cyan]Adult Movies[/COLOR]': self.bu + 'adult',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Film Links 4U')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        # mlink = SoupStrainer('div', {'class':re.compile('content')})
        # mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'pagination'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = re.findall('<article.*?a href="(.*?)">(.*?)<.*?post-cats">(.*?)</span.*?<img.*?data-src="(.*?)"', html, re.DOTALL)

        for url, title, adult, thumb in items:
            title = self.unescape(title)
            title = self.clean_title(title)
            if 'adult' not in adult.lower():
                movies.append((title, thumb, url))
            elif self.adult:
                movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextli = Paginator.find('span', {'id': 'tie-next-page'})
            purl = nextli.find('a')['href']
            pgtxt = Paginator.find('span', {'class': 'pages'}).text
            title = 'Next Page.. (Currently in {})'.format(pgtxt)
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'content'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            tabsdiv = videoclass.find('div', {'class': 'tabs'})
            tabs = tabsdiv.find_all('div', {'class': re.compile('^tab embed')})
            for tab in tabs:
                vidurl = tab.get('data-href')
                self.resolve_media(vidurl, videos)
        except:
            pass

        try:
            linksdiv = videoclass.find('div', {'class': 'entry'})
            alinks = linksdiv.find_all('a')
            prog_per = 0
            numlink = 0
            p_dialog = xbmcgui.DialogProgress()
            p_dialog.create('Deccan Delight', 'Collecting Links...')
            for alink in alinks:
                if 'target' in alink.attrs.keys() and alink.get('class')[0] == 'external':
                    vidurl = alink.get('href')
                    vidtxt = ''
                    t = re.search(r'(Part\s*\d*)', alink.text)
                    if t:
                        vidtxt = t.group(1)
                    self.resolve_media(vidurl, videos, vidtxt)
                    prog_per += int(100 / len(alinks))
                    numlink += 1
                    if p_dialog.iscanceled():
                        return videos
                    p_dialog.update(prog_per, 'Processed Links... {}'.format(numlink))
        except:
            pass

        return videos
