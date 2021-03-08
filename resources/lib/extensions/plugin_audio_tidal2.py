# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from re import sub

def getArt(art):
    newart = dict(album=art.get('thumb'))

    if art.get('fanart'):
        artistArt = sub('(\d+x\d+)', '320x320', art.get('fanart'))
        newart.update(dict(artist=artistArt))
    
    return newart