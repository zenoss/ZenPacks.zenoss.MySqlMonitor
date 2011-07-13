###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2008, 2009, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import Globals
import os.path

skinsDir = os.path.join(os.path.dirname(__file__), 'skins')
from Products.CMFCore.DirectoryView import registerDirectory
if os.path.isdir(skinsDir):
    registerDirectory(skinsDir, globals())

import logging
log = logging.getLogger("zen.MySqlMonitor")

from Products.ZenModel.ZenPack import ZenPackBase
class ZenPack(ZenPackBase):
    """
    ZenPacks.zenoss.MySqlMonitor ZenPack loader.
    """

    packZProperties = [
            ('zMySqlUsername', 'zenoss', 'string'),
            ('zMySqlPassword', '', 'password'),
            ('zMySqlPort', '3306', 'string'),
            ]

    def install(self, app):
        ZenPackBase.install(self, app)
        self.enableDefaultProcessMonitoring(app.zport.dmd)

    def upgrade(self, app):
        ZenPackBase.upgrade(self, app)
        self.enableDefaultProcessMonitoring(app.zport.dmd)

    def enableDefaultProcessMonitoring(self, dmd):
        try:
            p = dmd.Processes.MySQL.osProcessClasses.mysqld
            if p.hasProperty('zMonitor'): return
            log.info('Enabling monitoring for mysqld processes.')
            p._setProperty('zMonitor', True)
            for i in p.instances():
                i.index_object()
        except AttributeError:
            pass

