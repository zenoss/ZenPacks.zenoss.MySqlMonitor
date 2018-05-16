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

from . import CLASS_NAME, MODULE_NAME, SizeUnitsProxyProperty
from .MySQLComponent import MySQLComponent
from .utils import updateToMany, updateToOne


class MySQLTable(MySQLComponent):
    meta_type = portal_type = 'MySQLTable'

    table_rows = None
    table_schema = None
    table_name = None
    table_size_mb = None

    _properties = MySQLComponent._properties + (
        {'id': 'table_rows', 'type': 'int'},
        {'id': 'table_schema', 'type': 'string'},
        {'id': 'table_name', 'type': 'string'},
        {'id': 'table_size_mb', 'type': 'string'},
    )

    _relations = MySQLComponent._relations + (
        ('database', ToOne(ToManyCont, MODULE_NAME['MySQLDatabase'], 'tables')),
    )

    def device(self):
        return self.database().server().device()

class IMySQLTableInfo(IComponentInfo):
    '''
    API Info interface for MySQLTable.
    '''

    device = schema.Entity(title=_t(u'Device'))
    server = schema.Entity(title=_t(u'Server'))
    database = schema.Entity(title=_t(u'Database'))
    table_schema = schema.TextLine(title=_t(u'Table_schema'))
    table_name = schema.TextLine(title=_t(u'Table_name'))
    table_rows = schema.Int(title=_t(u'Number of rows'))
    table_size_mb = schema.TextLine(title=_t(u'Size on disk'))


class MySQLTableInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLTable.
    '''

    implements(IMySQLTableInfo)
    adapts(MySQLTable)

    table_rows = ProxyProperty('table_rows')
    table_schema = ProxyProperty('table_schema')
    table_name = ProxyProperty('table_name')
    table_size_mb = ProxyProperty('table_size_mb')

    @property
    @info
    def device(self):
        return self._object.device()

    @property
    @info
    def database(self):
        return self._object.database()

class MySQLTablePathReporter(DefaultPathReporter):
    ''' Path reporter for MySQLTable.  '''

    def getPaths(self):
        return super(MySQLTablePathReporter, self).getPaths()
