#!/usr/bin/env python

"""
Calculate rate of parallel and serial transfers for all
SI modes.

Computation reference is two emails from P. Plucinsky to
acisdude on 2012-Aug-24 ("CC mode and alternating exposure
modes" and "SI mode exposure time questions")
"""

import os
import re
import glob


def get_param(text, name):
    """
    Find the parameter ``name`` in ``text``, which should be the
    entire output of an SI mode query like::

      cmd = ('/data/acis/sacgs/bin/ratcfg '
             '-d /data/acis/cmdgen/sacgs/current.dat '
             '-c /data/acis/sacgs/odb/current.cfg {} '
             '| /data/acis/cmdgen/sacgs/bin/lcmd -r -v '
             .format(evenify(si_mode)))
    """
    regex = re.compile(r'^ \s*' + name + r'\s* = (.+)',
                       re.MULTILINE | re.VERBOSE)
    m = regex.search(text)
    if m:
        return m.group(1).strip()
    else:
        raise ValueError(name + ' not found')


def main(outfile='si_mode_rates.dat'):
    """
    Calculate rate of parallel and serial transfers for all
    SI modes.  Store results in si_mode_rates.dat
    """
    te_files = glob.glob('si_modes/TE_*')
    cc_files = glob.glob('si_modes/CC_*')

    with open(outfile, 'w') as out:
        for filename in te_files + cc_files:
            si_mode = os.path.basename(filename)
            with open(filename, 'r') as f:
                text = f.read()
            fep_sel = get_param(text, 'fepCcdSelect')
            n_ccd = sum(1 for x in fep_sel.split() if x != '10')
            if si_mode.startswith('TE'):
                prim_exp = int(get_param(text, 'primaryExposure'))
                start_row = int(get_param(text, 'subarrayStartRow'))
                row_count = int(get_param(text, 'subarrayRowCount'))

                prim_exp_sec = prim_exp / 10.0
                par_xfers = 1026 + start_row + row_count
                par_xfers_per_sec = par_xfers / prim_exp_sec * n_ccd
                ser_xfers_per_sec = row_count / prim_exp_sec * n_ccd
            else:
                prim_exp = -99
                start_row = 0
                row_count = 1023
                par_xfers_per_sec = 701.75 * n_ccd
                ser_xfers_per_sec = 1.0 / 0.00285

            out.write('{:9s} {:2d} {:3d} {:5d} {:5d} {:6.0f} {:6.0f}\n'
                      .format(si_mode, n_ccd, prim_exp, start_row, row_count,
                              par_xfers_per_sec, ser_xfers_per_sec))

if __name__ == '__main__':
    main()
