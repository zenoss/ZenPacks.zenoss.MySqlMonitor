##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


"""
$ mysql -u root -e "select TABLE_ROWS, AVG_ROW_LENGTH, DATA_LENGTH, MAX_DATA_LENGTH, INDEX_LENGTH, DATA_FREE  from information_schema.tables where TABLE_SCHEMA='test' and TABLE_NAME='hello'"
+------------+----------------+-------------+-----------------+--------------+-----------+
| TABLE_ROWS | AVG_ROW_LENGTH | DATA_LENGTH | MAX_DATA_LENGTH | INDEX_LENGTH | DATA_FREE |
+------------+----------------+-------------+-----------------+--------------+-----------+
|          0 |              0 |       16384 |               0 |            0 |   8388608 |
+------------+----------------+-------------+-----------------+--------------+-----------+

$ mysql -u root -e "select TABLE_SCHEMA, TABLE_NAME, TABLE_ROWS, AVG_ROW_LENGTH, DATA_LENGTH, MAX_DATA_LENGTH, INDEX_LENGTH, DATA_FREE  from information_schema.tables"

"""

from pprint import pprint

from Products.ZenRRD.CommandParser import CommandParser

def get_values(output):
    lines = output.splitlines()
    if len(lines) < 2:
        return {} # no data

    schema = dict((col.lower(), i)  # maps field name to position
        for i, col in enumerate(lines[0].split('\t'))
    )
    values = {}
    for line in lines[1:]:
        fields = dict(
            (schema(i), v) 
            for i, v in enumerate(line.split('\t'))
        )
        values[fields['table_schema'] + '.' + fields['table_name']] = dict((k, v)
            for k, v in fields.iteritems()
            if k not in ('table_schema', 'table_name')
        )



class TablesSchema(CommandParser):
    def processResults(self, cmd, result):
        for point in cmd.points:
            if point.component not in data['values']:
                continue
            if point.id not in data['values'][point.component]:
                continue

            result.values.append((
                point,
                data['values'][point.component][point.id]
            ))
        
tables_schema = TablesSchema # because zenoss is not happy with pep8

