##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, 2024, 2025, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

''' Models discovery tree for MySQL. '''

import collections
import re
import zope.component
from itertools import chain
from MySQLdb import cursors
from twisted.enterprise import adbapi
from twisted.internet import defer

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenCollector.interfaces import IEventService
from ZenPacks.zenoss.MySqlMonitor import MODULE_NAME, NAME_SPLITTER
from ZenPacks.zenoss.MySqlMonitor.modeler import queries

from ZenPacks.zenoss.MySqlMonitor.utils import (
    parse_mysql_connection_string, getMySqlSslParam)


class MySQLCollector(PythonPlugin):
    '''
    PythonCollector plugin for modelling device components
    '''
    is_clear_run = True
    device_om = None

    _eventService = zope.component.queryUtility(IEventService)

    deviceProperties = PythonPlugin.deviceProperties + (
        'zMySQLConnectionString',
        'zMySqlSslCaPemFile',
        'zMySqlSslCertPemFile',
        'zMySqlSslKeyPemFile'
        )

    queries = {
        'server': queries.SERVER_QUERY,
        'server_size': queries.SERVER_SIZE_QUERY,
        'source': queries.SOURCE_QUERY,
        'replica': queries.REPLICA_QUERY,
        'db': queries.DB_QUERY,
        'version': queries.VERSION_QUERY
    }

    @defer.inlineCallbacks
    def collect(self, device, log):
        log.info("Collecting data for device %s", device.id)
        self.is_clear_run = True
        self.device_om = None
        try:
            servers = parse_mysql_connection_string(
                device.zMySQLConnectionString)
        except ValueError, error:
            self.is_clear_run = False
            log.error(error.message)
            self._send_event(error.message, device.id, 5)
            defer.returnValue('Error')
            return

        result = []
        for el in servers.values():
            user = el.get("user")
            port = el.get("port")
            dbConnArgs = {
                'host': device.manageIp,
                'user': user,
                'port': port,
                'passwd': el.get("passwd"),
                'cursorclass': cursors.DictCursor,
            }
            sslArgs = getMySqlSslParam(
                device.zMySqlSslCaPemFile,
                device.zMySqlSslCertPemFile,
                device.zMySqlSslKeyPemFile
            )
            if sslArgs:
                dbConnArgs['ssl'] = sslArgs

            dbpool = adbapi.ConnectionPool(
                "MySQLdb",
                **dbConnArgs
            )

            res = {}
            res["id"] = "{0}_{1}".format(user, port)

            # Perform the simple SQL queries
            yield self._doSimpleQueries(dbpool, res, user, port, device.id, log)
            if self.is_clear_run is False:
                dbpool.close()
                defer.returnValue('Error')
                return
            log.info("_doSimpleQueries results - {}".format(res))
            log.info("_doSimpleQueries results ver - {}".format(res['version']))
            # Perform the more complex or special SQL queries
            yield self._doComplexQuery(dbpool, res, user, port, device.id, log)
            if self.is_clear_run is False:
                dbpool.close()
                defer.returnValue('Error')
                return

            dbpool.close()
            result.append(res)

        defer.returnValue(result)

    @defer.inlineCallbacks
    def _doSimpleQueries(self, dbpool, res, user, port, device_id, log):
        for key, query in self.queries.iteritems():
            # non str type queries identify them as complex ones 
            if not isinstance(query, str):
                continue
            try:
                res[key] = yield dbpool.runQuery(query)
            except Exception as ex:
                self.is_clear_run = False
                res[key] = ()
                msg, severity = self._error(
                    str(ex), user, port)
                log.error(msg)
                if severity == 5:
                    self._send_event(msg, device_id, severity)

    @defer.inlineCallbacks
    def _doComplexQuery(self, dbpool, res, user, port, device_id, log):
        # Get version info once
        is_mariadb, version_tuple = self._get_version_info(res.get('version'))
        if is_mariadb:
            log.info("Detected MariaDB database")

        for key, query in self.queries.iteritems():
            if not isinstance(query, str):
                if version_tuple is None:
                    # No version info, use first query as default
                    query = self.queries[key][0]
                elif is_mariadb and key == 'source':
                    # MariaDB source query: >= 10.5.2 uses BINLOG STATUS, < 10.5.2 uses MASTER STATUS
                    query_tuple = queries.SOURCE_QUERY_MARIADB
                    query = query_tuple[1] if version_tuple >= (10, 5, 2) else query_tuple[0]
                elif is_mariadb:
                    # Other MariaDB queries: use first query
                    query = self.queries[key][0]
                else:
                    # MySQL: >= 8.4.0 uses second query, < 8.4.0 uses first query
                    query = self.queries[key][1] if version_tuple >= (8, 4, 0) else self.queries[key][0]

                try:
                    res[key] = yield dbpool.runQuery(query)
                except Exception as ex:
                    self.is_clear_run = False
                    res[key] = ()
                    msg, severity = self._error(
                        str(ex), user, port)
                    log.error(msg)
                    if severity == 5:
                        self._send_event(msg, device_id, severity)

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        # 4.2.3 event sending
        if self.device_om:
            return self.device_om

        # 4.2.4 workaround
        if results == 'Error':
            return

        maps = collections.OrderedDict([
            ('servers', []),
            ('databases', []),
            ('device', []),
        ])

        # List of servers
        server_oms = []
        for server in results:
            s_om = ObjectMap(server.get("server_size")[0])
            s_om.id = self.prepId(server["id"])
            s_om.title = server["id"]
            s_om.percent_full_table_scans = self._table_scans(
                server.get('server', ''))
            s_om.source_status = self._source_status(server.get('source', ''))
            s_om.replica_status = self._replica_status(server.get('replica', ''), log)
            s_om.version = self._version(server.get('version', ''))
            server_oms.append(s_om)

            # List of databases
            db_oms = []
            for db in server['db']:
                db = {k.lower(): v for k, v in db.items()}
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
        if self.is_clear_run:
            self._send_event("clear", device.id, 0, True)
            if self.device_om:
                maps['device'] = [self.device_om]

        return list(chain.from_iterable(maps.itervalues()))

    def _error(self, error, user, port):
        """
        Create an error messsage for event.

        @param error: mysql error
        @type error: string
        @param user: user
        @type user: string
        @param port: port
        @type port: string
        @return: message and severity for event
        @rtype: str, int
        """

        if "privilege" in error:
            msg = ("The user '%s' needs (at least one of) the SUPER, "
                   "REPLICATION CLIENT privilege(s) to retrieve MySQL "
                   "Replication data" % user)
            severity = 4
        elif "Access denied" in error:
            msg = "Access denied for user '%s:***:%s'" % (user, port)
            severity = 5
        elif "Can't connect" in error:
            msg = ("Can't connect to MySQL server. Check permissions for "
                "remote connections for %s:***:%s" % (user, port))
            severity = 5
        else:
            msg = ("Error modeling MySQL server for %s:***:%s; "
                "MySQL Error: %s" % (user, port, error))
            severity = 5

        return msg, severity

    def _get_version_info(self, version_result):
        """
        Extract version information from VERSION_QUERY result.

        @param version_result: result of VERSION_QUERY
        @type version_result: list
        @return: tuple of (is_mariadb, version_tuple) where version_tuple is (major, minor, patch) or None
        @rtype: tuple
        """
        if not version_result:
            return (False, None)

        result = dict((el['Variable_name'], el['Value'])
                      for el in version_result)
        version_comment = result.get('version_comment', '').lower()
        is_mariadb = 'mariadb' in version_comment

        version_str = result.get('version', '')
        numVer = re.match('(\d+)\.(\d+)\.(\d+)', version_str)
        if numVer:
            version_tuple = tuple(int(x) for x in numVer.groups())
        else:
            version_tuple = None

        return (is_mariadb, version_tuple)

    def _version(self, version_result):
        """
        Return the version of MySQL server.

        @param version_result: result of VERSION_QUERY
        @type version_result: string
        @return: the server version with machine version
        @rtype: str
        """
        result = dict((el['Variable_name'], el['Value'])
                      for el in version_result)

        return "{0} {1} ({2})".format(
            result['version'],
            result['version_comment'],
            result['version_compile_machine']
        )

    def _table_scans(self, server_result):
        """
        Calculate the percent of full table scans for server.

        @param server_result: result of SERVER_QUERY
        @type server_result: string
        @return: rounded value with percent sign
        @rtype: str
        """

        r = dict((el['Variable_name'], el['Value'])
                 for el in server_result)

        if int(r['Handler_read_key']) == 0:
            return "N/A"

        # percent = float(result['Handler_read_first']) /\
        #    float(result['Handler_read_key'])
        # 1 - (handler_read_rnd_next + handler_read_rnd) /
        # (handler_read_rnd_next + handler_read_rnd + handler_read_first +
        # handler_read_next + handler_read_key + handler_read_prev )
        percent = 1 - (
            float(r['Handler_read_rnd_next']) +
            float(r['Handler_read_rnd'])) / (
            float(r['Handler_read_rnd_next']) + float(r['Handler_read_rnd']) +
            float(r['Handler_read_first']) + float(r['Handler_read_next']) +
            float(r['Handler_read_key']) + float(r['Handler_read_prev'])
        )

        return str(round(percent, 3)*100)+'%'

    def _source_status(self, source_result):
        """
        Parse the result of SOURCE_QUERY.

        @param source_result: result of SOURCE_QUERY
        @type source_result: string
        @return: source status
        @rtype: str
        """

        if source_result:
            source = source_result[0]
            return "ON; File: %s; Position: %s" % (
                source['File'], source['Position'])
        else:
            return "OFF"

    def _replica_status(self, replica_result, log):
        """
        Parse the result of REPLICA_QUERY.

        @param source_result: result of REPLICA_QUERY
        @type source_result: string
        @return: repica status
        @rtype: str
        """

        if replica_result:
            replica = replica_result[0]
            if 'Slave_IO_Running' in replica:
                return "IO running: %s; SQL running: %s; Seconds behind: %s" % (
                    replica['Slave_IO_Running'], replica['Slave_SQL_Running'],
                    replica['Seconds_Behind_Master'])
            elif 'Replica_IO_Running' in replica:
                return "IO running: %s; SQL running: %s; Seconds behind: %s" % (
                    replica['Replica_IO_Running'], replica['Replica_SQL_Running'],
                    replica['Seconds_Behind_Source'])
            else:
                log.error('Could not determine Replica info')
                return "UNKNOWN"
        else:
            return "OFF"

    def _send_event(self, reason, id, severity, force=False):
        """
        Send event for device with specified id, severity and
        error message.
        """

        if self._eventService:
            self._eventService.sendEvent(dict(
                summary=reason,
                eventClass='/Status',
                device=id,
                eventKey='ConnectionError',
                severity=severity,
                ))
            return True
        else:
            if force or (severity > 0):
                self.device_om = ObjectMap({
                    'setErrorNotification': reason
                })
