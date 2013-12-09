######################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

import sys
import unittest

from mock import Mock, patch, sentinel
from StringIO import StringIO

from Products.ZenTestCase.BaseTestCase import BaseTestCase

from ZenPacks.zenoss.MySqlMonitor.libexec import check_mysql_stats


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
    def test_run(self, mysqldb):
        MYSQL_STATS = (
            ('Aborted_clients', '1'),
            ('Aborted_connects', '2'),
        )

        connect = Mock()
        connect.cursor.return_value.fetchall.return_value = MYSQL_STATS
        mysqldb.connect.return_value = connect

        # Mock stdout to test print statements
        saved_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out

            self.ds.run()
            output = out.getvalue().strip()
        finally:
            sys.stdout = saved_stdout

        mysqldb.connect.assert_called_with(
            passwd=sentinel.passwd,
            host=sentinel.host,
            db='',
            user=sentinel.user,
            port=sentinel.port
        )
        self.assertEquals(
            output,
            'STATUS OK|Aborted_clients=1 Aborted_connects=2'
        )

    @patch.object(check_mysql_stats, 'MySQLdb')
    def test_error_statistics_run(self, mysqldb):
        MYSQL_STATS = ()
        connect = Mock()
        connect.cursor.return_value.fetchall.return_value = MYSQL_STATS
        mysqldb.connect.return_value = connect
        connect.cursor.return_value.execute.return_value = None

        # Mock stdout and exit to test print statements
        saved_stdout = sys.stdout
        saved_exit = sys.exit
        try:
            out = StringIO()
            sys.stdout = out
            sys.exit = Mock()

            self.ds.run()
            output = out.getvalue().strip()
        finally:
            sys.stdout = saved_stdout
            sys.exit = saved_exit

        connect.cursor.return_value.close.assert_called()
        self.assertEquals(
            output,
            'Error getting MySQL statistics\nSTATUS OK|'
        )


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestZenossMySqlStatsPlugin))
    return suite
