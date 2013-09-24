from mock import MagicMock

from Products.ZenRRD.CommandParser import ParsedResults
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenRRD.zencommand import Cmd, DataPointConfig
from Products.ZenCollector.services.config import DeviceProxy

from ZenPacks.zenoss.MySQL.parsers.mysql_parser import MySQL
from ZenPacks.zenoss.MySQL.parsers.tables_schema import TablesSchema

from .util import load_data

class FakeCmdResult(object):
    exit_code = None
    output = None

    def __init__(self, exit_code, output):
        self.exit_code = exit_code
        self.output = output

def get_fake_cmd(output_filename, points, exit_code=0):
    def point_from_id(id):
        dpc = DataPointConfig()
        dpc.id = id
        return dpc
    points = map(point_from_id, points)

    cmd = Cmd()

    cmd.deviceConfig = DeviceProxy()
    cmd.result = FakeCmdResult(exit_code, load_data(output_filename))
    cmd.points = points

    return cmd

class TestMySQL(BaseTestCase):

    def afterSetUp(self):
        self.results = ParsedResults()
        self.parser = MySQL()

    def test_parser_runs(self):
        self.parser.processResults(MagicMock(), self.results)

    def test_1(self):
        self.parser.processResults(
            get_fake_cmd('show_status_1.txt', ('bytes_received', 'bytes_sent')),
            self.results
        )

        self.assertEquals(len(self.results.values), 2)
        correct = dict(
            bytes_received='117',
            bytes_sent='188',
        )
        for dp, val in self.results.values:
            self.assertEquals(correct[dp.id], val)

class TestTablesSchema(BaseTestCase):
    def afterSetUp(self):
        self.results = ParsedResults()
        self.parser = TablesSchema()

    def test_gets_values(self):
        self.parser.processResults(
            get_fake_cmd('information_schema.txt', ('table_rows', )),
            self.results
        )

        self.assertEquals(len(self.results.values), 1)

        correct = dict(
            table_rows='30',
        )
        for dp, val in self.results.values:
            self.assertEquals(correct[dp.id], val)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQL))
    suite.addTest(makeSuite(TestTablesSchema))
    return suite
