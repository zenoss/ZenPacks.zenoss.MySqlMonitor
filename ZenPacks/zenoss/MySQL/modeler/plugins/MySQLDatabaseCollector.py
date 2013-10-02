##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

''' Models discovery tree for MySQL. '''

import queries

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from ZenPacks.zenoss.MySQL import MODULE_NAME

class MySQLDatabaseCollector(CommandPlugin):

    relname = "databases"
    modname = MODULE_NAME['MySQLDatabase']
    command = """mysql -e '{db}'""".format(
            db = queries.DB_QUERY
        )

    def condition(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )
        rm = self.relMap()

       # Database properties
        for db in queries.tab_parse(results.splitlines()).values():
            om = self.objectMap()
            om.id = self.prepId(db['schema_name'])
            om.title = db['schema_name']
            om.size = db['size']
            om.data_size = db['data_length']
            om.index_size = db['index_length']
            om.default_character_set = db['default_character_set_name']
            om.default_collation = db['default_collation_name']

            rm.append(om)

        return rm
