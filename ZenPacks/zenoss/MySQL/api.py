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


class IMySQLServerFacade(IFacade):

    def add_server(self, name, host, port, user, password, collector):
        ''' Schedule the addition of an MySQL server. '''

    def set_device_class_info(self, uid):
        '''
        Set the device classes into which to discovery the guest device
        devices from Linux and Windows instance platform respectively.
        '''

class MySQLServerFacade(ZuulFacade):
    implements(IMySQLServerFacade)

    def add_server(self, name, host, port, user, password, collector):
        deviceRoot = self._dmd.getDmdRoot("Devices")
        device = deviceRoot.findDeviceByIdExact(name)
        if device:
            return False, _t("A device named %s already exists." % name)

        @transact
        def create_device():
            dc = self._dmd.Devices.getOrganizer('/Devices')

            device = dc.createInstance(name)
            device.setPerformanceMonitor(collector)

            device.host = host
            device.port = port
            device.user = user
            device.password = password

            device.index_object()
            notify(IndexingEvent(device))

        # This must be committed before the following model can be
        # scheduled.
        create_device()

        # Schedule a modeling job for the new device.
        device = deviceRoot.findDeviceByIdExact(name)
        device.collectDevice(setlog=False, background=True)

        return True

    def set_device_class_info(self, uid):
        # XXX: What this do? 
        device = self._getObject(uid)



class MySQLRouter(DirectRouter):
    def _getFacade(self):
        return Zuul.getFacade('mysqlserver', self.context)

    def add_server(self, name, host, port, user, password, collector):
        success = self._getFacade().add_stub_device(
            name, host, port, user, password, collector
        )
        if success:
            return DirectResponse.succeed()
        else:
            return DirectResponse.fail("Failed to add MySQL server")

    def set_device_class_info(self, uid):
        self._getFacade().set_device_class_info(uid)
