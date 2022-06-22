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
import resolveurl


class tyogi(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'http://tamilyogi.best/home/'
        self.icon = self.ipath + 'tyogi.png'

    def get_menu(self):
        html = requests.get(self.bu, headers=self.hdr).text
        items = {}
        cats = re.findall('class="menu-item.+?href="?([^"]+)">([^<]+)', html, re.DOTALL)
        sno = 1
        for cat, title in cats:
            cat = cat if cat.startswith('http') else self.bu[:-6] + cat
            items['%02d' % sno + title] = cat
            sno += 1
        items['%02d' % sno + '[COLOR yellow]** Search **[/COLOR]'] = self.bu[:-6] + '/?s='
        return (items, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Tamil Yogi')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        regex = r"<iframe\s*srcdoc.+?iframe>"
        html = re.sub(regex, '', html, 0, re.MULTILINE)
        mlink = SoupStrainer("div", {"id": "archive"})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        plink = SoupStrainer("div", {"class": "navigation"})
        Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)
        items = mdiv.find_all('li')
        for item in items:
            if '"cleaner"' not in str(item):
                title = self.unescape(item.text)
                title = self.clean_title(title)
                url = item.a.get('href')
                try:
                    thumb = item.img.get('src')
                except:
                    thumb = self.icon
                movies.append((title, thumb, url))

        if 'next' in str(Paginator):
            nextpg = Paginator.find('a', {'class': 'next'})
            purl = nextpg.get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            pages = Paginator.find_all('a', {'class': 'page-numbers'})
            lastpg = pages[-2].text
            title = 'Next Page.. (Currently in Page %s of %s)' % (currpg, lastpg)
            movies.append((title, self.nicon, purl))

        return (movies, 9)

    def get_video(self, url):
        headers = self.hdr
        headers.update({'Referer': self.bu})
        html = requests.get(url, headers=headers).text
        regex = r"<iframe\s*srcdoc.+?iframe>"
        html = re.sub(regex, '', html, 0, re.MULTILINE)
        mlink = SoupStrainer('div', {'class': 'entry'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        mdiv.find('aside').decompose()
        eurl = mdiv.iframe.get('src')
        if resolveurl.HostedMediaFile(eurl):
            return eurl

        self.log('%s not resolvable.\n' % eurl)
        return
