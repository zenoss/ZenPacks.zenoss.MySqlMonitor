##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

import math
from Products.ZenModel.ZenPack import ZenPackBase


# Modules containing model classes. Used by zenchkschema to validate
# bidirectional integrity of defined relationships.
productNames = (
    'MySQLServer',
    'MySQLDatabase',
    'MySQLTable',
    'MySQLStoredProcedure',
    'MySQLStoredFunction',
    'MySQLProcess'
    )

# Useful to avoid making literal string references to module and class names
# throughout the rest of the ZenPack.
ZP_NAME = 'ZenPacks.zenoss.MySQL'
MODULE_NAME = {}
CLASS_NAME = {}
for product_name in productNames:
    MODULE_NAME[product_name] = '.'.join([ZP_NAME, product_name])
    CLASS_NAME[product_name] = '.'.join([ZP_NAME, product_name, product_name])

# Useful for components' ids.
NAME_SPLITTER = '(.,.)'

class ZenPack(ZenPackBase):
    '''
        ZenPack loader.
    '''
    packZProperties = [
        ('zMySQLCommand', 'mysql', 'string'),
    ]

def SizeUnitsProxyProperty(propertyName):
    """This uses a closure to make a getter and
    setter for the size property and assigns it
    a calculated value with unit type.
    """
    def setter(self, value):
        return setattr(self._object, propertyName, value)

    def getter(self):
        val = getattr(self._object, propertyName)
        try:
            val = int(val)
            if val == 0:
                return val
            units = ("B", "KB", "MB", "GB", "TB", "PB")
            i = int(math.floor(math.log(val, 1024)))
            p = math.pow(1024, i)
            s = round(val/p, 2)
            if (s > 0):
                return '%s %s' % (s, units[i])
            else:
                return '0 B'
        except:
            return val

    return property(getter, setter)
