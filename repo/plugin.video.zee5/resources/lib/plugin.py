
import sys

from . import kodilogging
from . import kodiutils
from . import settings

import six
from six.moves import urllib_parse
from kodi_six import xbmc, xbmcaddon, xbmcplugin, xbmcgui, xbmcvfs

import re 
import requests
import time
try:
    from StringIO import StringIO ## for Python 2
except ImportError:
    from io import StringIO ## for Python 3
import web_pdb
import uuid
import json
import math
import logging
from json import dumps
import hashlib
import os

# Python 2 and 3: option 3
try:
    import itertools.imap as map
except ImportError:
    pass
import operator

from datetime import datetime

#import server
import inputstreamhelper
try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

params = dict(urllib_parse.parse_qsl(sys.argv[2][1:]))

addon = xbmcaddon.Addon()
logger = logging.getLogger(addon.getAddonInfo('id'))
kodilogging.config()

_addonname = addon.getAddonInfo('name')
#_version = addon.getAddonInfo('version')
#_addonID = addon.getAddonInfo('id')
_icon = addon.getAddonInfo('icon')
_fanart = addon.getAddonInfo('fanart')

platform = 'desktop_web'
languages = settings.get_languages()
session = requests.Session()
ITEMS_LIMIT = 10
#device_id= 'o7JvbEPk3KRA14d8FwEr000000000000'
#device_id= '4363debbc0dded755df0b635277271c0'
#device_id= 'iIxsxYf40cqO3koIkwzKHZhnJzHN13zb"
#device_id= 'WebBrowser'
#platform = 'web_app'
# Initialise the token.

devid=addon.getSetting('devid')
deviceid=addon.getSetting('deviceID')

if deviceid:
    device_id= deviceid
elif devid=="D1":
    device_id= str(uuid.uuid4())
elif devid=="D2":
    device_id= 'WebBrowser'
elif devid=="D3":
    device_id= 'o7JvbEPk3KRA14d8FwEr000000000000'
elif devid=="D4":
    device_id= '56bc08d9-3cd4-4be0-8385-e9459feea721'
elif devid=="D5":
    device_id= 'o7JvbEPk3KRA14d8FwEr000000000000'
    
window = xbmcgui.Window(10000)
cache = StorageServer.StorageServer('zee5', 4)

"""
headers = {"user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
           
def get_header():
    url='https://www.zee5.com/requestheaders'
    data = requests.get(url,headers=headers).json()
    for name, value in six.iteritems(data):
        headers[name]=value
    return
        

get_header()
headers["content-type"] = "application/json"

"""
headers = {
    "origin": "https://www.zee5.com",
    "referer": "https://www.zee5.com",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "accept": "application/json, text/plain, */*",
    "content-type": "application/json",
    "cache-control": "no-cache"
}

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/95.0"
if xbmc.getCondVisibility('System.Platform.Android'):
    USER_AGENT = "Mozilla/5.0 (Linux; Android 7.1.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
elif xbmc.getCondVisibility('System.Platform.Windows'):
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
elif xbmc.getCondVisibility('System.Platform.Linux'): 
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36 Firefox/95.0" 

headers["user-agent"] = USER_AGENT


"""

def DeviceID():
    from selenium.webdriver import Chrome
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import platform
    cap = DesiredCapabilities().CHROME
    cap["marionette"] = False
    options = Options()
    options.headless = True
    options.add_argument("user-data-dir=%s" %xbmc.translatePath( "special://temp/" ))
    options.set_capability("marionette", False)
    system=platform.system()
    if system=="Windows":
        path =  xbmc.translatePath("special://home")+"addons\\script.module.selenium\\bin\\chromedriver\\win32\\chromedriver"
    elif system=="LibreELEC":
        path =  xbmc.translatePath("special://home")+"addons\\script.module.selenium\\bin\\chromedriver\\libreelec\\chromedriver"
    else:
        path =  xbmc.translatePath("special://home")+"addons\\script.module.selenium\\bin\\chromedriver\\linux64\\chromedriver"

    #log_path=xbmc.translatePath( "special://temp/" )+"geckodriver.log"
    devid=""
    browser = Chrome(desired_capabilities=cap, executable_path=path,options=options)
    try:
        browser.implicitly_wait(10)
        browser.get('https://www.zee5.com/')
    except:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(_addonname, "Device read timed out", 3000, _icon))
    else:
        time.sleep(10)
        #web_pdb.set_trace()
        devid=browser.execute_script('return localStorage.getItem("guestToken");')
        window.setProperty("DeviceID", devid) 
        browser.close()
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(_addonname, "Device Stored", 3000, _icon))
    return devid

def DeviceID2():
    from selenium import webdriver
    from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
    from selenium.webdriver.firefox.options import Options
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

    cap = DesiredCapabilities().FIREFOX
    cap["marionette"] = False
    options = Options()
    options.set_preference("browser.download.folderList",2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir",xbmc.translatePath( "special://temp/" ))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-bittorrent,application/octet-stream")
    options.add_argument("--headless")
    options.set_capability("marionette", False)
    path =  xbmc.translatePath("special://home")+"addons\\script.module.selenium\\bin\\geckodriver\\win32\\geckodriver\\geckodriver"
    log_path=xbmc.translatePath( "special://temp/" )+"geckodriver.log"
    #web_pdb.set_trace()
    browser = webdriver.Firefox(capabilities=cap, executable_path=path,firefox_options=options,log_path=log_path)
    return


hdr = {
    "origin": "https://www.zee5.com",
    "referer": "https://www.zee5.com",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "accept": "*/*",
    "content-type": "application/octet-stream",
    "user-agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}
    
def get_header():
    url='https://www.zee5.com/requestheaders'
    data = requests.get(url,headers=headers).json()
    for name, value in six.iteritems(data):
        hdr[name]=value
    return


def get_video_token():
    url='https://useraction.zee5.com/tokennd/'
    #https://gwapi.zee5.com/user/videoStreamingToken?channel_id=0-9-zing&country=IN&device_id=WebBrowser
    data = requests.get(url, headers=headers).json()
    return data['video_token']

if window.getProperty("DeviceID"):
    device_id=window.getProperty("DeviceID") 
elif devid=="D5":
    device= DeviceID()
    if device:
        device_id=device
        
def get_live_token():
    url='https://useraction.zee5.com/token/live.php'
    data = requests.get(url, headers=headers).json()
    return data['video_token']
"""
def get_token():
    url='https://useraction.zee5.com/token/platform_tokens.php?platform_name={}'.format(platform)
    data = requests.get(url, headers=headers).json()
    headers["x-access-token"] = data['token']
    return 

def add_device():
    url = "https://subscriptionapi.zee5.com/v1/device"
    body = {"name":"WebBrowser","identifier":device_id}
    body = dumps(body)    
    jd = requests.post(url,headers=headers,data=body).json()    
    return 
   
def login():
    email=addon.getSetting('email')
    password = addon.getSetting('password')

    if email:    
        Pattern = re.compile("[7-9][0-9]{9}")
        if (Pattern.match(email)):
            url = "https://whapi.zee5.com/v1/user/loginMobile_v2.php"
        else :
            url = "https://whapi.zee5.com/v1/user/loginemail_v2.php"

        if (Pattern.match(addon.getSetting('email'))):
            body = {"aid":"91955485578","guest_token":"48b30b9e-b677-4669-a079-5edc36bf54f9","lotame_cookie_id":"","mobile":"91"+email,"password":password,"platform":"web","version":"2.50.87"}
        else :
            body = {"aid":"91955485578","guest_token":"48b30b9e-b677-4669-a079-5edc36bf54f9","lotame_cookie_id":"", "email":email,"password":password,"platform": "web","version": "2.50.50"}
        
        body = dumps(body)

        jd = requests.post(url,headers=headers,data=body).json()
        
        if jd.get('access_token'):
            headers.update({'refreshToken': jd['refresh_token']})
            headers.update({'Authorization': 'bearer '+jd['access_token']})
            window.setProperty("refreshToken", jd['refresh_token'])
            window.setProperty("Authorization", 'bearer '+jd['access_token'])
            add_device()
        else:
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(_addonname, "Invalid login credential", 3000, _icon))
    return

def get_user():

    url='https://userapi.zee5.com/v1/user'
    data = requests.get(url, headers=headers).json()

    if not data.get('code'):
        headers.update({'uid': data['id']})
        Pattern = re.compile("[7-9][0-9]{9}")
        if (Pattern.match(addon.getSetting('email'))):
            headers.update({'mobile': data['mobile']})
        else:
            headers.update({'email': data['email']})
        headers.update({'country': data['registration_country']})
    return 


get_token()
refreshToken = window.getProperty("refreshToken")
        
if refreshToken:
    headers.update({'refreshToken': window.getProperty("refreshToken")})
    headers.update({'Authorization': window.getProperty("Authorization")})
else:
    login()
    
    
get_user()


def get_code():
    url = "https://useraction.zee5.com/device/v2/getcode.php"
    body = {"identifier":"pwa","partner":"zee5","authorization":headers["Authorization"]}
    
    body = dumps(body)
    jd = requests.post(url,headers=headers,data=body).json()
    devid=str(uuid.UUID(jd.get('token')))
    return devid



country=headers['country'] if headers.get('country') else 'IN'

def clear_cache():
    """
    Clear the cache database.
    """

    msg = 'Cached Data has been cleared'
    cache.table_name = 'zee5'
    cache.cacheDelete('%get%')
    window.clearProperty ("refreshToken")
    window.clearProperty ("Authorization")
    window.clearProperty ("xaccesstoken")
    window.clearProperty ("DeviceID")
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(_addonname, msg, 3000, _icon))
"""
def get_actor(cast):
    parts = cast.split('|')
    CastlistCastlist = ''
    for part in parts:
        if show not in part.lower():
            r = re.search(r'\d{4}',part)
            if not r:
                etitle += part + ' '
    if len(etitle) < 4:
        CastlistCastlist = cast
    return Castlist
"""

def get_genre(item):
    """
    Returns a string of genre -- comma separated if multiple genres.
    Returns ALL as default.
    """
    if not item:
        return 'ALL'

    genres = set()
    for genreField in ['genre', 'genres']:
        data = item.get(genreField)
        if not data:
            continue
        genres.update(map(operator.itemgetter('value'), data))

    return ",".join(list(genres)) if genres else 'ALL'

def go_page(sid,page,total):

    """
    kb = xbmc.Keyboard('', 'Search Page')
    kb.doModal()  # Onscreen keyboard appears
    if not kb.isConfirmed():
        return
    page=int(kb.getText())-1
    """
    pnum=xbmcgui.Dialog().numeric(0,'Page episodeNumber')
    #page=int(page)-1
    if int(pnum)>int(total):
        pnum=total 
    list_episodes(sid,pnum)
    # User input
    return 

"""
def get_srt(vttfile):
    content = requests.get(vttfile,headers=headers).content
    replacement = re.sub(r'([\d]+)\.([\d]+)', r'\1,\2', content)
    replacement = re.sub(r'WEBVTT\n\n', '', replacement)
    replacement = re.sub(r'^\d+\n', '', replacement)
    replacement = re.sub(r'\n\d+\n', '\n', replacement)
    replacement = StringIO.StringIO(replacement)
    idx = 1
    content = ''
    for line in replacement:
        if '-->' in line:
            if len(line.split(' --> ')[0]) < 12:
                line = re.sub(r'([\d]+):([\d]+),([\d]+)', r'00:\1:\2,\3', line)
            content += '%s\n%s'%(idx,line) 
            idx += 1
        else:
            content += line
    f = xbmcvfs.File('special://temp/TemporarySubs.en.srt','w')
    result = f.write(content)
    f.close()
    return 'special://temp/TemporarySubs.en.srt'
    """

def get_user_input():
    kb = xbmc.Keyboard('', 'Search for Movies/TV Shows/Trailers/Videos in all languages')
    kb.doModal()  # Onscreen keyboard appears
    if not kb.isConfirmed():
        return

    # User input
    return kb.getText()

def list_search():
    query = get_user_input()
    if not query:
        return []

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Search/{}'.format(query))
    """
    url = 'https://gwapi.zee5.com/content/getContent/search?q={}&start=0&limit={}&asset_type=0,6,1,9,9,101&country={}&languages={}&translation=en&version=5&page=1'.format(
        urllib_parse.quote_plus(query),
        ITEMS_LIMIT,
        country,
        languages
    )
    """
    url = 'https://gwapi.zee5.com/content/getContent/autoSuggest?country={}&q={}&limit={}&translation=en&languages={}&version=1'.format(
        country,
        urllib_parse.quote_plus(query),
        ITEMS_LIMIT,
        country,
        languages
    )
    data = requests.get(url,headers=headers).json()
    if not data.get('numFound'):
        kodiutils.notification('No Search Results', 'No item found for {}'.format(query))
        return
    listing = []
    
    for item in data['docs']:
        title=item['title']
        eid=item['id']
        mediatype=item['asset_subtype']
        list_item = xbmcgui.ListItem(label=title)
        image=item['image_url']
        icon={'poster': image,
              'icon': image,
              'thumb': image,
              'fanart': image}
        list_item.setArt(icon)
        list_item.setInfo('video',  
                    {'title': title,
                    'genre': get_genre(item),
                    #'castandrole':season['actors'] if season.get('actors') else [],
                    #'plot':description,
                    'year': item.get('release_date')[:4] if item.get('release_date') else None,
                    'aired': item.get('release_date')[:10] if item.get('release_date') else None,
                    'duration': item.get('duration') if item.get('duration') else None,
                    'mediatype': mediatype
                    })
        #
        if mediatype in ['movie','video','clip','trailer','episode']:
            list_item.setProperty('IsPlayable', 'true')
            url = '{0}?action=playNew&vid={1}&sid={2}&itemtype=MOVIE'.format(_url,eid,eid)
            is_folder = False
            xbmcplugin.setContent(_handle, 'movies')
        elif mediatype=='tvshow':
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=list_season&sid={1}&page=1&showtype={2}'.format(_url,eid,mediatype)
            is_folder = True
        else:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=list_season&sid={1}&page=1'.format(_url,eid)
            is_folder = True
        """
        if 'Next Page' in etitle:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=list_episodes&sid={1}&page={2}'.format(_url, eid, epid)
            is_folder = True
        else:
            list_item.setProperty('IsPlayable', 'true')
            url = '{0}?action=list_episodes&sid={1}&page={2}'.format(_url, eid, epid)
            is_folder = False
        """
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'episodes')
    xbmcplugin.endOfDirectory(_handle)


def get_top():

    top=[]
    top.append(('Live TV','3'))
    url='https://b2bapi.zee5.com/front/countrylist.php?lang=en&ccode={}'.format(country)
    data = requests.get(url,headers=headers).json()

    mains = data[0]['collections']['web_app']
    
    for name, collection_id in six.iteritems(mains):
        title=name.title()
        cid=collection_id
        if title!='Play5':
            top.append((title,cid)) 
 
    title = 'Search' 
    cid=1
    top.append((title,cid))
    title = 'Clear Cache'
    cid=2
    top.append((title,cid))
    return top


def get_channels(cid,page):
    """
    Get the list of channels.
    :return: list
    """
    channels = []
    #web_pdb.set_trace()
    url = 'https://gwapi.zee5.com/content/collection/{id}?country={country}&page={page}&limit={limit}&translation=en&item_limit=10&languages={lang}&version=10'.format(
                id=cid,
                country=country,
                page=page,
                limit=ITEMS_LIMIT,
                lang=languages
            )
    data = requests.get(url,headers=headers).json()

    for bucket in data['buckets'] or []:

        # Skip buckets without any items.
        if not bucket.get('items'):
            continue

        icon={'poster': bucket['items'][0]['image_url'].get('list'),
              'icon': bucket['items'][0]['image_url'].get('list'),
              'thumb': bucket['items'][0]['image_url'].get('list'),
              'fanart': bucket['items'][0]['image_url'].get('cover')}

        bid=bucket['id']
        title=bucket['title']
        asset_subtype=bucket['asset_subtype']
        labels = {'title': title,
                  'plot':bucket.get('description')
                }
        channels.append((title,icon,bid,labels,asset_subtype))
    
    #
    page = int(page)
    totals = int(data['total'])
    itemsleft = totals - page * 10

    finalpg=True
    if itemsleft > 0:
        finalpg = False
        pages = int(math.ceil(totals/10.0))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (page,pages)
        page += 1
        icon = {'poster': _icon,
               'icon': _icon,
               'thumb': _icon,
               'fanart': _fanart}
        labels = {}
        channels.append((title,icon,page,labels,''))

    return channels

def get_shows(showid,page):
    """
    Get the list of shows.
    :return: list
    """
    shows = []
    
    url='https://gwapi.zee5.com/content/collection/{id}?country={country}&page={page}&limit={limit}&languages={lang}&translation=en&version=10'.format(
            id=showid,
            country=country,
            page=page,
            limit=ITEMS_LIMIT,lang=languages)
    
    data = requests.get(url,headers=headers).json()

    seasons=data['buckets'][0]['items']
    for season in seasons:

        #title=season['title'].encode('utf-8')
        title=season['title']
        description=season.get('description')
        
        if season['asset_type']==9:
            stype='live'
            #
        else:
            stype=season['asset_subtype']

        if stype=='external_link':
            stype=season['slug'].split('/')[3] if season['slug'][:4] =='http' else season['slug'].split('/')[0]
            stype=stype[:-1]
            show_id=season['slug'].rsplit('/', 2)[1] if season['slug'].rsplit('/', 1)[1] =='latest1' else season['slug'].rsplit('/', 1)[1]

            """
            if season['asset_type']==101:
                show_id=season['slug'].rsplit('/', 1)[1]
                #stype='live'
            else:
                show_id=season['slug'].rsplit('/', 2)[1]
                #stype='tvshow'
            """
        else:
            show_id=season['id']
        
        if stype in ['movie','video','clip','episode','live','channel','collection','trailer']:
            mediatype='movie'
        else:
            mediatype='tvshow'
        labels = {	'title': title,
                    'genre': get_genre(season),
                    'castandrole':season['actors'] if season.get('actors') else [],
                    'plot':description,
                    'year': season.get('release_date')[:4] if season.get('release_date') else None,
                    'aired': season.get('release_date')[:10] if season.get('release_date') else None,
                    'duration': season.get('duration') if season.get('duration') else None,
                    'mediatype': mediatype
                 }
        icon={'poster': season['image_url'].get('list'),
              'icon': season['image_url'].get('list'),
              'thumb': season['image_url'].get('list'),
              'fanart': season['image_url'].get('cover')
            }

        shows.append((title,icon,show_id,labels,stype))

    page = int(page)
    totals = int(data['total'])
    itemsleft = totals - page * 10
    finalpg = True
    if itemsleft > 0:
        finalpg = False
        pages = int(math.ceil(totals/10.0))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (page,pages)
        page += 1
        labels = {}
        icon = {'poster': _icon,
               'icon': _icon,
               'thumb': _icon,
               'fanart': _fanart}
        shows.append((title,icon,page,labels,''))
    return shows

def get_season(season_id,page,showtype):
    """
    Get the list of episodes.
    :return: list
    """
    season = []
    if showtype == 'Manual':
        stype='collection'
    else:
        stype='tvshow'
    url='https://gwapi.zee5.com/content/{stype}/{id}?country={country}&page={page}&limit={limit}&languages={lang}&version=10'.format(
            stype=stype,
            id=season_id,
            country=country,
            page=page,
            limit=ITEMS_LIMIT,
            lang=languages
        )

    data = requests.get(url,headers=headers).json()
    if showtype == 'Manual':
        seasons=data['buckets'][0]['items']
    else:
        seasons=data['seasons']
    
    for show in seasons:
        if showtype == 'Manual':
            subtype=show.get('asset_subtype')
            rdate=show.get('release_date')[:10] if show.get('release_date') else None
            image1=show['image_url'].get('cover')
            image2=show['image_url'].get('list')
            desc=show.get('description')
        else:
            subtype=data.get('asset_subtype')
            rdate=data.get('release_date')[:10] if data.get('release_date') else None
            image1=data.get('image_url')
            image2=data.get('image_url')
            desc=data.get('description')

        
        if subtype in ['movie','video','clip','webisode','trailer']:
            mediatype='movie'
            image=data.get('image_url')
        else:
            mediatype='tvshow'

        sid=show.get('id')
        stitle = show.get('title')

        labels = {  'title': stitle,
                    'genre': get_genre(data),
                    'mediatype': mediatype,
                    'plot':desc,
                    'aired' : rdate,
                 }

        icon = {'poster': image1,
               'icon': image2,
               'thumb': image2,
               'fanart': image2}

        season.append((stitle,icon,sid,labels,subtype))

    if showtype == 'Manual':
        page = int(page)
        totals = int(data['total'])
        itemsleft = totals - page * 10
        finalpg = True
        if itemsleft > 0:
            finalpg = False
            pages = int(math.ceil(totals/10.0))

        if not finalpg:
            stitle = 'Next Page.. (Currently in Page %s of %s)' % (page,pages)
            page += 1
            labels = {}
            icon = {'poster': _icon,
                   'icon': _icon,
                   'thumb': _icon,
                   'fanart': _fanart}
            season.append((stitle,icon,page,labels,''))

    return season

def get_episodes(episodeid,page):
    """
    Get the list of episodes.
    :return: list
    """
    episodes = []
    page = int(page)
    
    url='https://gwapi.zee5.com/content/tvshow/?season_id={id}&type=episode&translation=en&country={country}&on_air=true&asset_subtype=tvshow&page={page}&limit={limit}'.format(
            id=episodeid,
            country=country,
            page=page,
            limit=ITEMS_LIMIT
        )

    data = requests.get(url,headers=headers).json()
    items = data['episode']
    for item in items:
        etitle = 'Episodes {} - {}'.format(item.get('episode_number'), six.ensure_str(item.get('title'), encoding='utf-8', errors='strict'))
        eid=item.get('id')
        showid=item['tvshow'].get('id')

        plot=item.get('description')
        eptype=item.get('asset_subtype')
        labels = {'title': etitle,
                  'genre': get_genre(item),
                  'plot': plot,
                  'duration': item.get('duration'),
                  'episode': item.get('episode_number'),
                  'tvshowtitle': etitle,
                  'year':item.get('release_date')[:4],
                  'aired':item.get('release_date')[:10],
                  'mediatype': 'episode'
                 }
        fanart = item['image_url']
        poster = item['image_url']
        icon = item['image_url']
        thumb = item['image_url']

        icon = {'poster': poster,
               'icon': icon,
               'thumb': thumb,
               'fanart': fanart}

        episodes.append((etitle,eid,icon,labels,eptype,showid))
    total=data['total']

    balcount=int(total)-page*10
    if balcount > 0:
        #pages=int(total)/10
        pages, mod = divmod(int(total), 10)

        pages=pages+1 if mod >0 else pages
        etitle = 'Next Page... (Page %s of %s)'%(page,pages)
        page += 1
        labels = {}
        icon = {'poster': _icon,
               'icon': _icon,
               'thumb': _icon,
               'fanart': _fanart}
        episodes.append((etitle,page,icon,labels,eptype,showid))


        etitle = 'Go Page...'
        labels = {}
        icon = {'poster': _icon,
               'icon': _icon,
               'thumb': _icon,
               'fanart': fanart}
        episodes.append((etitle,page,icon,labels,eptype,pages))

    return episodes


def list_top():
    """
    Create the list of countries in the Kodi interface.
    """
    
    items = get_top()
    listing = []
    for title,cid in items:
        list_item = xbmcgui.ListItem(label=title)
        if 'Search' in title:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=search'.format(_url)
            is_folder = True
        elif 'Clear Cache' in title:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=clear_cache'.format(_url)
            is_folder = True
        elif 'Live TV' in title:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=list_live'.format(_url)
            is_folder = True
            list_item.setArt({'poster': _icon,
                              'icon': _icon,
                              'thumb': _icon,
                              'fanart': _fanart})
        else:
            list_item.setInfo('video', {'title': title})
            list_item.setProperty('IsPlayable', 'false')
            list_item.setArt({'poster': _icon,
                              'icon': _icon,
                              'thumb': _icon,
                              'fanart': _fanart})
            url = '{0}?action=list_item&cid={1}&page=1'.format(_url, cid)
            is_folder = True
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    #xbmcplugin.setContent(_handle, 'addons')
    xbmcplugin.endOfDirectory(_handle)

def list_channels(cid, page):
    """
    Create the list of countries in the Kodi interface.
    """

    channels = cache.cacheFunction(get_channels,cid, page)
    listing = []

    for title,icon,bid,labels,subtype in channels:
        list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR]'%title)	
        if 'Next Page' in title:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=list_item&cid={1}&page={2}'.format(_url,cid,bid)
            is_folder = True
        else:
            list_item.setProperty('IsPlayable', 'false')
            list_item.setArt(icon)
            list_item.setInfo('video', labels)
            url = '{0}?action=list_shows&showid={1}&page=1'.format(_url, bid)
            is_folder = True
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    #xbmcplugin.setContent(_handle, 'addons')
    xbmcplugin.endOfDirectory(_handle)

def list_shows(showid,page):
    """
    Create the list of channels in the Kodi interface.
    """
    
    shows = cache.cacheFunction(get_shows,showid,page)
    listing = []
    for title,icon,sid,labels,stype in shows:
        list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR]'%title)
        list_item.setArt(icon)
        list_item.setInfo('video', labels)

        #title=str(title, 'utf-8')
        if 'Next Page' in title:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=list_shows&showid={1}&page={2}'.format(_url,showid,sid)
            is_folder = True
        else:
            if stype in ['movie','video','clip','episode','webisode','collection','trailer']:
                list_item.setProperty('IsPlayable', 'true')
                url = '{0}?action=playNew&vid={1}&sid={2}&itemtype=EPISODE'.format(_url,sid,showid)
                is_folder = False
                xbmcplugin.setContent(_handle, 'movies')
            elif stype in ['live','channel']:
                list_item.setProperty('IsPlayable', 'true')
                url = '{0}?action=playNew&vid={1}&sid={2}&itemtype=LIVE'.format(_url,sid,showid) #
                is_folder = False
            else:
                list_item.setProperty('IsPlayable', 'false')
                url = '{0}?action=list_season&sid={1}&page=1&showtype={2}'.format(_url,sid,stype)
                is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    #xbmcplugin.setContent(_handle, 'episodes')
    xbmcplugin.endOfDirectory(_handle)

def list_season(seasonid,page,showtype):
    """
    Create the list of channels in the Kodi interface.
    """
    shows = cache.cacheFunction(get_season,seasonid,page,showtype)
    listing = []

    for title,icon,sid,labels,stype in shows:
        list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR]'%title)
        list_item.setArt(icon)
        list_item.setInfo('video', labels)
        if 'Next Page' in title:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=list_season&showid={1}&page={2}&showtype={3}'.format(_url,seasonid,sid,showtype)
            is_folder = True
        else:
            if stype in ['movie','video','clip','webisode','trailer']:
                list_item.setProperty('IsPlayable', 'true')
                url = '{0}?action=playNew&vid={1}&sid={2}&itemtype=EPISODE'.format(_url,sid,seasonid)
                is_folder = False
                xbmcplugin.setContent(_handle, 'movie')
            else:
                list_item.setProperty('IsPlayable', 'false')
                url = '{0}?action=list_episodes&sid={1}&page=1'.format(_url,sid)
                is_folder = True
        listing.append((url, list_item, is_folder))

    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)
    
def list_episodes(eid,page):
    """
    Create the list of episodes in the Kodi interface.
    """
    episodes = cache.cacheFunction(get_episodes,eid,page)
    listing = []

    for etitle,epid,icon,labels,eptype,showid in episodes:
        list_item = xbmcgui.ListItem(label=etitle)
        list_item.setArt(icon)
        list_item.setInfo('video', labels)
        if 'Next Page' in etitle:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=list_episodes&sid={1}&page={2}'.format(_url, eid, epid)
            is_folder = True
        elif 'Go Page' in etitle:
            list_item.setProperty('IsPlayable', 'false')
            url = '{0}?action=gopage&sid={1}&page={2}&total={3}'.format(_url,eid,epid,showid)
            is_folder = True
        else:
            list_item.setProperty('IsPlayable', 'true')
            url = '{0}?action=playNew&vid={1}&sid={2}&itemtype=EPISODE'.format(_url,epid,showid)
            is_folder = False
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'episodes')
    xbmcplugin.endOfDirectory(_handle)



def list_live():

    channels = [('Music','0-8-3505'), ('GEC/Movies','0-8-homepagechannelswesh'), ('News','0-8-3491' ),('Premium','0-8-8487')] #, 0-8-5852('Religious'), ('Food'), ('Infotainment'), ('Lifestyle'), ('Sports')
    listing = []
    
    for title,lid in channels:
        
        list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR]'%title)
        list_item.setProperty('IsPlayable', 'false')
        url = '{0}?action=list_shows&showid={1}&page=1'.format(_url, lid)
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)
    
"""
def get_subtitles(title,data):
    subtitle_url = data
    if not subtitle_url:
        return []

    subtitles_files = []
    for subtitle_lang in subtitle_url:
        if not subtitle_lang:
            continue

        subtitle_file = kodiutils.download_url_content_to_temp(subtitle_url, '{}.srt'.format(title,subtitle_lang))
        subtitles_files.append(subtitle_file)

    return subtitles_files
"""

def playNew(item_id,show_id,item_type):
    
    userid= headers.get('uid') if 'uid' in headers else ''

    if headers.get('Authorization'):
        if item_type=='EPISODE':
            url='https://spapi.zee5.com/singlePlayback/getDetails/secure?content_id={}&show_id={}&device_id={}&platform_name={}&translation=en&user_language={}&country={}&app_version=2.51.26&user_type=register&check_parental_control=false&uid={}&ppid={}&version=12'.format(item_id,show_id,device_id,platform,languages,country,userid,device_id)
        elif item_type=='MOVIE':
            url='https://spapi.zee5.com/singlePlayback/getDetails/secure?content_id={}&device_id={}&platform_name={}&translation=en&user_language={}&country={}&app_version=2.51.26&user_type=register&check_parental_control=false&uid={}&ppid={}&version=12'.format(item_id,device_id,platform,languages,country,userid,device_id)
        else:
            url='https://spapi.zee5.com/singlePlayback/getDetails/secure?channel_id={}&device_id={}&platform_name={}&translation=en&user_language={}&country={}&app_version=2.51.26&user_type=register&check_parental_control=false&uid={}&ppid={}&version=12'.format(item_id,device_id,platform,languages,country,userid,device_id)
        
        body = {"Authorization":headers.get('Authorization'),"x-access-token":headers.get('x-access-token')}
    else:
        if item_type=='EPISODE':
            url='https://spapi.zee5.com/singlePlayback/getDetails/secure?content_id={}&show_id={}&device_id={}&platform_name={}&translation=en&user_language={}&country={}&app_version=2.51.26&user_type=guest&check_parental_control=false&ppid={}&version=12'.format(item_id,show_id,device_id,platform,languages,country,device_id)
        elif item_type=='MOVIE':
            url='https://spapi.zee5.com/singlePlayback/getDetails/secure?content_id={}&device_id={}&platform_name={}&translation=en&user_language={}&country={}&app_version=2.51.26&user_type=guest&check_parental_control=false&ppid={}&version=12'.format(item_id,device_id,platform,languages,country,device_id)
        else:
            url='https://spapi.zee5.com/singlePlayback/getDetails/secure?channel_id={}&show_id={}&device_id={}&platform_name={}&translation=en&user_language={}&country={}&app_version=2.51.26&user_type=guest&check_parental_control=false&ppid={}&version=12'.format(item_id,show_id,device_id,platform,languages,country,device_id)

        body = {"X-Z5-Guest-Token":device_id,"x-access-token":headers.get('x-access-token')}
    body = dumps(body)

    data = requests.post(url,headers=headers,data=body).json()
    
    if data.get('error_code')=='3608':
        if headers.get('Authorization'):
            add_device()
            data = requests.post(url,headers=headers,data=body).json()
    if data.get('error_msg'):
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(_addonname, data.get('error_msg'), 3000, _icon))
    else:
        video_url=""
        if not video_url:
            video_url=data['assetDetails'].get('hls_url') if data.get('assetDetails') else None
        if not video_url:
            video_url=data['keyOsDetails'].get('hls_token')
        if not video_url:
            video_url=data['keyOsDetails'].get('video_token')
        if not video_url and data['assetDetails'].get('video_url'):
            video_url=data['assetDetails']['video_url'].get('mpd')

       
        customdata=data['keyOsDetails'].get('sdrm')
        nl=data['keyOsDetails'].get('nl')
        #web_pdb.set_trace()
        lic_url='https://spapi.zee5.com/widevine/getLicense'        
        lic_hdr='Content-Type=&customdata=%s&nl=%s' % (customdata,nl)
        license_key = '%s|%s|R{SSM}|' % (lic_url,lic_hdr)
        
        play_item = xbmcgui.ListItem(path=video_url)

        #if data['assetDetails'].get('vtt_thumbnail_url'):
            #subtitles = data['assetDetails'].get('vtt_thumbnail_url').replace('thumbnails/index', 'manifest-en')
            #play_item.setSubtitles([subtitles])
        

        is_helper = inputstreamhelper.Helper('mpd', drm='widevine')
        inputstream_ready = is_helper.check_inputstream()

        hdr = "user-agent=%s"%USER_AGENT

        if six.PY3:
            play_item.setProperty('inputstream', 'inputstream.adaptive')
        else:
            play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        
        play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        
        if (video_url.find('mpd') != -1):
            play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            play_item.setMimeType('application/dash+xml')
            play_item.setProperty('inputstream.adaptive.license_key', license_key)
            
        elif (video_url.find('ism') != -1):
            play_item.setProperty('inputstream.adaptive.manifest_type', 'ism')
            play_item.setMimeType('application/vnd.ms-sstr+xml')   
            play_item.setProperty('inputstream.adaptive.license_type', 'com.microsoft.playready')   
        else:
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            play_item.setMimeType('application/vnd.apple.mpegurl')
        if item_type=='LIVE':
            play_item.setProperty('inputstream.adaptive.stream_headers', hdr)
        
        play_item.setContentLookup(False)
        
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)

def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring:
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(urllib_parse.parse_qsl(paramstring))
    # Check the parameters passed to the plugin

    if params:
        if params['action'] == 'list_item':
            list_channels(params['cid'],params['page'])
        elif params['action'] == 'list_shows':
            list_shows(params['showid'],params['page'])
        elif params['action'] == 'list_season':
            list_season(params['sid'],params['page'],params['showtype']) 
        elif params['action'] == 'list_episodes':
            list_episodes(params['sid'],params['page'])
        elif params['action'] == 'playNew':
            playNew(params['vid'],params['sid'],params['itemtype'])
        elif params['action'] == 'list_live':
            list_live()
        elif params['action'] == 'search':
            list_search()
        elif params['action'] == 'gopage':
            go_page(params['sid'],params['page'],params['total'])
        elif params['action'] == 'clear_cache':
            clear_cache()

    else:
        list_top()


def run():
    # Initial stuffs.
    kodiutils.cleanup_temp_dir()
    #device_id=DeviceID()
    router(sys.argv[2][1:])
