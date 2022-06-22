"""
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
"""
from resources.lib.base import Scraper
from bs4 import BeautifulSoup, SoupStrainer
from six.moves import urllib_parse
import re
import requests
from kodi_six import xbmcgui


class desit(Scraper):
    def __init__(self):
        Scraper.__init__(self)
        self.bu = 'https://www.desitellybox.me/'
        self.icon = self.ipath + 'desit.png'

    def get_menu(self):
        html = requests.get(self.bu, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'colm span_1_of_3'})
        items = BeautifulSoup(html, "html.parser", parse_only=mlink)
        mlist = {}
        ino = 1
        for item in items:
            mlist.update({'{0:02d}{1}'.format(ino, item.strong.text): item.strong.text})
            ino += 1
        mlist.update({'99[COLOR yellow]** Search **[/COLOR]': '{0}?s=MMMM7'.format(self.bu)})
        return (mlist, 5, self.icon)

    def get_second(self, iurl):
        """
        Get the list of shows.
        """
        shows = []

        html = requests.get(self.bu, headers=self.hdr).text
        mlink = SoupStrainer('div', {'class': 'colm span_1_of_3'})
        mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
        for source in mdiv:
            if source.strong.text == iurl:
                items = source.find_all('li')
                thumb = self.bu[:-1] + source.find('img')['src']
                for item in items:
                    title = self.unescape(item.text)
                    url = item.find('a')['href']
                    if 'completed shows' not in title.lower():
                        shows.append((title, thumb, url))
        return (shows, 7)

    def get_items(self, iurl):
        episodes = []
        if iurl[-3:] == '?s=':
            search_text = self.get_SearchQuery('Desi Tashan')
            search_text = urllib_parse.quote_plus(search_text)
            iurl += search_text
        nextpg = True
        while nextpg and len(episodes) < 21:
            html = requests.get(iurl).text
            mlink = SoupStrainer('div', {'class': 'col col_12_of_12'})
            mdiv = BeautifulSoup(html, "html.parser", parse_only=mlink)
            items = mdiv.find_all('div', {'class': 'item_content'})
            for item in items:
                title = self.unescape(item.h4.text)
                if 'watch online' in title.lower():
                    title = self.clean_title(title)
                    url = item.find('a')['href']
                    try:
                        icon = item.find('img')['src']
                    except:
                        icon = self.icon
                    episodes.append((title, icon, url))

            plink = SoupStrainer('ul', {'class': 'page-numbers'})
            Paginator = BeautifulSoup(html, "html.parser", parse_only=plink)

            if 'next' in str(Paginator):
                iurl = Paginator.find('a', {'class': 'next'}).get('href')
                if len(episodes) > 20:
                    currpg = Paginator.find('span', {'class': 'current'}).text
                    lastpg = Paginator.find_all('a', {'class': 'page-numbers'})[-2].text
                    title = 'Next Page.. (Currently in Page {0} of {1})'.format(currpg, lastpg)
                    episodes.append((title, self.nicon, iurl))
            else:
                nextpg = False
        return (episodes, 8)

    def get_videos(self, iurl):
        videos = []
        html = requests.get(iurl).text
        mlink = SoupStrainer('div', {'class': 'entry_content'})
        videoclass = BeautifulSoup(html, "html.parser", parse_only=mlink)
        items = videoclass.find_all('a', {'class': None})
        if len(items) < 1:
            items = videoclass.find_all('a', {'class': re.compile('nofollow')})
        prog_per = 0
        p_dialog = xbmcgui.DialogProgress()
        p_dialog.create('Deccan Delight', 'Collecting Links...')
        for item in items:
            vid_link = item['href']
            vidtxt = self.unescape(item.text)
            try:
                vidtxt = re.findall(r'(Part\s*\d*)', vidtxt)[0]
            except:
                vidtxt = ''
            self.resolve_media(vid_link, videos, vidtxt)
            prog_per += int(100 / len(items))
            if p_dialog.iscanceled():
                return videos
            p_dialog.update(prog_per, 'Collected Links... {} from {}'.format(len(videos), len(items)))
        return videos
