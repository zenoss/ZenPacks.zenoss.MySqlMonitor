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

    table_status = "--"

    _properties = MySQLComponent._properties + (
        {'id': 'table_status', 'type': 'string'},
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
    table_status = schema.TextLine(title=_t(u'Table status'))


class MySQLTableInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLTable.
    '''

    implements(IMySQLTableInfo)
    adapts(MySQLTable)

    table_status = ProxyProperty('table_status')

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
