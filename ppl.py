#!/usr/bin/env python2
import plistlib as pll
import sys
import argparse
from pprint import pprint, pformat
import json
import yaml


def main(argv):
    opts = parse_args(argv)
    data = parse_file(opts.ifile, opts)
    if opts.fmt == 'xml':
        converted = pll.writePlistToString(data)
    else:
        normalized = normalize_types(data)
        converted = convert_data(normalized, opts)
    return write_output(converted, opts)

def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Converts plists to xml, yaml and json.'
    )
    parser.add_argument('-j', '--json',
        dest='fmt', action='store_const', const='json', default='xml',
        help='output in JSON format')
    parser.add_argument('-y', '--yaml',
        dest='fmt', action='store_const', const='yaml', default='xml',
        help='output in YAML format')
    parser.add_argument('-p', '--pprint',
        dest='fmt', action='store_const', const='pprint', default='xml',
        help='output in Python\'s pprint format')
    parser.add_argument('-x', '--xml',
        dest='fmt', action='store_const', const='xml', default='xml',
        help='output as plist xml (default)')
    #parser.add_argument('-f', '--force',
    #    help='try to represent all data, even if the conversion is irreversible. ' +
    #    '(--json and --yaml only. Data fields will be represented as strings.)')
    #parser.add_argument('-n', '--no-annotate',
    #    help='remove comment indicating which fields were converted and how ' +
    #    '(--json or --yaml only when using --force)')
    parser.add_argument('ifile',
        default=sys.stdin, nargs='?', metavar='IFILE',
        help='the file to convert (default: stdin)')
    parser.add_argument('-o', '--out',
        dest='ofile', default=sys.stdout,
        help='the file to write the result to (default: stdout)')
    opts = parser.parse_args(args[1:])    
    return opts

def parse_file(f, opts):
    plist = pll.readPlist(f)
    return plist

def parse_string(s, opts):
    plist = pll.readPlistFromString(s)
    return plist

def normalize_types(data):
    """
    This allows YAML and JSON to store Data fields as strings. However, this
    operation is irreversible.  Only use if read-only access to the plist is
    required.
    """
    if isinstance(data, pll.Data): return data.data
    if isinstance(data, list):
        retval = []
        for child in data:
            retval.append(normalize_types(child))
        return retval
    if isinstance(data, dict):
        retval = {}
        for key, child in data.iteritems():
            retval[key] = normalize_types(child)
        return retval
    return data

def convert_data(data, opts):
    if opts.fmt == 'yaml':
        return yaml.dump(data, width=float('inf'), default_flow_style=False)
    if opts.fmt == 'json':
        return json.dumps(data, sort_keys=True, indent=4)
    #if opts.fmt == 'pprint':  # default
    return pformat(data)

def write_output(s, opts):
    if s[-1] != '\n': s += '\n'
    if isinstance(opts.ofile, file):
        return opts.ofile.write(s)
    with open(opts.ofile, 'w') as f:
        return f.write(s)

main(sys.argv)
