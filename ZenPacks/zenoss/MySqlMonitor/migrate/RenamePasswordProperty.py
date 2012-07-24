##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2007, 2008, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


import Globals
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version

class RenamePasswordProperty( ZenPackMigration ):
    """
    In versions of MySqlMonitor up to 1.1.1 the only zProperty was called
    zMySqlRootPassword. This was short-sighted in that you don't need root
    access to read from the stats table.

    This migrate script replaces zMySqlRootPassword with two new zProperties:
    zMySqlUsername and zMySqlPassword.
    """

    version = Version(2, 0, 0)

    def migrate(self, pack):
        dmd = pack.__primary_parent__.__primary_parent__

        try:
            from Products.MySqlMonitor.datasources.MySqlMonitorDataSource \
                    import MySqlMonitorDataSource
        except ImportError:
            #old version of data source no longer exists; nothing to upgrade
            return
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
