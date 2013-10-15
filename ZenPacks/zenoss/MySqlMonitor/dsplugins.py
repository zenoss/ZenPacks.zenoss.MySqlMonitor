import time

from twisted.enterprise import adbapi
from twisted.internet import defer

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin

from ZenPacks.zenoss.MySqlMonitor.utils import parse_mysql_connection_string

class RandomPlugin(PythonDataSourcePlugin):
    @defer.inlineCallbacks
    def collect(self, config):
        print '*' * 200
        for ds in config.datasources:
            yield

    def onSuccess(self, result, config):
        return {
            'events': [],
            'values': {
                'localhost.localdomain': {
                    'random': (2, time.time()),
                    },
                },
            }

class MySqlMonitorPlugin(PythonDataSourcePlugin):
    proxy_attributes = ('zMySQLConnectionString',)

    def collect(self, config):
        print 'Collecting!' * 100
        for ds in config.datasources:
            servers = parse_mysql_connection_string(ds.zMySQLConnectionString)
            server = servers[ds.component]

            dbpool = adbapi.ConnectionPool("MySQLdb",
                                           user=server['user'],
                                           port=server['port'],
                                           passwd=server['passwd']
                                           )
            return dbpool.runQuery("show global status")

    def onSuccess(self, result, config):
        print '*********'*10
        print result
        print '*********'*10

        return {
            'events': [],
            'values': {
                'root_3306': {
                    'random': (2, time.time()),
                    },
                },
            }

    def onError(self, result, config):
        print '*********'*10
        print result
        print '*********'*10

        return {
            'events': [{
                'summary': 'error: %s' % result,
                'eventKey': 'myPlugin_result',
                'severity': 4,
                }],
            }
