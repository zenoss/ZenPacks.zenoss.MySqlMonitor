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
import re
from datetime import datetime, timedelta
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId
from ZenPacks.zenoss.MySQL import MODULE_NAME, NAME_SPLITTER


TB_QUERY = """
    SELECT table_schema, table_name, engine, table_type, table_collation, 
        table_rows, (data_length + index_length) size
    FROM information_schema.TABLES;
"""

TB_STATUS_QUERY = """
    mysqlcheck -A;
"""

DB_QUERY = """
    SELECT schema_name, default_character_set_name, default_collation_name, size
    FROM information_schema.schemata LEFT JOIN 
        (SELECT table_schema, (data_length + index_length) size
        FROM information_schema.TABLES 
        GROUP BY table_schema) as sizes
    ON schema_name = sizes.table_schema;
"""

ROUTINE_QUERY = """
    SELECT routine_schema, routine_name, routine_type, 
        routine_body, routine_definition, external_language, 
        security_type, created, last_altered
    FROM information_schema.ROUTINES;
"""

PROCESS_QUERY = """
    SHOW PROCESSLIST;
"""

SERVER_QUERY = """
    SELECT variable_name, variable_value  
    FROM information_schema.SESSION_STATUS  
    WHERE variable_name IN ("Handler_read_first", "Handler_read_key", 
        "Slave_running");
"""

SERVER_SIZE_QUERY = """
    SELECT sum(data_length + index_length) size, 
        sum(data_length) data_length, sum(index_length) index_length 
    FROM information_schema.TABLES;
"""

MASTER_QUERY = """
    SHOW MASTER STATUS;
"""

SLAVE_QUERY = """
    SHOW SLAVE STATUS\G;
"""

SPLITTER_QUERY = """
    SELECT "splitter";
"""


def db_parse(result):
    """Parse the result of DB_QUERY.

    @param result: result of DB_QUERY
    @type result: string
    @return: dict with db name as a key and 
    db properties as a value
    """

    db_result = {}
    db_matcher = re.compile(r'^(?P<title>\S*)\t(?P<character_set>\S*)\t'
        '(?P<collation>\S*)\t(?P<size>\S*)$')

    for line in result:
        db_match = db_matcher.search(line.strip())

        db_result[db_match.group('title')] = {
            'id': prepId(db_match.group('title')),
            'title': db_match.group('title'),
            'size': db_match.group('size'),
            'character_set': db_match.group('character_set'),
            'collation': db_match.group('collation'),
        } 

    return db_result


def tb_parse(result, status_result):
    """Parse the result of TB_QUERY.

    @param result: result of TB_QUERY
    @type result: string
    @return: dict with db name as a key and 
    dict of table properties as a value
    """

    tb_result = {} 
    tb_matcher = re.compile(r'^(?P<db>.*)\t(?P<title>.*)'
        '\t(?P<engine>.*)\t(?P<table_type>.*)\t(?P<table_collation>.*)'
        '\t(?P<table_rows>\S*)\t(?P<size>.*)')

    for line in result:
        tb_match = tb_matcher.search(line.strip())
        tb_id = prepId(tb_match.group('db')) + \
            NAME_SPLITTER + prepId(tb_match.group('title'))

        tb = dict([(tb_match.group('title'), {
            'id': tb_id,
            'title': tb_match.group('title'),
            'engine': tb_match.group('engine'),
            'table_type': tb_match.group('table_type'),
            'table_collation': tb_match.group('table_collation'),
            'table_rows': tb_match.group('table_rows'),
            'size': tb_match.group('size'),
            'table_status': '', 
        })])

        if tb_match.group('db') in tb_result.keys():
            tb_result[tb_match.group('db')].update(tb)
        else:
            tb_result[tb_match.group('db')] = tb

    # TB_STATUS_QUERY parsing
    status_matcher = re.compile(r'^(?P<db>\S*)\.(?P<tb>\S*)\s+(?P<status>.*)')
    # Status property adding
    for line in status_result:
        s_match = status_matcher.search(line.strip())
        if s_match:
            table = tb_result[s_match.group('db')].get(s_match.group('tb'))
            table['table_status'] = s_match.group('status')

    return tb_result


def routine_parse(result):
    """Parse the result of ROUTINE_QUERY.

    @param result: result of ROUTINE_QUERY
    @type result: string
    @return: tuple of two dicts with db name as a key and 
    list of routine properties as a value
    """

    functions_result = {}
    procedures_result = {}
    r_matcher = re.compile(r'^(?P<db>\S*)\t(?P<title>\S*)\t'
        '(?P<r_type>\S*)\t(?P<body>\S*)\t(?P<definition>.*)\t'
        '(?P<external_language>.*)\t(?P<security_type>.*)\t'
        '(?P<created>.*)\t(?P<last_altered>.*)$')

    for line in result:
        r_match = r_matcher.search(line.strip())
        r_id = prepId(r_match.group('db')) + \
            NAME_SPLITTER + prepId(r_match.group('title'))

        routine = {
            'id': r_id,
            'title': r_match.group('title'),
            'body':r_match.group('body'),
            'definition':r_match.group('definition'),
            'external_language':r_match.group('external_language'),
            'security_type':r_match.group('security_type'),
            'created':r_match.group('created'),
            'last_altered':r_match.group('last_altered'),
        }

        r_type = procedures_result \
            if r_match.group('r_type') == "PROCEDURE" \
            else functions_result

        if r_match.group('db') in r_type.keys():
            r_type[r_match.group('db')].append(routine)
        else:
            r_type[r_match.group('db')] = [routine]

    return functions_result, procedures_result


def process_parse(result):
    """Parse the result of PROCESS_QUERY.

    @param result: result of PROCESS_QUERY
    @type result: string
    @return: dict with process ID as a key and 
    process properties as a value
    """

    process_results = {}
    proc_matcher = re.compile(r'^(?P<proc_id>.*)\t(?P<user>.*)\t'
        '(?P<host>.*)\t(?P<db>.*)\t(?P<command>.*)\t(?P<time>.*)\t'
        '(?P<state>.*)\t(?P<info>.*)$')

    for line in result:
        proc_match = proc_matcher.search(line.strip())
        proc_id = prepId(proc_match.group('proc_id'))
        time = timedelta(seconds=int(proc_match.group('time')))

        process_results[proc_match.group('proc_id')] = {
            'id': proc_id,
            'title': proc_match.group('proc_id'),
            'user':proc_match.group('user'),
            'host':proc_match.group('host'),
            'db':proc_match.group('db'),
            'command':proc_match.group('command'),
            'time':str(time),
            'state':proc_match.group('state'),
            'process_info':proc_match.group('info'),
        }

    return process_results

def server_parse(size_result, server_result, master, slave):
    """Parse the result of server queries.

    @param size_result: result of SERVER_SIZE_QUERY
    @type result: string
    @param server_result: result of SERVER_QUERY
    @type result: string
    @param master: result of MASTER_QUERY
    @type result: string
    @param slave: result of SLAVE_QUERY
    @type result: string
    @return: dict with server properties and 
    their values
    """
    # SERVER_SIZE_QUERY parsing
    size, data_size, index_size = size_result[0].split('\t')

    # SERVER_QUERY parsing
    server_result = dict((line.split('\t')[0], line.split('\t')[1])
        for line in server_result)

    percent_full_table_scans = float(server_result['HANDLER_READ_FIRST'])/\
        float(server_result['HANDLER_READ_KEY'])

    # MASTER_QUERY parsing
    master_status = "OFF"
    if master:
        master = master[0].split('\t')
        master_status = "ON; File: %s; Position: %s" % (
            master[0], master[1])

    # SLAVE_QUERY parsing
    slave_status = server_result['SLAVE_RUNNING']
    if slave:
        slave = dict((line.split(': ')[0].strip(), line.split(': ')[1])
        for line in slave)
        slave_status = "IO: %s; SQL: %s; Seconds behind: %s" % (
            slave['Slave_IO_Running'], slave['Slave_SQL_Running'],
            slave['Seconds_Behind_Master']) 

    server_results = {
        "model_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        "size": size,
        "data_size": data_size,
        "index_size": index_size,
        "percent_full_table_scans": str(round(percent_full_table_scans, 3)*100)+'%',
        "master_status": master_status,
        "slave_status": slave_status,
    }

    return server_results


class MySQLCollector(CommandPlugin):
    
    command = """mysql -e '%(db)s  %(splitter)s %(tb)s %(splitter)s \
        %(routine)s %(splitter)s %(process)s %(splitter)s %(server_size)s \
        %(splitter)s %(server)s %(splitter)s %(master)s %(splitter)s \
        %(slave)s %(splitter)s'; %(tb_status)s""" % {
            'db' : DB_QUERY,
            'splitter': SPLITTER_QUERY,
            'tb': TB_QUERY,
            'routine': ROUTINE_QUERY,
            'tb_status': TB_STATUS_QUERY,
            'process': PROCESS_QUERY,
            'server_size': SERVER_SIZE_QUERY,
            'server': SERVER_QUERY,
            'master': MASTER_QUERY,
            'slave': SLAVE_QUERY,
        }

    def condition(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        # Results parsing
        query_list = ('db', 'table', 'routine', 'process', 'server_size', 
            'server', 'master', 'slave', 'tb_status')
        result = dict((query_list[num], result.split('\n')[1:-1])
            for num, result in enumerate(results.split('splitter\nsplitter\n'))
        )

        db_result = db_parse(result['db'])
        tb_result = tb_parse(result['table'], result['tb_status'])
        sf_result, sp_result = routine_parse(result['routine'])
        process_result = process_parse(result['process'])
        server_result = server_parse(result['server_size'], result['server'], 
                                    result['master'], result['slave'])

        maps = collections.OrderedDict([
            ('databases', []),
            ('tables', []),
            ('stored_procedures', []),
            ('stored_functions', []),
            ('processes', []),
            ('server', [])
        ])
        # Database properties
        db_oms = []
        for db in db_result:
            db_oms.append(ObjectMap(db_result[db]))

            # Table properties
            tb_oms = []
            if db in tb_result.keys():
                for table in tb_result[db]:
                    tb_oms.append(ObjectMap(tb_result[db][table]))

            # Stored procedure properties
            sp_oms = []
            if db in sp_result.keys():
                for procedure in sp_result[db]:
                    sp_oms.append(ObjectMap(procedure))

            # Stored function properties
            sf_oms = []
            if db in sf_result.keys():
                for function in sf_result[db]:
                    sf_oms.append(ObjectMap(function))

            maps['stored_procedures'].append(RelationshipMap(
                compname='databases/%s' % prepId(db),
                relname='stored_procedures',
                modname=MODULE_NAME['MySQLStoredProcedure'],
                objmaps=sp_oms))

            maps['stored_functions'].append(RelationshipMap(
                compname='databases/%s' % prepId(db),
                relname='stored_functions',
                modname=MODULE_NAME['MySQLStoredFunction'],
                objmaps=sf_oms))

            maps['tables'].append(RelationshipMap(
                compname='databases/%s' % prepId(db),
                relname='tables',
                modname=MODULE_NAME['MySQLTable'],
                objmaps=tb_oms))

        maps['databases'].append(RelationshipMap(
            relname='databases',
            modname=MODULE_NAME['MySQLDatabase'],
            objmaps=db_oms))

        # Process properties
        process_oms = []
        for process in process_result:
            process_oms.append(ObjectMap(process_result[process]))

        maps['processes'].append(RelationshipMap(
            relname='processes',
            modname=MODULE_NAME['MySQLProcess'],
            objmaps=process_oms))

        # Device properties
        maps['server'].append(ObjectMap(server_result))

        return list(chain.from_iterable(maps.itervalues()))