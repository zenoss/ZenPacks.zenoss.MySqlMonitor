
import unittest
from mock import Mock, patch, sentinel

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.MySqlMonitor import NAME_SPLITTER
from ZenPacks.zenoss.MySqlMonitor import dsplugins

class Test_datasource_to_dbpool(BaseTestCase):

    @patch.object(dsplugins, 'parse_mysql_connection_string')
    @patch.object(dsplugins, 'adbapi')
    def test_extracts_server(self, adbapi, parse_mysql_connection_string):
        adbapi.ConnectionPool.return_value = sentinel.dbpool
        parse_mysql_connection_string.return_value = {
            'server_id': dict(
                user=sentinel.user,
                port=sentinel.port,
                passwd=sentinel.passwd
            )
        }
        ds = Mock()
        ds.component = 'server_id' + NAME_SPLITTER + 'something other'
        ds.zMySQLConnectionString = sentinel.zMySQLConnectionString

        dbpool = dsplugins.datasource_to_dbpool(ds)

        self.assertEquals(dbpool, sentinel.dbpool)

        adbapi.ConnectionPool.assert_called_with(
            'MySQLdb',
            user=sentinel.user,
            port=sentinel.port,
            passwd=sentinel.passwd
        )
        parse_mysql_connection_string.assert_called_with(
            sentinel.zMySQLConnectionString
        )

class  TestMysqlBasePlugin(BaseTestCase):
    def setUp(self):
        self.plugin = dsplugins.MysqlBasePlugin()

    def test_onSuccess_clears_event(self):
        result = {'events': []}

        self.plugin.onSuccess(result, sentinel.any_value)

        event = result['events'][0]
        self.assertEquals(event['severity'], 0)
        self.assertEquals(event['eventKey'], 'mysql_result')

    def test_onError_event(self):
        result = self.plugin.onError(sentinel.some_result, sentinel.any_value)

        event = result['events'][0]
        self.assertEquals(event['severity'], 4)
        self.assertEquals(event['eventKey'], 'mysql_result')


class TestMySqlMonitorPlugin(BaseTestCase):

    @patch.object(dsplugins, 'time')
    def test_results_to_values(self, time):
        time.time.return_value = sentinel.current_time
        results = (
            ('Value', sentinel.value),
        )

        plugin = dsplugins.MySqlMonitorPlugin()
        values = plugin.query_results_to_values(results)

        self.assertEquals(values, {
            'value': (sentinel.value, sentinel.current_time)
        })

        



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(Test_datasource_to_dbpool))
    suite.addTest(makeSuite(TestMysqlBasePlugin))
    suite.addTest(makeSuite(TestMySqlMonitorPlugin))
    return suite
