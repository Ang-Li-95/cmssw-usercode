# this script must be run from One2Two/

import sys, os, shutil, time
from JMTucker.Tools.general import save_git_status
from JMTucker.Tools.CondorSubmitter import CondorSubmitter
import ROOT; ROOT.gROOT.SetBatch()
import limitsinput

# The combine tarball is made in a locally checked-out combine environment so
# the worker nodes don't have to git clone, etc. In this environment, run
#   cmsMakeTarball.py --standalone > /tmp/tarball.py
# Then, *in the combine environment* do
#   /tmp/tarball.py --include-bin combine.tgz

script_template = '''#!/bin/bash
echo combine script starting at $(date) with args $*

export JOB=$1
export WHICH=$2
export WD=$(pwd)

source /cvmfs/cms.cern.ch/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
scram project CMSSW CMSSW_10_2_13 2>&1 >/dev/null
cd CMSSW_10_2_13/src
eval `scram runtime -sh`

cd ..
xrdcp -s root://cmseos.fnal.gov//store/user/tucker/combine_sl7_801.tgz combine.tgz
tar xf combine.tgz
scram b 2>&1 >/dev/null
hash -r
which combine

cd $WD

{
    echo "========================================================================="
    echo datacard:
    python datacard.py $WHICH __DATACARDARGS__ > datacard.txt
    awk '{print "DATACARD: " $0}' datacard.txt

    cmd="combine -H AsymptoticLimits -M MarkovChainMC --noDefaultPrior=0 --tries 20 -b 200 --iteration 100000 datacard.txt"

    if [[ $JOB == 0 ]]; then
        echo "========================================================================="
        echo Observed limit
        eval $cmd
        mv higgsCombine*root observed.root

#       echo "========================================================================="
#       echo Observed limit, no systematics
#       eval $cmd -S0
#       mv higgsCombine*root observed_S0.root
    fi

    echo "========================================================================="
    echo Expected limits
    eval $cmd --toys 100 --saveToys -s $((JOB+13068931))
    mv higgsCombine*root expected_${JOB}.root

#   echo "========================================================================="
#   echo Expected limits, no systematics
#   eval $cmd -S0 --toys 100 --saveToys -s $((JOB+13068931))
#   mv higgsCombine*root expected_S0_${JOB}.root

########################################################################

#   cmd="combine -M GoodnessOfFit --algo=saturated datacard.txt"
#
#   if [[ $JOB == 0 ]]; then
#       echo "========================================================================="
#       echo GoodnessOfFit observed
#       eval $cmd
#       mv higgsCombine*root gof_observed.root
#
#       echo "========================================================================="
#       echo GoodnessOfFit observed, no systematics
#       eval $cmd -S0
#       combine -S0 -M GoodnessOfFit datacard.txt --algo=saturated
#       mv higgsCombine*root gof_S0_observed.root
#   fi
#
#   echo "========================================================================="
#   echo GoodnessOfFit expected
#   eval $cmd --toys 100 -s $((JOB+13068931))
#   mv higgsCombine*root gof_expected_${JOB}.root
#
#   echo "========================================================================="
#   echo GoodnessOfFit expected, no systematics
#   eval $cmd -S0 --toys 100 -s $((JOB+13068931))
#   mv higgsCombine*root gof_S0_expected_${JOB}.root

########################################################################

#   cmd="combine -M Significance datacard.txt"
#
#   if [[ $JOB == 0 ]]; then
#       echo "========================================================================="
#       echo Observed significance
#       eval $cmd
#       mv higgsCombine*root signif_observed.root
#       
#       echo "========================================================================="
#       echo Observed significance, no systematics
#       eval $cmd -S0
#       mv higgsCombine*root signif_observed_S0.root
#   fi
#
#   echo "========================================================================="
#   echo Expected significance
#   eval $cmd --toys 100 -saveToys -s $((JOB+13068931))
#   mv higgsCombine*root signif_expected_${JOB}.root
#
#   echo "========================================================================="
#   echo Expected significances, no systematics
#   eval $cmd -S0 --toys 100 -saveToys -s $((JOB+13068931))
#   mv higgsCombine*root signif_expected_S0_${JOB}.root
} 2>&1 | gzip -c > combine_output_${JOB}.txt.gz
'''

if 'save_toys' not in sys.argv:
    script_template = script_template.replace(' --saveToys', '')

datacard_args = []

bkg_correlation = [x for x in ['bkg_fully_correlated', 'bkg_yearwise_correlated', 'bkg_binwise_correlated', 'bkg_fully_correlated'] if x in sys.argv]
assert len(bkg_correlation) <= 1
if bkg_correlation:
    datacard_args.append(bkg_correlation[0])

include_2016 = 'include_2016' in sys.argv
if include_2016:
    datacard_args.append('include_2016')

script_template = script_template.replace('__DATACARDARGS__', ' '.join(datacard_args))

jdl_template = '''universe = vanilla
Executable = run.sh
arguments = $(Process) %(isample)s
Output = stdout.$(Process)
Error = stderr.$(Process)
Log = log.$(Process)
stream_output = true
stream_error  = false
notification  = never
should_transfer_files = YES
when_to_transfer_output = ON_EXIT
transfer_input_files = %(input_files)s
+REQUIRED_OS = "rhel7"
+DesiredOS = REQUIRED_OS
Queue 50
'''

batch_root = '/uscms_data/d2/tucker/crab_dirs/combine_output_%i' % time.time()
if os.path.isdir(batch_root):
    raise IOError('%s exists' % batch_root)
print batch_root
os.mkdir(batch_root)
os.mkdir(os.path.join(batch_root, 'inputs'))

save_git_status(os.path.join(batch_root, 'gitstatus'))

input_files = []
for x in ['signal_efficiency.py', 'datacard.py', 'limitsinput.root']:
    nx = os.path.abspath(os.path.join(batch_root, 'inputs', os.path.basename(x)))
    shutil.copy2(x, nx)
    input_files.append(nx)
input_files = ','.join(input_files)

f = ROOT.TFile('limitsinput.root')

years = ('2016','2017','2018') if include_2016 else ('2017','2018')
samples = limitsinput.sample_iterator(f,
                                      require_years=years,
                                      test='test_batch' in sys.argv,
                                      slices_1d='slices_1d' in sys.argv,
                                      )
names = set(s.name for s in samples)
allowed = [arg for arg in sys.argv if arg in names]

for sample in samples:
    if allowed and sample.name not in allowed:
        continue

    print sample.isample, sample.name,
    isample = sample.isample # for locals use below

    batch_dir = os.path.join(batch_root, 'signal_%05i' % sample.isample)
    os.mkdir(batch_dir)
    open(os.path.join(batch_dir, 'nice_name'), 'wt').write(sample.name)

    run_fn = os.path.join(batch_dir, 'run.sh')
    open(run_fn, 'wt').write(script_template % locals())

    open(os.path.join(batch_dir, 'cs_dir'), 'wt')
    open(os.path.join(batch_dir, 'cs_submit.jdl'), 'wt').write(jdl_template % locals())

    CondorSubmitter._submit(batch_dir, 50)

# zcat signal_*/combine_output* | sort | uniq | egrep -v '^median expected limit|^mean   expected limit|^Observed|^Limit: r|^Generate toy|^Done in|random number generator seed is|^   ..% expected band' >! /tmp/duh