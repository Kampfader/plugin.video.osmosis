# Copyright (C) 2016 stereodruid(J.G.)
#
#
# This file is part of OSMOSIS
#
# OSMOSIS is free software: you can redistribute it.
# You can modify it for private use only.
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OSMOSIS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from kodi_six.utils import py2_encode, py2_decode
import os, sys
import time
import re
import xbmc
import xbmcgui
import xbmcplugin

from .common import Globals, jsonrpc
from .fileSys import readMediaList
from .stringUtils import getProvidername, getStrmname
from .utils import addon_log, key_natural_sort, zeitspanne
from .xmldialogs import show_modal_dialog, Skip

try:
    import urllib.parse as urllib
except:
    import urllib

globals = Globals()


def addItem(label, mode, icon):
    addon_log('addItem')
    u = 'plugin://{0}/?{1}'.format(globals.PLUGIN_ID, urllib.urlencode({'mode': mode, 'fanart': icon}))
    liz = xbmcgui.ListItem(label)
    liz.setInfo(type='Video', infoLabels={'Title': label})
    liz.setArt({'icon': icon, 'thumb': icon, 'fanart': globals.MEDIA_FANART})

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)


def addFunction(labels):
    addon_log('addItem')
    u = 'plugin://{0}/?{1}'.format(globals.PLUGIN_ID, urllib.urlencode({'mode': 666, 'fanart': globals.MEDIA_UPDATE}))
    liz = xbmcgui.ListItem(labels)
    liz.setInfo(type='Video', infoLabels={'Title': labels})
    liz.setArt({'icon': globals.MEDIA_UPDATE, 'thumb': globals.MEDIA_UPDATE, 'fanart':  globals.MEDIA_FANART})

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)


def addDir(name, url, mode, art, plot=None, genre=None, date=None, credits=None, showcontext=False, name_parent='', type=None):
    addon_log('addDir: {0} ({1})'.format(py2_decode(name), py2_decode(name_parent)))
    u = '{0}?{1}'.format(sys.argv[0], urllib.urlencode({'url': url, 'name': py2_encode(name), 'type': type, 'name_parent': py2_encode(name_parent), 'fanart': art.get('fanart', '')}))
    contextMenu = []
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Genre': genre, 'dateadded': date, 'credits': credits})
    liz.setArt(art)
    if type == 'tvshow':
        contextMenu.append(('Add TV-Show to MediaList', 'XBMC.RunPlugin({0}&mode={1})'.format(u, 200)))
        contextMenu.append(('Add seasons individually to MediaList', 'XBMC.RunPlugin({0}&mode={1})'.format(u, 202)))
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    elif re.findall('( - |, )*([sS](taffel|eason|erie[s]{0,1})|[pP]art|[tT]eil) \d+.*', name):
        contextMenu.append(('Add Season to MediaList', 'XBMC.RunPlugin({0}&mode={1})'.format(u, 200)))
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    elif type == 'movie':  # ???
        contextMenu.append(('Add Movie to MediaList', 'XBMC.RunPlugin({0}&mode={1})'.format(u, 200)))
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    else:
        contextMenu.append(('Create Strms', 'XBMC.RunPlugin({0}&mode={1})'.format(u, 200)))
    liz.addContextMenuItems(contextMenu)

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='{0}&mode={1}'.format(u, mode), listitem=liz, isFolder=True)


def addLink(name, url, mode, art, plot, genre, date, showcontext, playlist, regexs, total, setCookie='', type=None, year=None):
    addon_log('addLink: {0}'.format(py2_decode(name)))
    u = '{0}?{1}'.format(sys.argv[0], urllib.urlencode({'url': url, 'name': py2_encode(name), 'fanart': art.get('fanart', ''), 'type': type, 'year': year}))
    contextMenu = []
    liz = xbmcgui.ListItem(name)
    liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Genre': genre, 'dateadded': date})
    liz.setArt(art)
    liz.setProperty('IsPlayable', 'true')
    if type == 'movie':
        contextMenu.append(('Add Movie to MediaList', 'XBMC.RunPlugin({0}&mode={1}&filetype=file)'.format(u, 200)))
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    else:
        contextMenu.append(('Create Strm', 'XBMC.RunPlugin({0}&mode={1}&filetype=file)'.format(u, 200)))

    liz.addContextMenuItems(contextMenu)

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url='{0}&mode={1}'.format(u, mode), listitem=liz, totalItems=total)


def getSources():
    addon_log('getSources')
    xbmcplugin.setContent(int(sys.argv[1]), 'files')
    art = {'fanart': globals.MEDIA_FANART, 'thumb': globals.MEDIA_FOLDER}
    addDir('Video Plugins', 'video', 1, art)
    addDir('Music Plugins', 'audio', 1, art)
    addDir('Video Favoriten', '', 102, {'thumb': 'DefaultFavourites.png'}, type='video')
    addItem('Update', 4, globals.MEDIA_UPDATE)
    addItem('Update (with removal of unused .strm files)', 42, globals.MEDIA_UPDATE)
    addFunction('Update all')
    addItem('Rename', 41, globals.MEDIA_UPDATE)
    addItem('Remove Media', 5, globals.MEDIA_REMOVE)
    addItem('Remove Shows from TVDB cache', 51, globals.MEDIA_REMOVE)
    addItem('Remove all Shows from TVDB cache', 52, globals.MEDIA_REMOVE)
    if xbmc.getCondVisibility('System.HasAddon(service.watchdog)') != 1:
        addon_details = jsonrpc('Addons.GetAddonDetails', dict(addonid='service.watchdog', properties=['enabled', 'installed'])).get('addon')
        if addon_details and addon_details.get('installed'):
            addItem('Activate Watchdog', 7, globals.MEDIA_ICON)
        else:
            addItem('Install Watchdog', 6, globals.MEDIA_ICON)
    # ToDo Add label


def getType(url):
    if url.find('plugin.audio') != -1:
        Types = ['YouTube', 'Audio-Album', 'Audio-Single', 'Other']
    else:
        Types = ['Movies', 'TV-Shows', 'YouTube', 'Other']

    selectType = selectDialog('Select category', Types)

    if selectType == -1:
        return -1

    if selectType == 3:
        subType = ['(Music)', '(Movies)', '(TV-Shows)']
        selectOption = selectDialog('Select Video type:', subType)

    else:
        subType = ['(en)', '(de)', '(sp)', '(tr)', 'Other']
        selectOption = selectDialog('Select language tag', subType)

    if selectOption == -1:
        return -1

    if selectType >= 0 and selectOption >= 0:
        return Types[selectType] + subType[selectOption]


def getTypeLangOnly(Type):
    lang = ['(en)', '(de)', '(sp)', '(tr)', 'Other']
    selectOption = selectDialog('Select language tag', lang)

    if selectOption == -1:
        return -1

    return Type + lang[selectOption]


def selectDialog(header, list, autoclose=0, multiselect=False, useDetails=False, preselect=None):
    if multiselect:
        if preselect:
            return globals.dialog.multiselect(header, list, autoclose=autoclose, useDetails=useDetails, preselect=preselect)
        else:
            return globals.dialog.multiselect(header, list, autoclose=autoclose, useDetails=useDetails)
    else:
        if preselect:
            return globals.dialog.select(header, list, autoclose, useDetails=useDetails, preselect=preselect)
        else:
            return globals.dialog.select(header, list, autoclose, useDetails=useDetails)


def editDialog(nameToChange):
    return py2_decode(globals.dialog.input(nameToChange, type=xbmcgui.INPUT_ALPHANUM, defaultt=nameToChange))


# Before executing the code below we need to know the movie original title (string variable originaltitle) and the year (string variable year). They can be obtained from the infolabels of the listitem. The code filters the database for items with the same original title and the same year, year-1 and year+1 to avoid errors identifying the media.
def markMovie(movID, pos, total, done):
    if done:
        try:
            jsonrpc('VideoLibrary.SetMovieDetails', dict(movieid=movID, playcount=1))
            xbmc.executebuiltin('XBMC.Container.Refresh')
        except:
            print('markMovie: Movie not in DB!?')
            pass
    else:
        if xbmc.getCondVisibility('Library.HasContent(Movies)') and pos > 0 and total > 0:
            try:
                jsonrpc('VideoLibrary.SetMovieDetails', dict(movieid=movID, resume=dict(position=pos, total=total)))
                xbmc.executebuiltin('XBMC.Container.Refresh')
            except:
                print('markMovie: Movie not in DB!?')
                pass


def markSeries(epID, pos, total, done):
    if done:
        try:
            jsonrpc('VideoLibrary.SetEpisodeDetails', dict(episodeid=epID, playcount=1))
            xbmc.executebuiltin('XBMC.Container.Refresh')
        except:
            print('markMovie: Episode not in DB!?')
            pass
    else:
        if xbmc.getCondVisibility('Library.HasContent(TVShows)') and pos > 0 and total > 0:
            try:
                jsonrpc('VideoLibrary.SetEpisodeDetails', dict(episodeid=epID, resume=dict(position=pos, total=total)))
                xbmc.executebuiltin('XBMC.Container.Refresh')
            except:
                print('markSeries: Show not in DB!?')
                pass


# Functions not in usee yet:
def handle_wait(time_to_wait, header, title):
    dlg = globals.dialogProgress
    dlg.create('OSMOSIS', header)
    secs = 0
    percent = 0
    increment = int(100 / time_to_wait)
    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment * secs
        secs_left = str((time_to_wait - secs))
        remaining_display = 'Starts In {0} seconds, Cancel Channel Change?'.format(secs_left)
        dlg.update(percent, title, remaining_display)
        xbmc.sleep(1000)
        if (dlg.iscanceled()):
            cancelled = True
            break
    if cancelled == True:
        return False
    else:
        dlg.close()
        return True


def show_busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialog)')


def hide_busy_dialog():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    while xbmc.getCondVisibility('Window.IsActive(busydialog)'):
        time.sleep(.1)


def Error(header, line1='', line2='', line3=''):
    globals.dialog.ok(header, line1, line2, line3)


def infoDialog(str, header=globals.PLUGIN_NAME, time=10000):
    try: globals.dialog.notification(header, str, globals.MEDIA_ICON, time, sound=False)
    except: xbmc.executebuiltin('Notification({0}, {1}, {2}, {3})'.format(header, str, time, THUMB))


def okDialog(str1, str2='', header=globals.PLUGIN_NAME):
    globals.dialog.ok(header, str1, str2)


def yesnoDialog(str1, str2='', header=globals.PLUGIN_NAME, yes='', no=''):
    return globals.dialog.yesno(header, str1, str2, '', yes, no)


def browse(type, heading, shares, mask='', useThumbs=False, treatAsFolder=False, path='', enableMultiple=False):
    return globals.dialog.browse(type, heading, shares, mask, useThumbs, treatAsFolder, path, enableMultiple)


def resumePointDialog(resume, dialog, playback_rewind):
    if resume and resume.get('position') > 0.0:
        position = int(resume.get('position')) - playback_rewind
        resumeLabel = xbmc.getLocalizedString(12022).format(time.strftime("%H:%M:%S", time.gmtime(position)))
        if dialog == 0:
            sel = globals.dialog.contextmenu([resumeLabel, xbmc.getLocalizedString(12021)])
            if sel > -1:
                return position if sel == 0 else 0
        elif dialog == 1:
            skip = show_modal_dialog(Skip,
                'plugin-video-osmosis-continue.xml',
                globals.PLUGIN_PATH,
                minutes=0,
                seconds=15,
                skip_to=position,
                label=resumeLabel
            )
            if skip:
                return position

    return 0


def mediaListDialog(multiselect=True, expand=True, cTypeFilter=None, header_prefix=globals.PLUGIN_NAME, preselect_name=None):
    thelist = readMediaList()
    items = []
    if not cTypeFilter:
        selectAction = ['Movies', 'TV-Shows', 'Audio', 'All']
        choice = selectDialog('{0}: Select which Media Types to show'.format(header_prefix), selectAction)
        if choice != -1:
            if choice == 3:
                cTypeFilter = None
            else:
                cTypeFilter = selectAction[choice]
        else:
            return

    for index, entry in enumerate(thelist):
        splits = entry.strip().split('|')
        if cTypeFilter and not re.findall(cTypeFilter, splits[0]):
            continue
        name = getStrmname(splits[1])
        cType = splits[0].replace('(', '/').replace(')', '')
        matches = re.findall('(?:name_orig=([^;]*);)*(plugin:\/\/[^<]*)', splits[2])
        iconImage = ''
        if splits[0].find('TV-Shows') != -1:
            iconImage = 'DefaultTVShows.png'
        if splits[0].find('Movies') != -1:
            iconImage = 'DefaultMovies.png'
        if splits[0].find('Audio-Album') != -1:
            iconImage = 'DefaultMusicAlbums.png'
        if splits[0].find('Audio-Single') != -1:
            iconImage = 'DefaultMusicSongs.png'
        if matches:
            if expand:
                indent_text = ''
                indent_text2 = ''
                if len(matches) > 1:
                    items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} [{1}]'.format(name, cType), 'url': splits[2], 'iconImage': 'DefaultVideoPlaylists.png'})
                    indent_text = '    '
                    indent_text2 = '{0} '.format(indent_text)
                for match in matches:
                    name_orig = match[0]
                    url = match[1]
                    item_entry = '|'.join([splits[0], name, 'name_orig={0};{1}'.format(name_orig, url) if name_orig else url])
                    items.append({'index': index, 'entry': item_entry, 'name': name, 'text': '{2}{0} [{1}]'.format(name, cType, indent_text), \
                                  'text2': ('{2}{1}\n{2}[{0}]' if name_orig else '{2}[{0}]').format(getProvidername(url), name_orig, indent_text2), \
                                  'iconImage': iconImage, 'url': url, 'name_orig': name_orig})

            else:
                pluginnames = sorted(set([getProvidername(match[1]) for match in matches]), key=lambda k: k.lower())
                items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} ({1}: {2})'.format(name, cType, ', '.join(pluginnames)), 'url': splits[2]})
        else:
            items.append({'index': index, 'entry': entry, 'name': name, 'text': '{0} ({1})'.format(name, cType), 'url': splits[2]})

    preselect_idx = None
    if expand == False:
        sItems = sorted([item.get('text') for item in items], key=lambda k: key_natural_sort(k.lower()))
        if preselect_name:
            preselect_idx = [i for i, item in enumerate(sItems) if item.find(preselect_name) != -1 ]
    else:
        liz = []
        for item in items:
            li = xbmcgui.ListItem(label=item.get('text'), label2=item.get('text2'))
            li.setArt({'icon': item.get('iconImage')})
            liz.append(li)
        sItems = sorted(liz,
            key=lambda k: (re.sub('.* \[([^/]*)/.*\]', '\g<1>', py2_decode(k.getLabel())),
                            key_natural_sort(re.sub('^ *', '', py2_decode(k.getLabel().lower()))),
                            key_natural_sort(re.sub('( - |, )*([sS](taffel|eason|erie[s]{0,1})|[pP]art|[tT]eil) (?P<number>\d+).*', '\g<number>', py2_decode(k.getLabel2().lower()))),
                            key_natural_sort(re.sub('^ *', '', py2_decode(k.getLabel2().lower())))
                            )
                        )
        if preselect_name:
            preselect_idx = [i for i, item in enumerate(sItems) if item.getLabel().find(preselect_name) != -1 ]

    if multiselect == False and preselect_idx and isinstance(preselect_idx, list) and len(preselect_idx) > 0:
        preselect_idx = preselect_idx[0]

    selectedItemsIndex = selectDialog('{0}: Select items'.format(header_prefix), sItems, multiselect=multiselect, useDetails=expand, preselect=preselect_idx)
    if multiselect:
        if expand == False:
            return [item for item in items for index in selectedItemsIndex if item.get('text') == py2_decode(sItems[index])] if selectedItemsIndex and len(selectedItemsIndex) > 0 else None
        else:
            return [item for item in items for index in selectedItemsIndex if item.get('text') == py2_decode(sItems[index].getLabel()) and item.get('text2') == py2_decode(sItems[index].getLabel2())] if selectedItemsIndex and len(selectedItemsIndex) > 0 else None
    else:
        selectedList = [item for index, item in enumerate(items) if selectedItemsIndex > -1 and item.get('text') == py2_decode(sItems[selectedItemsIndex])]
        return selectedList[0] if len(selectedList) == 1 else None