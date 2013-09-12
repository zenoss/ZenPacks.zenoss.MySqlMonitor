##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

''' Models discovery tree for MySQL. '''

import re
import collections
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from Products.ZenUtils.Utils import prepId

from ZenPacks.zenoss.MySQL import MODULE_NAME
from ZenPacks.zenoss.MySQL.MySQLServer import CredentialsNotFound, get_credentials

class MySQLCollector(CommandPlugin):
    command = """mysql -e 'SELECT table_schema, table_name, engine, table_type, table_collation, table_rows, round(((data_length + index_length) / 1024 / 1024), 2) size_mb FROM information_schema.TABLES'"""

    # deviceProperties = CommandPlugin.deviceProperties + (
    #     'host',
    #     'port',
    #     'user',
    #     'password',
    # )

    # def getCommand(self):
    #     return """sshpass -p 'mySSHPasswordHere' ssh username@server.nixcraft.net.in "uptime" """

    def condition(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )
        maps = collections.OrderedDict([
            ('databases', []),
            ('processes', []),
            # ('server', []) # Our Device properties
        ])

        print "=============="
        print device.id
        print results
        print "=============="

        # # ---------------------------------------------------------------------
        # # Device properties
        # maps['server'].append(ObjectMap(data={
        # }))

        return list(chain.from_iterable(maps.itervalues()))
