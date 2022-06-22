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
import requests

try:
    import StorageServer
except:
    import storageserverdummy as StorageServer
cache = StorageServer.StorageServer('deccandelight', 8)


class skytamil(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.skytamil.net/'
        self.icon = self.ipath + 'skytamil.png'
        self.cj = cache.cacheFunction(self.get_ddg, self.bu)

    def get_ddg(self, url):
        headers = self.hdr
        headers.update({'Referer': url})
        # js = requests.get('https://check.ddos-guard.net/check.js', headers=headers).text
        # rurl = url[:-1] + re.findall(r"src\s*=\s*'([^']+)", js)[0]
        # r = requests.get(rurl, headers=headers)
        r = requests.post('https://check.ddos-guard.net/check.js', headers=headers)
        return {'__ddg2': r.cookies.get('__ddg2')}

    def get_url(self, url, headers=None):
        if headers is None:
            headers = self.hdr
        resp = requests.get(url, headers=headers, cookies=self.cj)
        if resp.status_code == 403 and "DDoS protection by DDoS-GUARD" in resp.text:
            host = urllib_parse.urljoin(url, '/')
            self.cj = cache.cacheFunction(self.get_ddg, host)
            resp = requests.get(url, headers=headers, cookies=self.cj)
        return resp.text

    def get_menu(self):
        html = self.get_url(self.bu)
        items = {}
        cats = re.findall('id="menu-item-(?!755|758|757).+?href="([^"]+)">([^<]+)', html, re.DOTALL)
        sno = 1
        for caturl, cat in cats:
            items['{0:02d}{1}'.format(sno, cat)] = caturl
            sno += 1
        items['99[COLOR yellow]** Search **[/COLOR]'] = self.bu + '?s='
        return (items, 7, self.icon)

    def get_items(self, url):
        movies = []
        if url[-3:] == '?s=':
            search_text = self.get_SearchQuery('Sky Tamil')
            search_text = urllib_parse.quote_plus(search_text)
            url = url + search_text

        headers = self.hdr
        headers.update({'Referer': self.bu})
        html = self.get_url(url, headers=headers)
        mlink = SoupStrainer("main")
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        Paginator = mdiv.find("div", {"class": "post-pagination"})
        items = mdiv.find_all('article')

        for item in items:
            title = self.unescape(item.find('h4').text)
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

        return (movies, 8)

    def get_videos(self, url):
        videos = []
        headers = self.hdr
        headers.update({'Referer': self.bu})
        html = self.get_url(url, headers=headers)
        mlink = SoupStrainer('div', {'class': re.compile('^entry-content')})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)

        try:
            links = videoclass.find_all('iframe')
            for link in links:
                iurl = link.get('src')
                if 'videoslala.com' in iurl:
                    iurl += '$$' + url
                self.resolve_media(iurl, videos)
        except:
            pass

        return videos
