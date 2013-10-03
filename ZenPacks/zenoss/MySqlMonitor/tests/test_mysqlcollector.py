##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import logging

from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenCollector.services.config import DeviceProxy

from ZenPacks.zenoss.MySqlMonitor.modeler.plugins.MySQLDatabaseCollector import MySQLDatabaseCollector
from ZenPacks.zenoss.MySqlMonitor.modeler.plugins.MySQLProcessCollector import MySQLProcessCollector
from ZenPacks.zenoss.MySqlMonitor.modeler.plugins.MySQLServerCollector import MySQLServerCollector

from .util import load_data

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
        self.logger = logging.getLogger('.'.join(['zen', __name__]))
        ObjectMap.asUnitTest = patch_asUnitTest

    def test_server_collector(self):
        collector = MySQLServerCollector()
        results = load_data('model_server_data.txt')
        object_map = collector.process(self.device, results, self.logger)
        object_map.model_time = 'test'

        self.assertEquals({
            'percent_full_table_scans': '66.7%',
            'model_time': 'test',
            'index_size': '12419072',
            'master_status': 'ON; File: mysqld-bin.000001; Position: 106',
            'slave_status': 'IO running: Yes; SQL running: Yes; Seconds behind: 10',
            'data_size': '150927376',
            'size': '163346448'}, object_map.asUnitTest())

    def test_server_no_slave_master_collector(self):
        collector = MySQLServerCollector()
        results = load_data('model_server_no_master_slave_data.txt')
        object_map = collector.process(self.device, results, self.logger)
        object_map.model_time = 'test'

        self.assertEquals({
            'percent_full_table_scans': 'N/A',
            'model_time': 'test',
            'index_size': '12419072',
            'master_status': 'OFF',
            'slave_status': 'OFF',
            'data_size': '150927376',
            'size': '163346448'}, object_map.asUnitTest())

    def test_table_collector(self):
        collector = MySQLDatabaseCollector()
        results = load_data('model_database_data.txt')
        object_map = collector.process(self.device, results, self.logger)[1].maps[0]

        self.assertEquals({
            'engine': 'InnoDB',
            'table_status': 'OK',
            'table_rows': '10',
            'title': 'table1',
            'table_type': 'InnoDB',
            'data_size': '8',
            'size': '10',
            'index_size': '2',
            'table_collation': 'utf32_general_ci',
            'id': 'zenoss_zep(.,.)table1'}, object_map.asUnitTest())

    def test_routine_collector(self):
        collector = MySQLDatabaseCollector()
        results = load_data('model_database_data.txt')
        rel_map = collector.process(self.device, results, self.logger)[2:]

        for el in rel_map:
            self.assertEquals({'body': 'SQL',
            'created': '2013-07-30 18:36:54',
            'definition': 'body',
            'external_language': 'NULL',
            'id': 'zenoss_zep(.,.)BINARY',
            'last_altered': '2013-07-30 18:36:54',
            'security_type': 'DEFINER',
            'title': 'BINARY'}, el.maps[0].asUnitTest())

    def test_no_routine_collector(self):
        collector = MySQLDatabaseCollector()
        results = load_data('model_database_no_routines_statuses_data.txt')
        rel_map = collector.process(self.device, results, self.logger)[2:]
        self.assertFalse(rel_map)

    def test_database_collector(self):
        collector = MySQLDatabaseCollector()
        results = load_data('model_database_data.txt')
        object_map = collector.process(self.device, results, self.logger)[0].maps[0]

        self.assertEquals({
            'data_size': '0',
            'default_character_set': 'utf8',
            'default_collation': 'utf8_general_ci',
            'id': 'zenoss_zep',
            'index_size': '9216',
            'size': '9216',
            'title': 'zenoss_zep'}, object_map.asUnitTest())

    def test_process_collector(self):
        collector = MySQLProcessCollector()
        results = load_data('model_process_data.txt')
        rel_map = collector.process(self.device, results, self.logger).maps
        oms = [object_map.asUnitTest() for object_map in rel_map]

        for el in ('0:00:00', 'NULL'):
            self.assertIn({'title': '2',
                'db': 'zenoss_zep',
                'state': 'None',
                'host': 'localhost:36176',
                'command': 'Sleep',
                'user': 'zenoss',
                'time': el,
                'id': '2',
                'process_info': 'NULL'}, oms)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQLCollector))
    return suite
