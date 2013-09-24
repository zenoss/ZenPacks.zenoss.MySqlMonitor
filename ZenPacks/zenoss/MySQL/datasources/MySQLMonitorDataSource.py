##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


from Products.ZenModel.BasicDataSource import BasicDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence

from Products.ZenUtils.ZenTales import talesCompile, getEngine

import os

class MySQLMonitorDataSource(ZenPackPersistence, BasicDataSource):
    ZENPACKID = 'ZenPacks.zenoss.MySQL'

    sourcetype = 'MySQLMonitor'
    sourcetypes = (sourcetype,)

    timeout = 15
    eventClass = '/Status'

    hostname = '${dev/manageIp}'
    ssl = True
    ngerror = ""

    _properties = BasicDataSource._properties + (
        {'id':'timeout', 'type':'int', 'mode':'w'},
        {'id':'eventClass', 'type':'string', 'mode':'w'},
        {'id':'hostname', 'type':'string', 'mode':'w'},
        {'id':'ssl', 'type':'boolean', 'mode':'w'},
        {'id':'ngerror', 'type':'string', 'mode':'w'},
    )

    _relations = BasicDataSource._relations

    def __init__(self, id, title=None, buildRelations=True):
        BasicDataSource.__init__(self, id, title, buildRelations)

    def getDescription(self):
        if self.sourcetype == 'MySQLMonitor':
            return self.hostname
        return BasicDataSource.getDescription(self)

    def useZenCommand(self):
        return True

    def getCommand(self, context):
        return BasicDataSource.getCommand(self, context, 'mysql -u root -e '
            '"select TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH, '
            'DATA_LENGTH, MAX_DATA_LENGTH, INDEX_LENGTH, DATA_FREE '
            'from information_schema.tables"'
        )

    def checkCommandPrefix(self, context, cmd):
        return os.path.join(context.zCommandPath, cmd)

    def addDataPoints(self):
        # for dpname in ('totalAccesses', 'totalKBytes'):
        #     dp = self.manage_addRRDDataPoint(dpname)
        #     dp.rrdtype = 'DERIVE'
        #     dp.rrdmin = 0

    def zmanage_editProperties(self, REQUEST=None):
        '''validation, etc'''
        if REQUEST:
            self.addDataPoints()
            if not REQUEST.form.get('eventClass', None):
                REQUEST.form['eventClass'] = self.__class__.eventClass
        return BasicDataSource.zmanage_editProperties(self,
                REQUEST)
