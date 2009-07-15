###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2009, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import Globals
from Products.ZenModel.ZenPack import ZenPackMigration
from Products.ZenModel.migrate.Migrate import Version

def transformZMySqlPasswords(manager):
    """
    Change zMySqlPassword to a password type at this level if it exists and
    recursively for any child property managers.
    """
    if manager.hasProperty('zMySqlPassword'):
        value = manager.getProperty('zMySqlPassword')
        manager._delProperty('zMySqlPassword')
        manager._setProperty('zMySqlPassword', value, 'password')
    if isinstance(manager, ObjectManager):
        for ob in manager.objectValues():
            if isinstance(ob, ZenPropertyManager):
                self.transformZMySqlPasswords(ob)
                
class PasswordType(ZenPackMigration):
    version = Version(2, 0, 2)
    
    def migrate(self, pack):
        """
        change zMySqlPassword to be of type 'password' and run transformer
        against it.
        """
        dmd = pack.__primary_parent__.__primary_parent__
        transformZMySqlPasswords(dmd.Devices)
        
