import re
from Products.ZenRRD.CommandParser import CommandParser


class MySQL(CommandParser): # TODO: check if this should be equal to filename
    pattern = re.compile(r'^\|\s*(\S+)\s*\|\s*(\S*)\s*\|$')

    def processResults(self, cmd, result):
        dp_map = dict((dp.id, dp) for dp in cmd.points)

        def ret(key, value):
            key = key.lower()
            if key in dp_map:
                result.values.append((dp_map[key], value))

        for line in cmd.result.output.splitlines():
            match = self.pattern.match(line)
            if match:
                ret(*match.groups())
