import sys
from JMTucker.Tools.BasicAnalyzer_cfg import *
debug = 'debug' in sys.argv

process.source.fileNames = ['root://osg-se.cac.cornell.edu//xrootd/path/cms/store/user/tucker/mfv_neu_tau01000um_M0800/gen/150728_203042/0000/gen_1.root']
process.TFileService.fileName = 'gen_histos.root'
file_event_from_argv(process)

#process.load('JMTucker.MFVNeutralino.GenParticleFilter_cfi')
#process.mfvGenParticleFilter.required_num_leptonic = 0

process.load('JMTucker.MFVNeutralino.GenHistos_cff')

#process.p = cms.Path(process.mfvGenParticleFilter * process.mfvGenHistos)
process.p = cms.Path(process.mfvGenHistos)

if debug:
    process.printList = cms.EDAnalyzer('JMTParticleListDrawer',
                                       src = cms.InputTag('genParticles'),
                                       printVertex = cms.untracked.bool(True),
                                       )
    process.p.insert(0, process.printList)

if __name__ == '__main__' and hasattr(sys, 'argv') and 'submit' in sys.argv:
    
    from JMTucker.Tools.Sample import anon_samples

    samples = anon_samples('''
/mfv_neu_tau00100um_M0400/tucker-gen-30031245991cdc59a4e779a57f211d2a/USER
/mfv_neu_tau00100um_M0800/tucker-gen-30031245991cdc59a4e779a57f211d2a/USER
/mfv_neu_tau00100um_M1200/tucker-gen-30031245991cdc59a4e779a57f211d2a/USER
/mfv_neu_tau00100um_M1600/tucker-gen-30031245991cdc59a4e779a57f211d2a/USER
/mfv_neu_tau00300um_M0400/tucker-gen-297aaf8461e8651140243c6762af3145/USER
/mfv_neu_tau00300um_M0800/tucker-gen-297aaf8461e8651140243c6762af3145/USER
/mfv_neu_tau00300um_M1200/tucker-gen-297aaf8461e8651140243c6762af3145/USER
/mfv_neu_tau00300um_M1600/tucker-gen-297aaf8461e8651140243c6762af3145/USER
/mfv_neu_tau01000um_M0400/tucker-gen-80424ff51c64a4a42ab32d70ea13233c/USER
/mfv_neu_tau01000um_M0800/tucker-gen-80424ff51c64a4a42ab32d70ea13233c/USER
/mfv_neu_tau01000um_M1200/tucker-gen-80424ff51c64a4a42ab32d70ea13233c/USER
/mfv_neu_tau01000um_M1600/tucker-gen-80424ff51c64a4a42ab32d70ea13233c/USER
/mfv_neu_tau10000um_M0400/tucker-gen-d9ae25c69fb344d73087168fa6b951ad/USER
/mfv_neu_tau10000um_M0800/tucker-gen-d9ae25c69fb344d73087168fa6b951ad/USER
/mfv_neu_tau10000um_M1200/tucker-gen-d9ae25c69fb344d73087168fa6b951ad/USER
/mfv_neu_tau10000um_M1600/tucker-gen-d9ae25c69fb344d73087168fa6b951ad/USER
''', dbs_inst='phys03')

    from JMTucker.Tools.CRAB3Submitter import CRABSubmitter
    cs = CRABSubmitter('GenHistos',
                       splitting = 'EventAwareLumiBased',
                       units_per_job = 20000,
                       total_units = -1,
                       )
    cs.submit_all(samples)
