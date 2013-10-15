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

    def get_query(self, component):
        return 'show global status'

    def query_results_to_values(self, results):
        t = time.time()
        return dict((k.lower(), (v, t)) for k, v in results)

    @defer.inlineCallbacks
    def collect(self, config):
        results = {}
        for ds in config.datasources:
            servers = parse_mysql_connection_string(ds.zMySQLConnectionString)
            server = servers[ds.component]

            dbpool = adbapi.ConnectionPool(
               "MySQLdb",
               user=server['user'],
               port=server['port'],
               passwd=server['passwd']
            )
            res = yield dbpool.runQuery('show global status')
            results[ds.component] = self.query_results_to_values(res)
        defer.returnValue(results)

    def onSuccess(self, result, config):
        return {
            'values': result,
            'events': [{
                'summary': 'Monitoring ok',
                'eventKey': 'mysql_result',
                'severity': 0,
            }],
        }

    def onError(self, result, config):
        return {
            'events': [{
                'summary': 'error: %s' % result,
                'eventKey': 'mysql_result',
                'severity': 4,
            }],
        }
