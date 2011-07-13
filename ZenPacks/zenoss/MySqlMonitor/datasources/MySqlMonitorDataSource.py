###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2008, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

__doc__='''MySqlMonitorDataSource.py

Defines datasource for MySqlMonitor
'''

from Globals import InitializeClass

import Products.ZenModel.BasicDataSource as BasicDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence
from AccessControl import ClassSecurityInfo, Permissions
from Products.ZenUtils.ZenTales import talesCompile, getEngine

import os


class MySqlMonitorDataSource(ZenPackPersistence,
                                BasicDataSource.BasicDataSource):
    
    MYSQL_MONITOR = 'MySqlMonitor'

    ZENPACKID = 'ZenPacks.zenoss.MySqlMonitor'

    sourcetypes = (MYSQL_MONITOR,)
    sourcetype = MYSQL_MONITOR

    timeout = 15
    eventClass = '/Status/MYSQL'

    versionFivePlus = True
    hostname = '${dev/manageIp}'
    port = '${here/zMySqlPort}'
    username = '${here/zMySqlUsername}'
    password = '${here/zMySqlPassword}'

    _properties = BasicDataSource.BasicDataSource._properties + (
        {'id':'versionFivePlus', 'type':'boolean', 'mode':'w'},
        {'id':'hostname', 'type':'string', 'mode':'w'},
        {'id':'port', 'type':'string', 'mode':'w'},
        {'id':'username', 'type':'string', 'mode':'w'},
        {'id':'password', 'type':'string', 'mode':'w'},
        {'id':'timeout', 'type':'int', 'mode':'w'},
        )
        
    _relations = BasicDataSource.BasicDataSource._relations + (
        )


    factory_type_information = ( 
    { 
        'immediate_view' : 'editMySqlMonitorDataSource',
        'actions'        :
        ( 
            { 'id'            : 'edit',
              'name'          : 'Data Source',
              'action'        : 'editMySqlMonitorDataSource',
              'permissions'   : ( Permissions.view, ),
            },
        )
    },
    )

    security = ClassSecurityInfo()


    def __init__(self, id, title=None, buildRelations=True):
        BasicDataSource.BasicDataSource.__init__(self, id, title,
                buildRelations)


    def getDescription(self):
        if self.sourcetype == self.MYSQL_MONITOR:
            return self.hostname
        return BasicDataSource.BasicDataSource.getDescription(self)


    def useZenCommand(self):
        return True


    def getCommand(self, context):
        parts = ['check_mysql_stats.py']
        if self.hostname:
            parts.append('-H %s' % self.hostname)
        if self.port:
            parts.append('-p %s' % self.port)
        if self.username:
            parts.append('-u %s' % self.username)
        if self.password:
            parts.append("-w '%s'" % self.password)
        if self.versionFivePlus:
            parts.append("-g")
        cmd = ' '.join(parts)
        cmd = BasicDataSource.BasicDataSource.getCommand(self, context, cmd)
        return cmd


    def checkCommandPrefix(self, context, cmd):
        if self.usessh:
            return os.path.join(context.zCommandPath, cmd)
        zp = self.getZenPack(context)
        return zp.path('libexec', cmd)


    def addDataPoints(self):
        dps = (
            ('Bytes_received', 'DERIVE'),
            ('Bytes_sent', 'DERIVE'),

            ('Com_delete', 'DERIVE'),
            ('Com_delete_multi', 'DERIVE'),
            ('Com_insert', 'DERIVE'),
            ('Com_insert_select', 'DERIVE'),
            ('Com_replace', 'DERIVE'),
            ('Com_replace_select', 'DERIVE'),
            ('Com_select', 'DERIVE'),
            ('Com_update', 'DERIVE'),
            ('Com_update_multi', 'DERIVE'),

            ('Handler_delete', 'DERIVE'),
            ('Handler_read_first', 'DERIVE'),
            ('Handler_read_key', 'DERIVE'),
            ('Handler_read_next', 'DERIVE'),
            ('Handler_read_prev', 'DERIVE'),
            ('Handler_read_rnd', 'DERIVE'),
            ('Handler_read_rnd_next', 'DERIVE'),
            ('Handler_update', 'DERIVE'),
            ('Handler_write', 'DERIVE'),

            ('Select_full_join', 'DERIVE'),
            ('Select_full_range_join', 'DERIVE'),
            ('Select_range', 'DERIVE'),
            ('Select_range_check', 'DERIVE'),
            ('Select_scan', 'DERIVE'),
        )
        for dpd in dps:
            dp = self.manage_addRRDDataPoint(dpd[0])
            dp.rrdtype = dpd[1]
            dp.rrdmin = 0


    def zmanage_editProperties(self, REQUEST=None):
        '''validation, etc'''
        if REQUEST:
            # ensure default datapoint didn't go away
            self.addDataPoints()
            # and eventClass
            if not REQUEST.form.get('eventClass', None):
                REQUEST.form['eventClass'] = self.__class__.eventClass
        return BasicDataSource.BasicDataSource.zmanage_editProperties(self,
                REQUEST)

InitializeClass(MySqlMonitorDataSource)
