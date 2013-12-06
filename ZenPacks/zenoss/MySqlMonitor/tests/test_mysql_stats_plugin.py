


# import sys
# sys.path.insert(0, 'ZenPacks/zenoss/MySqlMonitor/libexec/')

import unittest
from mock import Mock, patch, sentinel

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.MySqlMonitor import NAME_SPLITTER
from ZenPacks.zenoss.MySqlMonitor.libexec import check_mysql_stats
from .data import modeling_data


class TestZenossMySqlStatsPlugin(BaseTestCase):

    def afterSetUp(self):
        super(TestZenossMySqlStatsPlugin, self).afterSetUp()
        self.ds = check_mysql_stats.ZenossMySqlStatsPlugin(
            sentinel.host,
            sentinel.port,
            sentinel.user,
            sentinel.passwd,
            sentinel.gstatus
        )

    @patch.object(check_mysql_stats, 'MySQLdb')
    def test_getCommand(self, mysqldb):
        connect = Mock()
        connect.cursor.return_value.fetchall.return_value = modeling_data.MYSQL_STATS
        mysqldb.connect.return_value = connect

        self.ds.run()
        mysqldb.connect.assert_called_with(
            passwd=sentinel.passwd,
            host=sentinel.host,
            db='',
            user=sentinel.user,
            port=sentinel.port
        )

        connect.cursor.return_value.execute.return_value = modeling_data.MYSQL_STATS
        self.ds.run()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZenossMySqlStatsPlugin))
    return suite