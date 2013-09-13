set -x

zenpack --remove ZenPacks.zenoss.MySQL
cd ..
zenpack --link --install ZenPacks.zenoss.MySQL

zopectl restart
zenhub restart

cd ZenPacks.zenoss.MySQL
zendmd --script=add_device.py

set +x
