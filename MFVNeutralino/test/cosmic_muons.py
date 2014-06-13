import os, sys
from JMTucker.Tools.BasicAnalyzer_cfg import cms, process

process.source.fileNames = '''/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_1_1_X2h.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_2_2_vbl.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_3_2_yEE.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_4_1_vkj.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_5_3_Tce.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_6_1_a0t.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_7_2_Qv8.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_8_1_3WZ.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_9_1_ANl.root
/store/user/tucker/mfv_neutralino_tau1000um_M0400/mfv_neutralino_tau1000um_M0400/a6ab3419cb64660d6c68351b3cff9fb0/aodpat_10_1_VPN.root'''.split('\n')
process.TFileService.fileName = 'cosmic_muons.root'

from HLTrigger.HLTfilters.hltHighLevel_cfi import hltHighLevel
process.triggerFilter = hltHighLevel.clone()
process.triggerFilter.HLTPaths = ['HLT_QuadJet50_v*']
process.triggerFilter.andOr = True # = OR

process.CosmicMuons = cms.EDAnalyzer('CosmicMuons',
                                     track_src = cms.InputTag('globalCosmicMuons'),
                                     primary_vertex_src = cms.InputTag('goodOfflinePrimaryVertices'),
                                     beamspot_src = cms.InputTag('offlineBeamSpot'),
                                     general_track_src = cms.InputTag('generalTracks'),
                                     gen_particle_src = cms.InputTag('genParticles'),
                                     min_pt = cms.double(5),
                                     max_eta = cms.double(2.4),
                                     min_npxhits = cms.int32(1),
                                     min_nsthits = cms.int32(6),
                                     min_nmuhits = cms.int32(2),
                                     min_dxy = cms.double(0),
                                     max_relpterr = cms.double(0.5),
                                     )

process.CosmicMuonsPt1Nsthits6Dxy0 = process.CosmicMuons.clone(min_pt = 1)
process.CosmicMuonsPt1Nsthits6Dxy100 = process.CosmicMuons.clone(min_pt = 1, min_dxy = 0.01)
process.CosmicMuonsPt1Nsthits8Dxy0 = process.CosmicMuons.clone(min_pt = 1, min_nsthits = 8)
process.CosmicMuonsPt1Nsthits8Dxy100 = process.CosmicMuons.clone(min_pt = 1, min_nsthits = 8, min_dxy = 0.01)
process.CosmicMuonsPt5Nsthits6Dxy0 = process.CosmicMuons.clone()
process.CosmicMuonsPt5Nsthits6Dxy100 = process.CosmicMuons.clone(min_dxy = 0.01)
process.CosmicMuonsPt5Nsthits8Dxy0 = process.CosmicMuons.clone(min_nsthits = 8)
process.CosmicMuonsPt5Nsthits8Dxy100 = process.CosmicMuons.clone(min_nsthits = 8, min_dxy = 0.01)

process.p = cms.Path(process.triggerFilter
                   * process.CosmicMuonsPt1Nsthits6Dxy0
                   * process.CosmicMuonsPt1Nsthits6Dxy100
                   * process.CosmicMuonsPt1Nsthits8Dxy0
                   * process.CosmicMuonsPt1Nsthits8Dxy100
                   * process.CosmicMuonsPt5Nsthits6Dxy0
                   * process.CosmicMuonsPt5Nsthits6Dxy100
                   * process.CosmicMuonsPt5Nsthits8Dxy0
                   * process.CosmicMuonsPt5Nsthits8Dxy100)

if __name__ == '__main__' and hasattr(sys, 'argv') and 'submit' in sys.argv:
    from JMTucker.Tools.Samples import mfv_signal_samples
    from JMTucker.Tools.CRABSubmitter import CRABSubmitter

    cs = CRABSubmitter('CosmicMuons',
                       total_number_of_events = -1,
                       events_per_job = 10000,
                       )

    samples = mfv_signal_samples
    cs.submit_all(samples)
