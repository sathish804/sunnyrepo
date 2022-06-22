"""
    Voot Kodi Addon
    Copyright (C) 2018 gujal

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
from six.moves import urllib_parse
from kodi_six import xbmcaddon
from resources.lib import main

_addon = xbmcaddon.Addon()
_settings = _addon.getSetting

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
        if params['action'] == 'Channels':
            main.list_channels(params['id'],params['offSet'])
        elif params['action'] == 'Clear Cache':
            main.clear_cache()  
        elif params['action'] == 'Search':
            main.list_search()
        elif params['action'] == 'Movies':
            #main.list_langs()
            main.list_segments('movies',params['offSet'])
        elif params['action'] == 'Sports':
            main.list_segments('sports',params['offSet'])
        elif params['action'] == 'Premium':
            main.list_segments('premium',params['offSet'])
        elif params['action'] == 'Shows':
            main.list_segments('shows',params['offSet'])
        elif params['action'] == 'Live':
            main.list_channels(params['id'],params['offSet'])
        elif params['action'] == 'list_segment':
            main.list_segments(params['channel'],params['offSet'])
        elif params['action'] == 'list_channel':
            main.list_shows(params['SegUrl'],params['offSet'])
        elif params['action'] == 'list_movies':
            main.list_movies(params['lang'],params['offSet'],params['totals'])
        elif params['action'] == 'list_season':
            main.list_season(params['show'],params['offSet'],params['totals'])
        elif params['action'] == 'list_show':
            main.list_episodes(params['show'],params['offSet'],params['icon'])
        elif params['action'] == 'play':
            main.play(params['video'],params['vidtype'])
    else:
        main.list_top()


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    router(sys.argv[2][1:])
