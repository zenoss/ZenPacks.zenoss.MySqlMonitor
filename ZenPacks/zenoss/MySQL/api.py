##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from zope.event import notify
from zope.interface import implements

from ZODB.transact import transact

from Products.ZenUtils.Ext import DirectRouter, DirectResponse

from Products import Zuul
from Products.Zuul.catalog.events import IndexingEvent
from Products.Zuul.interfaces import IFacade
from Products.Zuul.facades import ZuulFacade
from Products.Zuul.utils import ZuulMessageFactory as _t


class IMySQLFacade(IFacade):

    def add_server(self, device_name, subscription_id, cert_file, collector):
        ''' Schedule the addition of an MySQL account.  '''

    def set_device_class_info(self, uid):
        '''
        Set the device classes into which to discovery the guest device
        devices from Linux and Windows instance platform respectively.
        '''

class MySQLFacade(ZuulFacade):
    implements(IMySQLFacade)

    def add_device(self, device_name, more_data, collector):
        deviceRoot = self._dmd.getDmdRoot("Devices")
        device = deviceRoot.findDeviceByIdExact(device_name)
        if device:
            return False, _t("A device named %s already exists." % device_name)

        @transact
        def create_device():
            dc = self._dmd.Devices.getOrganizer('/Devices/Server/MySQL')

            device = dc.createInstance(device_name)
            device.setPerformanceMonitor(collector)

            device.subscription_id = subscription_id
            device.cert_file = cert_file

            device.index_object()
            notify(IndexingEvent(device))

        # This must be committed before the following model can be
        # scheduled.
        create_device()

        # Schedule a modeling job for the new device.
        device = deviceRoot.findDeviceByIdExact(device_name)
        device.collectDevice(setlog=False, background=True)

        return True

    def set_device_class_info(self, uid):
        # XXX: What this do? 
        device = self._getObject(uid)



class MySQLRouter(DirectRouter):
    def _getFacade(self):
        return Zuul.getFacade('mysql', self.context)

    def add_device(self, device_name, subscription_id, cert_file, collector):
        success = self._getFacade().add_device(
            device_name, subscription_id, cert_file, collector)
        if success:
            return DirectResponse.succeed()
        else:
            return DirectResponse.fail("Failed to add MySQL Server")

    def set_device_class_info(self, uid):
        self._getFacade().set_device_class_info(uid)
