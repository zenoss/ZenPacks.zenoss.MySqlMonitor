import logging

from Products.ZenRRD.CommandParser import CommandParser

class Database(CommandParser):

    def processResults(self, cmd, result):

        logger = logging.getLogger('.'.join(['zen', __name__]))
       
        # data = cmd.result.output.splitlines()
        # query = {}
        # for line in data:
        #     query[line.split('\t')[0]] = line.split('\t')[1]
        print "================================================================================================================================================"
        for point in cmd.points:
            result.values.append((point, 100))

        return result

database = Database # Zenoss style
