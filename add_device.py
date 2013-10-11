#!/usr/bin/env python

import random
import os
import string
import sys
import subprocess


def get_stuff():
    # Zope magic ensues!
    import Zope2
    CONF_FILE = os.path.join(os.environ['ZENHOME'], 'etc', 'zope.conf')

    # hide any positional arguments during Zope2 configure
    _argv = sys.argv
    sys.argv = [sys.argv[0], ] + [x for x in sys.argv[1:] if x.startswith("-")]
    Zope2.configure(CONF_FILE)
    sys.argv = _argv  # restore normality

    from Products.ZenModel.zendmd import _customStuff
    return _customStuff()


def random_id(N):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in range(N)
    )


def add_device():
    dc = dmd.Devices.createOrganizer('/Server')
    name = 'test_' + random_id(3)
    device = dc.createInstance(name)
    device.setPerformanceMonitor('localhost')
    device.manageIp = '127.0.0.1'
    device.setZenProperty('zMySQLConnectionString', 'root::3306;')
    device.setZenProperty('zCollectorPlugins', ['MySQLCollector'])
    device.index_object()
    commit()
    return name


def model_device(name):
    os.system('zenmodeler run --device=%s' % name)


def python_monitor_device(name):
    device = '--device=' + name
    return subprocess.check_output(['zenpython', 'run', device])


def delete_device(name):
    commit()  # WTF?
    d = find(name)
    d.deleteDevice()
    commit()

stuff = get_stuff()
dmd = stuff['dmd']
commit = stuff['commit']
find = stuff['find']

if __name__ == '__main__':
    name = add_device()
    print name
    model_device(name)
