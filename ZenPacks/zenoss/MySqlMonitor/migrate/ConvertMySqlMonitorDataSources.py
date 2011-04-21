###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2007,2008 Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 or (at your
# option) any later version as published by the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import Globals
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenModel.ZenPack import ZenPack, ZenPackDataSourceMigrateBase
from ZenPacks.zenoss.MySqlMonitor.datasources.MySqlMonitorDataSource \
        import MySqlMonitorDataSource


class ConvertMySqlMonitorDataSources(ZenPackDataSourceMigrateBase):
    version = Version(2, 0, 1)
    
    # These provide for conversion of datasource instances to the new class
    dsClass = MySqlMonitorDataSource
    oldDsModuleName = 'Products.MySqlMonitor.datasources' \
                                                    '.MySqlMonitorDataSource'
    oldDsClassName = 'MySqlMonitorDataSource'
    
    # Reindex all applicable datasource instances
    reIndex = True
            
