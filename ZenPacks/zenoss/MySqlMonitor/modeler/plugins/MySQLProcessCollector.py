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
from datetime import timedelta

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from ZenPacks.zenoss.MySQL import MODULE_NAME

class MySQLProcessCollector(CommandPlugin):

    relname = "processes"
    modname = MODULE_NAME['MySQLProcess']
    command = """mysql -e '{process}'""".format(
            process = queries.PROCESS_QUERY
        )

    def condition(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        rm = self.relMap()

       # Process properties
        for process in queries.tab_parse(results.splitlines()).values():
            time = process['time'] if process['time'] == "NULL" \
                else timedelta(seconds=int(process['time']))

            om = self.objectMap()
            om.id = self.prepId(process['id'])
            om.title = process['id']
            om.user = process['user']
            om.host = process['host']
            om.db = process['db']
            om.command = process['command']
            om.time = str(time)
            om.state = process['state']
            om.process_info = process['info']

            rm.append(om)

        return rm
