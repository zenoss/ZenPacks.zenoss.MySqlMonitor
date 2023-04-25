######################################################################
#
# Copyright (C) Zenoss, Inc. 2013-2023, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is
# installed.
#
######################################################################

from logging import getLogger
log = getLogger('zen.python')

import re
import time
import MySQLdb
import MySQLdb.cursors as cursors

from twisted.internet import threads

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin
from Products.ZenEvents import ZenEventClasses
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId
#from ZenPacks.zenoss.PythonCollector import patches

from ZenPacks.zenoss.MySqlMonitor.utils import (
    parse_mysql_connection_string, adbapi_safe)
from ZenPacks.zenoss.MySqlMonitor import NAME_SPLITTER, MODULE_NAME


def connection_cursor(ds, ip, cursor_type=None):
    """Returns connection cursor for MySql server.

    :param ds: MySqlMonitor datasource
    :type ds: datasource
    :param ip: server ip address (device ip address)
    :type ip: str
    :param cursor_type: MySQLdb cursor type, defaults to None
    :type cursor_type: cursor

    :raises Exception: raises Exception if MySql connection string not configured

    :rtype: cursor
    :return: cursor on which queries may be performed.
    """
    if not ds.zMySQLConnectionString:
        raise Exception('MySQL Connection String not configured')

    servers = parse_mysql_connection_string(ds.zMySQLConnectionString)
    server_id = ds.component.split(NAME_SPLITTER)[0]
    server = servers.get(server_id)
    if not server:
        raise Exception(
            'MySQL Connection String not configured for {}'.format(server_id)
        )

    db = MySQLdb.connect(
        host=ip,
        user=server['user'],
        port=server['port'],
        passwd=server['passwd'],
        connect_timeout=getattr(ds, 'zMySqlTimeout', 30)
    )
    db.ping(True)
    return db.cursor(cursorclass=cursor_type)


class MysqlBasePlugin(PythonDataSourcePlugin):
    """
    Base plugin for MySQL monitoring tasks.
    """

    proxy_attributes = (
        'zMySQLConnectionString',
        'zMySqlTimeout',
        'table_count'
    )

    def __init__(self):
        # Form keyName from the class name without the trailing "Plugin"
        # self.keyName is used in eventKey and eventClassKey
        self.keyName = re.sub('Plugin$', '', self.__class__.__name__)

    # base_event is designed to facilitate event creation across classes.
    def base_event(self,
                   severity,
                   summary,
                   component=None,
                   eventKey=None,
                   eventClassKey=None,
                   eventClass=None):
        """Returns event during MySQL components monitoring.

        :param severity: severity for generated event
        :type severity: int
        :param summary: summary for generated event
        :type summary: str
        :param component: component id, defaults to None
        :type component: str
        :param eventKey: eventKey for generated event, defaults to None
        :type eventKey: str
        :param eventClassKey: eventClassKey for generated event, defaults to None
        :type eventClassKey: str
        :param eventClass: eventClass for generated event, defaults to None
        :type eventClass: str

        :rtype: dict
        :return: dictionary that represents event for MySql monitored component
        """

        if not eventKey: eventKey = self.keyName
        if not eventClassKey: eventClassKey = self.keyName

        return {
            'severity': severity,
            'summary': summary,
            'component': component,
            'eventKey': eventKey,
            'eventClassKey': eventClassKey,
            'eventClass': eventClass
        }

    def get_query(self, component):
        """Returns query for MySQL ZP datasource plugin.

        :param component: MySqlMonitor component id
        :type component: str

        :raises NotImplemented: raises NotImplemented error if not implemented in inherited classes

        :rtype: str
        :return: query for MySQL ZP datasource plugin
        """
        raise NotImplemented

    def query_results_to_values(self, results):
        """Returns parsed query results to values for MySqlMonitor components monitoring.

        :param results: raw data structure with monitoring values
        :type results: tuple

        :rtype: dict
        :return: dictionary of monitoring values for component
        """
        return {}

    def query_results_to_events(self, results, ds):
        """Returns parsed query results to events for MySqlMonitor components monitoring.

        :param results: raw data structure with monitoring values
        :type results: tuple
        :param ds: MySqlMonitor datasource
        :type ds: datasource

        :rtype: list
        :return: list of generated events
        """
        return []

    def query_results_to_maps(self, results, component):
        """Returns parsed query results to object maps for MySqlMonitor components monitoring.

        :param results: raw data structure with monitoring values
        :type results: tuple
        :param component: MySqlMonitor component id
        :type component: str

        :rtype: list
        :return: list of collected object maps
        """
        return []

    def inner(self, config):
        """Returns filled with events, values and maps data structure."""
        # Data structure with empty events, values and maps.
        data = self.new_data()

        # The query execution result.
        res = None
        curs = None

        for ds in config.datasources:
            try:
                curs = connection_cursor(ds, config.manageIp)
                curs.execute(self.get_query(ds.component))
                res = curs.fetchall()
                curs.close()
                if res:
                    data['values'][ds.component] = (
                        self.query_results_to_values(res))
                    data['events'].extend(
                        self.query_results_to_events(res, ds))
                    data['maps'].extend(
                        self.query_results_to_maps(res, ds.component))
            except Exception as e:
                # Make sure the event is sent only for MySQLServer
                # component, but not for all databases.
                if ds.component and NAME_SPLITTER in ds.component:
                    continue
                message = str(e)

                if ('MySQL server has gone away' in message or
                        "Can't connect to MySQL server" in message):
                    message = "Can't connect to MySQL server or timeout error in {}.".format(self.__class__.__name__)

                event = self.base_event(ds.severity, message, ds.component, eventClass=ds.eventClass)
                data['events'].append(event)

        return data

    def collect(self, config):
        return threads.deferToThread(lambda: self.inner(config))

    def onSuccess(self, result, config):
        for ds in config.datasources:
            # Clear events for success components.
            event = self.base_event(ZenEventClasses.Clear,
                                    'Monitoring ok',
                                    ds.component,
                                    eventClass=ds.eventClass)
            result['events'].insert(0, event)
        return result

    def onError(self, result, config):
        log.error(result)
        ds0 = config.datasources[0]
        data = self.new_data()
        summary = 'error: {}'.format(result)
        event = self.base_event(ds0.severity, summary, eventClass=ds0.eventClass)
        data['events'].append(event)
        return data


class MySqlMonitorPlugin(MysqlBasePlugin):
    def get_query(self, component):
        return 'show global status'

    def query_results_to_values(self, results):
        return dict((k.lower(), (v, 'N')) for k, v in results)


class MySqlDeadlockPlugin(MysqlBasePlugin):
    proxy_attributes = MysqlBasePlugin.proxy_attributes + ('deadlock_info',)

    deadlock_time = None
    deadlock_db = None
    deadlock_evt_clear_time = None

    deadlock_re = re.compile(
        '\n-+\n(LATEST DETECTED DEADLOCK\n-+\n.*?\n)-+\n',
        re.M | re.DOTALL
    )

    def _event(self, severity, summary, component, eventClass):
        event_key = self.keyName + '_innodb'
        return self.base_event(severity, summary, component, eventKey=event_key, eventClass=eventClass)

    def get_query(self, component):
        return 'show engine innodb status'

    def query_results_to_events(self, results, ds):
        events = []

        # MySQL 5.0 only has a single text block, not three columns
        if results[0][0] != 'InnoDB':
            text = results[0][0]
        else:
            text = results[0][2]

        deadlock_match = self.deadlock_re.search(text)
        component = ds.component

        # Clear a previous deadlock event after 30 mins.
        # Might be changed to another X minutes.
        if ds.deadlock_info and len(ds.deadlock_info) == 3:
            dl_time, dl_db, evt_clear_time = ds.deadlock_info

            if evt_clear_time and time.time() > evt_clear_time:
                events.append(self._event(ZenEventClasses.Clear, 'Ok', dl_db, ds.eventClass))
        else:
            dl_time = dl_db = evt_clear_time = None

        # Parse and process innodb status output.
        if deadlock_match:
            summary = deadlock_match.group(1)
            # Parse LATEST DETECTED DEADLOCK and find time identifier
            dtime = re.match(r'.+DEADLOCK\n-+\n(.+?)\n\*\*\*\s\(1\)\sTRANSACTION', summary)
            # Parse LATEST DETECTED DEADLOCK and find database name
            database = re.search(r"of table `(.+?)`\.", summary)
            if database:
                component = ds.component + NAME_SPLITTER + database.group(1)

            if dtime:
                self.deadlock_time = dtime.group(1)

                # Create event only for new deadlock
                if dl_time != self.deadlock_time:
                    events = []
                    self.deadlock_db = component
                    # Set clear event after 30 mins.
                    self.deadlock_evt_clear_time = time.time() + 60*30
                    # Clear a previous event
                    events.append(self._event(
                        ZenEventClasses.Clear, 'Ok', dl_db, ds.eventClass))
                    # Create a new event
                    events.append(self._event(
                        ZenEventClasses.Info, summary, component, ds.eventClass))

        return events

    def query_results_to_maps(self, results, component):
        if not self.deadlock_evt_clear_time:
            return []

        return [ObjectMap({
            "id": component,
            "modname": MODULE_NAME['MySQLServer'],
            "relname": 'mysql_servers',
            "deadlock_info": (self.deadlock_time, self.deadlock_db,
                              self.deadlock_evt_clear_time),
            '_add': False
        })]


class MySqlReplicationPlugin(MysqlBasePlugin):
    def get_query(self, component):
        return 'show slave status'

    def _event(self, severity, summary,  component, eventClass, suffix):
        eventKey = self.keyName + '_' + suffix
        return self.base_event(severity, summary, component, eventKey=eventKey, eventClass=eventClass)

    def query_results_to_events(self, results, ds):
        if not results:
            # Not a slave MySQL
            return []

        # Slave_IO_Running: Yes
        # Slave_SQL_Running: Yes
        slave_io = results[0][10]
        slave_sql = results[0][11]
        # Last_Errno: 0
        # Last_Error:
        # last_err_no = results[0][18]
        last_err_str = results[0][19]

        # For MySQL 5.0:
        if (len(results[0]) < 34):
            last_io_err_no = 0
            last_io_err_str = ''
            last_sql_err_no = 0
            last_sql_err_str = ''
        else:
            # Last_IO_Errno: 0
            # Last_IO_Error:
            last_io_err_no = results[0][34]
            last_io_err_str = results[0][35]
            # Last_SQL_Errno: 0
            # Last_SQL_Error:
            last_sql_err_no = results[0][36]
            last_sql_err_str = results[0][37]

        c = ds.component
        eventClass = ds.eventClass
        events = []

        if slave_io == "Yes":
            events.append(self._event(0, "Slave IO Running", c, eventClass, "io"))
        else:
            events.append(self._event(4, "Slave IO NOT Running", c, eventClass, "io"))

        if slave_sql == "Yes":
            events.append(self._event(0, "Slave SQL Running", c, eventClass, "sql"))
        else:
            events.append(self._event(4, "Slave SQL NOT Running", c, eventClass, "sql"))

        if last_err_str:
            events.append(self._event(4, last_err_str, c, eventClass, "err"))
        else:
            events.append(self._event(0, "No replication error", c, eventClass, "err"))

        if last_io_err_str:
            events.append(self._event(4, last_io_err_str, c, eventClass, "ioe"))
        else:
            events.append(self._event(0, "No replication IO error", c, eventClass, "ioe"))

        if last_sql_err_str:
            events.append(self._event(4, last_sql_err_str, c, eventClass, "se"))
        else:
            events.append(self._event(0, "No replication SQL error", c, eventClass, "se"))

        return events


class MySQLMonitorServersPlugin(MysqlBasePlugin):
    def get_query(self, component):
        return '''
        SELECT
            count(table_name) table_count,
            sum(data_length + index_length) size,
            sum(data_length) data_size,
            sum(index_length) index_size
        FROM
            information_schema.TABLES
        '''

    def query_results_to_values(self, results):
        fields = enumerate(('table_count', 'size', 'data_size', 'index_size'))
        return dict((f, (results[0][i] or 0)) for i, f in fields)


class MySQLMonitorDatabasesPlugin(MysqlBasePlugin):
    last_table_count_value = {}

    def get_query(self, component):
        return '''
        SELECT
            count(table_name) table_count,
            sum(data_length + index_length) size,
            sum(data_length) data_size,
            sum(index_length) index_size
        FROM
            information_schema.TABLES
        WHERE
            table_schema = "%s"
        ''' % adbapi_safe(component.split(NAME_SPLITTER)[-1])

    def query_results_to_values(self, results):
        fields = enumerate(('table_count', 'size', 'data_size', 'index_size'))
        return dict((f, (results[0][i] or 0)) for i, f in fields)

    def query_results_to_events(self, results, ds):
        if ds.device not in self.last_table_count_value.keys():
            self.last_table_count_value[ds.device] = {}
        if ds.component not in self.last_table_count_value.get(ds.device, {}).keys():
            self.last_table_count_value[ds.device][ds.component] = results[0][0]
            return []
        diff = results[0][0] - self.last_table_count_value.get(ds.device, {}).get(ds.component)
        self.last_table_count_value[ds.device][ds.component] = results[0][0]

        if diff == 0:
            return []

        grammar = 'table was' if abs(diff) == 1 else 'tables were'
        key, severity = ('added', 2) if diff > 0 else ('dropped', 3)
        summary = '{0} {1} {2}.'.format(abs(diff), grammar, key)

        eventKey = 'table_count{}'.format(str(time.time()))
        component = ds.component.split(NAME_SPLITTER)[-1]
        event = self.base_event(severity, summary, component, eventKey=eventKey, eventClass=ds.eventClass)

        return [event]


class MySQLDatabaseIncrementalModelingPlugin(MysqlBasePlugin):
    """
    An Incremental Modeling datasource plugin for MySQL databases
    """

    db_configs_by_server = {}

    @classmethod
    def config_key(cls, datasource, context):
        """
        Return a tuple defining collection uniqueness.
        """
        return (
            context.device().id,
            datasource.getCycleTime(context),
            datasource.rrdTemplate().id,
            datasource.id,
            datasource.plugin_classname,
            context.id,
        )

    def produce_event(self, db, eventClass, state):
        """Returns event after MySQL database addition or deletion.

        :param db: MySQL database ID
        :type db: str
        :param ds0: DbIncrementalModeling Datasource
        :type ds0: datasource
        :param state: key word that indicates whether database was added or deleted
        :type state: str


        :rtype: dict
        :return: event dict with all filled event fields
        """
        db_name = db.split(NAME_SPLITTER)[-1]
        summary = 'Database "{}" was {}.'.format(db_name, state)
        eventKey = self.keyName + '_{}_{}'.format(db_name, state)
        component = db.split(NAME_SPLITTER)[0]
        event = self.base_event(ZenEventClasses.Info,
                                summary,
                                component=component,
                                eventKey=eventKey,
                                eventClass=eventClass)

        return event

    def get_query(self, component):
        return """
        SELECT schema_name title,
               default_character_set_name,
               default_collation_name
        FROM information_schema.schemata;
        """

    def inner(self, config):
        # Data structure with empty events, values and maps.
        data = self.new_data()
        ds0 = config.datasources[0]
        ds0.id = ds0.device
        results = []
        for ds in config.datasources:
            res = {"id": ds.component}
            try:
                cursor = connection_cursor(ds, config.manageIp, cursor_type=cursors.DictCursor)
                cursor.execute(self.get_query(ds.component))
                res['db'] = cursor.fetchall()
                cursor.close()
            except Exception as e:
                message = str(e)
                if ('MySQL server has gone away' in message or
                        "Can't connect to MySQL server" in message):
                    message = "Can't connect to MySQL server or timeout error in {}.".format(self.__class__.__name__)
                event = self.base_event(ds.severity, message, ds.component)
                data['events'].append(event)
                return data
            results.append(res)
        maps = self.get_db_rel_map(results)
        # get old configuration from previous run
        db_config_key = ds0.id + NAME_SPLITTER + ds0.component
        old_db_config = self.db_configs_by_server.get(db_config_key) or []
        new_db_config = self.create_db_config(maps)
        if old_db_config != new_db_config:
            config_diff = list(set(old_db_config) ^ set(new_db_config))
            for db in config_diff:
                if db_config_key in self.db_configs_by_server.keys():
                    if db in new_db_config:
                        data['events'].append(self.produce_event(db, ds0.eventClass, 'added'))
                    else:
                        data['events'].append(self.produce_event(db, ds0.eventClass, 'dropped'))
            log.info('DB configuration has changed, sending new datamaps.')
            log.debug('Difference between DB configs %s', config_diff)
            data['maps'] = maps
        self.db_configs_by_server[db_config_key] = new_db_config
        return data

    @staticmethod
    def create_db_config(rel_maps):
        """Returns a list of collected during monitoring MySql database ids.

        :param rel_maps: list of MySqlDatabase Relationship Maps
        :type rel_maps: list

        :rtype: list
        :return: list of database ids
        """
        config = []
        for rel_map in rel_maps:
            for obj in getattr(rel_map, 'maps', []):
                config.append(obj.id)
        return sorted(config)

    @staticmethod
    def get_db_rel_map(parsed_query_results):
        """Returns a list of Relationship Maps for collected MySql database components

        :param parsed_query_results: list of MySql Servers data
        :type parsed_query_results: list

        :rtype: list
        :return: list of MySql Databases Relationship Maps
        """
        maps = []
        for server in parsed_query_results:
            # List of databases
            db_oms = []
            for db in server['db']:
                db_om = ObjectMap(db)
                db_om.id = prepId(server['id']) + NAME_SPLITTER + prepId(db['title'])
                db_oms.append(db_om)
            maps.append(RelationshipMap(
                compname='mysql_servers/%s' % server['id'],
                relname='databases',
                modname=MODULE_NAME['MySQLDatabase'],
                objmaps=db_oms))
        return maps
