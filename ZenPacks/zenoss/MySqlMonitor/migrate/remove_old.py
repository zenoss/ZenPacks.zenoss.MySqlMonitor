'''
    Migration script.

    Written with the help of following examples:
        https://github.com/zenoss/Community-Zenpacks/blob/master/ZenPacks.community.DellMon/ZenPacks/community/DellMon/migrate/removeOldDellReports.py
        https://github.com/zenoss/ZenPackTemplate/blob/master/CONTENT/migrate/ExampleMigration.py
'''
import logging
log = logging.getLogger('zen.migrate')

import Globals

from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version
from Products.ZenUtils.Utils import unused

from zExceptions import NotFound

unused(Globals)

class CleaningMigration(ZenPackMigration):
    # There are two scenarios under which this migrate script will execute.
    # 1. Fresh Install - If this ZenPack is being installed for the first
    # time and the migrate script version is greater than or equal to the
    # ZenPack's version, it will execute.
    #
    # 2. Upgrade - If this ZenPack is being upgraded and the migrate script
    # version is greater than or equal to the version of the ZenPack that
    # is already installed, it will execute.
    version = Version(3, 0, 1)

    def migrate(self, pack):
        log.info("Running ExampleMigration")
        dmd = pack.getDmd()

        for obj in OLD_OBJECTS.splitlines():
            remove_object(dmd, obj)

        for obj in OLD_ZPROPERTIES.splitlines():
            remove_property(dmd, obj)


remove_old = CleaningMigration

CleaningMigration()

def remove_property(dmd, path):
    remove_object(dmd, path, method='_delProperty')

def remove_object(dmd, path, method='_delObject'):
    try:
        path, id = path.rsplit('/', 1)
    except ValueError:
        return
    if not (path and id): return
    path = '/zport/dmd' + path
    try:
        obj = dmd.getObjByPath(path)
    except (KeyError, NotFound) as e:
        # log.info(path + ' not found')
        return
    # log.info('Removing from %s %s' % (path, id))
    try:
        getattr(obj, method)(id)
    except Exception as e:
        pass
        # log.error(e)

OLD_ZPROPERTIES = '''
/Devices/zMySqlRootPassword
/Devices/zMySqlPassword
/Devices/zMySqlPort
/Devices/zMySqlUsername
'''

OLD_OBJECTS = '''
/Devices/Server/rrdTemplates/MySQL
/Devices/Server/rrdTemplates/MySQL/datasources/mysql
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Bytes_received
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Bytes_sent
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Com_delete
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Com_delete_multi
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Com_insert
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Com_insert_select
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Com_select
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Com_update
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Com_update_multi
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_delete
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_read_first
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_read_key
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_read_next
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_read_prev
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_read_rnd
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_read_rnd_next
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_update
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Handler_write
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Select_full_join
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Select_full_range_join
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Select_range
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Select_range_check
/Devices/Server/rrdTemplates/MySQL/datasources/mysql/datapoints/Select_scan
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Command Statistics/graphPoints/Com_delete
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Command Statistics/graphPoints/Com_delete_multi
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Command Statistics/graphPoints/Com_insert
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Command Statistics/graphPoints/Com_insert_select
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Command Statistics/graphPoints/Com_select
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Command Statistics/graphPoints/Com_update
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Command Statistics/graphPoints/Com_update_multi
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_delete
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_read_first
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_read_key
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_read_next
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_read_prev
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_read_rnd
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_read_rnd_next
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_update
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Handler Statistics/graphPoints/Handler_write
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Network Traffic/graphPoints/Bytes_received
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Network Traffic/graphPoints/Bytes_sent
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Select Statistics/graphPoints/Select_full_join
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Select Statistics/graphPoints/Select_full_range_join
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Select Statistics/graphPoints/Select_range
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Select Statistics/graphPoints/Select_range_check
/Devices/Server/rrdTemplates/MySQL/graphDefs/MySQL - Select Statistics/graphPoints/Select_scan
/Events/App/MySQL
/Events/DB
/Manufacturers/MySQL
/Manufacturers/MySQL/products/MyODBC-2.50.39-19
/Manufacturers/MySQL/products/MyODBC-2.50.39-19.1
/Manufacturers/MySQL/products/mysql
/Manufacturers/MySQL/products/mysql-3.23.58-16.FC3.1
/Manufacturers/MySQL/products/mysql-bench-3.23.58-16.FC3.1
/Manufacturers/MySQL/products/MySQL-client-standard-5.0.24a-0.rhel4
/Manufacturers/MySQL/products/mysql-debuginfo-3.23.58-16.FC3.1
/Manufacturers/MySQL/products/mysql-devel-3.23.58-13
/Manufacturers/MySQL/products/mysql-devel-3.23.58-16.FC3.1
/Manufacturers/MySQL/products/MySQL-python-0.9.2-4
/Manufacturers/MySQL/products/mysql-server-3.23.58-16.FC3.1
/Manufacturers/MySQL/products/MySQL-server-standard-5.0.24a-0.rhel4
/Processes/MySQL
/Processes/MySQL/osProcessClasses/mysqld
/Services/IpService/Registered/serviceclasses/mysql
'''
