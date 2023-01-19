##############################################################################
#
# Copyright (C) Zenoss, Inc. 2023, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version


class RemoveDbExistenceDataSource(ZenPackMigration):
    # Main class that contains the migrate() method.
    # Note version setting.
    version = Version(3, 2, 0)

    def migrate(self, dmd):
        # Disable unnecessary DbExistence datasource for MySQL Databases.
        organizer = dmd.Devices.getOrganizer('/Server')
        if organizer:
            for template in organizer.getRRDTemplates():
                if template.id == 'MySQLDatabase':
                    template.manage_deleteRRDDataSources(('DbExistence',))
