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


class MySQLStoredProcedure(MySQLComponent):
    meta_type = portal_type = 'MySQLStoredProcedure'

    _relations = MySQLComponent._relations + (
        ('database', ToOne(ToManyCont, MODULE_NAME['MySQLDatabase'], 'stored_procedures')),
    )


class IMySQLStoredProcedureInfo(IComponentInfo):
    '''
    API Info interface for MySQLStoredProcedure.
    '''

    server = schema.Entity(title=_t(u'Server'))
    database = schema.Entity(title=_t(u'Database'))


class MySQLStoredProcedureInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLStoredProcedure.
    '''

    implements(IMySQLStoredProcedureInfo)
    adapts(MySQLStoredProcedure)

    @property
    @info
    def server(self):
        return self._object.device()

    @property
    @info
    def database(self):
        return self._object.database()


class MySQLStoredProcedurePathReporter(DefaultPathReporter):
    ''' Path reporter for MySQLStoredProcedure.  '''

    def getPaths(self):
        return super(MySQLStoredProcedurePathReporter, self).getPaths()
