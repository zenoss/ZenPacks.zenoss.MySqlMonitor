
from Products.ZenRRD.CommandParser import CommandParser

class CmdResToEvent(CommandParser):
    def processResults(self, cmd, result):
        data = cmd.result.output
        result.events.append(dict(
            severity=2,
            summary=cmd.command + '\n\n' + data,
            clear=True
        ))
        
cmdres2event = CmdResToEvent # because zenoss is not happy with pep8

