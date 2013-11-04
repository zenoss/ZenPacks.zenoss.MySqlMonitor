##############################################################################
#
# Copyright (C) Zenoss, Inc. 2013, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################

# These variables are overwritten by Zenoss when the ZenPack is exported
# or saved.  Do not modify them directly here.
# NB: PACKAGES is deprecated

NAME = "ZenPacks.zenoss.MySqlMonitor"

VERSION = "0.0.1"

AUTHOR = "Zenoss"

LICENSE = "GPL"

NAMESPACE_PACKAGES = [
    u'ZenPacks',
    u'ZenPacks.zenoss'
]

PACKAGES = [
    u'ZenPacks',
    u'ZenPacks.zenoss',
    u'ZenPacks.zenoss.MySqlMonitor',
]

INSTALL_REQUIRES = []
COMPAT_ZENOSS_VERS = ">=4.2"
PREV_ZENPACK_NAME = ""

# STOP_REPLACEMENTS
# Zenoss will not overwrite any changes you make below here.

from os.path import dirname
from setuptools import setup, find_packages

setup(
    # This ZenPack metadata should usually be edited with the Zenoss
    # ZenPack edit page.  Whenever the edit page is submitted it will
    # overwrite the values below (the ones it knows about) with new values.
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    license=LICENSE,
    description='MySQL Database Monitor (Core) ZenPack',
    long_description=(open(
        dirname(__file__) + 'README.md').read().split('\n'))[0],
    url='http://wiki.zenoss.org/ZenPack:MySQL_Database_Monitor_%28Core%29',

    # This is the version spec which indicates what versions of Zenoss
    # this ZenPack is compatible with
    compatZenossVers=COMPAT_ZENOSS_VERS,

    # previousZenPackName is a facility for telling Zenoss that the name
    # of this ZenPack has changed.  If no ZenPack with the current name is
    # installed then a zenpack of this name if installed will be upgraded.
    prevZenPackName=PREV_ZENPACK_NAME,

    # Indicate to setuptools which namespace packages the zenpack
    # participates in
    namespace_packages=NAMESPACE_PACKAGES,

    # Tell setuptools what packages this zenpack provides.
    packages=find_packages(),

    # Tell setuptools to figure out for itself which files to include
    # in the binary egg when it is built.
    include_package_data=True,

    # Tell setuptools what non-python files should also be included
    # with the binary egg.
    package_data={
        '': ['*.txt'],
        },

    # Indicate dependencies on other python modules or ZenPacks.  This line
    # is modified by zenoss when the ZenPack edit page is submitted.  Zenoss
    # tries to put add/delete the names it manages at the beginning of this
    # list, so any manual additions should be added to the end.  Things will
    # go poorly if this line is broken into multiple lines or modified to
    # dramatically.
    install_requires=INSTALL_REQUIRES,

    # Every ZenPack egg must define exactly one zenoss.zenpacks entry point
    # of this form.
    entry_points={
        'zenoss.zenpacks': '%s = %s' % (NAME, NAME),
    },
    # All ZenPack eggs must be installed in unzipped form.
    zip_safe=False,
)
