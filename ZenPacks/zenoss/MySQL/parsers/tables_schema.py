from Products.ZenRRD.CommandParser import CommandParser

'''
$ mysql -u root -e "select TABLE_ROWS, AVG_ROW_LENGTH, DATA_LENGTH, MAX_DATA_LENGTH, INDEX_LENGTH, DATA_FREE  from information_schema.tables where TABLE_SCHEMA='test' and TABLE_NAME='hello'"
+------------+----------------+-------------+-----------------+--------------+-----------+
| TABLE_ROWS | AVG_ROW_LENGTH | DATA_LENGTH | MAX_DATA_LENGTH | INDEX_LENGTH | DATA_FREE |
+------------+----------------+-------------+-----------------+--------------+-----------+
|          0 |              0 |       16384 |               0 |            0 |   8388608 |
+------------+----------------+-------------+-----------------+--------------+-----------+
'''


class TablesSchema(CommandParser):
    def processResults(self, cmd, result):
        dp_map = dict((dp.id, dp) for dp in cmd.points)

        lines = cmd.result.output.splitlines()
        if len(lines) < 2:
            return # no data

        schema = dict((col.lower(), i)
            for col, i in enumerate(lines[0].split('\t'))
        )
        for i, value in enumerate(lines[1].split('\t')):
            col = schema[i]
            if col in dp_map:
                result.values.append((dp_map[col], value))

tables_schema = TablesSchema # because zenoss is not happy with pep8
