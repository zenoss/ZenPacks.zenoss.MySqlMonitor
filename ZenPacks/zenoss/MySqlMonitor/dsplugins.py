import time

from twisted.enterprise import adbapi
from twisted.internet import defer

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin

from ZenPacks.zenoss.MySqlMonitor.utils import parse_mysql_connection_string


def zip_deferred(d, *args):
    nd = defer.Deferred()

    def new_callback(v):
        nd.callback((v,) + args)

    d.addCallback(new_callback)

    return nd


class MySqlMonitorPlugin(PythonDataSourcePlugin):
    proxy_attributes = ('zMySQLConnectionString',)

    def collect(self, config):
        print 'Collecting!' * 100
        for ds in config.datasources:
            servers = parse_mysql_connection_string(ds.zMySQLConnectionString)
            server = servers[ds.component]

            dbpool = adbapi.ConnectionPool(
               "MySQLdb",
               user=server['user'],
               port=server['port'],
               passwd=server['passwd']
            )
            return zip_deferred(dbpool.runQuery("show global status"), ds.component)

    def onSuccess(self, result, config):
        statuses, component = result
        t = time.time()

        values = dict((k.lower(), (v, t)) for k, v in statuses)

        return {
            'events': [],
            'values': {component: values}
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
