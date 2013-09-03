##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

''' Models discovery tree for MySQL. '''

import collections
from itertools import chain

from Products.DataCollector.plugins.CollectorPlugin import PythonPlugin
from Products.DataCollector.plugins.DataMaps import ObjectMap, RelationshipMap

from Products.ZenUtils.Utils import prepId

from ZenPacks.zenoss.MySQL import MODULE_NAME
from ZenPacks.zenoss.MySQL.MySQLServer import CredentialsNotFound, get_credentials

class MySQLCollector(PythonPlugin):
    deviceProperties = PythonPlugin.deviceProperties + (
        'host',
        'port',
        'user',
        'password',
    )

    def collect(self, device, log):
        return True

    def process(self, device, results, log):
        log.info(
            'Modeler %s processing data for device %s',
            self.name(), device.id
        )

        device_om = ObjectMap()

        log.debug("HOST: %s", device.host)
        log.debug("PORT: %s", device.port)
        log.debug("USER: %s", device.user)


        maps = collections.OrderedDict([
            ('databases', []),
        ])

        # # ---------------------------------------------------------------------
        # # List of databases
        # databases = []
        # for item in [42]:
        #     hs_id = prepId(str(item))

        #     hosted_service_oms.append(ObjectMap(data={
        #         'id': hs_id,
        #         'title': 'database' + str(item),
        #     }))

        # maps['databases'].append(RelationshipMap(
        #     relname='databases',
        #     modname=MODULE_NAME['MySQLDatabase'],
        #     objmaps=databases
        # ))

        # ---------------------------------------------------------------------
        # Device properties
        maps['server'].append(ObjectMap(data={
        }))

        return list(chain.from_iterable(maps.itervalues()))
