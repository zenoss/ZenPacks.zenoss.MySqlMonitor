import os
import subprocess

from add_device import add_device, model_device, python_monitor_device

ZENPACK_NAME = 'ZenPacks.zenoss.MySqlMonitor'


def main():
    if not unittests_ok():
        print 'Unittests failed'
        return False
    dump_zodb()
    zenpack_remove()
    zenpack_install()
    zenoss_restart()
    device = add_device()
    model_device(device)
    monitoring_results = python_monitor_device(device)

    assert (
        '- is that the correct name?' not in monitoring_results,
        'Wrong monitoring configuration'
    )

    restore_zodb()


def unittests_ok():
    ''' Run unittests and check if ok '''
    return subprocess.check_call(['make', 'test']) == 0


def dump_zodb():
    ''' Dump zodb database to file '''
    os.system('mysqldump -u root zodb > zodb.sql')


def restore_zodb():
    os.system('mysql -u root zodb < zodb.sql')


def zenpack_remove():
    assert os.system('zenpack --remove %s' % ZENPACK_NAME) == 0


def zenpack_install():
    assert os.system('zenpack --link --install %s' % ZENPACK_NAME) == 0


def zenoss_restart():
    os.system('zenoss restart')

if __name__ == '__main__':
    if main():
        print 'All ok'
