##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import logging
from .data import modeling_data
from mock import MagicMock

from Products.DataCollector.plugins.DataMaps import ObjectMap
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenCollector.services.config import DeviceProxy

from ZenPacks.zenoss.MySqlMonitor.modeler.plugins.MySQLCollector import MySQLCollector

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

    def test_collector(self):
        collector = MySQLCollector()
        collector._eventService = MagicMock()
        results = modeling_data.RESULT1
        server_map, db_map = collector.process(self.device, results, self.logger)

        self.assertEquals({
            'data_size': 53423729,
            'id': 'root_3306',
            'index_size': 4143104,
            'master_status': 'OFF',
            'percent_full_table_scans': '0.0%',
            'size': 57566833,
            'slave_status': 'IO running: No; SQL running: No; Seconds behind: None',
            'title': 'root:3306'}, server_map.maps[0].asUnitTest())

        self.assertEquals({
            'data_size': 0,
            'default_character_set_name': 'utf8',
            'default_collation_name': 'utf8_general_ci',
            'id': 'root_3306(.)information_schema',
            'index_size': 9216,
            'size': 9216,
            'table_count': 40L,
            'title': 'information_schema'}, db_map.maps[0].asUnitTest())

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQLCollector))
    return suite