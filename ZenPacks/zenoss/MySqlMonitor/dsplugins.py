from twisted.enterprise import adbapi
from twisted.internet import reactor, defer

from ZenPacks.zenoss.PythonCollector.datasources.PythonDataSource \
    import PythonDataSourcePlugin

from ZenPacks.zenoss.MySqlMonitor.utils import parse_mysql_connection_string
 
class MySqlMonitorPlugin(PythonDataSourcePlugin):
    """Explanation of what MyPlugin does."""
    proxy_attributes = ('zMySQLConnectionString',)

    def collect(self, config):
        """
        No default collect behavior. You must implement this method.
 
        This method must return a Twisted deferred. The deferred results will
        be sent to the onResult then either onSuccess or onError callbacks
        below.
        """
        for ds in config.datasources:
            servers = parse_mysql_connection_string(ds.zMySQLConnectionString)
            server = servers[ds.component]

            dbpool = adbapi.ConnectionPool("MySQLdb",
                user=server['user'],
                port=server['port'],
                passwd=server['passwd']
            )
            return dbpool.runQuery("show databases")
 
    def onSuccess(self, result, config):
        """
        Called only on success. After onResult, before onComplete.
 
        You should return a data structure with zero or more events, values
        and maps.
        """

        print '*********'*10
        print result
        print '*********'*10

        import random
        import time

        return {
            'values': {
                'root_3306': {
                    'random': random.random()
                    },
                },
            }
 
    def onError(self, result, config):
        """
        Called only on error. After onResult, before onComplete.
 
        You can omit this method if you want the error result of the collect
        method to be used without further processing. It recommended to
        implement this method to capture errors.
        """

        print '*********'*10
        print result
        print '*********'*10

        return {
            'events': [{
                'summary': 'error: %s' % result,
                'eventKey': 'myPlugin_result',
                'severity': 4,
                }],
            }