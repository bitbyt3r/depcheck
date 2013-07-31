#!/usr/bin/python
import os
import rpm
import sys
import re

ignoreFile = "./ignorefile"

ts = rpm.TransactionSet()
ts.setVSFlags(rpm._RPMVSF_NOSIGNATURES)

def readRpmHeader(ts, filename):
    """ Read an rpm header. """
    fd = os.open(filename, os.O_RDONLY)
    try:
        header = ts.hdrFromFdno(fd)
    except rpm.error:
        print filename + "has no available publickey."
        return False
    finally:
        os.close(fd)
    return header

def getDeps(header):
    output = []
    for i in header[rpm.RPMTAG_REQUIRENAME]:
        output.append(i.split("/")[-1])
    return output

def getProvides(header):
    output = []
    for i in header[rpm.RPMTAG_PROVIDENAME]:
        output.append(i.split("/")[-1])
    return output

def getDesc(header):
    return header[rpm.RPMTAG_NAME], header[rpm.RPMTAG_VERSION], header[rpm.RPMTAG_RELEASE]

def parseFile(fileName):
    fileHandle = open(fileName, "r")
    lines = fileHandle.read()
    fileHandle.close()
    return lines

def printDeps(dependencies, packages, names):
    ignore = parseFile(ignoreFile)
    needed = {}
    for i in dependencies.keys():
        satisfied = True
        needed[i] = []
        for j in dependencies[i]:
            if not(j in names) and not("rpmlib" in j) and not(j in ignore) and not("/" in j):
                satisfied = False
                needed[i].append(j)
        if satisfied:
            del(dependencies[i])
    overall_needed = {}
    depends = list(dependencies.keys())
    depends.sort()
    for i in depends:
        if arguments("-v"):
            print i[0] + "-" + i[1] + "-" + i[2] + " Requires the following, which were not found:"
        else:
            print i[0] + "-" + i[1] + "-" + i[2] + " Has missing requirements."
        for j in needed[i]:
            if arguments("-v"):
                print "    " + j
            if not(j in overall_needed.keys()):
                overall_needed[j] = 1
            else:
                overall_needed[j] += 1
                
    print "Overall missing packages:"
    neededList = overall_needed.keys()
    neededList.sort()
    for k in neededList:
        print str(overall_needed[k]) + "    " + k

def printDuplicates(packages):
    packages.sort()
    for i in range(0, len(packages)):
        for j in range(i + 1, len(packages)):
            if packages[i][0] == packages[j][0]:
                print packages[i][3] + "/" + packages[i][4] + " Duplicates " + packages[j][3] + "/" + packages[j][4]

def arguments(arg):
    for i in range(1, len(sys.argv)):
        if sys.argv[i]:
            if sys.argv[i] == arg:
                return True
    return False

provides = {}
packages = []
names = []

print "Compiling provides..."
for subdir, dirs, files in os.walk(sys.argv[2]):
    for file in files:
       rpm_regex = re.compile(".+\.rpm$")
       if rpm_regex.match(file):
           header = readRpmHeader(ts, subdir + "/" + file)
           if header:
              provides[getDesc(header)] = getProvides(header)
              packages.append(getDesc(header) + (subdir, file,))
              names.extend(header[rpm.RPMTAG_PROVIDES])
print "Sorting..."
names = list(set(names))
names.sort()

print "Searching Packages..."
for i in provides.keys():
  for j in provides[i]:
    if sys.argv[1] in j:
      print i, "provides:", sys.argv[1]
