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
from ZenPacks.zenoss.MySQL import MODULE_NAME, NAME_SPLITTER

class MySQLTableCollector(CommandPlugin):

    command = """mysql -e '{tb} {splitter}'; {tb_status}""".format(
            splitter = queries.SPLITTER_QUERY,
            tb = queries.TB_QUERY,
            tb_status = queries.TB_STATUS_QUERY,
        )

    def condition(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        # Results parsing
        query_list = ('tb', 'tb_status')
        result = dict((query_list[num], result.split('\n'))
            for num, result in enumerate(results.split('splitter\nsplitter\n'))
        )
        # Tables sorting according to db name as a key
        tb_result = self._tb_sort(result['tb'], result['tb_status'])

        maps = collections.OrderedDict([
            ('tables', []),
        ])

       # Table properties
        for db_name in tb_result.keys():
            tb_oms = []
            for table in tb_result[db_name]:
                tb_oms.append(ObjectMap(tb_result[db_name][table]))

            maps['tables'].append(RelationshipMap(
                compname='databases/%s' % prepId(db_name),
                relname='tables',
                modname=MODULE_NAME['MySQLTable'],
                objmaps=tb_oms))

        return list(chain.from_iterable(maps.itervalues()))

    def _tb_sort(self, result, status_result):
        """Sort the result of tb_query.

        @param result: result of tb_query
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

        # TB_STATUS_QUERY parsing
        status_matcher = re.compile(r'^(?P<db>\S*)\.(?P<tb>\S*)\s+'
            '(?P<status>.*)$')
        # Status property adding
        for line in status_result:
            s_match = status_matcher.search(line.strip())
            if s_match:
                table = tb_result[s_match.group('db')][s_match.group('tb')]
                table['table_status'] = s_match.group('status')

        return tb_result
