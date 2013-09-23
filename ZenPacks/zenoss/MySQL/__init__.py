##############################################################################
#
# Copyright (C) Zenoss, Inc. 2012, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

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
    pass

def SizeUnitsProxyProperty(propertyName, unitstr="B"):
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
            divby = 1024.0
            units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
            for i in range(units.index(unitstr), len(units)):
                if val<divby:
                    break
                val = val/divby
            return str(round(val, 2)) + ' ' + units[i]
        except:
            return val

    return property(getter, setter)
