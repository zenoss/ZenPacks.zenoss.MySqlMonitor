##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from twisted.internet import defer

from zope.component import adapts
from zope.interface import implements

from Products.ZenEvents import ZenEventClasses
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import RRDDataSourceInfo
from Products.Zuul.interfaces import IRRDDataSourceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t
from Products.ZenModel.RRDDataSource import RRDDataSource
from Products.ZenModel.ZenPackPersistence import ZenPackPersistence

class MySQLDataSource(ZenPackPersistence, RRDDataSource):
    ''' Datasource used to capture datapoints '''
    ZENPACKID = 'ZenPacks.zenoss.MySQL'

    # name for source type in drop-down selection
    sourcetypes = ('MySQLDataSource', )
    sourcetype = sourcetypes[0]

    eventClass = '/Server/MySQL'
    component = "${here/id}"

    cycletime = 300

    plugin_classname = 'ZenPacks.zenoss.MySQL.datasources.MySQLDataSource.MySQLDataSourcePlugin'

    @classmethod
    def config_key(cls, datasource, context):
        """ This allows pulling a list of unique datasources """
        return (context.device().id, datasource.getCycleTime(context), datasource.component)

    def getDescription(self):
        return 'Data source for monitoring MySQL database'


class IMySQLDataSourceInfo(IRRDDataSourceInfo):
    ''' API Info interface for MySQLDataSource.  '''

    cycletime = schema.TextLine(title=_t('Cycle time'))


class MySQLDataSourceInfo(RRDDataSourceInfo):
    ''' API Info adapter factory for MySQLMonitoringDataSource.  '''

    implements(IMySQLDataSourceInfo)
    adapts(MySQLDataSource)

    testable = False

    cycletime = ProxyProperty('cycletime')

