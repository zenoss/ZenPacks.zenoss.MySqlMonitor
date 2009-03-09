#!/usr/bin/env python
###########################################################################
#
# This program is part of Zenoss Core, an open source monitoring platform.
# Copyright (C) 2007, Zenoss Inc.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# For complete information please visit: http://www.zenoss.com/oss/
#
###########################################################################

import sys
from optparse import OptionParser, OptionValueError

try:
    import MySQLdb
except:
    print "Error importing MySQLdb module. This is a pre-requisite."
    sys.exit(1)

class ZenossMySqlStatsPlugin:
    def __init__(self, options):
        self.host = options.host
        self.port = options.port
        self.user = options.user
        self.passwd = options.passwd
        self.queries = self.buildQueries(options)
    
    def buildQueries(self, options):
        queries = []
        #add the standard query
        # (QUERY, processing by row True|False)
        if options.gstatus:
            queries.append(("SHOW GLOBAL STATUS", True))
        else:
            queries.append(("SHOW STATUS", True))
        #add additional slave/master queries if needed
        if options.slavestatus:
            queries.append(("SHOW SLAVE STATUS", False))
        if options.masterstatus:
            queries.append(("SHOW MASTER STATUS", False))
        return queries
    
    def runAndProcessQueries(self, cursor, qs):
        status = "STATUS OK"
        data = ""
        for q in qs:
            query = q[0]
            returncode = cursor.execute(query)
            if not returncode:
                print "STATUS Critical | Error getting MySQL statistics for %s" % query
                sys.exit(1)
            #process metrics returned by row
            if q[1]:
                data += (' '.join([ '='.join(r) for r in cursor.fetchall() ])) + " "
            #process metrics returned by column
            else:   
                data += " ".join(map(lambda meta, d: "%s=%s" % (meta[0], d[0]), cursor.description, cursor.fetchone()))
        return "%s|%s" % (status, data)
                
    def run(self):
        try:
            try:
                # Specify a blank database so no privileges are required
                # Thanks for this tip go to Geoff Franks <gfranks@hwi.buffalo.edu>
                self.conn = MySQLdb.connect(host=self.host, port=self.port,
                            db='', user=self.user, passwd=self.passwd)
                self.cursor = self.conn.cursor()
            except Exception, e:
                print "MySQL Error: %s" % (e,)
                sys.exit(1)
            print self.runAndProcessQueries(self.cursor, self.queries)
        finally:
            self.cursor.close()
            self.conn.close()

#check to make sure only -s or -m are specified
def checkSlave(option, opt, value, parser):
    ss = str(option).find("slavestatus") > -1
    if ( parser.values.masterstatus and ss ) or ( parser.values.slavestatus and not ss ):
        raise OptionValueError("Error: can't use masterstatus and slavestatus at the same time")
    if ss:
        parser.values.slavestatus = True
    else:
        parser.values.masterstatus = True

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
    parser.add_option('-s', '--slavestatus', dest='slavestatus', default=False,
            action='callback', callback=checkSlave, help="For slave servers, get slave status")
    parser.add_option('-m', '--masterstatus', dest='masterstatus', default=False,
            action='callback', callback=checkSlave, help="For master servers, get master status")
    parser.add_option('-g', '--global', dest='gstatus', default=False,
            action='store_true', help="Get global stats (Version 5+)")
    options, args = parser.parse_args()

    if not options.host:
        print "You must specify the host parameter."
        sys.exit(1)
    cmd = ZenossMySqlStatsPlugin(options)
    cmd.run()
