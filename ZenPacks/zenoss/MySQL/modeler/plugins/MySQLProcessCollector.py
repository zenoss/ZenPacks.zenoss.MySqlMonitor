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
from datetime import timedelta
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId
from ZenPacks.zenoss.MySQL import MODULE_NAME

class MySQLProcessCollector(CommandPlugin):

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

        maps = collections.OrderedDict([
            ('processes', []),
        ])

       # Process properties
        process_oms = []
        for process in queries.tab_parse(results.splitlines()).values():
            if process['time']:
                time = timedelta(seconds=int(process['time']))
            process_oms.append(ObjectMap({
                'id': prepId(process['id']),
                'title': process['id'],
                'user': process['user'],
                'host': process['host'],
                'db': process['db'],
                'command': process['command'],
                'time': str(time),
                'state': process['state'],
                'process_info': process['info'],
            }))

        maps['processes'].append(RelationshipMap(
            relname='processes',
            modname=MODULE_NAME['MySQLProcess'],
            objmaps=process_oms))

        return list(chain.from_iterable(maps.itervalues()))
