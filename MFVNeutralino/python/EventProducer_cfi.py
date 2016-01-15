import FWCore.ParameterSet.Config as cms

from JMTucker.Tools.L1GtUtils_cff import l1GtUtilsTags
from JMTucker.Tools.PATTupleSelection_cfi import jtupleParams

mfvEvent = cms.EDProducer('MFVEventProducer',
                          l1GtUtilsTags,
                          trigger_results_src = cms.InputTag('TriggerResults', '', 'HLT'),
                          cleaning_results_src = cms.InputTag('TriggerResults', '', 'PAT'),
                          skip_event_filter = cms.string('pevtsel'),
                          jet_pt_min = cms.double(20),
                          beamspot_src = cms.InputTag('offlineBeamSpot'),
                          primary_vertex_src = cms.InputTag('goodOfflinePrimaryVertices'),
                          gen_info_src = cms.InputTag('generator'),
                          gen_particles_src = cms.InputTag('genParticles'),
                          calojets_src = cms.InputTag(''),
                          jets_src = cms.InputTag('selectedPatJets'),
                          met_src = cms.InputTag('patMETsNoHF'),
                          b_discriminator = cms.string('pfCombinedInclusiveSecondaryVertexV2BJetTags'),
                          b_discriminator_mins = cms.vdouble(0.46, 0.8, 0.935),
                          muons_src = cms.InputTag('selectedPatMuons'),
                          muon_semilep_cut = jtupleParams.semilepMuonCut,
                          muon_dilep_cut = jtupleParams.dilepMuonCut,
                          electrons_src = cms.InputTag('selectedPatElectrons'),
                          electron_semilep_cut = jtupleParams.semilepElectronCut,
                          electron_dilep_cut = jtupleParams.dilepElectronCut,
                          vertex_seed_pt_quantiles_src = cms.InputTag('mfvVertices'),
                          )
