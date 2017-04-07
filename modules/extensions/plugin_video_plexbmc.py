from modules import stringUtils, jsonUtils
import re
import xbmc, xbmcaddon

ADDON_ID = 'plugin.video.osmosis'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
profile = xbmc.translatePath(REAL_SETTINGS.getAddonInfo('profile').decode('utf-8'))

def update(strm_name, url, media_type, thelist):
    plex_details = stringUtils.uni(jsonUtils.requestList("plugin://plugin.video.plexbmc", media_type))
    for plex_detail in plex_details:
        plex_detail = stringUtils.removeHTMLTAGS(plex_detail)
        label = re.search('"label" *: *"(.*?)",', plex_detail)
        if label and strm_name.replace('++RenamedTitle++', '') == stringUtils.cleanByDictReplacements(label.group(1)):
            serverurl = re.search('"file" *: *"(.*?)",', plex_detail).group(1)
            if url != serverurl:
                for entry in thelist:
                    if entry.split("|")[1] == strm_name:
                        newentry = '|'.join([entry.split("|")[0], entry.split("|")[1].decode("utf-8"), serverurl]) + '\n'
                        thelist = stringUtils.replaceStringElem(thelist, entry, newentry)
                        thefile = xbmc.translatePath(os.path.join(profile, 'MediaList.xml'))
                        with open(thefile.decode("utf-8"), 'w') as output_file: 
                            for linje in thelist:
                                if not linje.startswith('\n'):
                                    output_file.write(linje.strip().encode('utf-8') + '\n')
                                else:
                                    output_file.write(linje.strip())
                        break
                url = serverurl
    return url
