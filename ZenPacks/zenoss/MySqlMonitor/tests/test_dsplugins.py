
from Products.ZenTestCase.BaseTestCase import BaseTestCase

class TestMySQLMonitorPlugin(BaseTestCase):
    def test_imports(self):
    	from ZenPacks.zenoss.MySqlMonitor.dsplugins import MySqlMonitorPlugin
        # ok if imports


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQLMonitorPlugin))
    return suite
