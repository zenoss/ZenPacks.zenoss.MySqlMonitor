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
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from Products.ZenUtils.Utils import prepId

from ZenPacks.zenoss.MySQL import MODULE_NAME

NAME_SPLITTER = '.'

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

        maps = collections.OrderedDict([
            ('databases', []),
            ('tables', []),
            ('stored_procedures', []),
            ('stored_functions', []),
            ('processes', []),
            ('server', []) # Our Device properties
        ])

        db_oms = []
        db_matcher = re.compile(r'^(?P<db_name>\S*)\t(?P<size_mb>\S*)$')
        for line in result['db']:
            db_match = db_matcher.search(line.strip())
            db_id = prepId(db_match.group('db_name'))
            if db_match:
                db_oms.append(ObjectMap({
                    'id': db_id,
                    'title': db_match.group('db_name'),
                    'size_mb': db_match.group('size_mb'),
                }))

            tb_oms = []
            tb_matcher = re.compile(r'^(?P<table_schema>\S*)\t(?P<table_name>\S*)'
                '\t(?P<engine>\S*)\t(?P<table_type>.*)\t(?P<table_collation>\S*)'
                '\t(?P<table_rows>\S*)\t(?P<size_mb>\S*)')
            for line in result['table']:
                tb_match = tb_matcher.search(line.strip())
                tb_id = db_id + NAME_SPLITTER + prepId(tb_match.group('table_name'))
                if tb_match and tb_match.group('table_schema') == db_match.group('db_name'):
                    tb_oms.append(ObjectMap({
                        'id': tb_id,
                        'title': tb_match.group('table_name'),
                        'engine': tb_match.group('engine'),
                        'table_type': tb_match.group('table_type'),
                        'table_collation': tb_match.group('table_collation'),
                        'table_rows': tb_match.group('table_rows'),
                        'size_mb': tb_match.group('size_mb'),
                    }))

            sp_oms = []
            sf_oms = []
            routines_matcher = re.compile(r'^(?P<r_schema>\S*)\t(?P<r_name>\S*)\t'
                '(?P<r_type>\S*)\t(?P<r_body>\S*)\t(?P<r_definition>.*)\t'
                '(?P<external_lang>.*)\t(?P<security_type>.*)\t'
                '(?P<created>.*)\t(?P<altered>.*)$')
            for line in result['routine']:
                r_match = routines_matcher.search(line.strip())
                routine_id = db_id + NAME_SPLITTER + prepId(r_match.group('r_name'))
                if r_match and r_match.group('r_schema') == db_match.group('db_name'):
                    list_type = sp_oms if r_match.group('r_type') == "PROCEDURE" else sf_oms
                    list_type.append(ObjectMap({
                        'id': routine_id,
                        'title': r_match.group('r_name'),
                        'body':r_match.group('r_body'),
                        'definition':r_match.group('r_definition'),
                        'external_language':r_match.group('external_lang'),
                        'security_type':r_match.group('security_type'),
                        'created':r_match.group('created'),
                        'last_altered':r_match.group('altered'),
                    }))

            maps['stored_procedures'].append(RelationshipMap(
                compname='databases/%s' % db_id,
                relname='stored_procedures',
                modname=MODULE_NAME['MySQLStoredProcedure'],
                objmaps=sp_oms))

            maps['stored_functions'].append(RelationshipMap(
                compname='databases/%s' % db_id,
                relname='stored_functions',
                modname=MODULE_NAME['MySQLStoredFunction'],
                objmaps=sf_oms))

            maps['tables'].append(RelationshipMap(
                compname='databases/%s' % db_id,
                relname='tables',
                modname=MODULE_NAME['MySQLTable'],
                objmaps=tb_oms))

        maps['databases'].append(RelationshipMap(
            relname='databases',
            modname=MODULE_NAME['MySQLDatabase'],
            objmaps=db_oms))

        process_oms = []
        proc_matcher = re.compile(r'^(?P<proc_id>\S*)\t(?P<user>\S*)\t'
            '(?P<host>.*)\t(?P<db>.*)\t(?P<command>.*)\t(?P<time>.*)\t'
            '(?P<state>.*)\t(?P<info>.*)$')
        for line in result['process']:
            proc_match = proc_matcher.search(line.strip())
            proc_id = prepId(proc_match.group('proc_id'))
            if proc_match:
                process_oms.append(ObjectMap({
                    'id': proc_id,
                    'title': 'process#' + proc_match.group('proc_id'),
                    'process_id':proc_match.group('proc_id'),
                    'user':proc_match.group('user'),
                    'host':proc_match.group('host'),
                    'db':proc_match.group('db'),
                    'command':proc_match.group('command'),
                    'time':proc_match.group('time'),
                    'state':proc_match.group('state'),
                    'process_info':proc_match.group('info'),
                }))

        maps['processes'].append(RelationshipMap(
            relname='processes',
            modname=MODULE_NAME['MySQLProcess'],
            objmaps=process_oms))

        # # ---------------------------------------------------------------------
        # # Device properties
        # maps['server'].append(ObjectMap(data={}))
        # print list(chain.from_iterable(maps.itervalues()))

        return list(chain.from_iterable(maps.itervalues()))
