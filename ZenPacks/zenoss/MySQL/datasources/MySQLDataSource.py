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

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
            import PythonDataSource, PythonDataSourcePlugin

class MySQLDataSource(PythonDataSource):
    ''' Datasource used to capture datapoints '''
    ZENPACKID = 'ZenPacks.zenoss.MySQL'

    # name for source type in drop-down selection
    sourcetypes = ('MySQLDataSource', )
    sourcetype = sourcetypes[0]

    cycletime = 300

    plugin_classname = 'ZenPacks.zenoss.MySQL.datasources.MySQLDataSource.MySQLDataSourcePlugin'

    @classmethod
    def config_key(cls, datasource, context):
        """ This allows pulling a list of unique datasources """
        return (context.device().id, datasource.getCycleTime(context), datasource.component)

    def getDescription(self):
        return 'Data source for monitoring MySQL database'


class IMySQLMonitoringDataSourceInfo(IRRDDataSourceInfo):
    ''' API Info interface for MySQLDataSource.  '''

    cycletime = schema.TextLine(title=_t('Cycle time'))


class MySQLMonitoringDataSourceInfo(RRDDataSourceInfo):
    ''' API Info adapter factory for MySQLMonitoringDataSource.  '''

    implements(IMySQLMonitoringDataSourceInfo)
    adapts(MySQLMonitoringDataSource)

    testable = False

    cycletime = ProxyProperty('cycletime')


class MySQLMonitoringDataSourcePlugin(PythonDataSourcePlugin):
    proxy_attributes = ('host', 'port', 'device', 'password')

    @defer.inlineCallbacks
    def collect(self, config):
        ''' 
            This method must return a Twisted deferred. The deferred results will
            be sent to the onResult then either onSuccess or onError callbacks below.
        '''
        if False:
            yield  # without a yield function would not be a coroutine

        print '=' * 80
        for ds in config.datasources:
            print datasource.device
            print datasource.compoent
        print '=' * 80

        defer.returnValue(dict(
            events=[],
            values={
                None: {},
            }
        ))

    def onSuccess(self, result, config):
        from pprint import pprint
        print '<' * 50
        pprint(result)
        print '>' * 50
        return result

    def onError(self, result, config):
        print '!' * 300
        print result
        return {
            'events': [{
                'summary': 'error: %s' % result,
                'eventKey': 'MySQLMonitoring_error',
                'severity': 4,
            }]
        }
