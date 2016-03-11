#!/bin/bash

#exec 2>&1

JOBNUM=$1
TODO=$2
MAXEVENTS=$3

INDIR=$(pwd)
OUTDIR=$(pwd)

eval $(scram unsetenv -sh)

echo JOBNUM: ${JOBNUM}
echo TODO: ${TODO}
echo MAXEVENTS: ${MAXEVENTS}

################################################################################

echo
echo START GENSIM

(
scram project -n GENSIM CMSSW CMSSW_7_1_21_patch2
cd GENSIM/src
eval $(scram runtime -sh)
cd ../..

echo cmsRun
cmsRun gensim.py \
    jobnum=${JOBNUM} \
    ${MAXEVENTS} \
    ${TODO} \
    2>&1

EXITCODE=${PIPESTATUS[0]}
if [ $EXITCODE -eq 0 ]; then
    gzip RandomEngineState.xml
    mv RandomEngineState.xml.gz RandomEngineState_GENSIM.xml.gz
    echo GENSIM ls -l
    ls -l
fi

exit $EXITCODE
)

EXITCODE=$?
if [ $EXITCODE -ne 0 ]; then
  echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  echo @@@@ cmsRun exited GENSIM step with error code $EXITCODE
  echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  exit $EXITCODE
fi

echo END GENSIM

################################################################################

echo START RAWHLT

(
scram project -n RAWHLT CMSSW CMSSW_7_6_1
cd RAWHLT/src
eval $(scram runtime -sh)
cd ../..

echo cmsRun
cmsRun rawhlt.py 2>&1

EXITCODE=${PIPESTATUS[0]}
if [ $EXITCODE -eq 0 ]; then
    gzip RandomEngineState.xml
    mv RandomEngineState.xml.gz RandomEngineState_RAWHLT.xml.gz
    echo RAWHLT ls -l
    ls -l
fi

exit $EXITCODE
)

EXITCODE=$?
if [ $EXITCODE -ne 0 ]; then
  echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  echo @@@@ cmsRun exited RAWHLT step with error code $EXITCODE
  echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  exit $EXITCODE
fi

echo END RAWHLT

################################################################################

echo START RECO

(
scram project -n RECO CMSSW CMSSW_7_6_1
cd RECO/src
eval $(scram runtime -sh)
cd ../..

echo cmsRun
cmsRun -j FrameworkJobReport.xml reco.py 2>&1

EXITCODE=${PIPESTATUS[0]}
if [ $EXITCODE -eq 0 ]; then
    echo RECO ls -l
    ls -l
fi

exit $EXITCODE
)

EXITCODE=$?
if [ $EXITCODE -ne 0 ]; then
  echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  echo @@@@ cmsRun exited RECO step with error code $EXITCODE
  echo @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  exit $EXITCODE
fi

echo END RECO
