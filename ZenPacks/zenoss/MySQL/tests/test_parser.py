from mock import MagicMock

from Products.ZenRRD.CommandParser import ParsedResults
from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenRRD.tests.BaseParsersTestCase import Object
from Products.ZenRRD.zencommand import Cmd, DataPointConfig
from Products.ZenCollector.services.config import DeviceProxy

from .util import load_data

class FakeCmdResult(object):
    exit_code = None
    output = None

    def __init__(self, exit_code, output):
        self.exit_code = exit_code
        self.output = output

def get_fake_cmd(output_filename, points, exit_code=0, component=None):
    def point_from_id(id):
        dpc = DataPointConfig()
        dpc.id = id
        dpc.component = component
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
        from ZenPacks.zenoss.MySQL.parsers.mysql_parser import MySQL
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
        from ZenPacks.zenoss.MySQL.parsers.tables_schema import TablesSchema
        self.parser = TablesSchema()

    def test_gets_values(self):
        self.parser.processResults(
            get_fake_cmd(
                'information_schema.txt',
                ('table_rows', ),
                component='test.hello'
            ),
            self.results
        )

        self.assertEquals(len(self.results.values), 1)

        correct = dict(
            table_rows='30',
        )
        for dp, val in self.results.values:
            self.assertEquals(correct[dp.id], val)


class TestDatabase(BaseTestCase):
    def afterSetUp(self):
        self.results = ParsedResults()
        from ZenPacks.zenoss.MySQL.parsers.database import Database
        self.parser = Database()

    def test_database_process_results(self):
        cmd = get_fake_cmd('database.txt', ('size', 'index_size', 'data_size'))
        for point in cmd.points:
            point.component = 'test'

        self.parser.processResults(cmd, self.results)
        self.assertEquals(len(self.results.values), 3)

        correct = dict(
            size='1',
            index_size='2',
            data_size='3',
        )
        for dp, val in self.results.values:
            self.assertEquals(correct[dp.id], val)


class TestInnodbStatusParser(BaseTestCase):
    def afterSetUp(self):
        self.results = ParsedResults()
        from ZenPacks.zenoss.MySQL.parsers.innodb_status import InnodbStatus
        self.parser = InnodbStatus()

    def test_no_events(self):
        self.parser.processResults(
            get_fake_cmd('engine_innodb_status_ok.txt', ()),
            self.results
        )
        evt = {
            'severity': 0,
            'summary': 'No last deadlock data',
            'eventKey': 'innodb_deadlock',
            'eventClass': '/Status',
        }
        self.assertIn(evt, self.results.events)

    def test_deadlock(self):
        self.parser.processResults(
            get_fake_cmd('engine_innodb_deadlock.txt', ()),
            self.results
        )
        evt = {
            'severity': 3,
            'eventKey': 'innodb_deadlock',
            'eventClass': '/Status',
            'summary': '''LATEST DETECTED DEADLOCK
------------------------
130927 10:17:13
*** (1) TRANSACTION:
TRANSACTION 11703, ACTIVE 71 sec starting index read
mysql tables in use 1, locked 1
LOCK WAIT 5 lock struct(s), heap size 1024, 3 row lock(s)
MySQL thread id 40, OS thread handle 0xa4b6cb40, query id 131 localhost bunyk Searching rows for update
update test.innodb_deadlock_maker set a = 0 where a <> 0
*** (1) WAITING FOR THIS LOCK TO BE GRANTED:
RECORD LOCKS space id 0 page no 635 n bits 72 index `PRIMARY` of table `test`.`innodb_deadlock_maker` trx id 11703 lock_mode X waiting
Record lock, heap no 3 PHYSICAL RECORD: n_fields 3; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000011701; asc       ;;
 2: len 7; hex 82000001f8011d; asc        ;;

*** (2) TRANSACTION:
TRANSACTION 11702, ACTIVE 78 sec starting index read
mysql tables in use 1, locked 1
4 lock struct(s), heap size 320, 2 row lock(s)
MySQL thread id 41, OS thread handle 0xa4b3bb40, query id 132 localhost bunyk Searching rows for update
update test.innodb_deadlock_maker set a = 1 where a <> 1
*** (2) HOLDS THE LOCK(S):
RECORD LOCKS space id 0 page no 635 n bits 72 index `PRIMARY` of table `test`.`innodb_deadlock_maker` trx id 11702 lock mode S locks rec but not gap
Record lock, heap no 3 PHYSICAL RECORD: n_fields 3; compact format; info bits 0
 0: len 4; hex 80000001; asc     ;;
 1: len 6; hex 000000011701; asc       ;;
 2: len 7; hex 82000001f8011d; asc        ;;

*** (2) WAITING FOR THIS LOCK TO BE GRANTED:
RECORD LOCKS space id 0 page no 635 n bits 72 index `PRIMARY` of table `test`.`innodb_deadlock_maker` trx id 11702 lock_mode X waiting
Record lock, heap no 2 PHYSICAL RECORD: n_fields 3; compact format; info bits 0
 0: len 4; hex 80000000; asc     ;;
 1: len 6; hex 000000011701; asc       ;;
 2: len 7; hex 82000001f80110; asc        ;;

*** WE ROLL BACK TRANSACTION (2)
'''
        }
        self.assertIn(evt, self.results.events)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQL))
    suite.addTest(makeSuite(TestTablesSchema))
    suite.addTest(makeSuite(TestInnodbStatusParser))
    suite.addTest(makeSuite(TestDatabase))
    return suite
