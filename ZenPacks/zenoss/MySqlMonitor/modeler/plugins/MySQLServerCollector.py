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
from datetime import datetime

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from ZenPacks.zenoss.MySqlMonitor import MODULE_NAME

class MySQLServerCollector(CommandPlugin):

    relname = "server"
    modname = MODULE_NAME['MySQLServer']
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
        result = dict((query_list[num], result.split('\n'))
            for num, result in enumerate(results.split('splitter\nsplitter\n'))
        )

        # SERVER_SIZE_QUERY parsing
        size, data_size, index_size = result['server_size'][1].split('\t')

        # Server properties
        om = self.objectMap()
        om.model_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        om.size = size
        om.data_size = data_size
        om.index_size = index_size
        om.percent_full_table_scans = self._percent_full_table_scans(result['server'])
        om.master_status = self._master_status(result.get('master', ''))
        om.slave_status = self._slave_status(result.get('slave', ''))

        return om

    def _percent_full_table_scans(self, server_result):
        """Calculates the percent of full table scans for server.

        @param server_result: result of SERVER_QUERY
        @type server_result: string
        @return: str, rounded value with percent sign
        """

        server_result = dict((line.split('\t')[0], line.split('\t')[1])
            for line in server_result if line)

        if int(server_result['HANDLER_READ_KEY']) == 0:
            return "N/A"

        percent = float(server_result['HANDLER_READ_FIRST'])/\
            float(server_result['HANDLER_READ_KEY'])

        return str(round(percent, 3)*100)+'%'

    def _master_status(self, master_result):
        """Parse the result of MASTER_QUERY.

        @param master_result: result of MASTER_QUERY
        @type master_result: string
        @return: str, master status
        """

        if queries.tab_parse(master_result):
            master = master_result[1].split('\t')
            return "ON; File: %s; Position: %s" % (
                master[0], master[1])
        else:
            return "OFF"

    def _slave_status(self, slave_result):
        """Parse the result of SLAVE_QUERY.

        @param master_result: result of SLAVE_QUERY
        @type master_result: string
        @return: str, slave status
        """

        if queries.tab_parse(slave_result):
            slave = dict((line.split(': ')[0].strip(), line.split(': ')[1])
                for line in slave_result if line)
            return "IO running: %s; SQL running: %s; Seconds behind: %s" % (
                slave['Slave_IO_Running'], slave['Slave_SQL_Running'],
                slave['Seconds_Behind_Master'])
        else:
            return "OFF"
