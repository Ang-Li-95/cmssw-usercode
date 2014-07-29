import FWCore.ParameterSet.Config as cms

mfvAnalysisCuts = cms.EDFilter('MFVAnalysisCuts',
                               mevent_src = cms.InputTag('mfvEvent'),
                               trigger_bit = cms.int32(0),
                               re_trigger = cms.bool(False),
                               clean_bit = cms.int32(-1),
                               re_clean = cms.bool(True),
                               min_npv = cms.int32(0),
                               max_npv = cms.int32(100000),
                               min_4th_jet_pt = cms.double(60),
                               min_5th_jet_pt = cms.double(0),
                               min_6th_jet_pt = cms.double(0),
                               min_njets = cms.int32(4),
                               max_njets = cms.int32(100000),
                               min_nbtags = cms.vint32(0,0,0),
                               max_nbtags = cms.vint32(100000,100000,100000),
                               min_sumht = cms.double(500),
                               max_sumht = cms.double(1e9),
                               min_sum_other_pv_sumpt2 = cms.double(0),
                               max_sum_other_pv_sumpt2 = cms.double(1e9),
                               min_nmuons = cms.int32(0),
                               min_nsemilepmuons = cms.int32(0),
                               min_nleptons = cms.int32(0),
                               min_nsemileptons = cms.int32(0),
                               apply_vertex_cuts = cms.bool(True),
                               vertex_src = cms.InputTag('mfvSelectedVerticesTight'),
                               min_nvertex = cms.int32(2),
                               max_nvertex = cms.int32(100000),
                               min_ntracks01 = cms.int32(0),
                               max_ntracks01 = cms.int32(100000),
                               min_maxtrackpt01 = cms.double(0),
                               max_maxtrackpt01 = cms.double(1e9),
                               min_njetsntks01 = cms.int32(0),
                               min_tkonlymass01 = cms.double(0),
                               min_jetsntkmass01 = cms.double(0),
                               min_tksjetsntkmass01 = cms.double(0),
                               min_absdeltaphi01 = cms.double(0),
                               min_bs2ddist01 = cms.double(0),
                               min_svdist2d = cms.double(0),
                               max_ntrackssharedwpv01 = cms.int32(100000),
                               max_ntrackssharedwpvs01 = cms.int32(100000),
                               max_fractrackssharedwpv01 = cms.double(1e9),
                               max_fractrackssharedwpvs01 = cms.double(1e9),
                               )

mfvAnalysisCutsSig = mfvAnalysisCuts.clone(
    vertex_src = 'mfvSelectedVerticesTightSig',
    min_svdist2d = 0.05,
    )
