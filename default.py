import os
import sys
import urllib
import urlparse
import xbmcaddon
import xbmcgui
import xbmcplugin
import requests
from bs4 import BeautifulSoup


def build_url(query):
    base_url = sys.argv[0]
    return base_url + '?' + urllib.urlencode(query)


def get_page(url):
    # download the source HTML for the page using requests
    # and parse the page using BeautifulSoup
    return BeautifulSoup(requests.get(url).text, 'html.parser')


def parse_page(page):
    songs = {}
    index = 1

    for item in page.find_all('a'):
        # the item contains a link to an album cover
        if item['href'].find('.jpg') > 1:
            # format the url for the album cover to include the site url and url encode any spaces
        # the item contains a link to a song containing '.mp3'
        if item['href'].find('.mp3') > 1:
            # update dictionary with the album cover url, song filename, and song url
            songs.update({index: {'album_cover': album_cover, 'title': item['href'],
                                  'url': '{0}{1}'.format(sample_page, item['href'])}})
            index += 1
    return songs

def build_song_list(songs):
    song_list = []
    for song in songs:
        # create a list item using the song filename for the label
        li = xbmcgui.ListItem(label=songs[song]['title'], thumbnailImage=songs[song]['album_cover'])
        # set the fanart to the albumc cover
        li.setProperty('fanart_image', songs[song]['album_cover'])
        # set the list item to playable
        li.setProperty('IsPlayable', 'true')
        # build the plugin url for Kodi
        # Example: plugin://plugin.audio.example/?url=http%3A%2F%2Fwww.theaudiodb.com%2Ftestfiles%2F01-pablo_perez-your_ad_here.mp3&mode=stream&title=01-pablo_perez-your_ad_here.mp3
        url = build_url({'mode': 'stream', 'url': songs[song]['url'], 'title': songs[song]['title']})
        # add the current list item to a list
        song_list.append((url, li, False))
    # add list to Kodi per Martijn
    # http://forum.kodi.tv/showthread.php?tid=209948&pid=2094170#pid2094170
    xbmcplugin.addDirectoryItems(addon_handle, song_list, len(song_list))
    # set the content of the directory
    xbmcplugin.setContent(addon_handle, 'songs')
    xbmcplugin.endOfDirectory(addon_handle)

    def play_song(url):
        play_item = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

        def main():
            args = urlparse.parse_qs(sys.argv[2][1:])
            mode = args.get('mode', None)
            if mode is None:
                page = get_page(sample_page)
                content = parse_page(page)
                build_song_list(content)
            elif mode[0] == 'stream':
                play_song(args['url'][0])

                if __name__ == '__main__':
                    sample_page = 'http://www.theaudiodb.com/testfiles/'
                    addon_handle = int(sys.argv[1])
                    main()