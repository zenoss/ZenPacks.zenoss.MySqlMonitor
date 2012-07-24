##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2008, 2009, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


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
