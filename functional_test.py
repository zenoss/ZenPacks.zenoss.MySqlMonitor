import os
import subprocess
from pprint import pformat

from add_device import add_device, model_device, python_monitor_device

ZENPACK_NAME = 'ZenPacks.zenoss.MySqlMonitor'
DUMP_FILE = '/home/zenoss/all.sql'


def main():
    if not unittests_ok():
        print 'Unittests failed'
        return False
    try:
        dump_zodb()
        zenpack_remove()
        zenpack_install()
        zenoss('restart')
        device = add_device()
        model_device(device)
        monitoring_results = python_monitor_device(device)

        assert '- is that the correct name?' not in monitoring_results
        return True
    except Exception:
        raise
    finally:
        zenoss('stop')
        kill_proc()
        restore_zodb()
        zenoss('start')

    return True


def here():
    ''' return directory which contains this file '''
    return os.path.abspath(os.path.dirname(__file__))


def unittests_ok():
    bprint(''' Run unittests and check if ok ''')
    return subprocess.check_call(['make', 'test']) == 0


def dump_zodb():
    bprint(''' Dump zodb database to file ''')
    os.system('mysqldump -u root --all-databases > %s' % DUMP_FILE)


def kill_proc():
    bprint('''Kill all mysql processes!''')
    o = subprocess.check_output(['mysql', '--batch', '-u', 'root', '-e', 'show processlist'])
    pl = [x.split('\t') for x in o.splitlines()]
    cols = dict((c, i) for i, c in enumerate(pl[0]))
    print ' '.join(['%15s' % p for p in pl[0]])
    for process in pl[1:]:
        if (process[cols['Command']] == 'Sleep') and (process[cols['db']] in ('zodb', 'zodb_session')):
            print ' '.join(['%15s' % p for p in process])
            cmd = 'mysqladmin -u root KILL %s' % process[cols['Id']]
            os.system(cmd)


def restore_zodb():
    bprint('''Restoring zodb from file''')
    os.system('mysql -u root -e "drop database zodb;\
        drop database zodb_session"')
    os.system('mysql -u root < %s' % DUMP_FILE)


def zenpack_remove():
    bprint('removing zenpack')
    assert os.system('zenpack --remove %s' % ZENPACK_NAME) == 0


def zenpack_install():
    bprint('install zenpack')
    assert os.system('zenpack --link --install %s' % here()) == 0


def zenoss(cmd):
    bprint('zenoss %s' % cmd)
    os.system('zenoss %s' % cmd)


def bprint(*args):
    print '\033[94m%s\033[0m' % pformat(*args)


if __name__ == '__main__':
    if main():
        print 'All ok'
