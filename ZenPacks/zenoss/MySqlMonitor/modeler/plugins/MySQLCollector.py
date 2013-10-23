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
import zope.component
from itertools import chain
from MySQLdb import cursors
from twisted.enterprise import adbapi
from twisted.internet.defer import DeferredList

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenCollector.interfaces import IEventService
from ZenPacks.zenoss.MySqlMonitor import MODULE_NAME, NAME_SPLITTER
from ZenPacks.zenoss.MySqlMonitor.modeler import queries

from ZenPacks.zenoss.MySqlMonitor.utils import parse_mysql_connection_string


class MySQLCollector(PythonPlugin):

    _eventService = zope.component.queryUtility(IEventService)

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
        try:
            servers = parse_mysql_connection_string(
                device.zMySQLConnectionString)
        except ValueError, error:
            log.error(error.message)
            self._send_event(error.message, device.id, 5)
            return

        result = []
        for el in servers.values():
            dbpool = adbapi.ConnectionPool(
                "MySQLdb",
                user=el.get("user"),
                port=el.get("port"),
                passwd=el.get("passwd"),
                cursorclass=cursors.DictCursor
            )

            d = dbpool.runInteraction(
                self._get_result, log, el.get("user"), el.get("port"))
            d.addErrback(self._failure, log, device, el)
            result.append(d)

        return DeferredList(result)

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
        for success, server in results:
            # Twisted error handling
            if not success:
                log.error(server.getErrorMessage())
                continue

            # Connection error: send event in errback
            if not server:
                return

            s_om = ObjectMap(server.get("server_size")[0])
            s_om.id = self.prepId(server["id"])
            s_om.title = server["id"]
            s_om.percent_full_table_scans = self._table_scans(
                server.get('server', ''))
            s_om.master_status = self._master_status(server.get('master', ''))
            s_om.slave_status = self._slave_status(server.get('slave', ''))
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

        self._send_event("Clear", device.id, 0)

        log.info(
            'Modeler %s finished processing data for device %s',
            self.name(), device.id
        )

        return list(chain.from_iterable(maps.itervalues()))

    def _get_result(self, txn, log, user, port):
        """
        Is executed in a thread using a pooled connection.

        @param txn: Transaction object
        @type txn: object
        @param user: user name
        @type user: string
        @param port: port
        @type port: string
        @return: Deferred
        """

        result = {}
        result["id"] = "{0}_{1}".format(user, port)
        for key, query in self.queries.iteritems():
            try:
                txn.execute(query)
                result[key] = txn.fetchall()
            except Exception, e:
                result[key] = ()
                log.error(
                    "Execute query '%s' failed for user '%s': %s",
                    query.strip(), user, e
                )

        return result

    def _failure(self, error, log, device, el):
        """
        Twisted errBack to handle the exception.

        @parameter error: explanation of the failure
        @type error: Twisted error instance
        @parameter log: log object
        @type log: object
        """
        log.error(error.getErrorMessage())

        creds = "%s:***:%s" % (el["user"], el["port"])
        self._send_event(
            "Error modelling MySQL server for %s" % creds,
            device.id,
            5
        )
        return

    def _table_scans(self, server_result):
        """
        Calculates the percent of full table scans for server.

        @param server_result: result of SERVER_QUERY
        @type server_result: string
        @return: str, rounded value with percent sign
        """

        result = dict((el['variable_name'], el['variable_value'])
                      for el in server_result)

        if int(result['HANDLER_READ_KEY']) == 0:
            return "N/A"

        percent = float(result['HANDLER_READ_FIRST']) /\
            float(result['HANDLER_READ_KEY'])

        return str(round(percent, 3)*100)+'%'

    def _master_status(self, master_result):
        """
        Parse the result of MASTER_QUERY.

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
        """
        Parse the result of SLAVE_QUERY.

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

    def _send_event(self, reason, id, severity):
        """
        Send event for device with specified id, severity and
        error message.
        """
        self._eventService.sendEvent(dict(
            summary=reason,
            eventClass='/Status',
            device=id,
            eventKey='ConnectionError',
            severity=severity,
            ))
