
from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.MySqlMonitor.utils import parse_mysql_connection_string


class TestMysqlConnectionStringParsing(BaseTestCase):
    def tcase(self, input, output):
        self.assertEquals(parse_mysql_connection_string(input), output)

    def test_empty(self):
        self.tcase('', {})
        self.tcase(';;', {})

    def test_one(self):
        d = {
            'user_123': {
                'user': 'user',
                'passwd': 'passwd',
                'port': 123,
            }
        }
        self.tcase('user:passwd:123', d)
        self.tcase('user:passwd:123;', d)

    def test_two(self):
        d = {
            'user_123': {
                 'user': 'user',
                'passwd': 'passwd',
                'port': 123,
            },
            'u_2': {
                'user': 'u',
                'passwd': 'passwd',
                'port': 2,
            }
        }
        self.tcase('user:passwd:123;u:passwd:2;', d)

    def test_port_not_int(self):
        self.assertRaises(ValueError, lambda : parse_mysql_connection_string('user:password:port'))

    def test_no_port(self):
        self.assertRaises(ValueError, lambda : parse_mysql_connection_string('user:passwd'))



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMysqlConnectionStringParsing))
    return suite
