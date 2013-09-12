from Products.ZenRRD.CommandParser import CommandParser


class MySQL(CommandParser):
    def processResults(self, cmd, result):
        dp_map = dict((dp.id, dp) for dp in cmd.points)

        def ret(key, value):
            key = key.lower()
            if key in dp_map:
                result.values.append((dp_map[key], value))

        for line in cmd.result.output.splitlines():
            ret(*line.split('\t'))

mysql_parser = MySQL # because zenoss is not happy with pep8
