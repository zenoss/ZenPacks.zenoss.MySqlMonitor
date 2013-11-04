######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

from logging import getLogger
log = getLogger('zen.python')

import re
import time

from twisted.enterprise import adbapi
from twisted.internet import defer

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin

from ZenPacks.zenoss.MySqlMonitor.utils import parse_mysql_connection_string
from ZenPacks.zenoss.MySqlMonitor import NAME_SPLITTER


def datasource_to_dbpool(ds, ip):
    servers = parse_mysql_connection_string(ds.zMySQLConnectionString)
    server = servers[ds.component.split(NAME_SPLITTER)[0]]
    return adbapi.ConnectionPool(
        "MySQLdb",
        host=ip,
        user=server['user'],
        port=server['port'],
        passwd=server['passwd']
    )


class MysqlBasePlugin(PythonDataSourcePlugin):
    proxy_attributes = ('zMySQLConnectionString',)

    def get_query(self, component):
        raise NotImplemented

    def query_results_to_values(self, results):
        return {}

    def query_results_to_events(self, results, component):
        return []

    @defer.inlineCallbacks
    def collect(self, config):
        values = {}
        events = []
        maps = []
        for ds in config.datasources:
            try:
                dbpool = datasource_to_dbpool(ds, config.manageIp)
                res = yield dbpool.runQuery(self.get_query(ds.component))
                dbpool.close()
                values[ds.component] = self.query_results_to_values(res)
                events.extend(self.query_results_to_events(res, ds.component))
            except Exception, e:
                events.append({
                    'component': ds.component,
                    'summary': str(e),
                    'eventClass': '/Status',
                    'eventKey': 'mysql_result',
                    'severity': 4,
                })

        defer.returnValue(dict(
            events=events,
            values=values,
            maps=maps,
        ))

    def onSuccess(self, result, config):
        for component in result["values"].keys():
            # Clear events for success components.
            result['events'].insert(0, {
                'component': component,
                'summary': 'Monitoring ok',
                'eventClass': '/Status',
                'eventKey': 'mysql_result',
                'severity': 0,
            })
        return result

    def onError(self, result, config):
        log.error(result)
        return {
            'vaues': {},
            'events': [{
                'summary': 'error: %s' % result,
                'eventClass': '/Status',
                'eventKey': 'mysql_result',
                'severity': 4,
            }],
            'maps': [],
        }


class MySqlMonitorPlugin(MysqlBasePlugin):
    def get_query(self, component):
        return 'show global status'

    def query_results_to_values(self, results):
        t = time.time()
        return dict((k.lower(), (v, t)) for k, v in results)


class MySqlDeadlockPlugin(MysqlBasePlugin):
    deadlock_re = re.compile(
        '\n-+\n(LATEST DETECTED DEADLOCK\n-+\n.*?\n)-+\n',
        re.M | re.DOTALL
    )

    def get_query(self, component):
        return 'show engine innodb status'

    def query_results_to_events(self, results, component):
        text = results[0][2]
        deadlock_match = self.deadlock_re.search(text)
        if deadlock_match:
            summary = deadlock_match.group(1)
            severity = 3
        else:
            summary = 'No last deadlock data'
            severity = 0

        return [{
            'severity': severity,
            'eventKey': 'innodb_deadlock',
            'eventClass': '/Status',
            'summary': summary,
            'component': component,
        }]


class MySQLMonitorDatabasesPlugin(MysqlBasePlugin):
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
        ''' % adbapi.safe(component.split(NAME_SPLITTER)[-1])

    def query_results_to_values(self, results):
        t = time.time()
        fields = enumerate(('table_count', 'size', 'data_size', 'index_size'))
        return dict((f, (results[0][i] or 0, t)) for i, f in fields)


class MySQLDatabaseExistencePlugin(MysqlBasePlugin):
    def get_query(self, component):
        return ''' SELECT COUNT(*)
            FROM information_schema.SCHEMATA
            WHERE SCHEMA_NAME="%s"
        ''' % adbapi.safe(
            component.split(NAME_SPLITTER)[-1]
        )

    def query_results_to_events(self, results, component):
        if results[0][0]:
            severity = 0
            summary = 'Database exists'
        else:
            severity = 3
            summary = 'Database does not exist'

        return [{
            'severity': severity,
            'eventKey': 'db_existence',
            'eventClass': '/Status',
            'summary': summary,
            'component': component,
        }]
