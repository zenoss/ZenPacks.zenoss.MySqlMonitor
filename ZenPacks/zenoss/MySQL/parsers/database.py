##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################

from Products.ZenRRD.CommandParser import CommandParser

class Database(CommandParser):

    def processResults(self, cmd, result):
        # Results parsing
        data = cmd.result.output.splitlines()
        keys = [column.lower() for column in data[0].split('\t')]
        keys.pop(0)
        query_result = {}
        for line in data[1:]:
            line = line.split('\t')
            key = line.pop(0)
            values = dict((k, line[index]) for index, k in enumerate(keys))
            query_result[key] = values

        # Appending values
        for point in cmd.points:
            if point.component in query_result.keys():
                result.values.append((
                        point,
                        query_result[point.component][point.id]
                    ))

        return result

database = Database # Zenoss style
