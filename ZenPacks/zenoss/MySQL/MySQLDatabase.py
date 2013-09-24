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


class MySQLDatabase(MySQLComponent):
    meta_type = portal_type = 'MySQLDatabase'

    size = None
    data_size = None
    index_size = None
    default_character_set = None
    default_collation = None

    _properties = MySQLComponent._properties + (
        {'id': 'size', 'type': 'string'},
        {'id': 'data_size', 'type': 'string'},
        {'id': 'index_size', 'type': 'string'},
        {'id': 'default_character_set', 'type': 'string'},
        {'id': 'default_collation', 'type': 'string'},
    )

    _relations = MySQLComponent._relations + (
        ('server', ToOne(ToManyCont, MODULE_NAME['MySQLServer'], 'databases')),
        ('tables', ToManyCont(ToOne, MODULE_NAME['MySQLTable'], 'database')),
        ('stored_procedures', ToManyCont(ToOne, MODULE_NAME['MySQLStoredProcedure'], 'database')),
        ('stored_functions', ToManyCont(ToOne, MODULE_NAME['MySQLStoredFunction'], 'database')),
    )


class IMySQLDatabaseInfo(IComponentInfo):
    '''
    API Info interface for MySQLDatabase.
    '''

    server = schema.Entity(title=_t(u'Server'))
    size = schema.TextLine(title=_t(u'Size'))
    data_size = schema.TextLine(title=_t(u'Data size'))
    index_size = schema.TextLine(title=_t(u'Index size'))
    default_character_set = schema.TextLine(title=_t(u'Default character set'))
    default_collation = schema.TextLine(title=_t(u'Default collation'))
    table_count = schema.Int(title=_t(u'Number of tables'))
    stored_procedure_count = schema.Int(title=_t(u'Number of stored procedures'))
    stored_function_count = schema.Int(title=_t(u'Number of stored functions'))


class MySQLDatabaseInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLDatabase.
    '''

    implements(IMySQLDatabaseInfo)
    adapts(MySQLDatabase)

    size = SizeUnitsProxyProperty('size')
    data_size = SizeUnitsProxyProperty('data_size')
    index_size = SizeUnitsProxyProperty('index_size')
    default_character_set = ProxyProperty('default_character_set')
    default_collation = ProxyProperty('default_collation')

    @property
    @info
    def server(self):
        return self._object.device()

    @property
    def table_count(self):
        return self._object.tables.countObjects()

    @property
    def stored_procedure_count(self):
        return self._object.stored_procedures.countObjects()

    @property
    def stored_function_count(self):
        return self._object.stored_functions.countObjects()


class MySQLDatabasePathReporter(DefaultPathReporter):
    ''' Path reporter for MySQLDatabase.  '''

    def getPaths(self):
        return super(MySQLDatabasePathReporter, self).getPaths()
