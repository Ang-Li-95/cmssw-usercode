# this script sets up a working directory like crab would do--don't
# run nstep.sh/cmsRun in the same shell, but rather make a new one as
# the print out will instruct

echo be sure to change year.txt and steering.sh settings to what you want
owd=$(pwd)
input_version=$CMSSW_VERSION
tmpdir=/dev/shm/$USER/nstep_tryit_$(date +%s)
echo $tmpdir
mkdir -p $tmpdir 
edmConfigDump dummy.py > $tmpdir/pset.py
cp nstep.sh todoify.sh gensim.py modify.py dynamicconf.py scanpack.py rawhlt.py minbias.py minbias.txt.gz minbias_premix_*.txt.gz private_minbias.txt.gz reco.py miniaod.py fixfjr.py pythia8240.sh pythia8240-GeneratorInterface.tgz $tmpdir
for x in ntuple.py minitree.py; do
    cmsDumpPython.py ../$x > $tmpdir/$x
done
cd $tmpdir
scram project CMSSW $input_version
cd $input_version
cmsMakeTarball.py input.tgz
tar xf input.tgz
echo 2018 > $tmpdir/year.txt
cat > $tmpdir/steering.sh <<EOF
MAXEVENTS=1
EXPECTEDEVENTS=1
USETHISCMSSW=0
TRIGFILTER=0
PREMIX=1
export DUMMYFORHASH=1512629531475509
OUTPUTLEVEL=reco
SALT="saltissalty"
TODO=todo=mfv_neutralino,1.0,800
TODORAWHLT=SETME
TODORECO=SETME
TODONTUPLE=SETME
PYTHIA8240=1
EOF
echo in new shell, issue e.g.
echo "cd $tmpdir/$input_version/src ; source /cvmfs/cms.cern.ch/cmsset_default.sh ; eval \$(scramv1 runtime -sh) ; cd ../.. ; ./nstep.sh 1"
cd $owd
