set -x

zenpack --remove ZenPacks.zenoss.MySqlMonitor
cd ..
zenpack --link --install ZenPacks.zenoss.MySqlMonitor

zopectl restart
zenhub restart

cd ZenPacks.zenoss.MySqlMonitor

set +x
