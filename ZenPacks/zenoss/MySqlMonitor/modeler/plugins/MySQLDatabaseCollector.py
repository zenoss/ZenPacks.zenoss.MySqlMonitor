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
import re
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId
from ZenPacks.zenoss.MySqlMonitor import MODULE_NAME, NAME_SPLITTER

class MySQLDatabaseCollector(CommandPlugin):

    command = """mysql -e '{db} {splitter} {tb} {splitter} {routine} {splitter}'; \
        {tb_status}""".format(
            db = queries.DB_QUERY,
            splitter = queries.SPLITTER_QUERY,
            tb = queries.TB_QUERY,
            tb_status = queries.TB_STATUS_QUERY,
            routine = queries.ROUTINE_QUERY,
        )

    def condition(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        # Results parsing
        query_list = ('db', 'tb', 'routine', 'tb_status')
        result = dict((query_list[num], result.split('\n'))
            for num, result in enumerate(results.split('splitter\nsplitter\n'))
        )
        # Tables sorting according to db name as a key
        tb_result = self._tb_sort(result['tb'])
        tb_result = self._tb_status(tb_result, result['tb_status'])
        sf_result, sp_result = self._routine_sort(result['routine'])

        maps = collections.OrderedDict([
            ('databases', []),
            ('tables', []),
            ('stored_procedures', []),
            ('stored_functions', []),
        ])

       # Database properties
        db_oms = []
        for db in queries.tab_parse(result["db"]).values():
            db_name = db['schema_name']
            db_oms.append(ObjectMap({
                'id': prepId(db['schema_name']),
                'title': db['schema_name'],
                'size': db['size'],
                'data_size': db['data_length'],
                'index_size': db['index_length'],
                'default_character_set': db['default_character_set_name'],
                'default_collation': db['default_collation_name'],
            }))

            # Table properties
            tb_oms = []
            if db_name in tb_result.keys():
                for table in tb_result[db_name]:
                    tb_oms.append(ObjectMap(tb_result[db_name][table]))

                maps['tables'].append(RelationshipMap(
                    compname='databases/%s' % prepId(db_name),
                    relname='tables',
                    modname=MODULE_NAME['MySQLTable'],
                    objmaps=tb_oms))

            # Stored procedure properties
            sp_oms = []
            if db_name in sp_result.keys():
                for procedure in sp_result[db_name]:
                    sp_oms.append(ObjectMap(procedure))

                maps['stored_procedures'].append(RelationshipMap(
                    compname='databases/%s' % prepId(db_name),
                    relname='stored_procedures',
                    modname=MODULE_NAME['MySQLStoredProcedure'],
                    objmaps=sp_oms))

            # Stored function properties
            sf_oms = []
            if db_name in sf_result.keys():
                for function in sf_result[db_name]:
                    sf_oms.append(ObjectMap(function))

                maps['stored_functions'].append(RelationshipMap(
                    compname='databases/%s' % prepId(db_name),
                    relname='stored_functions',
                    modname=MODULE_NAME['MySQLStoredFunction'],
                    objmaps=sf_oms))

        maps['databases'].append(RelationshipMap(
            relname='databases',
            modname=MODULE_NAME['MySQLDatabase'],
            objmaps=db_oms))

        return list(chain.from_iterable(maps.itervalues()))

    def _tb_sort(self, result):
        """Sort the result of TB_QUERY.

        @param result: result of TB_QUERY
        @type result: string
        @return: dict with db name as a key and
        dict of table properties as a value
        """

        tb_result = {}

        result = queries.tab_parse(result)
        for props in result.values():
            tb_id = prepId(props['table_schema']) + \
                NAME_SPLITTER + prepId(props['table_name'])

            tb_props = dict([(props['table_name'], {
                'id': tb_id,
                'title': props['table_name'],
                'engine': props['engine'],
                'table_type': props['table_type'],
                'table_collation': props['table_collation'],
                'table_rows': props['table_rows'],
                'size_mb': props['size'],
                'data_size': props['data_length'],
                'index_size': props['index_length'],
                'table_status': '',
            })])

            if props['table_schema'] in tb_result.keys():
                tb_result[props['table_schema']].update(tb_props)
            else:
                tb_result[props['table_schema']] = tb_props

        return tb_result

    def _tb_status(self, tb_result, status_result):
        """Parse the result of TB_STATUS_QUERY and add status
        property to tables.

        @param tb_result: sorted tables
        @type tb_result: dict
        @param status_result: result of TB_STATUS_QUERY
        @type status_result: string
        @return: dict with db name as a key and
        dict of table properties with statuses as a value
        """

        status_matcher = re.compile(r'^(?P<db>\S*)\.(?P<tb>\S*)\s+'
            '(?P<status>.*)$')
        # Status property adding
        for line in status_result:
            s_match = status_matcher.search(line.strip())
            if s_match:
                table = tb_result[s_match.group('db')][s_match.group('tb')]
                table['table_status'] = s_match.group('status')

        return tb_result

    def _routine_sort(self, result):
        """Sort the result of ROUTINE_QUERY.

        @param result: result of ROUTINE_QUERY
        @type result: string
        @return: tuple of two dicts with db name as a key and
        list of routine properties as a value
        """

        functions_result = {}
        procedures_result = {}

        result = queries.tab_parse(result)
        for routine in result.values():
            db = routine['routine_schema']
            r_id = prepId(db) + NAME_SPLITTER + prepId(routine['routine_name'])

            routine_props = {
                'id': r_id,
                'title': routine['routine_name'],
                'body': routine['routine_body'],
                'definition': routine['routine_definition'],
                'external_language': routine['external_language'],
                'security_type': routine['security_type'],
                'created': routine['created'],
                'last_altered': routine['last_altered'],
            }

            r_type = procedures_result \
                if routine['routine_type'] == "PROCEDURE" \
                else functions_result

            if db in r_type.keys():
                r_type[db].append(routine_props)
            else:
                r_type[db] = [routine_props]

        return functions_result, procedures_result
