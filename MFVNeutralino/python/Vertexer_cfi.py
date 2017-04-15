import FWCore.ParameterSet.Config as cms

kvr_params = cms.PSet(
    maxDistance = cms.double(0.01),
    maxNbrOfIterations = cms.int32(10),
    doSmoothing = cms.bool(True),
)

mfvVertices = cms.EDProducer('MFVVertexer',
                             kvr_params = kvr_params,
                             avr_params = cms.PSet(
                                 finder = cms.string('avr'),
                                 primcut = cms.double(1.0),
                                 seccut = cms.double(3),
                                 smoothing = cms.bool(True)
                                 ),
                             beamspot_src = cms.InputTag('offlineBeamSpot'),
                             primary_vertices_src = cms.InputTag('goodOfflinePrimaryVertices'),
                             min_jet_pt_for_ht = cms.double(40),
                             disregard_event = cms.bool(False),
                             use_tracks = cms.bool(True),
                             track_src = cms.InputTag('generalTracks'),
                             use_non_pv_tracks = cms.bool(False),
                             use_non_pvs_tracks = cms.bool(False),
                             use_pf_candidates = cms.bool(False),
                             pf_candidate_src = cms.InputTag('particleFlow'),
                             use_pf_jets = cms.bool(False),
                             pf_jet_src = cms.InputTag('ak4PFJets'),
                             use_pat_jets = cms.bool(False),
                             pat_jet_src = cms.InputTag('selectedPatJets'),
                             use_second_tracks = cms.bool(False),
                             second_track_src = cms.InputTag('nothing'),
                             no_track_cuts = cms.bool(False),
                             min_seed_jet_pt = cms.double(30),
                             stlayers_v_eta = cms.bool(True),
                             min_all_track_pt = cms.double(1),
                             min_all_track_dxy = cms.double(0),
                             min_all_track_sigmadxy = cms.double(4),
                             min_all_track_sigmadxypv = cms.double(0),
                             min_all_track_hit_r = cms.int32(1),
                             min_all_track_nhits = cms.int32(0),
                             min_all_track_npxhits = cms.int32(0),
                             min_all_track_npxlayers = cms.int32(2),
                             min_all_track_nstlayers = cms.int32(3),
                             max_all_track_dxyerr = cms.double(1e9),
                             max_all_track_dxyipverr = cms.double(-1),
                             max_all_track_d3dipverr = cms.double(-1),
                             min_seed_track_pt = cms.double(1),
                             min_seed_track_dxy = cms.double(0),
                             min_seed_track_sigmadxy = cms.double(4),
                             min_seed_track_sigmadxypv = cms.double(0),
                             min_seed_track_hit_r = cms.int32(1),
                             min_seed_track_nhits = cms.int32(0),
                             min_seed_track_npxhits = cms.int32(0),
                             min_seed_track_npxlayers = cms.int32(2),
                             min_seed_track_nstlayers = cms.int32(3),
                             max_seed_track_dxyerr = cms.double(1e9),
                             max_seed_track_dxyipverr = cms.double(-1),
                             max_seed_track_d3dipverr = cms.double(-1),
                             max_seed_vertex_chi2 = cms.double(5),
                             use_2d_vertex_dist = cms.bool(False),
                             use_2d_track_dist = cms.bool(False),
                             merge_anyway_dist = cms.double(-1),
                             merge_anyway_sig = cms.double(3),
                             merge_shared_dist = cms.double(-1),
                             merge_shared_sig = cms.double(4),
                             max_track_vertex_dist = cms.double(-1),
                             max_track_vertex_sig = cms.double(5),
                             min_track_vertex_sig_to_remove = cms.double(1.5),
                             remove_one_track_at_a_time = cms.bool(True),
                             jumble_tracks = cms.bool(False),
                             remove_tracks_frac = cms.double(-1),
                             histos = cms.untracked.bool(True),
                             scatterplots = cms.untracked.bool(False),
                             track_histos_only = cms.untracked.bool(False),
                             verbose = cms.untracked.bool(False),
                             phitest = cms.untracked.bool(False),
                             )
