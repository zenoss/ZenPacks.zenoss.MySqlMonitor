##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from zope.component import adapts
from zope.interface import implements

from Products.ZenModel.Device import Device

from Products.ZenRelations.RelSchema import ToManyCont, ToOne

from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.device import DeviceInfo
from Products.Zuul.interfaces.device import IDeviceInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

from ZenPacks.zenoss.MySQL import MODULE_NAME


class MySQLServer(Device):
    meta_type = portal_type = 'MySQLServer'

    version = None
    model_time = None

    _properties = Device._properties + (
        {'id': 'version', 'type': 'string'},
        {'id': 'model_time', 'type': 'string'},
    )

    _relations = Device._relations + (
        ('databases', ToManyCont(
            ToOne, MODULE_NAME['MySQLDatabase'], 'server'
        )),
        ('processes', ToManyCont(
            ToOne, MODULE_NAME['MySQLProcess'], 'server'
        )),
    )

    def getIconPath(self):
        ''' Return the path to an icon for this component.  '''
        return '/++resource++ZenPacks_zenoss_MySQL/img/%s.png' % self.meta_type

    def setErrorNotification(self, status):
        msg = "Connection Failure, Please check server permissions "
        #send event that connection failed.
        self.dmd.ZenEventManager.sendEvent(dict(
            device=self.id,
            summary=msg,
            eventClass='/Status',
            eventKey='ConnectionError',
            severity=5,
            ))

        return

    def getErrorNotification(self):
        return


class IMySQLServerInfo(IDeviceInfo):
    '''
    API Info interface for MySQLServer.
    '''

    version = schema.TextLine(title=_t(u'MySQL Version'))
    model_time = schema.TextLine(title=_t(u'Model time'))


class MySQLServerInfo(DeviceInfo):
    ''' API Info adapter factory for MySQLServer '''

    implements(IMySQLServerInfo)
    adapts(MySQLServer)

    manageIp = ProxyProperty('manageIp')
    zCommandPort = ProxyProperty('zCommandPort')
    zCommandUsername = ProxyProperty('zCommandUsername')
    zCommandPassword = ProxyProperty('zCommandPassword')
    version = ProxyProperty('version')
    model_time = ProxyProperty('model_time')

    @property
    @info
    def first_seen(self):
        return self._object.getCreatedTimeString()
