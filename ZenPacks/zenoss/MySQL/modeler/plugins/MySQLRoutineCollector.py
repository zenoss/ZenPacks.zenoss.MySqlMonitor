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
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap
from Products.ZenUtils.Utils import prepId
from ZenPacks.zenoss.MySQL import MODULE_NAME, NAME_SPLITTER

class MySQLRoutineCollector(CommandPlugin):

    command = """mysql -e '{routine}'""".format(
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
        sf_result, sp_result = self._routine_sort(results.splitlines())

        maps = collections.OrderedDict([
            ('stored_procedures', []),
            ('stored_functions', []),
        ])

        # Stored procedure properties
        for db in sp_result.keys():
            sp_oms = []
            for procedure in sp_result[db]:
                sp_oms.append(ObjectMap(procedure))

            maps['stored_procedures'].append(RelationshipMap(
                compname='databases/%s' % prepId(db),
                relname='stored_procedures',
                modname=MODULE_NAME['MySQLStoredProcedure'],
                objmaps=sp_oms))

        # Stored function properties
        for db in sf_result.keys():
            sf_oms = []
            for function in sf_result[db]:
                sf_oms.append(ObjectMap(function))

            maps['stored_functions'].append(RelationshipMap(
                compname='databases/%s' % prepId(db),
                relname='stored_functions',
                modname=MODULE_NAME['MySQLStoredFunction'],
                objmaps=sf_oms))

        return list(chain.from_iterable(maps.itervalues()))

    def _routine_sort(self, result):
        """Sort the result of routine_query.

        @param result: result of routine_query
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
