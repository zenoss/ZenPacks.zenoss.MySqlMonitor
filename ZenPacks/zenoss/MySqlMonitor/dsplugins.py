from twisted.enterprise import adbapi
from twisted.internet import reactor, defer

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin

from ZenPacks.zenoss.MySqlMonitor.utils import parse_mysql_connection_string
 
class MySqlMonitorPlugin(PythonDataSourcePlugin):
    proxy_attributes = ('zMySQLConnectionString',)

    def collect(self, config):
        for ds in config.datasources:
            servers = parse_mysql_connection_string(ds.zMySQLConnectionString)
            server = servers[ds.component]

            dbpool = adbapi.ConnectionPool("MySQLdb",
                user=server['user'],
                port=server['port'],
                passwd=server['passwd']
            )
            return dbpool.runQuery("show databases")
 
    def onSuccess(self, result, config):
        print '*********'*10
        print result
        print '*********'*10

        import random
        import time

        return {
            'events': [],
            'values': {
                'root_3306': {
                    'random': random.random()
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
