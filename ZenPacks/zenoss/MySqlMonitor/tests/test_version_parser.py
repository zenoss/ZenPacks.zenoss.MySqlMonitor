##############################################################################
#
# Copyright (C) Zenoss, Inc. 2025, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

''' Tests version parser for MySQL and MariaDB. '''

from ZenPacks.zenoss.MySqlMonitor.modeler.plugins.MySQLCollector import MySQLCollector
from Products.ZenTestCase.BaseTestCase import BaseTestCase


def make_version_result(mapping):
    """Helper to convert a dict of Variable_name->Value into the list-of-dicts
    shape that _get_version_info expects."""
    return [{'Variable_name': k, 'Value': v} for k, v in mapping.items()]


class TestVersionParser(BaseTestCase):

    def afterSetUp(self):
        self.collector = MySQLCollector()

    def test_mysql_version_parsing(self):
        data = make_version_result({
            'version': '8.4.0',
            'version_comment': 'MySQL Community Server',
        })
        is_mariadb, version_tuple = self.collector._get_version_info(data)
        self.assertFalse(is_mariadb)
        self.assertEqual(version_tuple, (8, 4, 0))

    def test_mariadb_detection_and_parsing(self):
        data = make_version_result({
            'version': '11.8.5-MariaDB',
            'version_comment': '11.8.5-MariaDB',
        })
        is_mariadb, version_tuple = self.collector._get_version_info(data)
        self.assertTrue(is_mariadb)
        self.assertEqual(version_tuple, (11, 8, 5))

    def test_empty_and_none_input(self):
        # empty list
        is_mariadb, version_tuple = self.collector._get_version_info([])
        self.assertFalse(is_mariadb)
        self.assertIsNone(version_tuple)

        # None
        is_mariadb, version_tuple = self.collector._get_version_info(None)
        self.assertFalse(is_mariadb)
        self.assertIsNone(version_tuple)

    def test_malformed_version_string(self):
        # Malformed numeric version but mariadb comment
        data = make_version_result({
            'version': 'vX.Y',
            'version_comment': 'MariaDB Server',
        })
        is_mariadb, version_tuple = self.collector._get_version_info(data)
        self.assertTrue(is_mariadb)
        self.assertIsNone(version_tuple)

        # Malformed numeric version and not mariadb
        data = make_version_result({
            'version': 'vX.Y',
            'version_comment': 'MySQL Community Server',
        })
        is_mariadb, version_tuple = self.collector._get_version_info(data)
        self.assertFalse(is_mariadb)
        self.assertIsNone(version_tuple)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestVersionParser))
    return suite
