import os, sys
from JMTucker.Tools.BasicAnalyzer_cfg import *

del process.TFileService
process.MessageLogger.cerr.FwkReport.reportEvery = 1

process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
add_analyzer('JMTParticleListDrawer',
             src = cms.InputTag('genParticles'),
             printVertex = cms.untracked.bool(True),
             )

input_from_argv()

if __name__ == '__main__' and hasattr(sys, 'argv') and 'submit' in sys.argv:
    crab_cfg = '''
[CRAB]
jobtype = cmssw
scheduler = condor

[CMSSW]
dbs_url = https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet
datasetpath = /QCD_Pt-15to30_TuneZ2star_8TeV_pythia6/tucker-sstoptuple_v1_qcd15-3312fbeda721580c3cdebaec6739016e/USER
pset = particle_list.py
total_number_of_events = -1
events_per_job = 1000

[USER]
ui_working_dir = crab_particle_list
return_data = 1
'''
    
    just_testing = 'testing' in sys.argv
    open('crab.cfg', 'wt').write(crab_cfg)
    if not just_testing:
        os.system('crab -create -submit')
        os.system('rm crab.cfg')
