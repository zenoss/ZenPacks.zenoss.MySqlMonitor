###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2010, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################
from zope.interface import implements
from Products.Zuul.infos import ProxyProperty
from Products.Zuul.infos.template import BasicDataSourceInfo
from ZenPacks.zenoss.MySqlMonitor.interfaces import IMySqlMonitorDataSourceInfo


class MySqlMonitorDataSourceInfo(BasicDataSourceInfo):
    implements(IMySqlMonitorDataSourceInfo)
    timeout = ProxyProperty('timeout')
    usessh = ProxyProperty('usessh')
    versionFivePlus = ProxyProperty('versionFivePlus')
    hostname = ProxyProperty('hostname')
    port = ProxyProperty('port')
    username = ProxyProperty('username')
    password = ProxyProperty('password')
        
    @property
    def testable(self):
        """
        We can NOT test this datsource against a specific device
        """
        return False
    


