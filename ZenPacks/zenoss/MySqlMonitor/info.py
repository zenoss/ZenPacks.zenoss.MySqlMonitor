##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2010, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


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
