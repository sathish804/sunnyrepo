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
from six.moves import urllib_parse
import re
import json
import requests
import resolveurl


class tamilian(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://tamilian.to/'
        self.icon = self.ipath + 'tamilian.png'

    def get_menu(self):
        html = requests.get(self.bu, headers=self.hdr).text
        items = {'01Latest': self.bu}
        cats = re.findall(r'id="menu-item-\d+".+?href="([^"]+)">([^<]+)', html, re.DOTALL)
        sno = 2
        for caturl, cat in cats:
            items['{0:02d}{1}'.format(sno, cat)] = caturl
            sno += 1
        items['{0:02d}[COLOR yellow]** Search **[/COLOR]'.format(sno)] = self.bu + '?s='
        return (items, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Tamilian')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        html = requests.get(url, headers=self.hdr).text
        mdiv = BeautifulSoup(html, "html.parser")
        Paginator = mdiv.find('a', {'class': 'loadnavi'})
        items = mdiv.find_all("div", {"class": "movie-preview"})
        for item in items:
            title = self.unescape(item.find("span", {"class": "movie-title"}).text.strip())
            title = self.clean_title(title)
            title += ' [{0}]'.format(item.find("span", {"class": "movie-release"}).text.strip())
            iurl = item.find('a')['href']
            try:
                thumb = item.find('img')['src']
                if thumb.startswith('//'):
                    thumb = 'https:' + thumb
            except:
                thumb = self.icon
            movies.append((title, thumb, iurl))

        if 'Load More' in str(Paginator):
            purl = Paginator.get('href')
            currpg = Paginator.find('span', {'class': 'current'}).text
            lastpg = Paginator.find('span', {'class': 'total'}).text
            if int(currpg) < int(lastpg):
                title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
                movies.append((title, self.nicon, purl))

        return (movies, 9)

    def get_video(self, url):
        headers = self.hdr
        headers.update({'Referer': self.bu})
        html = requests.get(url, headers=headers).text
        mlink = SoupStrainer('div', {'class': 'video-content'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        purl = mdiv.find('form').get('action')
        if purl.startswith('/'):
            purl = urllib_parse.urljoin(self.bu, purl)
        pid = mdiv.find('form').find('input', {'name': 'id'}).get('value')
        pdata = {'id': pid}
        html = requests.post(purl, data=pdata, headers=headers).text
        mdiv = BeautifulSoup(html, "html.parser")
        purl = mdiv.find('form').get('action')
        pid = mdiv.find('form').find('input', {'name': 'id'}).get('value')
        pdata = {'id': pid}
        html = requests.post(purl, data=pdata, headers=headers).text
        # mdiv = BeautifulSoup(html, "html.parser")
        # headers.update({'Referer': purl})
        # purl = mdiv.find('form').get('action')
        # pid = mdiv.find('form').find('input', {'name': 'id'}).get('value')
        # pdata = {'id': pid}
        # html = requests.post(purl, data=pdata, headers=headers).text
        # items = re.findall(r'var\s[^\s]+\s=\s\[([^\]]+)', html)[0]
        # items = items.split(', ')
        # spread = int(re.findall(r'fromCharCode[^\d]+(\d+)', html)[0])
        # shtml = ''
        # for i in items:
        #     shtml += chr(int(i) - spread)
        try:
            items = re.findall(r'=\s*(\[[^;]+)', html)[0]
            items = json.loads(items)
            subitem = int(re.findall(r'parse.+?-\s*(\d+)', html)[0])
            html = ''.join(list(map(lambda val: chr(int(val) - subitem), items)))
        except:
            pass

        eurl = re.findall(r'<iframe.+?src="([^"]+)', html, re.I)[0].split('?')[0]
        if resolveurl.HostedMediaFile(eurl).valid_url():
            return '{0}$${1}'.format(eurl, purl)

        self.log('{0} not resolvable {1}.\n'.format(url, eurl))
        return
