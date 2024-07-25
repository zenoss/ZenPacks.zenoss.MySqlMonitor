#!/usr/bin/env python
##############################################################################
#
# Copyright (C) Zenoss, Inc. 2007-2024, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


import sys
from optparse import OptionParser

import pymysql


from ZenPacks.zenoss.MySqlMonitor.utils import getMySqlSslParam


class ZenossMySqlStatsPlugin:
    def __init__(self, host, port, user, passwd, gstatus, sslCaPemFile, sslCertPemFile, sslKeyPemFile):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.sslCaPemFile = sslCaPemFile
        self.sslCertPemFile = sslCertPemFile
        self.sslKeyPemFile = sslKeyPemFile
        if gstatus:
            self.cmd = 'SHOW GLOBAL STATUS'
        else:
            self.cmd = 'SHOW STATUS'

    def run(self):
        dbConnArgs = {
            'host': self.host,
            'user': self.user,
            'port': self.port,
            'passwd': self.passwd,
            'db': ''
        }
        sslArgs = getMySqlSslParam(
            self.zMySqlSslCaPemFile,
            self.zMySqlSslCertPemFile,
            self.zMySqlSslKeyPemFile
        )
        if sslArgs:
            dbConnArgs['ssl'] = sslArgs

        try:
            # Specify a blank database so no privileges are required
            # Thanks for this tip go to Geoff Franks <gfranks@hwi.buffalo.edu>
            self.conn = pymysql.connect(**dbConnArgs)
            # TODO: adding SSL CA info causes "TLSV1_ALERT_PROTOCOL_VERSION".
            # May not be needed, this script may be legacy....

            cursor = self.conn.cursor()
        except Exception, e:
            print "MySQL Error: %s" % (e,)
            sys.exit(1)

        ret = cursor.execute(self.cmd)
        if not ret:
            cursor.close()
            print 'Error getting MySQL statistics'
            sys.exit(1)

        print "STATUS OK|%s" % \
            (' '.join(['='.join(r) for r in cursor.fetchall()]))

        cursor.close()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-H', '--host', dest='host',
            help='Hostname of MySQL server')
    parser.add_option('-p', '--port', dest='port', default=3306, type='int',
            help='Port of MySQL server')
    parser.add_option('-u', '--user', dest='user', default='zenoss',
            help='MySQL username')
    parser.add_option('-w', '--password', dest='passwd', default='',
            help='MySQL password')
    parser.add_option('-g', '--global', dest='gstatus', default=False,
            action='store_true', help="Get global stats (Version 5+)")
    parser.add_option('-s', '--sslCaPemFile', dest='sslCaPemFile', default='',
            help='Path to the file that contains a PEM-formatted CA certificate.')
    parser.add_option('-t', '--sslCertPemFile', dest='sslCertPemFile', default='',
            help='Path to the file that contains a PEM-formatted client certificate.')
    parser.add_option('-u', '--sslKeyPemFile', dest='sslKeyPemFile', default='',
            help='Path to the file that contains a PEM-formatted private key for the client certificate.')
    options, args = parser.parse_args()

    if not options.host:
        print "You must specify the host parameter."
        sys.exit(1)

    cmd = ZenossMySqlStatsPlugin(options.host, options.port,
            options.user, options.passwd, options.gstatus,
            options.sslCaPemFile, options.sslCertPemFile, options.sslKeyPemFile)

    cmd.run()
