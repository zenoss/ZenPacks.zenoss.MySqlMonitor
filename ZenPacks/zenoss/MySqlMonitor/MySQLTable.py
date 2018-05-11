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

    database = None
    name = None
    row_numbers = None

    _properties = MySQLComponent._properties + (
        {'id': 'database', 'type': 'string'},
        {'id': 'name', 'type': 'string'},
        {'id': 'row_numbers', 'type': 'int'},
    )

    _relations = MySQLComponent._relations + (
        ('databases', ToOne(ToManyCont, MODULE_NAME['MySQLDatabase'], 'tables')),
    )

    def device(self):
        return self.databases().device()


class IMySQLTableInfo(IComponentInfo):
    '''
    API Info interface for MySQLTable.
    '''

    database = schema.Entity(title=_t(u'Database'))
    name = schema.TextLine(title=_t(u'Name'))
    row_numbers = schema.Int(title=_t(u'Number of rows'))


class MySQLTableInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLTable.
    '''

    implements(IMySQLTableInfo)
    adapts(MySQLTable)

    database = ProxyProperty('database')
    name = ProxyProperty('name')
    row_numbers = ProxyProperty('row_numbers')

    @property
    @info
    def device(self):
        return self._object.device()

    @property
    @info
    def databases(self):
        return self._object.databases()

class MySQLTablePathReporter(DefaultPathReporter):
    ''' Path reporter for MySQLTable.  '''

    def getPaths(self):
        return super(MySQLTablePathReporter, self).getPaths()
