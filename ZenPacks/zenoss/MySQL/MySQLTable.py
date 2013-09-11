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


class MySQLTable(MySQLComponent):
    meta_type = portal_type = 'MySQLTable'

    engine = None
    table_type = None
    table_collation = None
    table_rows = None
    table_status = None
    size_mb = None

    _properties = MySQLComponent._properties + (
        {'id': 'engine', 'type': 'string'},
        {'id': 'table_type', 'type': 'string'},
        {'id': 'table_collation', 'type': 'string'},
        {'id': 'table_rows', 'type': 'string'},
        {'id': 'table_status', 'type': 'string'},
        {'id': 'size_mb', 'type': 'string'},
    )

    _relations = MySQLComponent._relations + (
        ('database', ToOne(ToManyCont, MODULE_NAME['MySQLDatabase'], 'tables')),
    )


class IMySQLTableInfo(IComponentInfo):
    '''
    API Info interface for MySQLTable.
    '''

    server = schema.Entity(title=_t(u'Server'))
    database = schema.Entity(title=_t(u'Database'))
    engine = schema.TextLine(title=_t(u'Engine'))
    table_type = schema.TextLine(title=_t(u'Type'))
    table_collation = schema.TextLine(title=_t(u'Collation'))
    table_rows = schema.TextLine(title=_t(u'Rows'))
    table_status = schema.TextLine(title=_t(u'Table status'))
    size_mb = schema.TextLine(title=_t(u'Size'))


class MySQLTableInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLTable.
    '''

    implements(IMySQLTableInfo)
    adapts(MySQLTable)

    engine = ProxyProperty('engine')
    table_type = ProxyProperty('table_type')
    table_collation = ProxyProperty('table_collation')
    table_rows = ProxyProperty('table_rows')
    table_status = ProxyProperty('table_status')
    size_mb = ProxyProperty('size_mb')

    @property
    @info
    def server(self):
        return self._object.device()

    @property
    @info
    def database(self):
        return self._object.database()


class MySQLTablePathReporter(DefaultPathReporter):
    ''' Path reporter for MySQLTable.  '''

    def getPaths(self):
        return super(MySQLTablePathReporter, self).getPaths()
