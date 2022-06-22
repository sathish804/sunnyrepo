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


class hlinks(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.hindilinks4u.to/category/'
        self.icon = self.ipath + 'hlinks.png'
        self.list = {'01Hindi Movies': self.bu + 'hindi-movies/',
                     '02Dubbed Movies': self.bu + 'dubbed-movies/',
                     '03Documentary Movies': self.bu + 'documentaries/',
                     '11Amazon Prime Series': self.bu + "series/amazon-prime/MMMM5",
                     '12Netflix Series': self.bu + "series/netflix/MMMM5",
                     '13Hotstar Series': self.bu + "series/hotstar/MMMM5",
                     '14Eros Now Series': self.bu + "series/eros-now/MMMM5",
                     '15HBO Series': self.bu + "series/hbo/MMMM5",
                     '16ALTBalaji Series': self.bu + "series/altbalaji/MMMM5",
                     '17TVF Play Series': self.bu + "series/tvf-play/MMMM5",
                     '18Zee5 Series': self.bu + "series/zee5/MMMM5",
                     '19Syfy Series': self.bu + "series/syfy/MMMM5",
                     '97[COLOR cyan]ULLU Adult Series[/COLOR]': self.bu + "series/ullu/MMMM5",
                     '98[COLOR cyan]Adult Movies[/COLOR]': self.bu + 'adult/',
                     '99[COLOR yellow]** Search **[/COLOR]': self.bu[:-9] + '?s='}

    def get_menu(self):
        return (self.list, 7, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        :return: list
        """
        shows = []
        html = requests.get(iurl, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'nag cf'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'id': re.compile('^post-')})

        for item in items:
            title = self.unescape(item.find('a')['title'])
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
                if thumb.startswith('data'):
                    thumb = item.find('img')['data-src']
            except:
                thumb = self.icon
            movdet = item.find('p', {'class': 'entry-summary'}).text.lower()
            if 'adult' not in movdet and 'short' not in movdet:
                shows.append((title, thumb, url))
            elif self.adult:
                shows.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextli = Paginator.find('a', {'class': 'nextpostslink'})
            purl = nextli.get('href')
            pgtxt = Paginator.find('span', {'class': 'pages'}).text
            title = 'Next Page.. (Currently in %s)' % pgtxt
            shows.append((title, self.nicon, purl))

        return (shows, 6)

    def get_third(self, iurl):
        """
        Get the list of episodes.
        :return: list
        """
        episodes = []
        html = requests.get(iurl, headers=self.hdr).text
        thumb = re.findall(r'<img\s*src="([^"]+)', html, re.DOTALL)[0]
        mlink = SoupStrainer('div', {'id': 'content'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        table = mdiv.find('table')
        items = table.find_all('tr')
        for item in items:
            if item.find('th'):
                continue
            else:
                tdiv = item.find('td', {'class': 'episode-title'})
                url = item.find('a')['href']
                eno = item.find('a').text.replace(' ', '')
                if tdiv.find('small'):
                    edate = tdiv.find('small').text
                    tdiv.find('small').decompose()
                else:
                    edate = ''
                etitle = self.clean_title(tdiv.text)
                title = '[COLOR yellow]{0}[/COLOR] {1} - [COLOR cyan]{2}[/COLOR]'.format(eno, etitle, edate)

            episodes.append((title, thumb, url))

        return (episodes, 8)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Hindi Links 4U')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'nag cf'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer('div', {'class': 'wp-pagenavi'})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('div', {'id': re.compile('^post-')})

        for item in items:
            title = self.unescape(item.find('a')['title'])
            title = self.clean_title(title)
            url = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
                if thumb.startswith('data'):
                    thumb = item.find('img')['data-src']
            except:
                thumb = self.icon
            movdet = item.find('p', {'class': 'entry-summary'}).text.lower()
            if 'adult' not in movdet and 'short' not in movdet:
                movies.append((title, thumb, url))
            elif self.adult:
                movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextli = Paginator.find('a', {'class': 'nextpostslink'})
            purl = nextli.get('href')
            pgtxt = Paginator.find('span', {'class': 'pages'}).text
            title = 'Next Page.. (Currently in %s)' % pgtxt
            movies.append((title, self.nicon, purl))

        return (movies, 8)

    def get_videos(self, url):
        videos = []

        html = requests.get(url, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'entry-content rich-content'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            vtabs = re.findall('data-href=."(.*?)."', html)
            for vtab in vtabs:
                self.resolve_media(vtab, videos)
        except:
            pass

        try:
            links = videoclass.find_all('a')
            for link in links:
                vidurl = link.get('href')
                self.resolve_media(vidurl, videos)
        except:
            pass

        return videos
