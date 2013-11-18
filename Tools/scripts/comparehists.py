#!/usr/bin/env python

import sys
from pprint import pprint
import JMTucker.Tools.argparse as argparse

parser = argparse.ArgumentParser(description = 'comparehists: compare all histograms in multiple files',
                                 usage = '%(prog)s [options] file1.root [file2.root ... fileN.root] dir_path plot_path')

parser.add_argument('positional', nargs='*')

parser.add_argument('--recurse', action='store_true',
                    help='Recurse down the directory structure, i.e. use all histograms in the given directory and all subdirectories.')
parser.add_argument('--per-page', type=int, default=100,
                    help='Put PER_PAGE histograms per html page (default: 100 per page).')
parser.add_argument('--only-n-first', type=int, default=-1,
                    help='Only do the first ONLY_N_FIRST histograms (default: do all).')
parser.add_argument('--size', nargs=2, type=int, default=(600,600), metavar='SIZE',
                    help='Set the plot size to SIZEX x SIZEY (default %(default)s.')
parser.add_argument('--nice', nargs='+', default=[],
                    help='Nice names for the files (default is file1, file2, ...).')
parser.add_argument('--colors', nargs='+', default=['ROOT.kRed', 'ROOT.kBlue', 'ROOT.kGreen+2', 'ROOT.kMagenta'],
                    help='Colors for the files: may be a python snippet, e.g. the default %(default)s.')

group = parser.add_argument_group('Callback function snippets: will be of the form lambda name, hists, curr: <snippet here>')
group.add_argument('--no-stats', default='False',
                    help='Snippet for no_stats lambda (default: %(default)s).')
group.add_argument('--apply-commands', default='None',
                  help='Snippet for apply_commands (default: %(default)s).')
group.add_argument('--separate-plots', default='None',
                  help='Snippet for separate_plots (default: %(default)s).')
group.add_argument('--skip', default='None',
                  help='Snippet for skip lambda (default: %(default)s).')
group.add_argument('--draw-command', default='""',
                   help='Snippet for draw_command lambda (default: %(default)s).')
group.add_argument('--scaling', default='1.',
                   help='Snippet for scaling lambda (default: %(default)s).')

options = parser.parse_args()

if len(options.positional) < 3:
    print 'Required args missing, including at least one filename\n'
    parser.print_help()
    sys.exit(1)

from JMTucker.Tools.ROOTTools import *

options.files = options.positional[:-2]
options.dir_path, options.plot_path = options.positional[-2:]
nfiles = len(options.files)

options.nice = options.nice[:nfiles]
while len(options.nice) < nfiles:
    options.nice.append('file%i' % (len(options.nice) + 1))

options.colors = options.colors[:nfiles]
options.colors = [eval(c) for c in options.colors]
ncolors = len(options.colors)
while len(options.colors) < nfiles:
    options.colors.append(ROOT.kMagenta + 1 + len(options.colors) - ncolors)

_lambda = 'lambda name, hists, curr: '
options.no_stats       = _lambda + options.no_stats
options.apply_commands = _lambda + options.apply_commands
options.separate_plots = _lambda + options.separate_plots
options.skip           = _lambda + options.skip
options.draw_command   = _lambda + options.draw_command
options.scaling        = _lambda + options.scaling
options.lambda_no_stats       = eval(options.no_stats)
options.lambda_apply_commands = eval(options.apply_commands)
options.lambda_separate_plots = eval(options.separate_plots)
options.lambda_skip           = eval(options.skip)
options.lambda_draw_command   = eval(options.draw_command)
options.lambda_scaling        = eval(options.scaling)

print 'comparehists running with these options:'
pprint(vars(options))

#import sys ; print 'argv:', sys.argv ; raise 1 ; sys.exit(1)

########################################################################

set_style()
ps = plot_saver(options.plot_path, size=options.size, per_page=options.per_page)

files = [ROOT.TFile(file) for file in options.files]
for i,f in enumerate(files):
    if not f.IsOpen():
        raise ValueError('file %s not readable' % options.files[i])

dirs = [file.Get(options.dir_path) for file in files]
for i,d in enumerate(dirs):
    if not issubclass(type(d), ROOT.TDirectory):
        raise ValueError('dir %s not found in file %s' % (options.dir_path, options.files[i]))

compare_all_hists(ps,
                  samples = zip(options.nice, dirs, options.colors),
                  recurse = options.recurse,
                  only_n_first = options.only_n_first,
                  no_stats = options.lambda_no_stats,
                  apply_commands = options.lambda_apply_commands,
                  separate_plots = options.lambda_separate_plots,
                  skip = options.lambda_skip,
                  draw_command = options.lambda_draw_command,
                  scaling = options.lambda_scaling,
                  )
