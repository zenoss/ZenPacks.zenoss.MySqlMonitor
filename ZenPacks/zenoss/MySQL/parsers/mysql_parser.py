
from Products.ZenRRD.CommandParser import CommandParser

class MySQL(CommandParser): # TODO: check if this should be equal to filename

    def processResults(self, cmd, result):
        dp_map = dict((dp.id, dp) for dp in cmd.points)

        print dp_map

        for line in cmd.result.output.splitlines():
            print line

        # results.values.append(datapoint(from map), datapoint value)
