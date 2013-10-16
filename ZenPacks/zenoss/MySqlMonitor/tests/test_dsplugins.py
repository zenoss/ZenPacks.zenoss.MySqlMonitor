import unittest
from mock import MagicMock
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from ZenPacks.zenoss.MySqlMonitor import dsplugins


class TestMySQLMonitorPlugin(BaseTestCase):
    def test_imports(self):
        from ZenPacks.zenoss.MySqlMonitor.dsplugins import MySqlMonitorPlugin
        # ok if imports


class TestMonitoring(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.ds = MagicMock()
        self.ds.zMySQLConnectionString = 'root::3306;'
        self.ds.component = 'root_3306'
        self.config.datasources = [self.ds]
        dsplugins.adbapi = MagicMock()
        dsplugins.adbapi.ConnectionPool.return_value.runQuery.return_value = MagicMock(return_value='a')

    def test_collect_defered(self):
        deferred = dsplugins.MySqlMonitorPlugin().collect(self.config)
        self.assertIn("Deferred", str(deferred))

    def test_collect_entered_zMySQLConnectionString(self):
        self.ds.zMySQLConnectionString = 'root::306;'
        self.assertRaises(KeyError, dsplugins.MySqlMonitorPlugin().collect, self.config)

    def test_collect_entered_component(self):
        self.ds.component = 'root3306'
        self.assertRaises(KeyError, dsplugins.MySqlMonitorPlugin().collect, self.config)

 
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQLMonitorPlugin))
    suite.addTest(makeSuite(TestMonitoring))
    return suite
