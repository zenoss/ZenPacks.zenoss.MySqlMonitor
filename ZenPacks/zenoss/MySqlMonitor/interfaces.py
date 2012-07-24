##############################################################################
# 
# Copyright (C) Zenoss, Inc. 2010, all rights reserved.
# 
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
# 
##############################################################################


from Products.Zuul.interfaces import IBasicDataSourceInfo
from Products.Zuul.form import schema
from Products.Zuul.utils import ZuulMessageFactory as _t


class IMySqlMonitorDataSourceInfo(IBasicDataSourceInfo):
    usessh = schema.Bool(title=_t(u"Use SSH"))
    cycletime = schema.Int(title=_t(u'Cycle Time (seconds)'))
    timeout = schema.Int(title=_t(u'Timeout (seconds)'))
    hostname = schema.TextLine(title=_t(u'MySQL Host'), group=_t(u'MySQL'))
    username = schema.TextLine(title=_t(u'MySQL Username'), group=_t(u'MySQL'))
    port = schema.TextLine(title=_t(u'MySQL Port'), group=_t(u'MySQL'))
    password = schema.Password(title=_t(u'MySQL Password'), group=_t(u'MySQL'))
    versionFivePlus = schema.Bool(title=_t(u'MySQL Version 5+'), group=_t(u'MySQL'))
