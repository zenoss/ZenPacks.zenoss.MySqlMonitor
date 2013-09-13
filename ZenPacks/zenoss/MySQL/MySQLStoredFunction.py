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


class MySQLStoredFunction(MySQLComponent):
    meta_type = portal_type = 'MySQLStoredFunction'

    body = None
    definition = None
    external_language = None
    security_type = None
    created = None
    last_altered = None

    _properties = MySQLComponent._properties + (
        {'id': 'body', 'type': 'string'},
        {'id': 'definition', 'type': 'string'},
        {'id': 'external_language', 'type': 'string'},
        {'id': 'security_type', 'type': 'string'},
        {'id': 'created', 'type': 'string'},
        {'id': 'last_altered', 'type': 'string'},
    )

    _relations = MySQLComponent._relations + (
        ('database', ToOne(ToManyCont, MODULE_NAME['MySQLDatabase'], 'stored_functions')),
    )


class IMySQLStoredFunctionInfo(IComponentInfo):
    '''
    API Info interface for MySQLStoredFunction.
    '''

    server = schema.Entity(title=_t(u'Server'))
    database = schema.Entity(title=_t(u'Database'))
    body = schema.TextLine(title=_t(u'Body'))
    definition = schema.TextLine(title=_t(u'Definition'))
    external_language = schema.TextLine(title=_t(u'External language'))
    security_type = schema.TextLine(title=_t(u'Security type'))
    created = schema.TextLine(title=_t(u'Created on'))
    last_altered = schema.TextLine(title=_t(u'Altered on'))


class MySQLStoredFunctionInfo(ComponentInfo):
    '''
    API Info adapter factory for MySQLStoredFunction.
    '''

    implements(IMySQLStoredFunctionInfo)
    adapts(MySQLStoredFunction)

    body = ProxyProperty('body')
    definition = ProxyProperty('definition')
    external_language = ProxyProperty('external_language')
    security_type = ProxyProperty('security_type')
    created = ProxyProperty('created')
    last_altered = ProxyProperty('last_altered')

    @property
    @info
    def server(self):
        return self._object.device()

    @property
    @info
    def database(self):
        return self._object.database()


class MySQLStoredFunctionPathReporter(DefaultPathReporter):
    ''' Path reporter for MySQLStoredFunction.  '''

    def getPaths(self):
        return super(MySQLStoredFunctionPathReporter, self).getPaths()
