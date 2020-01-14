# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import utils


def getModule(plugin_id):
    extension = None
    if plugin_id and plugin_id != '':
        plugin_id = plugin_id.replace('.', '_')
        try:
            extension = __import__('resources.lib.extensions.{0}'.format(plugin_id), fromlist=[plugin_id])
        except ImportError:
            utils.addon_log('Extension {0} could not be found'.format(plugin_id))

    return extension