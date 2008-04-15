###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2007, 2008, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import Globals
from Products.ZenModel.migrate.Migrate import Version
from Products.MySqlMonitor.datasources.MySqlMonitorDataSource \
        import MySqlMonitorDataSource

class RenamePasswordProperty:
    """
    In versions of MySqlMonitor up to 1.1.1 the only zProperty was called
    zMySqlRootPassword. This was short-sighted in that you don't need root
    access to read from the stats table.

    This migrate script replaces zMySqlRootPassword with two new zProperties:
    zMySqlUsername and zMySqlPassword.
    """

    version = Version(1, 1, 2)

    def migrate(self, pack):
        dmd = pack.__primary_parent__.__primary_parent__

        # Update existing templates that use the MySqlMonitorDataSource to use
        # the new zProperty names
        for template in dmd.Devices.getAllRRDTemplates():
            for datasource in template.datasources():
                if isinstance(datasource, MySqlMonitorDataSource):
                    datasource.username = '${here/zMySqlUsername}'
                    datasource.password = '${here/zMySqlPassword}'

        # Copy the value from zMySqlRootPassword to zMySqlPassword for all
        # device classes
        self.copyZMySqlPassword(dmd.Devices)
        for deviceClass in dmd.Devices.getSubOrganizers():
            self.copyZMySqlPassword(deviceClass)

        # Copy the zMySqlRootPassword to zMySqlPassword for all devices
        for device in dmd.Devices.getSubDevices():
            self.copyZMySqlPassword(device)

        # Remove the old zMySqlRootPassword zProperty
        if dmd.Devices.hasProperty('zMySqlRootPassword'):
            dmd.Devices._delProperty('zMySqlRootPassword')


    def copyZMySqlPassword(self, obj):
        if obj.hasProperty('zMySqlRootPassword'):
            obj.zMySqlPassword = obj.zMySqlRootPassword


RenamePasswordProperty()
