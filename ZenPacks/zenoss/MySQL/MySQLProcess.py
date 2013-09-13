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

from Products.ZenRelations.RelSchema import ToOne, ToMany, ToManyCont

from Products.Zuul.catalog.paths import DefaultPathReporter, relPath
from Products.Zuul.decorators import info
from Products.Zuul.form import schema
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.component import ComponentInfo
from Products.Zuul.interfaces.component import IComponentInfo
from Products.Zuul.utils import ZuulMessageFactory as _t

from . import CLASS_NAME, MODULE_NAME
from .MySQLComponent import MySQLComponent
from .utils import updateToMany, updateToOne


class MySQLProcess(MySQLComponent):
    meta_type = portal_type = 'MySQLProcess'

    user = None
    host = None
    db = None
    command = None
    time = None
    state = None
    process_info = None

    _properties = MySQLComponent._properties + (
        {'id': 'user', 'type': 'string'},
        {'id': 'host', 'type': 'string'},
        {'id': 'db', 'type': 'string'},
        {'id': 'command', 'type': 'string'},
        {'id': 'time', 'type': 'string'},
        {'id': 'state', 'type': 'string'},
        {'id': 'process_info', 'type': 'string'},
    )

    _relations = MySQLComponent._relations + (
        ('server', ToOne(ToManyCont, MODULE_NAME['MySQLServer'], 'processes')),
    )


class IMySQLProcessInfo(IComponentInfo):
    '''
    API Info interface for MySQLProcess.
    '''

    server = schema.Entity(title=_t(u'Server'))
    user = schema.TextLine(title=_t(u'User'))
    host = schema.TextLine(title=_t(u'Host'))
    db = schema.TextLine(title=_t(u'Database'))
    command = schema.TextLine(title=_t(u'Command'))
    time = schema.TextLine(title=_t(u'Time'))
    state = schema.TextLine(title=_t(u'State'))
    process_info = schema.TextLine(title=_t(u'Info'))


class MySQLProcessInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLProcess.
    '''

    implements(IMySQLProcessInfo)
    adapts(MySQLProcess)

    user = ProxyProperty('user')
    host = ProxyProperty('host')
    db = ProxyProperty('db')
    command = ProxyProperty('command')
    time = ProxyProperty('time')
    state = ProxyProperty('state')
    process_info = ProxyProperty('process_info')

    @property
    @info
    def server(self):
        return self._object.device()


class MySQLProcessPathReporter(DefaultPathReporter):
    ''' Path reporter for MySQLProcess.  '''

    def getPaths(self):
        return super(MySQLProcessPathReporter, self).getPaths()
