#!/usr/bin/env python

"""
Get information about all SI modes using SACGS tools and store as files
"si_modes/<SI_MODE>".  This can be re-run when new SI modes are added.

Usage::

  ./get_si_modes.py
"""

import sys
import os

from Chandra.cmd_states import fetch_states
import Ska.Shell


def evenify(si_mode):
    """Make ``si_mode`` end in an even hex digit"""
    # Translate an odd digit to corresponding even one
    translate = {chr(ord(x) + 1): x for x in '02468ACE'}
    last = si_mode[-1]
    return si_mode[:-1] + translate.get(last, last)


def main():
    """
    Get information about all SI modes using SACGS tools and store as files
    "si_modes/<SI_MODE>".
    """
    states = fetch_states('2000:001', vals=['si_mode'])
    si_modes = set(states['si_mode'])

    bash = Ska.Shell.Spawn(shell=True, stdout=None)

    for si_mode in sorted(si_modes):
        outfile = os.path.join('si_modes', si_mode)
        fail_outfile = os.path.join('si_modes', 'FAIL_' + si_mode)
        if os.path.exists(outfile) or os.path.exists(fail_outfile):
            print 'Skipping', si_mode
            continue
        print 'Processing', si_mode, evenify(si_mode)
        cmd = ('/data/acis/sacgs/bin/ratcfg '
               '-d /data/acis/cmdgen/sacgs/current.dat '
               '-c /data/acis/sacgs/odb/current.cfg {} '
               '| /data/acis/cmdgen/sacgs/bin/lcmd -r -v '
               .format(evenify(si_mode)))
        status = bash.run(cmd)
        if status or len(bash.outlines) < 10:
            print 'Some problem status=', status
            outfile = fail_outfile

        sys.stdout.flush()
        with open(outfile, 'w') as f:
            f.writelines(bash.outlines)


if __name__ == '__main__':
    main()
