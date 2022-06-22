"""
    Voot Kodi Addon

"""

import sys
from kodi_six import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import six
from six.moves import urllib_parse
import re
import requests
import math

import web_pdb
from json import dumps
try:
    import StorageServer
except:
    import storageserverdummy as StorageServer

# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])

_addon = xbmcaddon.Addon()
_addonname = _addon.getAddonInfo('name')
_version = _addon.getAddonInfo('version')
_addonID = _addon.getAddonInfo('id')
_icon = _addon.getAddonInfo('icon')
_fanart = _addon.getAddonInfo('fanart')
_settings = _addon.getSetting

cache = StorageServer.StorageServer('voot', _settings('timeout'))
window = xbmcgui.Window(10000)

def clear_cache():
    """
    Clear the cache database.
    """
    msg = 'Cached Data has been cleared'
    cache.table_name = 'voot'
    cache.cacheDelete('%get%')
    window.clearProperty ("accessToken")
    xbmcgui.Dialog().notification(_addonname, msg, _icon, 3000, False)


if _settings('version') != _version:
    _addon.setSetting('version', _version)
    clear_cache()
    _addon.openSettings()

def refresh_login():
    #url = "https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/login"

    url = "https://userauth.voot.com/usersV3/v3/login"

    email=_addon.getSetting('email')
    password = _addon.getSetting('password')
    #
    if email:    
        Pattern = re.compile("[7-9][0-9]{9}")

        if (Pattern.match(email)):
            body = {"type":"mobile","deviceId":"Windows NT 10.0","deviceBrand":"PC/MAC", "data":{"countryCode": "+91","mobile":email,"password":password}}
        else :
            body = {"type":"traditional","deviceId":"Windows NT 10.0","deviceBrand":"PC/MAC", "data":{"email":email,"password":password}}
  
        body = dumps(body)

        jd = requests.post(url,headers=headers,data=body).json()
        if jd.get('data'):
            #headers.update({'refreshToken': jd['data']['authToken']['refreshToken']})
            headers.update({'accessToken': jd['data']['authToken']['accessToken']})
            #headers.update({'kToken': jd['data']['kToken']})
            #headers.update({'kTokenId': jd['data']['kTokenId']})
            #headers.update({'kUserId': jd['data']['kUserId']})
            #headers.update({'uId': jd['data']['uId']})
            #headers.update({'householdId': str(jd['data']['householdId'])})
            #headers.update({'ks': jd['data']['ks']})
            window.setProperty("accessToken", jd['data']['authToken']['accessToken'])
    return

apiUrl = 'https://psapi.voot.com/jio/voot/v1/voot-web'

headers = { #"User-Agent": "okhttp/3.4.1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "content-type": "application/json; charset=utf-8",
            "referer": "https://www.voot.com/",
            "Content-Version": "V4",
            "origin":"https://www.voot.com",
            "usertype": "avod"
          }

accessToken = window.getProperty("accessToken")
  
#refresh_login()


if accessToken:
    headers.update({'accessToken': window.getProperty("accessToken")})
else:
    refresh_login()


if _settings('EnableIP') == 'true':
    headers['X-Forwarded-For'] = _settings('ipaddress')

sortID = 'sortId=mostPopular'
if _settings('tvsort') == 'Name':
    sortID = 'sortId=a_to_z'

msort = 'sortId=mostPopular'
if _settings('msort') == 'Name':
    msort = 'sortId=a_to_z'

 
def get_top():
    """
    Get the list of countries.
    :return: list
    """
    MAINLIST = [('Channels','c4fb9fbd71bc23b070b21db8283fdc36'), ('Shows',''),('Movies','944d95ca210b6560a2718743ee1d14f1'),('Sports','30339426afb3cf69df12b15cdfffa050'),('Premium','f7fec50e02ce7da0a6819ab67c50cfe6'),('Live','e95ab780b4262539e79e2e2e2becff4d'),('Search','1'),('Clear Cache','2')]
    #MAINLIST = ['Channels', 'Movies','Live', 'Clear Cache']
    return MAINLIST

def get_langs():
    """
    Get the list of languages.
    :return: list
    """
    languages = ['Hindi','Marathi','Telugu','Kannada','Bengali','Gujarati','Tulu']

    langs = []
    for item in languages:
        url = '%s/content/generic/movies-by-language?language=include:%s&sort=title:asc,mostpopular:desc&responseType=common'%(apiUrl,item)

        jd = requests.get(url,headers=headers).json()        
        tcount = jd['totalAsset']
        langs.append((item,tcount))
    
    return langs


def getlicense(id):
    token=""
    if headers.get('ks'):
        hdr = { "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
                "content-type": "application/json",
                "authority": "rest-as.ott.kaltura.com",
                "accept-encoding": "gzip, deflate, br",
                "referer": "https://www.voot.com/",
                "origin":"https://www.voot.com"
              }
        url = "https://rest-as.ott.kaltura.com/v4_4/api_v3/service/multirequest"

        body = {"1":{"service":"asset","action":"get","id":id,"assetReferenceType":"media","ks":headers['ks']},"2":{"service":"asset","action":"getPlaybackContext","assetId":id,"assetType":"media","contextDataParams":{"objectType":"KalturaPlaybackContextOptions","context":"PLAYBACK"},"ks":headers['ks']},"apiVersion":"5.2.6","ks":headers['ks'],"partnerId":225}
        body = dumps(body)
        jd = requests.post(url,headers=hdr,data=body).json()
        for lictoken in jd['result'][1]['sources']:
            if lictoken.get('type') == 'DASH_LINEAR_APP' or lictoken.get('type') == 'DASHENC_PremiumHD':
                token=lictoken['drm'][1]['licenseURL']
    return token

def get_channels(id,offSet):
    """
    Get the list of channels.
    :return: list
    """
    channels = []
    finalpg = True

    url = '%s/content/specific/editorial?query=include:%s&responseType=common&page=%s'%(apiUrl,id,offSet)
    
    jd = requests.get(url,headers=headers).json()
    items = jd['result']
    for item in items:
        title = item.get('name')
        tcount = item.get('sampledCount')
        icon = item['seo'].get('ogImage').replace(' ','%20')
        sbu = item.get('SBU')
        item_id = item.get('jioMediaId')          #jioMediaId
        mediaType= item.get('mediaType')
        channels.append((title, icon, sbu, item_id, mediaType))

    offSet = int(offSet)
    totals = int(jd['totalAsset'])
    itemsLeft = totals - offSet * 10
    
    if itemsLeft > 0:
        finalpg = False
        pages = int(math.ceil(totals/10.0))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (offSet,pages)
        offSet += 1

        labels = {}
        channels.append((title,_icon,sbu,offSet,pages))
    return channels

def get_segments(channel,offSet):
    """
    Get the list of shows.
    :return: list
    """
    
    segments = []
    finalpg = True

    if channel in ('premium','sports','shows','movies'):
        url = '%s/view/%s?page=%s&responseType=common&features=include:buttonsTray'%(apiUrl,channel,offSet)
    else:
        url = '%s/view/channel/%s?page=%s&responseType=common&features=include:buttonsTray'%(apiUrl,channel,offSet)
    jd = requests.get(url,headers=headers).json()
    items = jd['trays']
    for item in items:
        title = item.get('title')
        if title:
            SegUrl = item.get('apiUrl')
            labels = {'title': title,
                      'mediatype': 'tvshow'}
            segments.append((title,SegUrl,labels))

    offSet = int(offSet)
    totals = int(jd['trayCount'])
    itemsLeft = totals - offSet * 4
    if itemsLeft > 0:
        offSet += 1
        if channel in ('premium','sports','shows','movies'):
            url = '%s/view/%s?page=%s&responseType=common&features=include:buttonsTray'%(apiUrl,channel,offSet)
        else:
            url = '%s/view/channel/%s?page=%s&responseType=common&features=include:buttonsTray'%(apiUrl,channel,offSet)
        jd = requests.get(url,headers=headers).json()
        items = jd['trays']
        for item in items:
            title = item.get('title')
            SegUrl = item.get('apiUrl')
            labels = {'title': title,
                      'mediatype': 'tvshow'}
            segments.append((title,SegUrl,labels))

        itemsLeft = totals - offSet * 4        
    if itemsLeft > 0:
        finalpg = False
        pages = int(math.ceil(totals/8.0))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (offSet//2,pages)
        offSet += 1

        segments.append((title,offSet,totals))

    return segments

def get_shows(SegUrl,offSet):
    """
    Get the list of shows.
    :return: list
    """
    
    shows = []
    finalpg = True

    url = '%s/%s&page=%s&responseType=common'%(apiUrl,SegUrl,offSet)
    jd = requests.get(url,headers=headers).json()
    items = jd['result']
    
    for item in items:
        title = item.get('fullTitle') if item.get('fullTitle') else  item.get('name')
        tcount = item.get('season') if item.get('season') else 1
        mediatype = item.get('mediaType')
        item_id= item.get('jioMediaId')         #jioMediaId
        premium=item.get('isPremium')
        icon = 'https://v3img.voot.com/resizeMedium,w_540,h_303/'+item['showImage'].replace(' ','%20')
        labels = {'title': title,
                  'genre': item.get('genres'),
                  'season': item.get('season'),
                  'plot': item['fullSynopsis'],
                  'mediatype': 'tvshow',
                  'year': item['releaseYear']}
        shows.append((title,icon,mediatype,item_id,tcount,labels,premium))

    offSet = int(offSet)
    totals = int(jd['totalAsset'])
    itemsLeft = totals - offSet * 10

    if itemsLeft > 0:
        finalpg = False
        pages = int(math.ceil(totals/10.0))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (offSet,pages)
        offSet += 1

        labels = {}
        shows.append((title,_icon,mediatype,offSet,tcount,labels,premium))

    return shows

def get_season(show,offSet,totals):
    """
    Get the list of episodes.
    :return: list
    """
    season = []

    finalpg = True
    url = '%s/content/generic/season-by-show?sort=season:desc&id=%s&page=%s&responseType=common'%(apiUrl,show,offSet)

    jd = requests.get(url,headers=headers).json()        
    items = jd['result']
    for item in items:
        title = item.get('seasonName')
        item_id = item.get('seasonId')
        icon = item['seo'].get('ogImage')
        sbu=item.get('SBU')
        labels = {'title': title,
                  'genre': item.get('genres'),
                  'plot': item['seo'].get('description'),
                  'cast':item.get('contributors'),
                  'tvshowtitle': item['fullTitle'],
                  'mediatype': 'tvshow',
                  'season': item.get('season')
                 }
        season.append((title,icon,sbu,item_id,labels,totals))

    offSet = int(offSet)
    totals = int(totals)
    itemsLeft = totals - offSet * 10

    if itemsLeft > 0:
        finalpg = False
        pages = int(math.ceil(totals/10.0))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (offSet,pages)
        offSet += 1

        labels = {}
        season.append((title,_icon,offSet,show,labels,totals))
    return season

def get_episodes(show,offSet):
    """
    Get the list of episodes.
    :return: list
    """
    episodes = []
    url = '%s/content/generic/series-wise-episode?sort=episode:desc&id=%s&&page=%s&responseType=common'%(apiUrl,show,offSet)

    jd = requests.get(url,headers=headers).json()
    totals = jd['totalAsset']
    finalpg = True 
    items = jd['result']
    
    for item in items:
        title = item['seo'].get('title')
        eid = item.get('id')
        icon={  'poster': item['seo'].get('ogImage'),
                'thumb': item['seo'].get('ogImage'), #'https://v3img.voot.com/resizeMedium,w_175,h_100/'+item.get('image16x9'),
                'icon': item['seo'].get('ogImage'),
                'fanart': item['seo'].get('ogImage')
                    }
        labels = {'title': title,
                  'genre': item.get('genres'),
                  'cast':item.get('contributors'),
                  'plot': item.get('fullSynopsis'),
                  'duration': item['duration'],
                  'tvshowtitle': item['shortTitle'],
                  'mediatype': 'episode',
                  'episode': item.get('episode'),
                  'season': item.get('season'),
                  'aired':item.get('telecastDate')[:4] + '-' + item.get('telecastDate')[4:6] + '-' + item.get('telecastDate')[6:],
                  'year': item.get('releaseYear')
                 }
        #title = 'E%s %s'%(labels.get('episode'), title) if labels.get('episode') else title
        #title = 'S%02d%s'%(int(labels.get('season')), title) if labels.get('season') else title
        #td = item.get('telecastDate')
        #if td:
        #    labels.update({'aired': td[:4] + '-' + td[4:6] + '-' + td[6:]})
        premium=item.get('isPremium')
        episodes.append((title,icon,eid,labels,totals,premium))

    offSet = int(offSet)
    totals = int(totals)
    itemsLeft = totals - offSet * 10

    if itemsLeft > 0:
        finalpg = False
        pages = int(math.ceil(totals/10.0))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (offSet,pages)
        offSet += 1

        labels = {}
        episodes.append((title,_icon,offSet,labels,totals,premium))

    return episodes

def get_movies(lang,offSet,totals):
    """
    Get the list of movies.
    :return: list
    title:asc,
    """
    movies = []
    totals = int(totals)
    offSet = int(offSet)
    finalpg = True
    itemsLeft = totals - (offSet) * 10
    if itemsLeft > 0:
        finalpg = False
        pages = int(math.ceil(totals/10.0))

    url = '%s/content/generic/movies-by-language?language=include:%s&sort=mostpopular:desc&&page=%s&responseType=common'%(apiUrl,lang,offSet)
    jd = requests.get(url,headers=headers).json()        
    items = jd['result']

    for item in items:
        title = item.get('name')
        mid = item.get('id')
        icon = item['seo'].get('ogImage')
        premium=item.get('isPremium')
        labels = {'title': title,
                  'genre': item.get('genres'),
                  'plot': item.get('fullSynopsis'),
                  'cast':item.get('contributors'),
                  'duration':item.get('duration'),   #int(item.get('duration', '0'))/60,
                  'mediatype': 'movie',
                  'mpaa':item.get('age'),
                  'aired':item.get('telecastDate')[:4] + '-' + item.get('telecastDate')[4:6] + '-' + item.get('telecastDate')[6:],
                  'year': item.get('releaseYear')
                 }
        movies.append((title,icon,mid,labels,premium))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (offSet,pages)
        offSet += 1
        labels = {}
        movies.append((title,_icon,offSet,labels,premium))

    return movies

def get_user_input():
    kb = xbmc.Keyboard('', 'Search for Movies/TV Shows/Trailers/Videos in all languages')
    kb.doModal()  # Onscreen keyboard appears
    if not kb.isConfirmed():
        return

    # User input
    return kb.getText()

def get_search(Query):
    """
    Get the list of shows.
    :return: list
    """
    search = []
    nextpg = True
    page = 0      
    
    url='https://jn1rdqrfn5-dsn.algolia.net/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.33.0)%3B%20Browser&x-algolia-application-id=JN1RDQRFN5&x-algolia-api-key=e426ce68fbce6f9262f6b9c3058c4ea9'
    body = {"requests":[{"indexName":"prod_voot_v4_elastic_jio","params":"query="+Query+"&hitsPerPage=20&page=0&filters=availability.available.IN.from%20%3C%201651655166%20AND%20availability.available.IN.to%20%3E%201651655166"}]}
    body = dumps(body)
    jd = requests.post(url,headers=headers,data=body).json()
    items=jd['results'][0]['hits']
    for item in items:
        title = item.get('fullTitle') if item.get('fullTitle') else item.get('name')
        eid = item.get('jioMediaId')
        showtype=item.get('mediaType')
        icon={  'poster': item['seo'].get('ogImage'),
                'thumb': item['seo'].get('ogImage'), #'https://v3img.voot.com/resizeMedium,w_175,h_100/'+item.get('image16x9'),
                'icon': item['seo'].get('ogImage'),
                'fanart': item['seo'].get('ogImage')
                    }
        labels = {'title': title,
                  'genre': item.get('genres'),
                  'cast':item.get('contributors'),
                  'plot': item.get('fullSynopsis'),
                  'duration': item['duration'],
                  'tvshowtitle': item['shortTitle'],
                  'mediatype': 'episode',
                  'episode': item.get('episode'),
                  'season': item.get('season'),
                  'aired':item.get('telecastDate')[:4] + '-' + item.get('telecastDate')[4:6] + '-' + item.get('telecastDate')[6:],
                  'year': item.get('releaseYear')
                 }

        premium=item.get('isPremium')
        search.append((title,icon,eid,labels,showtype,premium))
    """
    offSet = int(offSet)
    totals = int(totals)
    itemsLeft = totals - offSet * 10

    if itemsLeft > 0:
        finalpg = False
        pages = int(math.ceil(totals/10.0))

    if not finalpg:
        title = 'Next Page.. (Currently in Page %s of %s)' % (offSet,pages)
        offSet += 1

        labels = {}
        search.append((title,_icon,offSet,labels,premium))
    """
    return search

def list_search():
    """
    Create the list of channels in the Kodi interface.
    """

    query = get_user_input()
    if not query:
        return []
    
    #shows = cache.cacheFunction(get_search,query)
    search = get_search(query)
    listing = []
    #
    for title,icon,item_id,labels,mediatype,premium in search:
        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt(icon)
        list_item.setInfo('video', labels)

        if 'Next Page' not in title:
            if mediatype in ('MOVIE','CAC','EPISODE'):
                list_item.setProperty('IsPlayable', 'true')
                if premium:
                    url = '{0}?action=play&video={1}&vidtype=PREMIUM'.format(_url, item_id)
                else:
                    url = '{0}?action=play&video={1}&vidtype=VIDEO'.format(_url, item_id)
                is_folder = False
            elif mediatype in ('LIVECHANNEL'):
                list_item.setProperty('IsPlayable', 'true')
                url = '{0}?action=play&video={1}&vidtype=LIVE'.format(_url, item_id)
                is_folder = False
            else:
                url = '{0}?action=list_season&offSet=1&show={1}&totals=1'.format(_url,item_id)
                is_folder = True
        else:
            url = '{0}?action=list_show&show={1}&offSet={2}&totals=1&icon={4}'.format(_url,show,item_id,icon)
            is_folder = True 
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'tvshows')
    xbmcplugin.endOfDirectory(_handle)
    
def list_top():
    """
    Create the list of countries in the Kodi interface.
    """
    items = get_top()

    listing = []
    for item,id in items:
        list_item = xbmcgui.ListItem(label=item)
        list_item.setInfo('video', {'title': item, 'genre': item})
        list_item.setArt({'icon': _icon,
                          'poster': _icon,
                          'thumb': _icon,
                          'fanart': _fanart})
        url = '{0}?action={1}&id={2}&offSet=1'.format(_url,item,id)
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

    
def list_channels(id,offSet):
    """
    Create the list of countries in the Kodi interface.
    """

    channels = cache.cacheFunction(get_channels,id,offSet)
    listing = []
    for title,icon,sbu,item_id,mediaType in channels:
        list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR]'%(title))
        list_item.setArt({'poster': icon,
                          'icon': icon,
                          'thumb': icon,
                          'fanart': _fanart})
        list_item.setInfo('video', {'title': title})

        if 'Next Page' in title:
            url = '{0}?action=Channels&id={1}&offSet={2}'.format(_url, id, item_id)
            is_folder = True
        elif mediaType =='LIVECHANNEL':
            list_item.setProperty('IsPlayable', 'true')
            url = '{0}?action=play&video={1}&vidtype=LIVE'.format(_url, item_id)
            is_folder = False
        else:
            url = '{0}?action=list_segment&channel={1}&offSet=1'.format(_url, item_id)
            is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    #xbmcplugin.setContent(_handle, 'videos')
    xbmcplugin.endOfDirectory(_handle)

def list_segments(channel,offSet):
    """
    Create the list of channels in the Kodi interface.
    """
    segments = cache.cacheFunction(get_segments,channel,offSet)
    listing = []
    for title,SegUrl,labels in segments:
        if 'Next Page' not in title:
            list_item = xbmcgui.ListItem(label='[COLOR yellow]%s  [COLOR cyan][/COLOR]'%(title))
            url = '{0}?action=list_channel&SegUrl={1}&offSet=1'.format(_url,SegUrl)
        else:
            list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR]'%(title))
            url = '{0}?action=list_segment&channel={1}&offSet={2}'.format(_url,channel,SegUrl)

        list_item.setInfo('video', labels)

        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    #xbmcplugin.setContent(_handle, 'tvshows')
    xbmcplugin.endOfDirectory(_handle)
    
def list_shows(SegUrl,offSet):
    """
    Create the list of channels in the Kodi interface.
    """
    shows = cache.cacheFunction(get_shows,SegUrl,offSet)
    listing = []

    for title,icon,mediatype,item_id,tcount,labels,premium in shows:
        if 'Next Page' not in title:
            list_item = xbmcgui.ListItem(label='[COLOR yellow]%s  [COLOR cyan][/COLOR]'%(title))
            if mediatype in ('MOVIE','CAC','EPISODE'):
                list_item.setProperty('IsPlayable', 'true')
                if premium:
                    url = '{0}?action=play&video={1}&vidtype=PREMIUM'.format(_url, item_id)
                else:
                    url = '{0}?action=play&video={1}&vidtype=VIDEO'.format(_url, item_id)
                is_folder = False
            elif mediatype in ('LIVECHANNEL'):
                list_item.setProperty('IsPlayable', 'true')
                url = '{0}?action=play&video={1}&vidtype=LIVE'.format(_url, item_id)
                is_folder = False
            else:
                url = '{0}?action=list_season&offSet=1&show={1}&totals={2}'.format(_url,item_id,tcount)
                is_folder = True
        else:
            list_item = xbmcgui.ListItem(label='[COLOR yellow]%s[/COLOR]'%(title))
            url = '{0}?action=list_channel&SegUrl={1}&offSet={2}'.format(_url,SegUrl,item_id)
            is_folder = True
        
        list_item.setArt({'poster': icon,
                          'thumb': icon,
                          'icon': icon,
                          'fanart': icon})

        list_item.setInfo('video', labels)
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))

    if mediatype in ('MOVIE','CAC','EPISODE','LIVECHANNEL'):
        xbmcplugin.setContent(_handle, 'movies')
    xbmcplugin.endOfDirectory(_handle)

def list_season(show,offSet,totals):
    """
    Create the list of episodes in the Kodi interface.
    """
    season = cache.cacheFunction(get_season,show,offSet,totals)
    listing = []
    for title,icon,sid,item_id,labels,tcount in season:
        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt({'poster': icon,
                          'thumb': icon,
                          'icon': icon,
                          'fanart': icon})
        list_item.setInfo('video', labels)
        if 'Next Page' not in title:
            url = '{0}?action=list_show&show={1}&offSet={2}&icon={3}'.format(_url,item_id,offSet,icon)
        else:
            url = '{0}?action=list_season&offSet={1}&show={2}&totals={3}'.format(_url,sid,item_id,tcount)

        is_folder = True        
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    #xbmcplugin.setContent(_handle, 'tvshows')
    xbmcplugin.endOfDirectory(_handle)

def list_episodes(show,offSet,sicon):
    """
    Create the list of episodes in the Kodi interface.
    """
    episodes = cache.cacheFunction(get_episodes,show,offSet)
    listing = []
     
    for title,icon,eid,labels,totals,premium in episodes:
        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt(icon)
        list_item.setInfo('video', labels)
        is_folder = False
        if 'Next Page' not in title:
            list_item.setProperty('IsPlayable', 'true')
            if premium:
                url = '{0}?action=play&video={1}&vidtype=PREMIUM'.format(_url, eid)
            else:
                url = '{0}?action=play&video={1}&vidtype=VIDEO'.format(_url, eid)
            is_folder = False
        else:
            url = '{0}?action=list_show&show={1}&offSet={2}&totals={3}&icon={4}'.format(_url,show,eid,totals,sicon)
            is_folder = True        
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'episodes')
    xbmcplugin.endOfDirectory(_handle)

def list_langs():
    """
    Create the list of countries in the Kodi interface.
    """
    langs = cache.cacheFunction(get_langs)
    listing = []
    for lang,tcount in langs:
        list_item = xbmcgui.ListItem(label='[COLOR yellow]%s  [COLOR cyan](%s movies)[/COLOR]'%(lang,tcount))
        list_item.setInfo('video', {'title': lang, 'genre': lang})
        list_item.setArt({'poster': _icon,
                          'icon': _icon,
                          'thumb': _icon,
                          'fanart': _fanart})
        url = '{0}?action=list_movies&lang={1}&offSet=1&totals={2}'.format(_url, lang, tcount)
        is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.endOfDirectory(_handle)

def list_movies(lang,offSet,totals):
    """
    Create the list of episodes in the Kodi interface.
    """
    movies = cache.cacheFunction(get_movies,lang,offSet,totals)
    listing = []
    for title,icon,mid,labels,premium in movies:
        list_item = xbmcgui.ListItem(label=title)
        list_item.setArt({'poster': icon,
                          'icon': icon,
                          'thumb': icon,
                          'fanart': icon})
        list_item.setInfo('video', labels)
        is_folder = False
        if 'Next Page' not in title:
            list_item.setProperty('IsPlayable', 'true')
            if premium:
                url = '{0}?action=play&video={1}&vidtype=PREMIUM'.format(_url, mid)
            else:
                url = '{0}?action=play&video={1}&vidtype=VIDEO'.format(_url, mid)
        else:
            url = '{0}?action=list_movies&lang={1}&offSet={2}&totals={3}'.format(_url, lang, mid, totals)
            is_folder = True
        listing.append((url, list_item, is_folder))
    xbmcplugin.addDirectoryItems(_handle, listing, len(listing))
    xbmcplugin.setContent(_handle, 'movies')
    xbmcplugin.endOfDirectory(_handle, succeeded=True, updateListing=True, cacheToDisc=True)    

def play(urlid, vidtype):
    """
    Play a video by the provided path.

    """
    #
    
    stream_url=''
    max_bandwidth=None
    hdr={
         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
         "Connection": "keep-alive"
         } 

    if vidtype=='LIVE':
        url = "https://tv.media.jio.com/apis/v1.6/getchannelurl/getchannelurl"
        headers.update({'vootid': urlid})
        if headers.get('accessToken'):
            headers.update({'voottoken': headers['accessToken']})
        else:
            headers.update({'voottoken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIwdVhWN3h1U0hMY09CeGZDS0t1enBYNjVYc3VCIiwiZW1haWwiOiJhamF5X2s3M0Bob3RtYWlsLmNvbSIsImRldmljZUlkIjoiZTFiNGJjZTQtNjhiOC00N2YwLTgyYTQtZjczNTRlNWNiN2E1Iiwia1VzZXJJZCI6IjYyMTc4NTA3NiIsImlhdCI6MTY1MTQ3NTczNiwiZXhwIjoxNjUyMzM5NzM2LCJpc3MiOiJ2b290In0.C3g8aPbcdBMvuQ4YTaK4xWJ1CaXs8-5yykdy1e7Bwi8'})
        headers.update({'platform': 'androidwebdesktop'})
        body = {}
        body = dumps(body)
        jd = requests.post(url,headers=headers,data=body).json()

        stream_url=jd.get('m3u8')
        if stream_url:
            videoid=jd.get('videoId') if jd.get('videoId') else urlid       
            lic_url='%s?videoid=%s&vootid=%s&isVoot=true&voottoken=%s' % (jd['mpdKey'],videoid,urlid,headers['voottoken'])  
            license_key = '%s|%s&Content-Type=application/octet-stream|R{SSM}|' % (lic_url,urllib_parse.urlencode(hdr))
    elif vidtype=='PREMIUM' and headers.get('accessToken'):
        url = "https://vootapi.media.jio.com/playback/v1/playbackrights"
        headers.update({'vootid': urlid})
        headers.update({'voottoken': headers['accessToken']})
        headers.update({'platform': 'androidwebdesktop'})
        body = {}
        body = dumps(body)
        jd = requests.post(url,headers=headers,data=body).json()
        stream_url=jd.get('mpd')
        if stream_url:
            videoid=jd.get('videoId') if jd.get('videoId') else urlid
            lic_url='%s?videoid=%s&vootid=%s&isVoot=true&voottoken=%s' % (jd['mpdKey'],videoid,urlid,headers['accessToken'])   
            #license_key = '%s|Content-Type=application/octet-stream|R{SSM}|' % (lic_url)
            license_key = '%s|%s&Content-Type=application/octet-stream|R{SSM}|' % (lic_url,urllib_parse.urlencode(headers))
            max_bandwidth='1000000'
    else:
        #url = 'https://apiv2.voot.com/wsv_2_3/playBack.json?mediaId=%s'%(urlid)
        license_key=''
        url = 'https://wapi.voot.com/ws/ott/getMediaInfo.json?platform=Web&pId=2&mediaId=%s'%(urlid)
        jd = requests.get(url, headers=headers).json()
        
        if jd['total_items']!=0:
            files = jd['assets']['Files']
            
            if 'TV Main'  in str(files):
                urlquality = 'TV Main'
            elif 'HLS_Linear_P' in str(files):
                urlquality = 'HLS_Linear_P'
            elif 'HLS_LINEAR_APP' in str(files):
                urlquality = 'HLS_LINEAR_APP'
            else:
                urlquality = 'HLS_PremiumHD'

            for file in files:
                if file.get('Format') == urlquality:
                    #stream_url = file.get('URL')+ '|User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'    #+|User-Agent=playkit/android-3.4.5 com.tv.v18.viola/2.1.42 (Linux;Android 5.1.1) ExoPlayerLib/2.7.0'
                    stream_url = file.get('URL')
                    break
    #web_pdb.set_trace()
    if not stream_url:
        msg="Need Premium subsription"
        xbmcgui.Dialog().notification(_addonname, msg, _icon, 3000, False)
    else:
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setPath(stream_url)
       
        if six.PY3:
            play_item.setProperty('inputstream', 'inputstream.adaptive')
        else:
            play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')

        if (stream_url.find('mpd') != -1):
            play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            play_item.setMimeType('application/dash+xml')
        else:
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            play_item.setMimeType('application/vnd.apple.mpegurl')

        if license_key!="":
            play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            play_item.setProperty('inputstream.adaptive.license_key', license_key)
            play_item.setProperty("inputstream.adaptive.stream_headers", urllib_parse.urlencode(headers))
            #xbmcgui.Dialog().notification(_addonname, 'Playing DRM.......', _icon, 3000, False)
            if max_bandwidth:
                play_item.setProperty('inputstream.adaptive.max_bandwidth', max_bandwidth)
        play_item.setContentLookup(False)

        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
                
def playNew(urlid,vidtype):
    """
    Play a video by the provided path.

    """

    stream_url=''
    #headers.update({'accessToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiIwdVhWN3h1U0hMY09CeGZDS0t1enBYNjVYc3VCIiwiZW1haWwiOiJhamF5X2s3M0Bob3RtYWlsLmNvbSIsImRldmljZUlkIjoiZTFiNGJjZTQtNjhiOC00N2YwLTgyYTQtZjczNTRlNWNiN2E1Iiwia1VzZXJJZCI6IjYyMTc4NTA3NiIsImlhdCI6MTY1MTQ3NTczNiwiZXhwIjoxNjUyMzM5NzM2LCJpc3MiOiJ2b290In0.C3g8aPbcdBMvuQ4YTaK4xWJ1CaXs8-5yykdy1e7Bwi8'})

    if not headers.get('accessToken'):
        msg="Need userID and Password even for Free Users"
        xbmcgui.Dialog().notification(_addonname, msg, _icon, 3000, False)
        sys.exit()
            
    #vidtype='LIVE'
    if vidtype=='LIVE':
        url = "https://tv.media.jio.com/apis/v1.6/getchannelurl/getchannelurl"
    else:
        url = "https://vootapi.media.jio.com/playback/v1/playbackrights"
        
    headers.update({'vootid': urlid})
    headers.update({'voottoken': headers['accessToken']})
    headers.update({'platform': 'androidwebdesktop'})
    body = {}
    body = dumps(body)
    jd = requests.post(url,headers=headers,data=body).json()

    stream_url=jd.get('mpd')
    videoid=jd.get('videoId') if jd.get('videoId') else urlid
    
    if not stream_url:
        msg="Need Premium subsription"
        xbmcgui.Dialog().notification(_addonname, msg, _icon, 3000, False)
    else:
        play_item = xbmcgui.ListItem(path=stream_url)
        play_item.setPath(stream_url)

        if six.PY3:
            play_item.setProperty('inputstream', 'inputstream.adaptive')
        else:
            play_item.setProperty('inputstreamaddon', 'inputstream.adaptive')

        if (stream_url.find('mpd') != -1):
            play_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            play_item.setMimeType('application/dash+xml')
        else:
            play_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
            play_item.setMimeType('application/vnd.apple.mpegurl')
             
        hdr={
             "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
             "Connection": "keep-alive"
             } 
        lic_url='%s?videoid=%s&vootid=%s&isVoot=true&voottoken=%s' % (jd['mpdKey'],videoid,urlid,headers['accessToken'])   
        if vidtype=='LIVE':
            license_key = '%s|%s&Content-Type=application/octet-stream|R{SSM}|' % (lic_url,urllib_parse.urlencode(hdr))
        else:
            license_key = '%s|Content-Type=application/octet-stream|R{SSM}|' % (lic_url)
        

        play_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        play_item.setProperty('inputstream.adaptive.license_key', license_key)
        play_item.setProperty('inputstream.adaptive.max_bandwidth', '1000000')
        #xbmcgui.Dialog().notification(_addonname, 'Playing DRM.......', _icon, 3000, False)
        #play_item.setProperty('inputstream.adaptive.license_key', license+ '|%s&Content-Type=application/octet-stream|R{SSM}|' % urllib_parse.urlencode(headers))
        #play_item.setProperty("inputstream.adaptive.stream_headers", urllib_parse.urlencode(headers))
        
        play_item.setProperty("inputstream.adaptive.stream_headers", urllib_parse.urlencode(hdr))
        play_item.setContentLookup(False)
        # Pass the item to the Kodi player.
        xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
    
