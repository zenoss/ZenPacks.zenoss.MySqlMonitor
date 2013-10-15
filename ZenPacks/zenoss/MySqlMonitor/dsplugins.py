import time

from twisted.enterprise import adbapi
from twisted.internet import defer

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin

from ZenPacks.zenoss.MySqlMonitor.utils import parse_mysql_connection_string
from ZenPacks.zenoss.MySqlMonitor import NAME_SPLITTER


def zip_deferred(d, *args):
    nd = defer.Deferred()

    def new_callback(v):
        nd.callback((v,) + args)

    d.addCallback(new_callback)

    return nd


class MysqlBasePlugin(PythonDataSourcePlugin):
    proxy_attributes = ('zMySQLConnectionString',)

    def get_query(self, component):
        raise NotImplemented

    def query_results_to_values(self, results):
        raise NotImplemented

    @defer.inlineCallbacks
    def collect(self, config):
        results = {}
        for ds in config.datasources:
            servers = parse_mysql_connection_string(ds.zMySQLConnectionString)
            server = servers[ds.component.split(NAME_SPLITTER)[0]]

            dbpool = adbapi.ConnectionPool(
               "MySQLdb",
               user=server['user'],
               port=server['port'],
               passwd=server['passwd']
            )
            res = yield dbpool.runQuery(self.get_query(ds.component))
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
            'vaues': {},
            'events': [{
                'summary': 'error: %s' % result,
                'eventKey': 'mysql_result',
                'severity': 4,
            }],
        }

class MySqlMonitorPlugin(MysqlBasePlugin):
    def get_query(self, component):
        return 'show global status'

    def query_results_to_values(self, results):
        t = time.time()
        return dict((k.lower(), (v, t)) for k, v in results)


class MySQLMonitorDatabasesPlugin(MySqlMonitorPlugin):
    def get_query(self, component):
        return '''
        SELECT
            count(table_name) table_count,
            sum(data_length + index_length) size,
            sum(data_length) data_size,
            sum(index_length) index_size
        FROM
            information_schema.TABLES
        WHERE
            table_schema = "%s"
        ''' % component.split(NAME_SPLITTER)[-1]

    def query_results_to_values(self, results):
        t = time.time()
        fields = enumerate(('table_count', 'size', 'data_size', 'index_size'))
        return dict((f, (results[0][i], t)) for i, f in fields)
