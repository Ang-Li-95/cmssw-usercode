#!/usr/bin/env python

from JMTucker.Tools.CMSSWTools import set_events_to_process
from JMTucker.Tools.PATTuple_cfg import *

runOnMC = True # magic line, don't touch
njets = 2
nbjets = 1

process, common_seq = pat_tuple_process(runOnMC)
no_skimming_cuts(process)
process.patMuonsPF.embedTrack = False
process.patElectronsPF.embedTrack = False

process.TFileService = cms.Service('TFileService',
                                   fileName = cms.string('movedtree.root'))

process.RandomNumberGeneratorService = cms.Service('RandomNumberGeneratorService',
                                                   mfvMovedTracks = cms.PSet(initialSeed = cms.untracked.uint32(1220)))

del process.out
del process.outp

process.load('JMTucker.MFVNeutralino.Vertexer_cff')
process.load('JMTucker.MFVNeutralino.EventProducer_cfi')

process.mfvEvent.cleaning_results_src = ''

cleaning_seq = process.eventCleaningAll._seq
for p in process.paths.keys():
    delattr(process, p)

process.p = cms.Path(cleaning_seq * common_seq * process.mfvEvent)

import JMTucker.MFVNeutralino.TriggerFilter
JMTucker.MFVNeutralino.TriggerFilter.setup_trigger_filter(process)

process.mfvMovedTracks = cms.EDProducer('MFVTrackMover',
                                        tracks_src = cms.InputTag('generalTracks'),
                                        primary_vertices_src = cms.InputTag('goodOfflinePrimaryVertices'),
                                        jets_src = cms.InputTag('selectedPatJetsPF'),
                                        min_jet_pt = cms.double(50),
                                        min_jet_ntracks = cms.uint32(4),
                                        b_discriminator = cms.string('combinedSecondaryVertexBJetTags'),
                                        b_discriminator_veto = cms.double(0.244),
                                        b_discriminator_tag = cms.double(0.898),
                                        njets = cms.uint32(njets),
                                        nbjets = cms.uint32(nbjets),
                                        tau = cms.double(1),
                                        sig_theta = cms.double(0.2),
                                        sig_phi = cms.double(0.2),
                                        )

process.mfvVertices.track_src = 'mfvMovedTracks'
process.p *= process.mfvMovedTracks * process.mfvVertexSequence

process.load('JMTucker.MFVNeutralino.WeightProducer_cfi')
process.p *= process.mfvWeight

process.mfvMovedTree = cms.EDAnalyzer('MFVMovedTracksTreer',
                                      event_src = cms.InputTag('mfvEvent'),
                                      weight_src = cms.InputTag('mfvWeight'),
                                      mover_src = cms.string('mfvMovedTracks'),
                                      vertices_src = cms.InputTag('mfvVerticesAux'),
                                      max_dist2move = cms.double(0.02),
                                      )

process.p *= process.mfvMovedTree

if __name__ == '__main__' and hasattr(sys, 'argv') and 'submit' in sys.argv:
    from JMTucker.Tools.CRABSubmitter import CRABSubmitter
    import JMTucker.Tools.Samples as Samples

    def modify(sample):
        to_add = []
        to_replace = []

        if not sample.is_mc:
            magic = 'runOnMC = True'
            err = 'trying to submit on data, and tuple template does not contain the magic string "%s"' % magic
            to_replace.append((magic, 'runOnMC = False', err))
            if sample.name.startswith('MultiJetPk2012'):
                for name_part, tag in [
                    ('2012B', 'FT_53_V6C_AN4'),
                    ('2012C1', 'FT53_V10A_AN4'),
                    ('2012C2', 'FT_P_V42C_AN4'),
                    ('2012D1', 'FT_P_V42_AN4'),
                    ('2012D2', 'FT_P_V42D_AN4'),
                    ]:
                    if name_part in sample.name:
                        to_add.append('process.GlobalTag.globaltag = "%s::All"' % tag)
            to_add.append('process.dummyToMakeDiffHash = cms.PSet(submitName = cms.string("%s"))' % (sample.name + 'hello'))

        return to_add, to_replace

    cs = CRABSubmitter('TrackMover',
                       pset_modifier = modify,
                       job_control_from_sample = True,
                       get_edm_output = False,
                       data_retrieval = 'fnal',
                       publish_data_name = 'trackmover%i%i' % (njets, nbjets),
                       max_threads = 3,
                       )

    timing = { 'dyjetstollM10': 0.011203, 'dyjetstollM50': 0.019867, 'qcdbce020': 0.008660, 'qcdbce030': 0.007796, 'qcdbce080': 0.061260, 'qcdbce170': 0.328891, 'qcdbce250': 0.481813, 'qcdbce350': 0.519482, 'qcdem020': 0.010137, 'qcdem030': 0.01, 'qcdem080': 0.037925, 'qcdem170': 0.286123, 'qcdem250': 0.471398, 'qcdem350': 0.686303, 'qcdht0100': 0.008273, 'qcdht0250': 0.116181, 'qcdht0500': 0.738374, 'qcdht1000': 1.002745, 'qcdmu0020': 0.012301, 'qcdmu0030': 0.015762, 'qcdmu0050': 0.018178, 'qcdmu0080': 0.119300, 'qcdmu0120': 0.245562, 'qcdmu0170': 0.32, 'qcdmu0300': 0.419818, 'qcdmu0470': 0.584266, 'qcdmu0600': 0.455305, 'qcdmu0800': 0.879171, 'qcdmu1000': 1.075712, 'singletop_s': 0.093429, 'singletop_s_tbar': 0.146642, 'singletop_tW': 0.327386, 'singletop_tW_tbar': 0.184349, 'singletop_t': 0.092783, 'singletop_t_tbar': 0.060983, 'ttbarhadronic': 0.752852, 'ttbarsemilep': 0.419073, 'ttbardilep': 0.295437, 'ttgjets': 0.861987, 'ttwjets': 0.714156, 'ttzjets': 0.827464, 'wjetstolnu': 0.010842, 'ww': 0.046754, 'wz': 0.049839, 'zz': 0.059791, }

    for sample in Samples.all_mc_samples:
        if timing.has_key(sample.name):
            sample.events_per = int(3.5*3600/timing[sample.name]/2)
            sample.timed = True
            nj = int(sample.nevents_orig / float(sample.events_per)) + 1
            assert nj < 5000

    for sample in Samples.data_samples:
        sample.lumis_per = 15

    samples = Samples.from_argv(Samples.data_samples + Samples.ttbar_samples + Samples.qcd_samples)

    for sample in samples:
        if sample.is_mc:
            sample.total_events = -1
            assert hasattr(sample, 'timed')
        else:
            sample.json = '../ana_all.json'
            sample.total_lumis = -1

    cs.submit_all(samples)
