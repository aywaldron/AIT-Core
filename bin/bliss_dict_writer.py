#!/usr/bin/env python
'''
Usage:
        bliss_dict_writer.py [options] (--tlm | --cmd)

--tlm               Run dictionary processor for Telemetry dictionary.
--cmd               Run dictionary processor for Command dictionary.
--format=<format>   Specify output format. Possible values: csv
                    [Default: csv]
--path=<path>       Output file path.


Description:
        BLISS TLM and CMD Dictionary Definitions to Specified Output Format

        Outputs BLISS TLM and CMD Dictionary Definitions in Specific output format. Currently supports:
        * TLM -> CSV

        TODO
        * TLM -> TeX
        * CMD -> CSV
        * CMD -> TeX

        Copyright 2016 California Institute of Technology.  ALL RIGHTS RESERVED.
        U.S. Government Sponsorship acknowledged.

'''

from docopt import docopt

import bliss
import sys

if __name__ == '__main__':
    arguments = docopt(__doc__)

    # output format for the file
    format = arguments.pop('--format')

    # output path
    path = arguments.pop('--path') or ''

    # initialize telemetry dictionary writer
    if arguments.pop('--tlm'):
        writer = bliss.tlm.TlmDictWriter()

    # initialize command dictionary writer
    if arguments.pop('--cmd'):
        bliss.log.error("Not yet supported")
        sys.exit()

    # write to csv
    if format == 'csv':
        writer.writeToCSV(output_path=path)
    else:
        bliss.log.error("Invalid <format> specified.")