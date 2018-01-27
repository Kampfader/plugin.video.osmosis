# Copyright (C) 2016 stereodruid(J.G.) Mail: stereodruid@gmail.com
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
import os
import time
import xbmc, xbmcaddon, xbmcvfs
import re

addon = xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
startup_time = None


def setDBs(files, path):
    dbtypes = ['video', 'music']

    for dbtype in dbtypes:
        dbname = None
        for file in files:
            if file.lower().startswith('my' + dbtype):
                if dbname is None:
                    dbname = file
                elif re.search('(\d+)', dbname) and re.search('(\d+)', file):
                    dbnumber = int(re.search('(\d+)', dbname).group(1))
                    filedbnumber = int(re.search('(\d+)', file).group(1))
                    if filedbnumber > dbnumber:
                        dbname = file

        if dbname is not None:
            dbpath = xbmc.translatePath(os.path.join(path, dbname))
            dbsetting = addon.getSetting('KMovie-DB path') if dbtype == 'video' else addon.getSetting('KMusic-DB path')
            if dbpath != dbsetting:
                addon.setSetting('KMovie-DB path', dbpath) if dbtype == 'video' else addon.setSetting('KMusic-DB path', dbpath)


if __name__ == "__main__":
    if addon.getSetting('USE_MYSQL') == 'false' and addon.getSetting('Find_SQLite_DB') == 'true':
        path = xbmc.translatePath(os.path.join("special://home/", 'userdata/Database/'))
        if xbmcvfs.exists(path):
            dirs, files = xbmcvfs.listdir(path)
            setDBs(files, path)

        if addon.getSetting('Update_at_startup') == "true":
            xbmc.executebuiltin('XBMC.RunPlugin(plugin://%s/?url=&mode=666)' % (addon_id))

        monitor = xbmc.Monitor()
        while not monitor.abortRequested():
            # Sleep/wait for abort for 10 seconds
            if monitor.waitForAbort(10):
                # Abort was requested while waiting. We should exit
                break

            if addon.getSetting('Automatic_Update_Run') == "true":
                if startup_time is None:
                    startup_time = time.time()

                next_peridoc_update = startup_time + float(addon.getSetting('Automatic_Update_Time')) * 60 * 60
                if (next_peridoc_update <= time.time()):
                    startup_time = time.time()
                    xbmc.executebuiltin('XBMC.RunPlugin(plugin://%s/?url=&mode=666&updateActor=1)' % (addon_id))
                    monitor.waitForAbort(60)
            else:
                if startup_time is not None:
                    startup_time = None

                Timed_Update_Run = addon.getSetting('update_time')[:5] if addon.getSetting('update_time') != '' else addon.getSetting('update_time')
                if Timed_Update_Run != '' and Timed_Update_Run != "00:00":
                    if time.strftime("%H:%M") == Timed_Update_Run:
                        xbmc.executebuiltin('XBMC.RunPlugin(plugin://%s/?url=&mode=666&updateActor=2)' % (addon_id))
                        monitor.waitForAbort(60)
