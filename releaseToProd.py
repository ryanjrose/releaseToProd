#!/usr/bin/env python
"""releaseToProd
    Push staging environment to production via rsync.

    Usage:
        releaseToProd.py  [options]

    Options:
        -h --help       Show this screen.

        -c --config	YAML config file specifying source and target paths for code push

        -d --dry        Does not actually push code; Just show the files that would be pushed.

        --version       Show version.
"""
from docopt import docopt
from yaml import load as parseYAML
from subprocess import call
from os import getcwd
import os.path
import re
import sys

OPTS = docopt(__doc__, version='releaseToProd 1.0')
RSYNC = '/usr/bin/rsync'
SSH = '/usr/bin/ssh'
DEFAULT_CONFIG = os.getcwd() + '/config.yaml'

def chkOptions():
    if OPTS['--config'] == None:
        OPTS['--config'] = DEFAULT_CONFIG

    try:
        OPTS['config'] = parseYAML(open(OPTS['--config'], 'r').read())
    except IOError as e:
        if e.strerror == 'No such file or directory':
            print "{0}: {1}".format(e.strerror, DEFAULT_CONFIG)
        else:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        sys.exit()

def pushCode():
    for configKey in OPTS['config']:
        rsync_opts = '-avz --delete -e "ssh -oStrictHostKeyChecking=no"'

        if OPTS['--dry']:
            rsync_opts += ' --dry-run'

        p = re.compile('(.*?)\s+((.*?)@)?(.*?):(/.*)$')
        (src, ignore, tUser, tHost, tPath) = p.match(configKey).groups()

        if not tHost:
            print >>sys.stderr, 'No target host specified for code push; skipping.'

        #
        #  Add exclude options
        #
        if OPTS['config'][configKey] != None and 'excludeFiles' in OPTS['config'][configKey]:
            if OPTS['config'][configKey]['excludeFiles']:
                excludeStr = ""
                for excludeFile in OPTS['config'][configKey]['excludeFiles']:
                    excludeStr += " --exclude '{}'".format(excludeFile)
                rsync_opts += excludeStr

    cmd = RSYNC + " {} {} ".format(rsync_opts, src)
    if tUser:
        cmd += tUser + '@'

    if tHost:
        cmd += tHost + ':'

    if tPath:
        cmd += tPath

    if OPTS['--dry']:
        print "CMD: {}\n".format(cmd)

    try:
        retcode = call(cmd, shell=True)
        if retcode < 0:
            print >>sys.stderr, "Child was terminated by signal", -retcode
    except OSError as e:
        print >>sys.stderr, "Execution failed:", e

    #
    # Handle Post Processes
    #
    if OPTS['config'][configKey] != None and 'postProcess' in OPTS['config'][configKey]:
        if OPTS['config'][configKey]['postProcess']:
            for postProcess in OPTS['config'][configKey]['postProcess']:
                print "Running commmand: {}\n".format(postProcess)
                if not OPTS['--dry']:
                    try:
                        retcode = call(postProcess, shell=True)
                        if retcode < 0:
                            print >>sys.stderr, "Child was terminated by signal", -retcode
                    except OSError as e:
                        print >>sys.stderr, "Execution failed:", e

if __name__ == '__main__':
    chkOptions()
    pushCode()
