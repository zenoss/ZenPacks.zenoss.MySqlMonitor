##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################
import logging

from Products.ZenTestCase.BaseTestCase import BaseTestCase
from Products.ZenRRD.tests.BaseParsersTestCase import Object
from Products.ZenCollector.services.config import DeviceProxy

from ZenPacks.zenoss.MySQL.modeler.plugins.MySQLTableCollector import MySQLTableCollector

from .util import load_data

class TestMySQLTableCollector(BaseTestCase):

    def afterSetUp(self):
        self.results = load_data('modeler_data.txt')
        self.device = DeviceProxy()
        self.device.id = "test"
        self.logger = logging.getLogger('.'.join(['zen', __name__]))

    def test_process(self):
        collector = MySQLTableCollector()
        collector.process(self.device, self.results, self.logger)
        # TODO: asserts


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMySQLTableCollector))
    return suite



