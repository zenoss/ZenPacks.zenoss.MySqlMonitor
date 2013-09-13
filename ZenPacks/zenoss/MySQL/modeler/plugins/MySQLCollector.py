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
from datetime import datetime
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from Products.ZenUtils.Utils import prepId

from ZenPacks.zenoss.MySQL import MODULE_NAME

NAME_SPLITTER = '(.,.)'

table_query = """
    SELECT table_schema, table_name, engine, table_type, table_collation, 
        table_rows, (data_length + index_length) size_mb
    FROM information_schema.TABLES;
"""

db_query = """
    SELECT schema_name, size_mb
    FROM information_schema.schemata LEFT JOIN 
        (SELECT table_schema, (data_length + index_length) size_mb
        FROM information_schema.TABLES 
        GROUP BY table_schema) as sizes
    ON schema_name = sizes.table_schema;
"""

sp_sf_query = """
    SELECT ROUTINE_SCHEMA, ROUTINE_NAME, ROUTINE_TYPE, 
        ROUTINE_BODY, ROUTINE_DEFINITION, EXTERNAL_LANGUAGE, 
        SECURITY_TYPE, CREATED, LAST_ALTERED
    FROM INFORMATION_SCHEMA.ROUTINES;
"""

process_query = """SHOW PROCESSLIST;"""

splitter_query = """
    SELECT "splitter";
"""

def db_parse(result):
    # databases parsing
    db_result = {}
    db_matcher = re.compile(r'^(?P<title>\S*)\t(?P<size_mb>\S*)$')

    for line in result:
        db_match = db_matcher.search(line.strip())

        db_result[db_match.group('title')] = {
            'id': prepId(db_match.group('title')),
            'title': db_match.group('title'),
            'size_mb': db_match.group('size_mb'),
        }

    return db_result

def tb_parse(result):
    tb_result = {}
    tb_matcher = re.compile(r'^(?P<db>.*)\t(?P<title>.*)'
        '\t(?P<engine>.*)\t(?P<table_type>.*)\t(?P<table_collation>.*)'
        '\t(?P<table_rows>\S*)\t(?P<size_mb>.*)')

    for line in result:
        tb_match = tb_matcher.search(line.strip())
        tb_id = prepId(tb_match.group('db')) + \
            NAME_SPLITTER + prepId(tb_match.group('title'))

        tb = {
            'id': tb_id,
            'title': tb_match.group('title'),
            'engine': tb_match.group('engine'),
            'table_type': tb_match.group('table_type'),
            'table_collation': tb_match.group('table_collation'),
            'table_rows': tb_match.group('table_rows'),
            'size_mb': tb_match.group('size_mb'),    
        }

        if tb_match.group('db') in tb_result.keys():
            tb_result[tb_match.group('db')].append(tb)
        else:
            tb_result[tb_match.group('db')] = [tb]

    return tb_result

def routine_parse(result):
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
    process_results = {}
    proc_matcher = re.compile(r'^(?P<proc_id>\S*)\t(?P<user>\S*)\t'
        '(?P<host>.*)\t(?P<db>.*)\t(?P<command>.*)\t(?P<time>.*)\t'
        '(?P<state>.*)\t(?P<info>.*)$')

    for line in result:
        proc_match = proc_matcher.search(line.strip())
        proc_id = prepId(proc_match.group('proc_id'))

        process_results[proc_match.group('proc_id')] = {
            'id': proc_id,
            'title': proc_match.group('proc_id'),
            'user':proc_match.group('user'),
            'host':proc_match.group('host'),
            'db':proc_match.group('db'),
            'command':proc_match.group('command'),
            'time':proc_match.group('time'),
            'state':proc_match.group('state'),
            'process_info':proc_match.group('info'),
        }

    return process_results


class MySQLCollector(CommandPlugin):
    command = """mysql -e '%s %s %s %s %s %s %s'""" % (db_query, 
        splitter_query, table_query, splitter_query,
        sp_sf_query, splitter_query, process_query)

    def condition(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        # results parsing
        query_list = ['db', 'table', 'routine', 'process']
        result = dict((query_list[num], result.split('\n')[1:-1])
            for num, result in enumerate(results.split('splitter\nsplitter\n'))
        )

        db_result = db_parse(result['db'])
        tb_result = tb_parse(result['table'])
        sf_result, sp_result = routine_parse(result['routine'])
        process_result = process_parse(result['process'])

        maps = collections.OrderedDict([
            ('databases', []),
            ('tables', []),
            ('stored_procedures', []),
            ('stored_functions', []),
            ('processes', []),
            ('server', []) # Our Device properties
        ])
        # database properties
        db_oms = []
        for db in db_result:
            db_oms.append(ObjectMap(db_result[db]))

            # table properties
            tb_oms = []
            if db in tb_result.keys():
                for table in tb_result[db]:
                    tb_oms.append(ObjectMap(table))

            # stored procedure properties
            sp_oms = []
            if db in sp_result.keys():
                for procedure in sp_result[db]:
                    sp_oms.append(ObjectMap(procedure))

            # stored function properties
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

        # process properties
        process_oms = []
        for process in process_result:
            process_oms.append(ObjectMap(process_result[process]))

        maps['processes'].append(RelationshipMap(
            relname='processes',
            modname=MODULE_NAME['MySQLProcess'],
            objmaps=process_oms))

        # ---------------------------------------------------------------------
        # Device properties
        maps['server'].append(ObjectMap(data={
            "model_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        }))

        return list(chain.from_iterable(maps.itervalues()))
