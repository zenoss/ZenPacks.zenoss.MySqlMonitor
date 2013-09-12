from mock import MagicMock

from Products.ZenRRD.CommandParser import ParsedResults
from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.MySQL.parsers.mysql_parser import MySQL

class TestMySQL(BaseTestCase):

    def afterSetUp(self):
        self.results = ParsedResults()
        self.parser = MySQL()

    def test_parser_runs(self):
        self.parser.processResults(MagicMock(), self.results)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQL))
    return suite
