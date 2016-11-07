#!/usr/bin/env python

from JMTucker.Tools.MiniAOD_cfg import which_global_tag
from JMTucker.Tools.CMSSWTools import *

parser, args_printer = friendly_argparse(description='Overlay tracks from pairs of 1-vertex events')
parser.add_argument('+which-event', '+e', type=int, help='which event from minitree to use', required=True)
parser.add_argument('+sample', help='which sample to use', choices=['ttbar', 'qcdht1500'], default='ttbar')
parser.add_argument('+ntracks', type=int, help='ntracks to use', default=3)
parser.add_argument('+rest-of-event', action='store_true', help='whether to use the rest of the tracks in the edm event')
parser.add_argument('+z-model', help='z model', choices=['deltasv', 'deltasvgaus', 'deltapv', 'none'], default='deltasv')
parser.add_argument('+z-width', type=float, help='width of gaus used in z model (cm)', default=0.02)
parser.add_argument('+dz-true-max', type=float, help='max dz allowed for z model (cm)', default=1e9)
parser.add_argument('+found-dist', type=float, help='3D distance for matching by position (cm)', default=0.008)
parser.add_argument('+rotate-x', action='store_true', help='azimuthally rotate x of tracks (around beam line)')
parser.add_argument('+rotate-p', action='store_true', help='azimuthally rotate p of tracks')
parser.add_argument('+is-data', action='store_true', help='whether input is data / MC')
parser.add_argument('+batch', action='store_true', help='run in batch mode')
parser.add_argument('+debug', action='store_true', help='turn on debug prints')
parser.add_argument('+out-fn', help='override output fn')
parser.add_argument('+minitree-path', help='override minitree path')
parser.add_argument('+minitree-fn', help='override minitree fn')
parser.add_argument('+max-events', type=int, help='max edm events to run on', default=-1)

args = parser.parse_args()
if args.out_fn is None:
    args.out_fn = 'overlay_%i.root' % args.which_event
if args.minitree_path is None:
    args.minitree_path = 'root://cmsxrootd.fnal.gov//store/user/tucker/MinitreeV9/ntk%i' % args.ntracks
if args.minitree_fn is None:
    args.minitree_fn = '%s/%s.root' % (args.minitree_path, args.sample)

args_printer('overlay args', args)

####

if args.sample == 'ttbar':
    file_base = '/store/user/tucker/TTJets_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8/pick1vtx/161104_153826/0000'
    file_nums = range(1,94)
elif args.sample == 'qcdht1500':
    file_base = '/store/user/tucker/QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/pick1vtx/161104_153718/0000'
    file_nums = range(1,15)
    file_nums.remove(9)
else:
    raise ValueError('bad sample %s' % args.sample)

in_fns = [os.path.join(file_base, 'pick_%i.root' % i) for i in file_nums]

####

process = basic_process('Overlay')
process.source.fileNames = in_fns
process.maxEvents.input = args.max_events
report_every(process, 1000000 if args.batch else 100)
geometry_etc(process, which_global_tag(not args.is_data))
tfileservice(process, args.out_fn)
random_service(process, {'mfvVertices': 12179, 'mfvOverlayTracks': 12180})

if not args.is_data:
    process.load('JMTucker.Tools.MCStatProducer_cff')
    process.mcStat.histos = True

process.load('CommonTools.ParticleFlow.goodOfflinePrimaryVertices_cfi')
process.load('JMTucker.MFVNeutralino.Vertexer_cfi')

process.mfvVertices.histos = False
process.mfvVertices.verbose = args.debug
process.mfvVertices.use_second_tracks = True
process.mfvVertices.second_track_src = 'mfvOverlayTracks'
if not args.rest_of_event:
    process.mfvVertices.disregard_event = True

process.mfvOverlayTracks = cms.EDFilter('MFVOverlayVertexTracks',
                                        minitree_fn = cms.string(args.minitree_fn),
                                        which_event = cms.int32(args.which_event),
                                        rotate_x = cms.bool(args.rotate_x),
                                        rotate_p = cms.bool(args.rotate_p),
                                        z_model = cms.string(args.z_model),
                                        z_width = cms.double(args.z_width),
                                        only_other_tracks = cms.bool(args.rest_of_event),
                                        verbose = cms.bool(args.debug),
                                        )

process.mfvOverlayHistos = cms.EDAnalyzer('MFVOverlayVertexHistos',
                                          truth_src = cms.InputTag('mfvOverlayTracks'),
                                          beamspot_src = cms.InputTag('offlineBeamSpot'),
                                          vertices_src = cms.InputTag('mfvVertices'),
                                          dz_true_max = cms.double(args.dz_true_max),
                                          min_ntracks = cms.int32(args.ntracks),
                                          found_dist = cms.double(args.found_dist),
                                          debug = cms.bool(args.debug),
                                          )

process.p = cms.Path(process.goodOfflinePrimaryVertices * process.mfvOverlayTracks * process.mfvVertices * process.mfvOverlayHistos)
