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
from datetime import datetime
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap

class MySQLServerCollector(CommandPlugin):

    command = """mysql -e '{server_size} {splitter} {server} \
        {splitter} {master} {splitter} {slave}'""".format(
            server_size = queries.SERVER_SIZE_QUERY,
            server = queries.SERVER_QUERY,
            master = queries.MASTER_QUERY,
            slave = queries.SLAVE_QUERY,
            splitter = queries.SPLITTER_QUERY,
        )

    def condition(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        # Results parsing
        query_list = ('server_size', 'server', 'master', 'slave')
        result = dict((query_list[num], result.split('\n')[1:-1])
            for num, result in enumerate(results.split('splitter\nsplitter\n'))
        )

        # SERVER_SIZE_QUERY parsing
        size, data_size, index_size = result['server_size'][0].split('\t')

        # SERVER_QUERY parsing
        server_result = dict((line.split('\t')[0], line.split('\t')[1])
            for line in result['server'])

        percent_full_table_scans = float(server_result['HANDLER_READ_FIRST'])/\
            float(server_result['HANDLER_READ_KEY'])

        # MASTER_QUERY parsing
        master_status = "OFF"
        if result['master']:
            master = result['master'][0].split('\t')
            master_status = "ON; File: %s; Position: %s" % (
                master[0], master[1])

        # SLAVE_QUERY parsing
        slave_status = server_result['SLAVE_RUNNING']
        if result['slave']:
            slave = dict((line.split(': ')[0].strip(), line.split(': ')[1])
                for line in result['slave'])
            slave_status = "IO: %s; SQL: %s; Seconds behind: %s" % (
                slave['Slave_IO_Running'], slave['Slave_SQL_Running'],
                slave['Seconds_Behind_Master'])

        maps = collections.OrderedDict([
            ('server', []),
        ])

        # Server properties
        maps['server'].append(ObjectMap({
            "model_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "size": size,
            "data_size": data_size,
            "index_size": index_size,
            "percent_full_table_scans": str(round(percent_full_table_scans, 3)*100)+'%',
            "master_status": master_status,
            "slave_status": slave_status,
        }))

        return list(chain.from_iterable(maps.itervalues()))
