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


class MySQLDatabase(MySQLComponent):
    meta_type = portal_type = 'MySQLDatabase'

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


class MySQLDatabaseInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLDatabase.
    '''

    implements(IMySQLDatabaseInfo)
    adapts(MySQLDatabase)

    @property
    @info
    def server(self):
        return self._object.device()


class MySQLDatabasePathReporter(DefaultPathReporter):
    ''' Path reporter for MySQLDatabase.  '''

    def getPaths(self):
        return super(MySQLDatabasePathReporter, self).getPaths()
