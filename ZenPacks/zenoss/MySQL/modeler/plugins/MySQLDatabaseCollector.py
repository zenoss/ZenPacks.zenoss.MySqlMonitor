##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

''' Models discovery tree for MySQL. '''

import collections
import queries
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId
from ZenPacks.zenoss.MySQL import MODULE_NAME

class MySQLDatabaseCollector(CommandPlugin):

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

        maps = collections.OrderedDict([
            ('databases', []),
        ])

       # Database properties
        db_oms = []
        for db in queries.tab_parse(results.splitlines()).values():
            db_oms.append(ObjectMap({
                'id': prepId(db['schema_name']),
                'title': db['schema_name'],
                'size': db['size'],
                'data_size': db['data_length'],
                'index_size': db['index_length'],
                'default_character_set': db['default_character_set_name'],
                'default_collation': db['default_collation_name'],
            }))

        maps['databases'].append(RelationshipMap(
            relname='databases',
            modname=MODULE_NAME['MySQLDatabase'],
            objmaps=db_oms))

        return list(chain.from_iterable(maps.itervalues()))
