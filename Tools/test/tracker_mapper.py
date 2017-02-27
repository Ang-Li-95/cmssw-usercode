import sys
from JMTucker.Tools.BasicAnalyzer_cfg import cms, process

import JMTucker.Tools.SampleFiles as sf
sf.set_process(process, 'qcdht2000', 'main', 4)
process.TFileService.fileName = 'tracker_mapper.root'

import JMTucker.MFVNeutralino.TriggerFilter
JMTucker.MFVNeutralino.TriggerFilter.setup_trigger_filter(process)

process.TrackerMapper = cms.EDAnalyzer('TrackerMapper',
                                       track_src = cms.InputTag('generalTracks'),
                                       beamspot_src = cms.InputTag('offlineBeamSpot'),
                                       primary_vertex_src = cms.InputTag('offlinePrimaryVertices'),
                                       pileup_weights = cms.vdouble(*([1]*100)),
                                       )

process.p = cms.Path(process.triggerFilter * process.TrackerMapper)

if __name__ == '__main__' and hasattr(sys, 'argv') and 'submit' in sys.argv:
    import JMTucker.Tools.Samples as Samples

    samples = [Samples.qcdht2000] + Samples.my_qcd_test_samples
    for s in samples:
        s.events_per = 5000

    from JMTucker.Tools.MetaSubmitter import *
    ms = MetaSubmitter('TrackerMapper_testqcdht2000_15')
    ms.submit(samples)
