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

from ZenPacks.zenoss.MySQL import MODULE_NAME, SizeUnitsProxyProperty


class MySQLServer(Device):
    meta_type = portal_type = 'MySQLServer'

    ip = None
    version = None
    model_time = None
    cmd = None
    size = None
    data_size = None
    index_size = None
    percent_full_table_scans = None
    slave_status = None
    master_status = None

    _properties = Device._properties + (
        {'id': 'ip', 'type': 'string'},
        {'id': 'version', 'type': 'string'},
        {'id': 'model_time', 'type': 'string'},
        {'id': 'cmd', 'type': 'string'},
        {'id': 'size', 'type': 'string'},
        {'id': 'data_size', 'type': 'string'},
        {'id': 'index_size', 'type': 'string'},
        {'id': 'percent_full_table_scans', 'type': 'string'},
        {'id': 'slave_status', 'type': 'string'},
        {'id': 'master_status', 'type': 'string'},
        {'id': 'zCommandPassword', 'type': 'password', 'visible': True},
        {'id': 'zCommandPort', 'type': 'string', 'visible': True},
        {'id': 'zCommandUsername', 'type': 'string', 'visible': True},
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

    @property
    def manageIp(self):
        #return self.manageIp
        return self.ip


class IMySQLServerInfo(IDeviceInfo):
    '''
    API Info interface for MySQLServer.
    '''

    ip = schema.TextLine(title=_t(u'MySQL Server IP address'))
    version = schema.TextLine(title=_t(u'MySQL Version'))
    model_time = schema.TextLine(title=_t(u'Model time'))
    cmd = schema.TextLine(title=_t(u'SSH command tool'))
    size = schema.TextLine(title=_t(u'Size'))
    data_size = schema.TextLine(title=_t(u'Data Size'))
    index_size = schema.TextLine(title=_t(u'Index Size'))
    percent_full_table_scans = schema.TextLine(title=_t(u'Percentage of full table scans'))
    slave_status = schema.TextLine(title=_t(u'Slave status'))
    master_status = schema.TextLine(title=_t(u'Master status'))


class MySQLServerInfo(DeviceInfo):
    ''' API Info adapter factory for MySQLServer '''

    implements(IMySQLServerInfo)
    adapts(MySQLServer)

    ip = ProxyProperty('ip')
    manageIp = ProxyProperty('manageIp')
    zCommandPort = ProxyProperty('zCommandPort')
    zCommandUsername = ProxyProperty('zCommandUsername')
    zCommandPassword = ProxyProperty('zCommandPassword')
    version = ProxyProperty('version')
    model_time = ProxyProperty('model_time')
    cmd = ProxyProperty('cmd')
    size = SizeUnitsProxyProperty('size')
    data_size = SizeUnitsProxyProperty('data_size')
    index_size = SizeUnitsProxyProperty('index_size')
    percent_full_table_scans = ProxyProperty('percent_full_table_scans')
    slave_status = ProxyProperty('slave_status')
    master_status = ProxyProperty('master_status')


    @property
    @info
    def first_seen(self):
        return self._object.getCreatedTimeString()