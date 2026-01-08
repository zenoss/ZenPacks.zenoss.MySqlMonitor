##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, 1015, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import Globals

import logging
from .data import modeling_data
from mock import MagicMock, patch
from MySQLdb import cursors
from twisted.internet import defer

from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenCollector.services.config import DeviceProxy

from ZenPacks.zenoss.MySqlMonitor.modeler.plugins.MySQLCollector \
    import MySQLCollector
from ZenPacks.zenoss.MySqlMonitor.modeler import queries


def patch_asUnitTest(self):
    """
    Patch asUnitTest method of ObjectMap so that it does not
    raise key errors of 'classname' and 'compname'.
    """
    map = {}
    map.update(self.__dict__)
    del map["_attrs"]
    try:
        del map["modname"]
        del map["compname"]
        del map["classname"]
    except:
        pass
    return map


class TestMySQLCollector(BaseTestCase):

    def afterSetUp(self):
        self.device = DeviceProxy()
        self.device.id = "test"
        self.device.manageIp = "127.0.0.1"
        self.logger = logging.getLogger('.'.join(['zen', __name__]))
        ObjectMap.asUnitTest = patch_asUnitTest
        self.collector = MySQLCollector()
        self.collector._eventService = MagicMock()
        self.collector.queries = {'test': 'test'}

    def test_process_data(self):
        results = modeling_data.RESULT1
        server_map, db_map = self.collector.\
            process(self.device, results, self.logger)

        self.assertEquals({
            'data_size': 53423729,
            'id': 'root_3306',
            'index_size': 4143104,
            'source_status': 'OFF',
            'percent_full_table_scans': '71.2%',
            'size': 57566833,
            'replica_status': 'IO running: No; SQL running: '
                            'No; Seconds behind: None',
            'version': '5.5.28 MySQL Community Server (GPL) (i686)',
            'title': 'root_3306'}, server_map.maps[0].asUnitTest())

        self.assertEquals({
            'data_size': 0,
            'default_character_set_name': 'utf8',
            'default_collation_name': 'utf8_general_ci',
            'id': 'root_3306(.)information_schema',
            'index_size': 9216,
            'size': 9216,
            'table_count': 40L,
            'title': 'information_schema'}, db_map.maps[0].asUnitTest())

    @patch('ZenPacks.zenoss.MySqlMonitor.modeler.'
           'plugins.MySQLCollector.adbapi')
    def test_collect(self, mock_adbapi):
        self.device.zMySqlSslCaPemFile = ''
        self.device.zMySqlSslCertPemFile = ''
        self.device.zMySqlSslKeyPemFile = ''
        self.device.zMySQLConnectionString = ['{"user":"root",'
                                              '"passwd":"zenoss",'
                                              '"port":"3306"}']
        self.collector.collect(self.device, self.logger)
        mock_adbapi.ConnectionPool.assert_called_with(
            'MySQLdb',
            passwd='zenoss',
            port=3306,
            host='127.0.0.1',
            user='root',
            cursorclass=cursors.DictCursor
        )

    def test_table_scans(self):
        self.assertEquals(
            self.collector._table_scans(modeling_data.SERVER_STATUS1),
            '71.2%'
        )
        self.assertEquals(
            self.collector._table_scans(modeling_data.SERVER_STATUS2),
            'N/A'
        )

    def test_source_status(self):
        self.assertEquals(
            self.collector._source_status(modeling_data.SOURCE_STATUS1),
            "ON; File: mysql-bin.000002; Position: 107"
        )
        self.assertEquals(
            self.collector._source_status(modeling_data.SOURCE_STATUS2),
            "OFF"
        )

    def test_replica_status(self):
        self.assertEquals(
            self.collector._replica_status(modeling_data.REPLICA_STATUS1, self.logger),
            "IO running: No; SQL running: No; Seconds behind: 10"
        )
        self.assertEquals(
            self.collector._replica_status(modeling_data.REPLICA_STATUS2, self.logger),
            "OFF"
        )

    def test_replica_status_v84(self):
        self.assertEquals(
            self.collector._replica_status(modeling_data.REPLICA_STATUS1_v84, self.logger),
            "IO running: Yes; SQL running: Yes; Seconds behind: 0"
        )

    def test_version(self):
        self.assertEquals(
            self.collector._version(modeling_data.VERSION1),
            '5.5.28 MySQL Community Server (GPL) (i686)'
        )

    def test_doComplexQuery_mysql_old_version(self):
        """_doComplexQuery should pick SOURCE_QUERY_MYSQL[0] for MySQL < 8.4.0."""
        self.collector.queries = {'source': queries.SOURCE_QUERY_MYSQL, 'replica': queries.REPLICA_QUERY}
        res = {'version': (
            {'Value': '5.7.31', 'Variable_name': 'version'},
            {'Value': 'MySQL Community Server', 'Variable_name': 'version_comment'},
        )}
        
        mock_dbpool = MagicMock()
        mock_dbpool.runQuery.return_value = defer.succeed((('src',),))
        
        d = self.collector._doComplexQuery(mock_dbpool, res, 'root', 3306, self.device.id, self.logger)
        if hasattr(d, 'addBoth'):
            d.addBoth(lambda _: None)
        
        expected_query = queries.SOURCE_QUERY_MYSQL[0].strip()
        called_queries = [call[0][0].strip() for call in mock_dbpool.runQuery.call_args_list]
        self.assertIn(expected_query, called_queries)

    def test_doComplexQuery_mysql_new_version(self):
        """_doComplexQuery should pick SOURCE_QUERY_MYSQL[1] for MySQL >= 8.4.0."""
        self.collector.queries = {'source': queries.SOURCE_QUERY_MYSQL, 'replica': queries.REPLICA_QUERY}
        res = {'version': (
            {'Value': '8.4.0', 'Variable_name': 'version'},
            {'Value': 'MySQL Community Server', 'Variable_name': 'version_comment'},
        )}
        
        mock_dbpool = MagicMock()
        mock_dbpool.runQuery.return_value = defer.succeed((('src2',),))
        
        d = self.collector._doComplexQuery(mock_dbpool, res, 'root', 3306, self.device.id, self.logger)
        if hasattr(d, 'addBoth'):
            d.addBoth(lambda _: None)
        
        expected_query = queries.SOURCE_QUERY_MYSQL[1].strip()
        called_queries = [call[0][0].strip() for call in mock_dbpool.runQuery.call_args_list]
        self.assertIn(expected_query, called_queries)

    def test_doComplexQuery_mariadb_new_version(self):
        """_doComplexQuery should pick SOURCE_QUERY_MARIADB[1] for MariaDB >= 10.5.2."""
        self.collector.queries = {'source': queries.SOURCE_QUERY_MARIADB, 'replica': queries.REPLICA_QUERY}
        res = {'version': (
            {'Value': '11.8.5', 'Variable_name': 'version'},
            {'Value': '11.8.5-MariaDB', 'Variable_name': 'version_comment'},
        )}
        
        mock_dbpool = MagicMock()
        mock_dbpool.runQuery.return_value = defer.succeed((('src',),))
        
        d = self.collector._doComplexQuery(mock_dbpool, res, 'root', 3306, self.device.id, self.logger)
        if hasattr(d, 'addBoth'):
            d.addBoth(lambda _: None)
        
        expected_query = queries.SOURCE_QUERY_MARIADB[1].strip()
        called_queries = [call[0][0].strip() for call in mock_dbpool.runQuery.call_args_list]
        self.assertIn(expected_query, called_queries)

    def test_doComplexQuery_mariadb_old_version(self):
        """_doComplexQuery should pick SOURCE_QUERY_MARIADB[0] for MariaDB < 10.5.2."""
        self.collector.queries = {'source': queries.SOURCE_QUERY_MARIADB, 'replica': queries.REPLICA_QUERY}
        res = {'version': (
            {'Value': '10.5.1', 'Variable_name': 'version'},
            {'Value': '10.5.1-MariaDB', 'Variable_name': 'version_comment'},
        )}
        
        mock_dbpool = MagicMock()
        mock_dbpool.runQuery.return_value = defer.succeed((('src_old',),))
        
        d = self.collector._doComplexQuery(mock_dbpool, res, 'root', 3306, self.device.id, self.logger)
        if hasattr(d, 'addBoth'):
            d.addBoth(lambda _: None)
        
        expected_query = queries.SOURCE_QUERY_MARIADB[0].strip()
        called_queries = [call[0][0].strip() for call in mock_dbpool.runQuery.call_args_list]
        self.assertIn(expected_query, called_queries)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQLCollector))
    return suite
