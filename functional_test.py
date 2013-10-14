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

        bprint(monitoring_results)

        assert '- is that the correct name?' not in monitoring_results
    except:
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
    os.system('mysqladmin -u root processlist > fullproce;')
    os.system('''cat fullproce |grep Sleep |awk -F " " '{print $2}' > id;''')
    os.system('''for todos_id in `cat ./id`; do  mysqladmin -u root KILL \
        $todos_id ; done''')
    os.system('rm fullproce;')
    os.system('rm id;')


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
