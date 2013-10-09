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
from itertools import chain
from MySQLdb import cursors
from twisted.enterprise import adbapi
from twisted.internet.defer import DeferredList

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from ZenPacks.zenoss.MySqlMonitor import MODULE_NAME, NAME_SPLITTER
from ZenPacks.zenoss.MySqlMonitor.modeler import queries

class MySQLCollector(PythonPlugin):

    deviceProperties = PythonPlugin.deviceProperties + (
        'zMySQLConnectionString',
        )

    queries = {
        'server': queries.SERVER_QUERY,
        'server_size': queries.SERVER_SIZE_QUERY,
        'master': queries.MASTER_QUERY,
        'slave': queries.SLAVE_QUERY,
        'db': queries.DB_QUERY
    }

    def collect(self, device, log):
        log.info("Collecting data for device %s", device.id)
        servers = device.zMySQLConnectionString.split(';')

        result = []
        for el in servers:
            if not el:
                break

            try:
                user, passwd, port = el.split(':')
                port = int(port)
            except:
                log.error("Please set zMySQLConnectionString as "
                    "'[username]:[password]:[port];'")
                return 

            dbpool = adbapi.ConnectionPool(
                "MySQLdb",
                user=user,
                port=port,
                passwd=passwd,
                cursorclass=cursors.DictCursor
            )

            d = dbpool.runInteraction(self._getResult, user, port)
            result.append(d)

        return DeferredList(result).addCallback(lambda values: values)

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        maps = collections.OrderedDict([
            ('servers', []),
            ('databases', []),
        ])

        # List of servers
        server_oms = []
        for b, server in results:
            s_om = ObjectMap(server["server_size"][0])
            s_om.id = self.prepId(server["id"])
            s_om.title = server["id"]
            s_om.percent_full_table_scans = self._table_scans(server['server'])
            s_om.master_status = self._master_status(server['master'])
            s_om.slave_status = self._slave_status(server['slave'])
            server_oms.append(s_om)

            # List of databases
            db_oms = []
            for db in server['db']:
                d_om = ObjectMap(db)
                d_om.id = s_om.id + NAME_SPLITTER + self.prepId(db['title'])
                db_oms.append(d_om)

            maps['databases'].append(RelationshipMap(
                compname='mysql_servers/%s' % s_om.id,
                relname='databases',
                modname=MODULE_NAME['MySQLDatabase'],
                objmaps=db_oms))

        maps['servers'].append(RelationshipMap(
            relname='mysql_servers',
            modname=MODULE_NAME['MySQLServer'],
            objmaps=server_oms))

        log.info(
            'Modeler %s finished processing data for device %s',
            self.name(), device.id
        )

        return list(chain.from_iterable(maps.itervalues()))
            

    def _getResult(self, txn, user, port):
        """Is executed in a thread using a pooled connection.

        @param txn: Transaction object
        @type txn: object
        @param user: user name
        @type user: string
        @param port: port
        @type port: string
        @return: Deferred
        """
        
        result = {}
        result["id"] = "%s:%s" % (user, port)
        for key, query in self.queries.iteritems():
            txn.execute(query)
            result[key]=txn.fetchall()

        return result

    def _table_scans(self, server_result):
        """Calculates the percent of full table scans for server.

        @param server_result: result of SERVER_QUERY
        @type server_result: string
        @return: str, rounded value with percent sign
        """

        result = dict((el['variable_name'], el['variable_value']) 
            for el in server_result)

        if int(result['HANDLER_READ_KEY']) == 0:
            return "N/A"

        percent = float(result['HANDLER_READ_FIRST'])/\
            float(result['HANDLER_READ_KEY'])

        return str(round(percent, 3)*100)+'%'

    def _master_status(self, master_result):
        """Parse the result of MASTER_QUERY.

        @param master_result: result of MASTER_QUERY
        @type master_result: string
        @return: str, master status
        """

        if master_result:
            master = master_result[0]
            return "ON; File: %s; Position: %s" % (
                master['File'], master['Position'])
        else:
            return "OFF"

    def _slave_status(self, slave_result):
        """Parse the result of SLAVE_QUERY.

        @param master_result: result of SLAVE_QUERY
        @type master_result: string
        @return: str, slave status
        """

        if slave_result:
            slave = slave_result[0]
            return "IO running: %s; SQL running: %s; Seconds behind: %s" % (
                slave['Slave_IO_Running'], slave['Slave_SQL_Running'],
                slave['Seconds_Behind_Master'])
        else:
            return "OFF"
