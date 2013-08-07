#!/usr/bin/python
import os
import shutil
import yum
import sys
import re
from types import *
import ConfigParser

CONFIGFILE = "/usr/csee/etc/updaterpm.conf"
yumopts = ['yum', '-y', '--nogpgcheck']

# Clean Yum cache files to make sure that we get the most recent ones
os.system('yum clean all')

base = yum.YumBase()
base.doGenericSetup()

# Gets all installed groups, and the available but not installed groups
installedGroups, availableGroups = base.doGroupLists()
installedGroups = set([i.name for i in installedGroups])
availableGroups = set([i.name for i in availableGroups])

with open(CONFIGFILE) as configFile:
  config = ConfigParser.ConfigParser()
  config.readfp(configFile)
  allowedGroups = set([i.strip().split("@")[-1] for i in config.get("main", "allowed").split("\n")])
  ignoreGroups = set([i.strip().split("@")[-1] for i in config.get("main", "ignore").split("\n")])  

# Packages that are installed, but not in any repository
available = base.doPackageLists('available').available  

# For any package for which there is an update, the older version is marked as
# an extra, but we don't want to remove them, so we get a list of them:
installed = base.doPackageLists('installed').installed
available = set(installed + available)
available = [x.name for x in available]
availableGroups = [(base.comps.return_groups(x)[0].name, base.comps.return_groups(x)[0].packages) for x in availableGroups]
whole = []
for i in availableGroups:
  if [x for x in i[1] if not(x in available)] and i[0] in allowedGroups:
    print "\n" + i[0] + ":"
    gaps = list(set(["\t"+x+"\n" for x in i[1] if not(x in available)]))
    gaps.sort()
    whole.extend(list(gaps))
    for j in gaps:
      print j,

whole = list(set(whole))
whole.sort()
print "\nAggregate Gaps:" + str(len(whole))
for i in whole:
  print i,
