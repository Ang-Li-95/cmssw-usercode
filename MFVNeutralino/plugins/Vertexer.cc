#include "TH2.h"
#include "TMath.h"
#include "TFitResult.h"
#include "CLHEP/Random/RandomEngine.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Utilities/interface/RandomNumberGenerator.h"
#include "RecoVertex/ConfigurableVertexReco/interface/ConfigurableVertexReconstructor.h"
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "RecoVertex/VertexTools/interface/VertexDistance3D.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "JMTucker/Tools/interface/TrackerSpaceExtent.h"

namespace {
  template <typename T>
  T mag(T x, T y) {
    return sqrt(x*x + y*y);
  }
  
  template <typename T>
  T mag(T x, T y, T z) {
    return sqrt(x*x + y*y + z*z);
  }
}

class MFVVertexer : public edm::EDProducer {
public:
  MFVVertexer(const edm::ParameterSet&);
  virtual void produce(edm::Event&, const edm::EventSetup&);

private:
  void finish(edm::Event&, std::auto_ptr<reco::VertexCollection>, std::auto_ptr<std::vector<float>>);

  typedef std::set<reco::TrackRef> track_set;

  template <typename T>
  void print_track_set(const T& ts) const {
    for (auto r : ts)
      printf(" %u", r.key());
  }

  template <typename T>
  void print_track_set(const T& ts, const reco::Vertex& v) const {
    for (auto r : ts)
      printf(" %u%s", r.key(), (v.trackWeight(r) < 0.5 ? "!" : ""));
  }

  void print_track_set(const reco::Vertex& v) const {
    for (auto r = v.tracks_begin(), re = v.tracks_end(); r != re; ++r)
      printf(" %lu%s", r->key(), (v.trackWeight(*r) < 0.5 ? "!" : ""));
  }

  bool is_track_subset(const track_set& a, const track_set& b) const {
    bool is_subset = true;
    const track_set& smaller = a.size() <= b.size() ? a : b;
    const track_set& bigger  = a.size() <= b.size() ? b : a;
    
    for (auto t : smaller)
      if (bigger.count(t) < 1) {
        is_subset = false;
        break;
      }

    return is_subset;
  }

  track_set vertex_track_set(const reco::Vertex& v, const double min_weight = 0.5) const {
    std::set<reco::TrackRef> result;

    for (auto it = v.tracks_begin(), ite = v.tracks_end(); it != ite; ++it) {
      const double w = v.trackWeight(*it);
      const bool use = w >= min_weight;
      //if (verbose) ("trk #%2i pt %6.3f eta %6.3f phi %6.3f dxy %6.3f dz %6.3f w %5.3f  use? %i\n", int(it-v.tracks_begin()), (*it)->pt(), (*it)->eta(), (*it)->phi(), (*it)->dxy(), (*it)->dz(), w, use);
      if (use)
        result.insert(it->castTo<reco::TrackRef>());
    }

    return result;
  }

  Measurement1D vertex_dist(const reco::Vertex& v0, const reco::Vertex& v1) const {
    if (use_2d_vertex_dist)
      return vertex_dist_2d.distance(v0, v1);
    else
      return vertex_dist_3d.distance(v0, v1);
  }

  std::pair<bool, Measurement1D> track_dist(const reco::TransientTrack& t, const reco::Vertex& v) const {
    if (use_2d_track_dist)
      return IPTools::absoluteTransverseImpactParameter(t, v);
    else
      return IPTools::absoluteImpactParameter3D(t, v);
  }

  VertexDistanceXY vertex_dist_2d;
  VertexDistance3D vertex_dist_3d;
  std::auto_ptr<KalmanVertexFitter> kv_reco;
  std::auto_ptr<VertexReconstructor> av_reco;

  std::vector<TransientVertex> kv_reco_dropin(std::vector<reco::TransientTrack>& ttks) {
    if (ttks.size() < 2)
      return std::vector<TransientVertex>();
    std::vector<TransientVertex> v(1, kv_reco->vertex(ttks));
    if (v[0].normalisedChiSquared() > 5)
      return std::vector<TransientVertex>();
    return v;
  }

  TrackerSpaceExtents tracker_extents;

  const edm::EDGetTokenT<reco::BeamSpot> beamspot_token;
  const edm::EDGetTokenT<reco::VertexCollection> primary_vertices_token;
  const bool use_tracks;
  const edm::EDGetTokenT<reco::TrackCollection> track_token;
  const bool use_non_pv_tracks;
  const bool use_non_pvs_tracks;
  const bool use_pf_candidates;
  const edm::EDGetTokenT<reco::PFCandidateCollection> pf_candidate_token;
  const bool use_pf_jets;
  const edm::EDGetTokenT<reco::PFJetCollection> pf_jet_token;
  const bool use_pat_jets;
  const edm::EDGetTokenT<pat::JetCollection> pat_jet_token;
  const double min_seed_jet_pt;
  const double min_all_track_pt;
  const double min_all_track_dxy;
  const double min_all_track_sigmadxy;
  const double min_all_track_sigmadxypv;
  const int min_all_track_hit_r;
  const int min_all_track_nhits;
  const int min_all_track_npxhits;
  const int min_all_track_npxlayers;
  const int min_all_track_nstlayers;
  const double max_all_track_dxyerr;
  const double max_all_track_dxyipverr;
  const double max_all_track_d3dipverr;
  const double min_seed_track_pt;
  const double min_seed_track_dxy;
  const double min_seed_track_sigmadxy;
  const double min_seed_track_sigmadxypv;
  const int min_seed_track_hit_r;
  const int min_seed_track_nhits;
  const int min_seed_track_npxhits;
  const int min_seed_track_npxlayers;
  const int min_seed_track_nstlayers;
  const double max_seed_track_dxyerr;
  const double max_seed_track_dxyipverr;
  const double max_seed_track_d3dipverr;
  const double max_seed_vertex_chi2;
  const bool use_2d_vertex_dist;
  const bool use_2d_track_dist;
  const double merge_anyway_dist;
  const double merge_anyway_sig;
  const double merge_shared_dist;
  const double merge_shared_sig;
  const double max_track_vertex_dist;
  const double max_track_vertex_sig;
  const double min_track_vertex_sig_to_remove;
  const bool remove_one_track_at_a_time;
  const bool jumble_tracks;
  const double remove_tracks_frac;
  const bool write_tracks;
  const bool histos;
  const bool scatterplots;
  const bool track_histos_only;
  const bool verbose;
  const bool phitest;

  TH1F* h_n_all_tracks;
  TH1F* h_all_track_pars[6];
  TH1F* h_all_track_errs[6];
  TH2F* h_all_track_pars_v_pars[6][6];
  TH2F* h_all_track_errs_v_pars[6][6];
  TH1F* h_all_track_sigmadxybs;
  TH1F* h_all_track_sigmadxypv;
  TH1F* h_all_track_nhits;
  TH1F* h_all_track_npxhits;
  TH1F* h_all_track_nsthits;
  TH1F* h_n_seed_tracks;
  TH1F* h_seed_track_pars[6];
  TH1F* h_seed_track_errs[6];
  TH2F* h_seed_track_pars_v_pars[6][6];
  TH2F* h_seed_track_errs_v_pars[6][6];
  TH1F* h_seed_track_sigmadxybs;
  TH1F* h_seed_track_sigmadxypv;
  TH1F* h_seed_track_nhits;
  TH1F* h_seed_track_npxhits;
  TH1F* h_seed_track_nsthits;
  TH1F* h_seed_track_npxlayers;
  TH1F* h_seed_track_deltar2px;
  TH1F* h_seed_track_deltaz2px;
  TH1F* h_seed_track_deltar3px;
  TH1F* h_seed_track_deltaz3px;
  TH1F* h_n_seed_vertices;
  TH1F* h_seed_vertex_track_weights;
  TH1F* h_seed_vertex_chi2;
  TH1F* h_seed_vertex_ndof;
  TH1F* h_seed_vertex_x;
  TH1F* h_seed_vertex_y;
  TH1F* h_seed_vertex_rho;
  TH1F* h_seed_vertex_phi;
  TH1F* h_seed_vertex_z;
  TH1F* h_seed_vertex_r;
  TH1F* h_seed_vertex_paird2d;
  TH1F* h_seed_vertex_pairdphi;
  TH1F* h_seed_track_multiplicity;
  TH1F* h_max_seed_track_multiplicity;
  TH1F* h_n_resets;
  TH1F* h_n_onetracks;
  TH1F* h_noshare_vertex_tkvtxdist;
  TH1F* h_noshare_vertex_tkvtxdisterr;
  TH1F* h_noshare_vertex_tkvtxdistsig;
  TH1F* h_n_noshare_vertices;
  TH1F* h_noshare_vertex_ntracks;
  TH1F* h_noshare_vertex_track_weights;
  TH1F* h_noshare_vertex_chi2;
  TH1F* h_noshare_vertex_ndof;
  TH1F* h_noshare_vertex_x;
  TH1F* h_noshare_vertex_y;
  TH1F* h_noshare_vertex_rho;
  TH1F* h_noshare_vertex_phi;
  TH1F* h_noshare_vertex_z;
  TH1F* h_noshare_vertex_r;
  TH1F* h_noshare_vertex_paird2d;
  TH1F* h_noshare_vertex_pairdphi;
  TH1F* h_noshare_track_multiplicity;
  TH1F* h_max_noshare_track_multiplicity;
  TH1F* h_n_output_vertices;

  TH1F* h_pairs_d2d[6]; // only using 0,2,3,4,5
  TH1F* h_pairs_dphi[6];
  TH1F* h_share_d2d[6]; // only using 0,2,3,4,5
  TH1F* h_share_dphi[6];
  TH1F* h_merge_d2d[6]; // only using 0,2,3,4,5
  TH1F* h_merge_dphi[6];
  TH1F* h_erase_d2d[6]; // only using 0,2,3,4,5
  TH1F* h_erase_dphi[6];

  TH1F* h_phitest_nev;
  TH1F* h_phitest_nvtx;
  TH1F* h_phitest_mean;
  TH1F* h_phitest_rms;
  TH1F* h_phitest_p0;
  TH1F* h_phitest_p1;

  struct track_cuts {
    const MFVVertexer& mv;
    const reco::Track& tk;
    const reco::BeamSpot& bs;
    const reco::Vertex* pv;
    const TransientTrackBuilder& tt_builder;

    double pt;
    double dxybs;
    double dxypv;
    double dxyerr;
    double sigmadxybs;
    double sigmadxypv;
    int nhits;
    int npxhits;
    int npxlayers;
    int nstlayers;
    NumExtents ne;
    
    track_cuts(const MFVVertexer* mv_, const reco::Track& tk_, const reco::BeamSpot& bs_, const reco::Vertex* pv_, const TransientTrackBuilder& tt)
      : mv(*mv_), tk(tk_), bs(bs_), pv(pv_), tt_builder(tt)
    {
      pt = tk.pt();
      dxybs = tk.dxy(bs);
      dxypv = pv ? tk.dxy(pv->position()) : 1e99;
      dxyerr = tk.dxyError();
      sigmadxybs = dxybs / dxyerr;
      sigmadxypv = dxypv / dxyerr;
      nhits = tk.hitPattern().numberOfValidHits(); // JMTBAD this is supposed to be strip hits...
      npxhits = tk.hitPattern().numberOfValidPixelHits();
      npxlayers = tk.hitPattern().pixelLayersWithMeasurement();
      nstlayers = tk.hitPattern().stripLayersWithMeasurement();
      ne = mv.tracker_extents.numExtentInRAndZ(tk.hitPattern(), false);
    }

    // these are cheap
    bool use_ex(bool for_seed) const {
      if (for_seed) {
        return 
          npxlayers >= mv.min_seed_track_npxlayers && 
          nstlayers >= mv.min_seed_track_nstlayers && 
          (mv.min_seed_track_hit_r == 999 || ne.min_r <= mv.min_seed_track_hit_r) &&
          pt > mv.min_seed_track_pt &&
          fabs(sigmadxybs) > mv.min_seed_track_sigmadxy &&
          fabs(dxybs) > mv.min_seed_track_dxy &&
          fabs(sigmadxypv) > mv.min_seed_track_sigmadxypv &&
          nhits >= mv.min_seed_track_nhits && 
          npxhits >= mv.min_seed_track_npxhits && 
          dxyerr < mv.max_seed_track_dxyerr;
      }
      else {
        return 
          npxlayers >= mv.min_all_track_npxlayers && 
          nstlayers >= mv.min_all_track_nstlayers && 
          (mv.min_all_track_hit_r == 999 || ne.min_r <= mv.min_all_track_hit_r) &&
          pt > mv.min_all_track_pt &&
          fabs(sigmadxybs) > mv.min_all_track_sigmadxy &&
          fabs(dxybs) > mv.min_all_track_dxy &&
          fabs(sigmadxypv) > mv.min_all_track_sigmadxypv &&
          nhits >= mv.min_all_track_nhits && 
          npxhits >= mv.min_all_track_npxhits && 
          dxyerr < mv.max_all_track_dxyerr;
      }
    }

    bool use(bool for_seed) const {
      if (!use_ex(for_seed))
        return false;

      if (!pv)
        return true;

      const double max_dxyipverr = for_seed ? mv.max_seed_track_dxyipverr : mv.max_all_track_dxyipverr;
      const double max_d3dipverr = for_seed ? mv.max_seed_track_d3dipverr : mv.max_all_track_d3dipverr;

      if (max_dxyipverr <= 0 && max_d3dipverr <= 0)
        return true;

      reco::TransientTrack ttk = tt_builder.build(tk);

      if (max_dxyipverr > 0) {
        auto dxy_ipv = IPTools::absoluteTransverseImpactParameter(ttk, *pv);
        if (!dxy_ipv.first || dxy_ipv.second.error() >= max_dxyipverr)
          return false;
      }

      if (max_d3dipverr > 0) {
        auto d3d_ipv = IPTools::absoluteImpactParameter3D(ttk, *pv);
        if (!d3d_ipv.first || d3d_ipv.second.error() >= max_d3dipverr)
          return false;
      }
      
      return true;
    }
  };
};

MFVVertexer::MFVVertexer(const edm::ParameterSet& cfg)
  : kv_reco(new KalmanVertexFitter(cfg.getParameter<edm::ParameterSet>("kvr_params"), cfg.getParameter<edm::ParameterSet>("kvr_params").getParameter<bool>("doSmoothing"))),
    av_reco(new ConfigurableVertexReconstructor(cfg.getParameter<edm::ParameterSet>("avr_params"))),
    beamspot_token(consumes<reco::BeamSpot>(cfg.getParameter<edm::InputTag>("beamspot_src"))),
    primary_vertices_token(consumes<reco::VertexCollection>(cfg.getParameter<edm::InputTag>("primary_vertices_src"))),
    use_tracks(cfg.getParameter<bool>("use_tracks")),
    track_token(consumes<reco::TrackCollection>(cfg.getParameter<edm::InputTag>("track_src"))),
    use_non_pv_tracks(cfg.getParameter<bool>("use_non_pv_tracks")),
    use_non_pvs_tracks(cfg.getParameter<bool>("use_non_pvs_tracks")),
    use_pf_candidates(cfg.getParameter<bool>("use_pf_candidates")),
    pf_candidate_token(consumes<reco::PFCandidateCollection>(cfg.getParameter<edm::InputTag>("pf_candidate_src"))),
    use_pf_jets(cfg.getParameter<bool>("use_pf_jets")),
    pf_jet_token(consumes<reco::PFJetCollection>(cfg.getParameter<edm::InputTag>("pf_jet_src"))),
    use_pat_jets(cfg.getParameter<bool>("use_pat_jets")),
    pat_jet_token(consumes<pat::JetCollection>(cfg.getParameter<edm::InputTag>("pat_jet_src"))),
    min_seed_jet_pt(cfg.getParameter<double>("min_seed_jet_pt")),
    min_all_track_pt(cfg.getParameter<double>("min_all_track_pt")),
    min_all_track_dxy(cfg.getParameter<double>("min_all_track_dxy")),
    min_all_track_sigmadxy(cfg.getParameter<double>("min_all_track_sigmadxy")),
    min_all_track_sigmadxypv(cfg.getParameter<double>("min_all_track_sigmadxypv")),
    min_all_track_hit_r(cfg.getParameter<int>("min_all_track_hit_r")),
    min_all_track_nhits(cfg.getParameter<int>("min_all_track_nhits")),
    min_all_track_npxhits(cfg.getParameter<int>("min_all_track_npxhits")),
    min_all_track_npxlayers(cfg.getParameter<int>("min_all_track_npxlayers")),
    min_all_track_nstlayers(cfg.getParameter<int>("min_all_track_nstlayers")),
    max_all_track_dxyerr(cfg.getParameter<double>("max_all_track_dxyerr")),
    max_all_track_dxyipverr(cfg.getParameter<double>("max_all_track_dxyipverr")),
    max_all_track_d3dipverr(cfg.getParameter<double>("max_all_track_d3dipverr")),
    min_seed_track_pt(cfg.getParameter<double>("min_seed_track_pt")),
    min_seed_track_dxy(cfg.getParameter<double>("min_seed_track_dxy")),
    min_seed_track_sigmadxy(cfg.getParameter<double>("min_seed_track_sigmadxy")),
    min_seed_track_sigmadxypv(cfg.getParameter<double>("min_seed_track_sigmadxypv")),
    min_seed_track_hit_r(cfg.getParameter<int>("min_seed_track_hit_r")),
    min_seed_track_nhits(cfg.getParameter<int>("min_seed_track_nhits")),
    min_seed_track_npxhits(cfg.getParameter<int>("min_seed_track_npxhits")),
    min_seed_track_npxlayers(cfg.getParameter<int>("min_seed_track_npxlayers")),
    min_seed_track_nstlayers(cfg.getParameter<int>("min_seed_track_nstlayers")),
    max_seed_track_dxyerr(cfg.getParameter<double>("max_seed_track_dxyerr")),
    max_seed_track_dxyipverr(cfg.getParameter<double>("max_seed_track_dxyipverr")),
    max_seed_track_d3dipverr(cfg.getParameter<double>("max_seed_track_d3dipverr")),
    max_seed_vertex_chi2(cfg.getParameter<double>("max_seed_vertex_chi2")),
    use_2d_vertex_dist(cfg.getParameter<bool>("use_2d_vertex_dist")),
    use_2d_track_dist(cfg.getParameter<bool>("use_2d_track_dist")),
    merge_anyway_dist(cfg.getParameter<double>("merge_anyway_dist")),
    merge_anyway_sig(cfg.getParameter<double>("merge_anyway_sig")),
    merge_shared_dist(cfg.getParameter<double>("merge_shared_dist")),
    merge_shared_sig(cfg.getParameter<double>("merge_shared_sig")),
    max_track_vertex_dist(cfg.getParameter<double>("max_track_vertex_dist")),
    max_track_vertex_sig(cfg.getParameter<double>("max_track_vertex_sig")),
    min_track_vertex_sig_to_remove(cfg.getParameter<double>("min_track_vertex_sig_to_remove")),
    remove_one_track_at_a_time(cfg.getParameter<bool>("remove_one_track_at_a_time")),
    jumble_tracks(cfg.getParameter<bool>("jumble_tracks")),
    remove_tracks_frac(cfg.getParameter<double>("remove_tracks_frac")),
    write_tracks(cfg.getParameter<bool>("write_tracks")),
    histos(cfg.getUntrackedParameter<bool>("histos", false)),
    scatterplots(cfg.getUntrackedParameter<bool>("scatterplots", false)),
    track_histos_only(cfg.getUntrackedParameter<bool>("track_histos_only", false)),
    verbose(cfg.getUntrackedParameter<bool>("verbose", false)),
    phitest(cfg.getUntrackedParameter<bool>("phitest", false))
{
  if (use_tracks + use_non_pv_tracks + use_non_pvs_tracks + use_pf_candidates + use_pf_jets + use_pat_jets != 1)
    throw cms::Exception("MFVVertexer") << "must enable exactly one of use_tracks/use_non_pv_tracks/use_non_pvs_tracks/pf_candidates/pf_jets/pat_jets";

  edm::Service<edm::RandomNumberGenerator> rng;
  if ((jumble_tracks || remove_tracks_frac > 0) && !rng.isAvailable())
    throw cms::Exception("Vertexer") << "RandomNumberGeneratorService not available for jumbling or removing tracks!\n";

  produces<reco::VertexCollection>();
  produces<std::vector<float>>();

  if (write_tracks)
    produces<reco::TrackCollection>();

  if (histos) {
    edm::Service<TFileService> fs;

    h_n_all_tracks  = fs->make<TH1F>("h_n_all_tracks",  "", 40, 0, 2000);
    h_n_seed_tracks = fs->make<TH1F>("h_n_seed_tracks", "", 50, 0,  200);

    const char* par_names[6] = {"pt", "eta", "phi", "dxybs", "dxypv", "dz"};
    const int par_nbins[6] = {  50, 50, 50, 100, 100, 80 };
    const double par_lo[6] = {   0, -2.5, -3.15, -0.2, -0.2, -20 };
    const double par_hi[6] = {  10,  2.5,  3.15,  0.2,  0.2,  20 };
    const double err_lo[6] = { 0 };
    const double err_hi[6] = { 0.15, 0.01, 0.01, 0.2, 0.2, 0.4 };
    for (int i = 0; i < 6; ++i)
      h_all_track_pars[i] = fs->make<TH1F>(TString::Format("h_all_track_%s",    par_names[i]), "", par_nbins[i], par_lo[i], par_hi[i]);
    for (int i = 0; i < 6; ++i)
      h_all_track_errs[i] = fs->make<TH1F>(TString::Format("h_all_track_err%s", par_names[i]), "", par_nbins[i], err_lo[i], err_hi[i]);
    if (scatterplots) {
      for (int i = 0; i < 6; ++i)
        for (int j = i+1; j < 6; ++j)
          h_all_track_pars_v_pars[i][j] = fs->make<TH2F>(TString::Format("h_all_track_%s_v_%s", par_names[j], par_names[i]), "", par_nbins[i], par_lo[i], par_hi[i], par_nbins[j], par_lo[j], par_hi[j]);
      for (int i = 0; i < 6; ++i)
        for (int j = 0; j < 6; ++j)
          h_all_track_errs_v_pars[i][j] = fs->make<TH2F>(TString::Format("h_all_track_err%s_v_%s", par_names[j], par_names[i]), "", par_nbins[i], par_lo[i], par_hi[i], par_nbins[j], err_lo[j], err_hi[j]);
    }

    h_all_track_sigmadxybs           = fs->make<TH1F>("h_all_track_sigmadxybs",           "", 40, -10,     10);
    h_all_track_sigmadxypv           = fs->make<TH1F>("h_all_track_sigmadxypv",           "", 40, -10,     10);
    h_all_track_nhits                = fs->make<TH1F>("h_all_track_nhits",                "",  40,   0,     40);
    h_all_track_npxhits              = fs->make<TH1F>("h_all_track_npxhits",              "",  12,   0,     12);
    h_all_track_nsthits              = fs->make<TH1F>("h_all_track_nsthits",              "",  28,   0,     28);

    for (int i = 0; i < 6; ++i)
      h_seed_track_pars[i] = fs->make<TH1F>(TString::Format("h_seed_track_%s",    par_names[i]), "", par_nbins[i], par_lo[i], par_hi[i]);
    for (int i = 0; i < 6; ++i)
      h_seed_track_errs[i] = fs->make<TH1F>(TString::Format("h_seed_track_err%s", par_names[i]), "", par_nbins[i], err_lo[i], err_hi[i]);
    if (scatterplots) {
      for (int i = 0; i < 6; ++i)
        for (int j = i+1; j < 6; ++j)
          h_seed_track_pars_v_pars[i][j] = fs->make<TH2F>(TString::Format("h_seed_track_%s_v_%s", par_names[j], par_names[i]), "", par_nbins[i], par_lo[i], par_hi[i], par_nbins[j], par_lo[j], par_hi[j]);
      for (int i = 0; i < 6; ++i)
        for (int j = 0; j < 6; ++j)
          h_seed_track_errs_v_pars[i][j] = fs->make<TH2F>(TString::Format("h_seed_track_err%s_v_%s", par_names[j], par_names[i]), "", par_nbins[i], par_lo[i], par_hi[i], par_nbins[j], err_lo[j], err_hi[j]);
    }

    h_seed_track_sigmadxybs = fs->make<TH1F>("h_seed_track_sigmadxybs", "", 40, -10, 10);
    h_seed_track_sigmadxypv = fs->make<TH1F>("h_seed_track_sigmadxypv", "", 40, -10, 10);
    h_seed_track_nhits      = fs->make<TH1F>("h_seed_track_nhits",      "", 40,   0, 40);
    h_seed_track_npxhits    = fs->make<TH1F>("h_seed_track_npxhits",    "", 12,   0, 12);
    h_seed_track_nsthits    = fs->make<TH1F>("h_seed_track_nsthits",    "", 28,   0, 28);
    h_seed_track_npxlayers  = fs->make<TH1F>("h_seed_track_npxlayers",  "",  6,   0,  6);

    h_seed_track_deltar2px = fs->make<TH1F>("h_seed_track_deltar2px", "", 20, 0, 10);
    h_seed_track_deltaz2px = fs->make<TH1F>("h_seed_track_deltaz2px", "", 20, 0, 20);
    h_seed_track_deltar3px = fs->make<TH1F>("h_seed_track_deltar3px", "", 20, 0, 10);
    h_seed_track_deltaz3px = fs->make<TH1F>("h_seed_track_deltaz3px", "", 20, 0, 20);

    h_n_seed_vertices                = fs->make<TH1F>("h_n_seed_vertices",                "",  50,   0,    200);
    h_seed_vertex_track_weights      = fs->make<TH1F>("h_seed_vertex_track_weights",      "",  21,   0,      1.05);
    h_seed_vertex_chi2               = fs->make<TH1F>("h_seed_vertex_chi2",               "",  20,   0, max_seed_vertex_chi2);
    h_seed_vertex_ndof               = fs->make<TH1F>("h_seed_vertex_ndof",               "",  10,   0,     20);
    h_seed_vertex_x                  = fs->make<TH1F>("h_seed_vertex_x",                  "", 100,  -1,      1);
    h_seed_vertex_y                  = fs->make<TH1F>("h_seed_vertex_y",                  "", 100,  -1,      1);
    h_seed_vertex_rho                = fs->make<TH1F>("h_seed_vertex_rho",                "", 100,   0,      2);
    h_seed_vertex_phi                = fs->make<TH1F>("h_seed_vertex_phi",                "",  50,  -3.15,   3.15);
    h_seed_vertex_z                  = fs->make<TH1F>("h_seed_vertex_z",                  "",  40, -20,     20);
    h_seed_vertex_r                  = fs->make<TH1F>("h_seed_vertex_r",                  "", 100,   0,      2);
    h_seed_vertex_paird2d            = fs->make<TH1F>("h_seed_vertex_paird2d",            "", 100,   0,      0.2);
    h_seed_vertex_pairdphi           = fs->make<TH1F>("h_seed_vertex_pairdphi",           "", 100,  -3.14,   3.14);
    h_seed_track_multiplicity        = fs->make<TH1F>("h_seed_track_multiplicity",        "",  40,   0,     40);
    h_max_seed_track_multiplicity    = fs->make<TH1F>("h_max_seed_track_multiplicity",    "",  40,   0,     40);

    h_n_resets                       = fs->make<TH1F>("h_n_resets",                       "", 50,   0,   500);
    h_n_onetracks                    = fs->make<TH1F>("h_n_onetracks",                    "",  5,   0,     5);

    h_n_noshare_vertices             = fs->make<TH1F>("h_n_noshare_vertices",             "", 50,   0,    50);
    h_noshare_vertex_tkvtxdist       = fs->make<TH1F>("h_noshare_vertex_tkvtxdist",       "", 100,  0,   0.1);
    h_noshare_vertex_tkvtxdisterr    = fs->make<TH1F>("h_noshare_vertex_tkvtxdisterr",    "", 100,  0,   0.1);
    h_noshare_vertex_tkvtxdistsig    = fs->make<TH1F>("h_noshare_vertex_tkvtxdistsig",    "", 100,  0,     6);
    h_noshare_vertex_ntracks         = fs->make<TH1F>("h_noshare_vertex_ntracks",         "",  30,  0, 30);
    h_noshare_vertex_track_weights   = fs->make<TH1F>("h_noshare_vertex_track_weights",   "",  21,   0,      1.05);
    h_noshare_vertex_chi2            = fs->make<TH1F>("h_noshare_vertex_chi2",            "", 20,   0, max_seed_vertex_chi2);
    h_noshare_vertex_ndof            = fs->make<TH1F>("h_noshare_vertex_ndof",            "", 10,   0,     20);
    h_noshare_vertex_x               = fs->make<TH1F>("h_noshare_vertex_x",               "", 100,  -1,      1);
    h_noshare_vertex_y               = fs->make<TH1F>("h_noshare_vertex_y",               "", 100,  -1,      1);
    h_noshare_vertex_rho             = fs->make<TH1F>("h_noshare_vertex_rho",             "", 100,   0,      2);
    h_noshare_vertex_phi             = fs->make<TH1F>("h_noshare_vertex_phi",             "", 50,  -3.15,   3.15);
    h_noshare_vertex_z               = fs->make<TH1F>("h_noshare_vertex_z",               "", 40, -20,     20);
    h_noshare_vertex_r               = fs->make<TH1F>("h_noshare_vertex_r",               "", 100,   0,      2);
    h_noshare_vertex_paird2d         = fs->make<TH1F>("h_noshare_vertex_paird2d",            "", 100,   0,      0.2);
    h_noshare_vertex_pairdphi        = fs->make<TH1F>("h_noshare_vertex_pairdphi",           "", 100,  -3.15,   3.15);
    h_noshare_track_multiplicity     = fs->make<TH1F>("h_noshare_track_multiplicity",     "",  40,   0,     40);
    h_max_noshare_track_multiplicity = fs->make<TH1F>("h_max_noshare_track_multiplicity", "",  40,   0,     40);
    h_n_output_vertices           = fs->make<TH1F>("h_n_output_vertices",           "", 50, 0, 50);

    h_pairs_d2d [0] = fs->make<TH1F>(TString::Format("h_pairs_d2d" ), "", 100, 0, 0.1);
    h_pairs_dphi[0] = fs->make<TH1F>(TString::Format("h_pairs_dphi"), "", 100, -3.15, 3.15);
    h_share_d2d [0] = fs->make<TH1F>(TString::Format("h_share_d2d" ), "", 100, 0, 0.1);
    h_share_dphi[0] = fs->make<TH1F>(TString::Format("h_share_dphi"), "", 100, -3.15, 3.15);
    h_merge_d2d [0] = fs->make<TH1F>(TString::Format("h_merge_d2d" ), "", 100, 0, 0.1);
    h_merge_dphi[0] = fs->make<TH1F>(TString::Format("h_merge_dphi"), "", 100, -3.15, 3.15);
    h_erase_d2d [0] = fs->make<TH1F>(TString::Format("h_erase_d2d" ), "", 100, 0, 0.1);
    h_erase_dphi[0] = fs->make<TH1F>(TString::Format("h_erase_dphi"), "", 100, -3.15, 3.15);
    for (int i = 2; i <= 5; ++i) {
      h_pairs_d2d [i] = fs->make<TH1F>(TString::Format("h_pairs_d2d_maxtk%i" , i), "", 100, 0, 0.1);
      h_pairs_dphi[i] = fs->make<TH1F>(TString::Format("h_pairs_dphi_maxtk%i", i), "", 100, -3.15, 3.15);
      h_share_d2d [i] = fs->make<TH1F>(TString::Format("h_share_d2d_maxtk%i" , i), "", 100, 0, 0.1);
      h_share_dphi[i] = fs->make<TH1F>(TString::Format("h_share_dphi_maxtk%i", i), "", 100, -3.15, 3.15);
      h_merge_d2d [i] = fs->make<TH1F>(TString::Format("h_merge_d2d_maxtk%i" , i), "", 100, 0, 0.1);
      h_merge_dphi[i] = fs->make<TH1F>(TString::Format("h_merge_dphi_maxtk%i", i), "", 100, -3.15, 3.15);
      h_erase_d2d [i] = fs->make<TH1F>(TString::Format("h_erase_d2d_maxtk%i" , i), "", 100, 0, 0.1);
      h_erase_dphi[i] = fs->make<TH1F>(TString::Format("h_erase_dphi_maxtk%i", i), "", 100, -3.15, 3.15);
    }

    if (phitest) {
      h_phitest_nev = fs->make<TH1F>("h_phitest_nev", "", 1, 0, 1);
      const int N = 1500;
      h_phitest_nvtx = fs->make<TH1F>("h_phitest_nvtx", "", N, 0, N);
      h_phitest_mean = fs->make<TH1F>("phitest_mean",   "", N, 0, N);
      h_phitest_rms  = fs->make<TH1F>("phitest_rms",    "", N, 0, N);
      h_phitest_p0   = fs->make<TH1F>("phitest_p0",     "", N, 0, N);
      h_phitest_p1   = fs->make<TH1F>("phitest_p1",     "", N, 0, N);
      for (TH1F* h : { h_phitest_nvtx, h_phitest_mean, h_phitest_rms, h_phitest_p0, h_phitest_p1 })
        h->Sumw2();
    }
  }
}

void MFVVertexer::finish(edm::Event& event, std::auto_ptr<reco::VertexCollection> vertices, std::auto_ptr<std::vector<float>> pt_quantiles) {
  if (write_tracks) {
    std::auto_ptr<reco::TrackCollection> tracks(new reco::TrackCollection);

    for (const reco::Vertex& v : *vertices)
      for (auto it = v.tracks_begin(), ite = v.tracks_end(); it != ite; ++it) {
        reco::TrackRef tk = it->castTo<reco::TrackRef>();
        tracks->push_back(*tk);
      }

    event.put(tracks);
  }

  if (verbose)
    printf("n_output_vertices: %lu\n", vertices->size());
  if (histos)
    h_n_output_vertices->Fill(vertices->size());

  event.put(vertices);
  event.put(pt_quantiles);
}

void MFVVertexer::produce(edm::Event& event, const edm::EventSetup& setup) {
  if (verbose) {
    printf("------------------------------------------------------------------------\n");
    printf("MFVVertexer::produce: run %u, lumi %u, event ", event.id().run(), event.luminosityBlock());
    std::cout << event.id().event() << "\n";
  }

  int iphitest = 0;
  if (phitest)
    h_phitest_nev->Fill(0);

  edm::Handle<reco::BeamSpot> beamspot;
  event.getByToken(beamspot_token, beamspot);
  const double bs_x = beamspot->position().x();
  const double bs_y = beamspot->position().y();
  const double bs_z = beamspot->position().z();

  edm::Handle<reco::VertexCollection> primary_vertices;
  event.getByToken(primary_vertices_token, primary_vertices);
  const reco::Vertex* primary_vertex = 0;
  if (primary_vertices->size())
    primary_vertex = &primary_vertices->at(0);

  //////////////////////////////////////////////////////////////////////
  // The tracks to be used. Will be filled from a track collection or
  // from raw-PF/PF2PAT jet constituents with cuts on pt/nhits/dxy.
  //////////////////////////////////////////////////////////////////////

  edm::ESHandle<TransientTrackBuilder> tt_builder;

  setup.get<TransientTrackRecord>().get("TransientTrackBuilder", tt_builder);

  std::vector<reco::TrackRef> all_tracks;
  std::vector<reco::TransientTrack> seed_tracks;
  std::map<reco::TrackRef, size_t> seed_track_ref_map;

  if (!tracker_extents.filled())
    tracker_extents.fill(setup, GlobalPoint(bs_x, bs_y, bs_z));

  if (use_tracks) {
    edm::Handle<reco::TrackCollection> tracks;
    event.getByToken(track_token, tracks);
    for (size_t i = 0, ie = tracks->size(); i < ie; ++i)
      all_tracks.push_back(reco::TrackRef(tracks, i));
  }
  else if (use_non_pv_tracks || use_non_pvs_tracks) {
    std::map<reco::TrackRef, std::vector<std::pair<int, float> > > tracks_in_pvs;
    for (size_t i = 0, ie = primary_vertices->size(); i < ie; ++i) {
      const reco::Vertex& pv = primary_vertices->at(i);
      for (auto it = pv.tracks_begin(), ite = pv.tracks_end(); it != ite; ++it) {
        float w = pv.trackWeight(*it);
        reco::TrackRef tk = it->castTo<reco::TrackRef>();
        tracks_in_pvs[tk].push_back(std::make_pair(i, w));
      }
    }

    edm::Handle<reco::TrackCollection> tracks;
    event.getByToken(track_token, tracks);
    for (size_t i = 0, ie = tracks->size(); i < ie; ++i) {
      reco::TrackRef tkref(tracks, i);
      bool ok = true;
      for (const auto& pv_use : tracks_in_pvs[tkref])
        if (use_non_pvs_tracks || (use_non_pv_tracks && pv_use.first == 0)) {
          ok = false;
          break;
        }

      if (ok)
        all_tracks.push_back(tkref);
    }
  }
  else if (use_pf_candidates) {
    edm::Handle<reco::PFCandidateCollection> pf_candidates;
    event.getByToken(pf_candidate_token, pf_candidates);

    for (const reco::PFCandidate& cand : *pf_candidates) {
      reco::TrackRef tkref = cand.trackRef();
      if (tkref.isNonnull())
        all_tracks.push_back(tkref);
    }
  }
  else if (use_pf_jets) {
    edm::Handle<reco::PFJetCollection> jets;
    event.getByToken(pf_jet_token, jets);
    for (const reco::PFJet& jet : *jets) {
      if (jet.pt() > min_seed_jet_pt &&
          fabs(jet.eta()) < 2.5 &&
          jet.numberOfDaughters() > 1 &&
          jet.neutralHadronEnergyFraction() < 0.99 &&
          jet.neutralEmEnergyFraction() < 0.99 &&
          (fabs(jet.eta()) >= 2.4 || (jet.chargedEmEnergyFraction() < 0.99 && jet.chargedHadronEnergyFraction() > 0. && jet.chargedMultiplicity() > 0))) {
        for (const reco::TrackRef& tk : jet.getTrackRefs())
          all_tracks.push_back(tk);
      }
    }
  }
  else if (use_pat_jets) {
    edm::Handle<pat::JetCollection> jets;
    event.getByToken(pat_jet_token, jets);
    for (const pat::Jet& jet : *jets) {
      if (jet.pt() > min_seed_jet_pt) { // assume rest of id above already applied at tuple time
        for (const reco::PFCandidatePtr& pfcand : jet.getPFConstituents()) {
          const reco::TrackRef& tk = pfcand->trackRef();
          if (tk.isNonnull())
            all_tracks.push_back(tk);
        }
      }
    }
  }

  if (jumble_tracks) {
    edm::Service<edm::RandomNumberGenerator> rng;
    CLHEP::HepRandomEngine& rng_engine = rng->getEngine(event.streamID());
    auto random_converter = [&](size_t n) { return size_t(rng_engine.flat() * n); };
    std::random_shuffle(all_tracks.begin(), all_tracks.end(), random_converter);
  }

  const int max_n_seed_pts = 1000;
  double seed_tracks_pt[max_n_seed_pts] = {0};

  for (size_t i = 0, ie = all_tracks.size(); i < ie; ++i) {
    const reco::TrackRef& tk = all_tracks[i];
    const track_cuts tc(this, *tk, *beamspot, primary_vertex, *tt_builder);
    bool use = tc.use(false);

    if (use && remove_tracks_frac > 0) {
      edm::Service<edm::RandomNumberGenerator> rng;
      CLHEP::HepRandomEngine& rng_engine = rng->getEngine(event.streamID());
      if (rng_engine.flat() < remove_tracks_frac)
        use = false;
    }

    if (use) {
      seed_tracks.push_back(tt_builder->build(tk));
      if (seed_tracks.size() <= max_n_seed_pts)
        seed_tracks_pt[seed_tracks.size()-1] = tk->pt();
      seed_track_ref_map[tk] = seed_tracks.size() - 1;
    }

    if (verbose) {
      printf("track %5lu: pt: %7.3f dxy: %7.3f nhits %3i ", i, tc.pt, tc.dxybs, tc.nhits);
      if (use)
        printf(" selected for seed! (#%lu)", seed_tracks.size()-1);
      printf("\n");
    }        

    if (histos) {
      const double pars[6] = {tc.pt, tk->eta(), tk->phi(), tc.dxybs, tc.dxypv, tk->dz(beamspot->position()) };
      const double errs[6] = { tk->ptError(), tk->etaError(), tk->phiError(), tk->dxyError(), tk->dxyError(), tk->dzError() };

      for (int i = 0; i < 6; ++i) {
        h_all_track_pars[i]->Fill(pars[i]);
        h_all_track_errs[i]->Fill(errs[i]);
        if (scatterplots) {
          for (int j = 0; j < 6; ++j) {
            if (j >= i+1)
              h_all_track_pars_v_pars[i][j]->Fill(pars[i], pars[j]);
            h_all_track_errs_v_pars[i][j]->Fill(pars[i], errs[j]);
          }
        }
      }
      
      h_all_track_sigmadxybs->Fill(tc.sigmadxybs);
      h_all_track_sigmadxypv->Fill(tc.sigmadxypv);
      h_all_track_nhits->Fill(tc.nhits);
      h_all_track_npxhits->Fill(tk->hitPattern().numberOfValidPixelHits());
      h_all_track_nsthits->Fill(tk->hitPattern().numberOfValidStripHits());

      if (use) {
        for (int i = 0; i < 6; ++i) {
          h_seed_track_pars[i]->Fill(pars[i]);
          h_seed_track_errs[i]->Fill(errs[i]);
          if (scatterplots) {
            for (int j = 0; j < 6; ++j) {
              if (j >= i+1)
                h_seed_track_pars_v_pars[i][j]->Fill(pars[i], pars[j]);
              h_seed_track_errs_v_pars[i][j]->Fill(pars[i], errs[j]);
            }
          }
        }

	h_seed_track_sigmadxybs->Fill(tc.sigmadxybs);
	h_seed_track_sigmadxypv->Fill(tc.sigmadxypv);
        h_seed_track_nhits->Fill(tc.nhits);
        h_seed_track_npxhits->Fill(tk->hitPattern().numberOfValidPixelHits());
        h_seed_track_nsthits->Fill(tk->hitPattern().numberOfValidStripHits());
	h_seed_track_npxlayers->Fill(tk->hitPattern().pixelLayersWithMeasurement());

        if (tk->hitPattern().numberOfValidPixelHits() >= 2) {
          const SpatialExtents se = tracker_extents.extentInRAndZ(tk->hitPattern(), tc.npxhits != 0);
          if (tk->hitPattern().numberOfValidPixelHits()==2) {
            double deltaR = se.max_r - se.min_r;
            double deltaZ = se.max_z - se.min_z;
            h_seed_track_deltar2px->Fill(deltaR);
            h_seed_track_deltaz2px->Fill(deltaZ);
          }
          else if (tk->hitPattern().numberOfValidPixelHits()==3) {
            double deltaR = se.max_r - se.min_r;
            double deltaZ = se.max_z - se.min_z;
            h_seed_track_deltar3px->Fill(deltaR);
            h_seed_track_deltaz3px->Fill(deltaZ);
          }
        }
      }
    }
  }

  const size_t ntk = seed_tracks.size();

  if (verbose)
    printf("n_all_tracks: %5lu   n_seed_tracks: %5lu\n", all_tracks.size(), ntk);
  if (histos) {
    h_n_all_tracks->Fill(all_tracks.size());
    h_n_seed_tracks->Fill(ntk);
  }

  //////////////////////////////////////////////////////////////////////
  // Form seed vertices from all pairs of tracks whose vertex fit
  // passes cuts.
  //////////////////////////////////////////////////////////////////////

  std::auto_ptr<reco::VertexCollection> vertices(new reco::VertexCollection);
  std::auto_ptr<std::vector<float> > pt_quantiles(new std::vector<float>(7));
  std::vector<std::vector<std::pair<int, int> > > track_use(ntk);

  if (ntk == 0 || track_histos_only) {
    if (verbose) {
      if (ntk == 0)
        printf("no seed tracks");
      else
        printf("track histos only");
      printf(" -> putting empty vertex collection into event\n");
    }
    finish(event, vertices, pt_quantiles);
    return;
  }

  const int n_seed_pts = std::min(int(seed_tracks.size()), max_n_seed_pts);
  std::sort(seed_tracks_pt, seed_tracks_pt + n_seed_pts);
  double pt_quantiles_temp[7] = {0};
  double pt_prob[7] = { 0.05, 0.1, 0.25, 0.5, 0.75, 0.90, 0.95 };
  TMath::Quantiles(n_seed_pts, 7, seed_tracks_pt, pt_quantiles_temp, pt_prob);
  for (int i = 0; i < 7; ++i) {
    (*pt_quantiles)[i] = pt_quantiles_temp[i];
    if (verbose) printf("pt seed quantile i=%i prob %f pt %f\n", i, pt_prob[i], (*pt_quantiles)[i]);
  }

  std::vector<bool> seed_use(ntk, 0);
  for (size_t itk = 0; itk < ntk; ++itk) {
    const track_cuts itk_tc(this, seed_tracks[itk].track(), *beamspot, primary_vertex, *tt_builder);
    seed_use[itk] = itk_tc.use(true);
  }

  for (size_t itk = 0; itk < ntk-1; ++itk) {
    if (!seed_use[itk])
      continue;

    for (size_t jtk = itk+1; jtk < ntk; ++jtk) {
      if (!seed_use[jtk])
        continue;

      std::vector<reco::TransientTrack> ttks;
      ttks.push_back(seed_tracks[itk]);
      ttks.push_back(seed_tracks[jtk]);

      //printf("itk %lu jtk %lu\n", itk, jtk); fflush(stdout);

      TransientVertex seed_vertex = kv_reco->vertex(ttks);
      if (seed_vertex.isValid() && seed_vertex.normalisedChiSquared() < max_seed_vertex_chi2) {
        vertices->push_back(reco::Vertex(seed_vertex));
        track_use[itk].push_back(std::make_pair(jtk, int(vertices->size()-1)));

        if (verbose || histos) {
          const reco::Vertex& v = vertices->back();
          const double vchi2 = v.normalizedChi2();
          const double vndof = v.ndof();
          const double vx = v.position().x() - bs_x;
          const double vy = v.position().y() - bs_y;
          const double vz = v.position().z() - bs_z;
          const double phi = atan2(vy, vx);
          const double rho = mag(vx, vy);
          const double r = mag(vx, vy, vz);
          if (verbose)
            printf("from tracks %3lu and %3lu: vertex #%3lu: chi2/dof: %7.3f dof: %7.3f pos: <%7.3f, %7.3f, %7.3f>  rho: %7.3f  phi: %7.3f  r: %7.3f\n", itk, jtk, vertices->size()-1, vchi2, vndof, vx, vy, vz, rho, phi, r);
          if (histos) {
            for (auto it = v.tracks_begin(), ite = v.tracks_end(); it != ite; ++it)
              h_seed_vertex_track_weights->Fill(v.trackWeight(*it));
            h_seed_vertex_chi2->Fill(vchi2);
            h_seed_vertex_ndof->Fill(vndof);
            h_seed_vertex_x->Fill(vx);
            h_seed_vertex_y->Fill(vy);
            h_seed_vertex_rho->Fill(rho);
            h_seed_vertex_phi->Fill(phi);
            h_seed_vertex_z->Fill(vz);
            h_seed_vertex_r->Fill(r);
          }
        }
      }
    }
  }

  if (histos) {
    for (std::vector<reco::Vertex>::const_iterator v0 = vertices->begin(); v0 != vertices->end(); ++v0) {
      const double v0x = v0->position().x() - bs_x;
      const double v0y = v0->position().y() - bs_y;
      const double phi0 = atan2(v0y, v0x);
      for (std::vector<reco::Vertex>::const_iterator v1 = v0 + 1; v1 != vertices->end(); ++v1) {
        const double v1x = v1->position().x() - bs_x;
        const double v1y = v1->position().y() - bs_y;
        const double phi1 = atan2(v1y, v1x);
        h_seed_vertex_paird2d ->Fill(mag(v0x - v1x, v0y - v1y));
        h_seed_vertex_pairdphi->Fill(reco::deltaPhi(phi0, phi1));
      }
    }
  }

  if (verbose)
    printf("n_seed_vertices: %lu\n", vertices->size());
  if (histos)
    h_n_seed_vertices->Fill(vertices->size());

  if (histos || verbose) {
    int max_seed_track_multiplicity = 0;

    for (size_t i = 0; i < ntk; ++i) {
      const auto& vec = track_use[i];
      int mult = int(vec.size());

      if (verbose && mult > 1) {
        printf("track %3lu used %3i times:", i, mult);
        for (const auto& pii : vec)
          printf(" (%i, %i)", pii.first, pii.second);
        printf("\n");
      }

      if (histos)
        h_seed_track_multiplicity->Fill(mult);

      if (mult > max_seed_track_multiplicity)
        max_seed_track_multiplicity = mult;
    }

    if (histos)
      h_max_seed_track_multiplicity->Fill(max_seed_track_multiplicity);
  }

  //////////////////////////////////////////////////////////////////////
  // Take care of track sharing. If a track is in two vertices, and
  // the vertices are "close", refit the tracks from the two together
  // as one vertex. If the vertices are not close, keep the track in
  // the vertex to which it is "closer".
  //////////////////////////////////////////////////////////////////////

  if (verbose)
    printf("fun time!\n");

  track_set discarded_tracks;
  int n_resets = 0;
  int n_onetracks = 0;
  std::vector<reco::Vertex>::iterator v[2];
  size_t ivtx[2];
  for (v[0] = vertices->begin(); v[0] != vertices->end(); ++v[0]) {
    track_set tracks[2];
    ivtx[0] = v[0] - vertices->begin();
    tracks[0] = vertex_track_set(*v[0]);

    if (tracks[0].size() < 2) {
      if (verbose)
        printf("track-sharing: vertex-0 #%lu is down to one track, junking it\n", ivtx[0]);
      v[0] = vertices->erase(v[0]) - 1;
      ++n_onetracks;
      continue;
    }

    bool duplicate = false;
    bool merge = false;
    bool refit = false;
    track_set tracks_to_remove_in_refit[2];

    for (v[1] = v[0] + 1; v[1] != vertices->end(); ++v[1]) {
      ivtx[1] = v[1] - vertices->begin();
      tracks[1] = vertex_track_set(*v[1]);

      if (tracks[1].size() < 2) {
        if (verbose)
          printf("track-sharing: vertex-1 #%lu is down to one track, junking it\n", ivtx[1]);
        v[1] = vertices->erase(v[1]) - 1;
        ++n_onetracks;
        continue;
      }

      if (verbose) {
        printf("track-sharing: # vertices = %lu. considering vertices #%lu (chi2/dof %.3f prob %.2e, track set", vertices->size(), ivtx[0], v[0]->chi2()/v[0]->ndof(), TMath::Prob(v[0]->chi2(), int(v[0]->ndof())));
        print_track_set(tracks[0], *v[0]);
        printf(") and #%lu (chi2/dof %.3f prob %.2e, track set", ivtx[1], v[1]->chi2()/v[1]->ndof(), TMath::Prob(v[1]->chi2(), int(v[1]->ndof())));
        print_track_set(tracks[1], *v[1]);
        printf("):\n");
      }

      if (is_track_subset(tracks[0], tracks[1])) {
        if (verbose)
          printf("   subset/duplicate vertices %lu and %lu, erasing second and starting over\n", ivtx[0], ivtx[1]);
        duplicate = true;
        break;
      }

      if (histos) {
        const int ntk_min = std::min(5, int(std::min(tracks[0].size(), tracks[1].size())));
        const int ntk_max = std::min(5, int(std::max(tracks[0].size(), tracks[1].size())));
        if (verbose) printf("t0 %i t1 %i min %i max %i\n", int(tracks[0].size()), int(tracks[1].size()), ntk_min, ntk_max);
        h_pairs_d2d [0]->Fill(mag(v[0]->x() - v[1]->x(),
                                  v[0]->y() - v[1]->y()));
        h_pairs_dphi[0]->Fill(reco::deltaPhi(atan2(v[0]->y() - bs_y, v[0]->x() - bs_x),
                                             atan2(v[1]->y() - bs_y, v[1]->x() - bs_x)));
        if (ntk_max >= 2) {
          h_pairs_d2d [ntk_max]->Fill(mag(v[0]->x() - v[1]->x(),
                                          v[0]->y() - v[1]->y()));
          h_pairs_dphi[ntk_max]->Fill(reco::deltaPhi(atan2(v[0]->y() - bs_y, v[0]->x() - bs_x),
                                                     atan2(v[1]->y() - bs_y, v[1]->x() - bs_x)));
        }
      }
      
      reco::TrackRefVector shared_tracks;
      for (auto tk : tracks[0])
        if (tracks[1].count(tk) > 0)
          shared_tracks.push_back(tk);

      if (verbose) {
        if (shared_tracks.size()) {
          printf("   shared tracks are: ");
          print_track_set(shared_tracks);
          printf("\n");
        }
        else
          printf("   no shared tracks\n");
      }  

      if (shared_tracks.size() > 0) {
        Measurement1D v_dist = vertex_dist(*v[0], *v[1]);
        if (verbose)
          printf("   vertex dist (2d? %i) %7.3f  sig %7.3f\n", use_2d_vertex_dist, v_dist.value(), v_dist.significance());
        if (histos) {
          const int ntk_max = std::min(5, int(std::max(tracks[0].size(), tracks[1].size())));
          h_share_d2d [0]->Fill(mag(v[0]->x() - v[1]->x(),
                                    v[0]->y() - v[1]->y()));
          h_share_dphi[0]->Fill(reco::deltaPhi(atan2(v[0]->y() - bs_y, v[0]->x() - bs_x),
                                               atan2(v[1]->y() - bs_y, v[1]->x() - bs_x)));
          if (ntk_max >= 2) {
            h_share_d2d [ntk_max]->Fill(mag(v[0]->x() - v[1]->x(),
                                            v[0]->y() - v[1]->y()));
            h_share_dphi[ntk_max]->Fill(reco::deltaPhi(atan2(v[0]->y() - bs_y, v[0]->x() - bs_x),
                                                       atan2(v[1]->y() - bs_y, v[1]->x() - bs_x)));
          }
        }

        if (v_dist.value() < merge_shared_dist || v_dist.significance() < merge_shared_sig) {
          if (verbose) printf("          dist < %7.3f || sig < %7.3f, will try using merge result first before arbitration\n", merge_shared_dist, merge_shared_sig);
          merge = true;
        }
        else
          refit = true;

        if (verbose) printf("   checking for arbitration refit:\n");
        for (auto tk : shared_tracks) {
          const reco::TransientTrack& ttk = seed_tracks[seed_track_ref_map[tk]];
          std::pair<bool, Measurement1D> t_dist_0 = track_dist(ttk, *v[0]);
          std::pair<bool, Measurement1D> t_dist_1 = track_dist(ttk, *v[1]);
          if (verbose) {
            printf("      track-vertex0 dist (2d? %i) calc success? %i  dist %7.3f  sig %7.3f\n", use_2d_track_dist, t_dist_0.first, t_dist_0.second.value(), t_dist_0.second.significance());
            printf("      track-vertex1 dist (2d? %i) calc success? %i  dist %7.3f  sig %7.3f\n", use_2d_track_dist, t_dist_1.first, t_dist_1.second.value(), t_dist_1.second.significance());
          }

          t_dist_0.first = t_dist_0.first && (t_dist_0.second.value() < max_track_vertex_dist || t_dist_0.second.significance() < max_track_vertex_sig);
          t_dist_1.first = t_dist_1.first && (t_dist_1.second.value() < max_track_vertex_dist || t_dist_1.second.significance() < max_track_vertex_sig);
          bool remove_from_0 = !t_dist_0.first;
          bool remove_from_1 = !t_dist_1.first;
          if (t_dist_0.second.significance() < min_track_vertex_sig_to_remove && t_dist_1.second.significance() < min_track_vertex_sig_to_remove) {
            if (tracks[0].size() > tracks[1].size())
              remove_from_1 = true;
            else
              remove_from_0 = true;
          }
          else if (t_dist_0.second.significance() < t_dist_1.second.significance())
            remove_from_1 = true;
          else
            remove_from_0 = true;

          if (verbose) {
            printf("   for tk %u:\n", tk.key());
            printf("      track-vertex0 dist < %7.3f || sig < %7.3f ? %i  remove? %i\n", max_track_vertex_dist, max_track_vertex_sig, t_dist_0.first, remove_from_0);
            printf("      track-vertex1 dist < %7.3f || sig < %7.3f ? %i  remove? %i\n", max_track_vertex_dist, max_track_vertex_sig, t_dist_1.first, remove_from_1);
          }

          if (remove_from_0) tracks_to_remove_in_refit[0].insert(tk);
          if (remove_from_1) tracks_to_remove_in_refit[1].insert(tk);

          if (remove_one_track_at_a_time) {
            if (verbose)
              printf("   arbitrate only one track at a time\n");
            break;
          }
        }

        if (verbose)
          printf("   breaking to refit\n");
        
        break;
      }

      if (verbose) printf("   moving on to next vertex pair.\n");
    }

    if (duplicate) {
      vertices->erase(v[1]);
    }
    else if (merge) {
      if (verbose)
        printf("      before merge, # total vertices = %lu\n", vertices->size());

      track_set tracks_to_fit;
      for (int i = 0; i < 2; ++i)
        for (auto tk : tracks[i])
          tracks_to_fit.insert(tk);

      if (verbose) {
        printf("   merging vertices %lu and %lu with these tracks:", ivtx[0], ivtx[1]);
        print_track_set(tracks_to_fit);
        printf("\n");
      }

      std::vector<reco::TransientTrack> ttks;
      for (auto tk : tracks_to_fit)
        ttks.push_back(seed_tracks[seed_track_ref_map[tk]]);
      
      reco::VertexCollection new_vertices;
      for (const TransientVertex& tv : kv_reco_dropin(ttks))
        new_vertices.push_back(reco::Vertex(tv));
      
      if (verbose) {
        printf("      got %lu new vertices out of the av fit\n", new_vertices.size());
        printf("      these (chi2/dof : prob | track sets):");
        for (const auto& nv : new_vertices) {
          printf(" (%.3f : %.2e | ", nv.chi2()/nv.ndof(), TMath::Prob(nv.chi2(), int(nv.ndof())));
          print_track_set(nv);
          printf(" ),");
        }
        printf("\n");
      }

      // If we got two new vertices, maybe it took A B and A C D and made a better one from B C D, and left a broken one A B! C! D!.
      // If we get one that is truly the merger of the track lists, great. If it is just something like A B , A C -> A B C!, or we get nothing, then default to arbitration.
      if (new_vertices.size() > 1) {
        if (verbose)
          printf("   jiggled again?\n");   
        assert(new_vertices.size() == 2);
        *v[1] = reco::Vertex(new_vertices[1]);
        *v[0] = reco::Vertex(new_vertices[0]);
      }
      else if (new_vertices.size() == 1 && vertex_track_set(new_vertices[0], 0) == tracks_to_fit) {
        if (verbose)
          printf("   merge worked!\n");   
        if (histos) {
          const int ntk_max = std::min(5, int(std::max(tracks[0].size(), tracks[1].size())));
          h_merge_d2d [0]->Fill(mag(v[0]->x() - v[1]->x(),
                                    v[0]->y() - v[1]->y()));
          h_merge_dphi[0]->Fill(reco::deltaPhi(atan2(v[0]->y() - bs_y, v[0]->x() - bs_x),
                                               atan2(v[1]->y() - bs_y, v[1]->x() - bs_x)));
          if (ntk_max >= 2) {
            h_merge_d2d [ntk_max]->Fill(mag(v[0]->x() - v[1]->x(),
                                            v[0]->y() - v[1]->y()));
            h_merge_dphi[ntk_max]->Fill(reco::deltaPhi(atan2(v[0]->y() - bs_y, v[0]->x() - bs_x),
                                                       atan2(v[1]->y() - bs_y, v[1]->x() - bs_x)));
          }
        }
        vertices->erase(v[1]);
        *v[0] = reco::Vertex(new_vertices[0]); // ok to use v[0] after the erase(v[1]) because v[0] is by construction before v[1]
      }
      else {
        if (verbose)
          printf("   merge didn't work, trying arbitration refits\n");   
        refit = true;
      }

      if (verbose)
        printf("   vertices size is now %lu\n", vertices->size());
    }

    if (refit) {
      bool erase[2] = { false };
      reco::Vertex vsave[2] = { *v[0], *v[1] };

      for (int i = 0; i < 2; ++i) {
        if (tracks_to_remove_in_refit[i].empty())
          continue;

        if (verbose) {
          printf("   refit vertex%i %lu with these tracks:", i, ivtx[i]);
          print_track_set(tracks[i]);
          printf("   but skip these:");
          print_track_set(tracks_to_remove_in_refit[i]);
          printf("\n");
        }

        std::vector<reco::TransientTrack> ttks;
        for (auto tk : tracks[i])
          if (tracks_to_remove_in_refit[i].count(tk) == 0) 
            ttks.push_back(seed_tracks[seed_track_ref_map[tk]]);

        reco::VertexCollection new_vertices;
        for (const TransientVertex& tv : kv_reco_dropin(ttks))
          new_vertices.push_back(reco::Vertex(tv));
        if (verbose) {
          printf("      got %lu new vertices out of the av fit for v%i\n", new_vertices.size(), i);
          printf("      these track sets:");
          for (const auto& nv : new_vertices) {
            printf(" (");
            print_track_set(nv);
            printf(" ),");
          }
          printf("\n");
        }
        if (new_vertices.size() == 1)
          *v[i] = new_vertices[0];
        else
          erase[i] = true;
      }

      if (histos && (erase[0] || erase[1])) {
        const int ntk_max = std::min(5, int(std::max(tracks[0].size(), tracks[1].size())));
        h_erase_d2d [0]->Fill(mag(vsave[0].x() - vsave[1].x(),
                                  vsave[0].y() - vsave[1].y()));
        h_erase_dphi[0]->Fill(reco::deltaPhi(atan2(vsave[0].y() - bs_y, vsave[0].x() - bs_x),
                                             atan2(vsave[1].y() - bs_y, vsave[1].x() - bs_x)));
        if (ntk_max >= 2) {
          h_erase_d2d [ntk_max]->Fill(mag(vsave[0].x() - vsave[1].x(),
                                          vsave[0].y() - vsave[1].y()));
          h_erase_dphi[ntk_max]->Fill(reco::deltaPhi(atan2(vsave[0].y() - bs_y, vsave[0].x() - bs_x),
                                                     atan2(vsave[1].y() - bs_y, vsave[1].x() - bs_x)));
        }
      }

      if (erase[1]) vertices->erase(v[1]);
      if (erase[0]) vertices->erase(v[0]);

      if (verbose)
        printf("      vertices size is now %lu\n", vertices->size());
    }

    // If we changed the vertices at all, start loop over completely.
    if (duplicate || merge || refit) {
      v[0] = vertices->begin() - 1;  // -1 because about to ++sv
      ++n_resets;
      if (verbose) printf("   resetting from vertices %lu and %lu. # of resets: %i\n", ivtx[0], ivtx[1], n_resets);
      
      if (phitest) {
        TH1F* phi_temp = new TH1F("phi_temp", "", 50, -3.14159266, 3.14159266);
        for (const reco::Vertex& v : *vertices)
          phi_temp->Fill(atan2(v.y(), v.x()));
        TFitResultPtr fit = phi_temp->Fit("pol1", "Q0LS");
        h_phitest_nvtx->SetBinContent(iphitest, vertices->size());
        h_phitest_mean->SetBinContent(iphitest, phi_temp->GetMean());
        h_phitest_mean->SetBinError  (iphitest, phi_temp->GetMeanError());
        h_phitest_rms ->SetBinContent(iphitest, phi_temp->GetRMS());
        h_phitest_rms ->SetBinError  (iphitest, phi_temp->GetRMSError());
        h_phitest_p0  ->SetBinContent(iphitest, fit->Parameter(0));
        h_phitest_p0  ->SetBinError  (iphitest, fit->ParError(0));
        h_phitest_p1  ->SetBinContent(iphitest, fit->Parameter(1));
        h_phitest_p1  ->SetBinError  (iphitest, fit->ParError(1));
        ++iphitest;
        delete phi_temp;
      }

      //if (n_resets == 3000)
      //  throw "I'm dumb";
    }
  }

  if (verbose)
    printf("n_resets: %i  n_onetracks: %i  n_noshare_vertices: %lu\n", n_resets, n_onetracks, vertices->size());
  if (histos) {
    h_n_resets->Fill(n_resets);
    h_n_onetracks->Fill(n_onetracks);
    h_n_noshare_vertices->Fill(vertices->size());
  }

  if (histos || verbose) {
    std::map<reco::TrackRef, int> track_use;
    for (size_t i = 0, ie = vertices->size(); i < ie; ++i) {
      const reco::Vertex& v = vertices->at(i);
      const int ntracks = v.nTracks();
      const double vchi2 = v.normalizedChi2();
      const double vndof = v.ndof();
      const double vx = v.position().x() - bs_x;
      const double vy = v.position().y() - bs_y;
      const double vz = v.position().z() - bs_z;
      const double rho = mag(vx, vy);
      const double phi = atan2(vy, vx);
      const double r = mag(vx, vy, vz);
      for (const auto& r : vertex_track_set(v)) {
        if (track_use.find(r) != track_use.end())
          track_use[r] += 1;
        else
          track_use[r] = 1;
      }

      if (verbose)
        printf("no-share vertex #%3lu: ntracks: %i chi2/dof: %7.3f dof: %7.3f pos: <%7.3f, %7.3f, %7.3f>  rho: %7.3f  phi: %7.3f  r: %7.3f\n", i, ntracks, vchi2, vndof, vx, vy, vz, rho, phi, r);

      if (histos) {
        h_noshare_vertex_ntracks->Fill(ntracks);
        for (auto it = v.tracks_begin(), ite = v.tracks_end(); it != ite; ++it) {
	  h_noshare_vertex_track_weights->Fill(v.trackWeight(*it));

	  reco::TransientTrack seed_track;
	  seed_track = tt_builder->build(*it.operator*());
	  std::pair<bool, Measurement1D> tk_vtx_dist = track_dist(seed_track, v);
	  h_noshare_vertex_tkvtxdist->Fill(tk_vtx_dist.second.value());
	  h_noshare_vertex_tkvtxdisterr->Fill(tk_vtx_dist.second.error());
	  h_noshare_vertex_tkvtxdistsig->Fill(tk_vtx_dist.second.significance());
	}
        h_noshare_vertex_chi2->Fill(vchi2);
        h_noshare_vertex_ndof->Fill(vndof);
        h_noshare_vertex_x->Fill(vx);
        h_noshare_vertex_y->Fill(vy);
        h_noshare_vertex_rho->Fill(rho);
        h_noshare_vertex_phi->Fill(phi);
        h_noshare_vertex_z->Fill(vz);
        h_noshare_vertex_r->Fill(r);

        for (size_t j = i+1, je = vertices->size(); j < je; ++j) {
          const reco::Vertex& vj = vertices->at(j);
          const double vjx = vj.position().x() - bs_x;
          const double vjy = vj.position().y() - bs_y;
          const double phij = atan2(vjy, vjx);
          h_noshare_vertex_paird2d->Fill(mag(vx - vjx, vy - vjy));
          h_noshare_vertex_pairdphi->Fill(reco::deltaPhi(phi, phij));
        }
      }
    }
    
    if (verbose)
      printf("track multiple uses:\n");

    int max_noshare_track_multiplicity = 0;
    for (const auto& p : track_use) {
      if (verbose && p.second > 1)
        printf("track %3u used %3i times\n", p.first.key(), p.second);
      if (histos)
        h_noshare_track_multiplicity->Fill(p.second);
      if (p.second > max_noshare_track_multiplicity)
        max_noshare_track_multiplicity = p.second;
    }
    if (histos)
      h_max_noshare_track_multiplicity->Fill(max_noshare_track_multiplicity);
  }

  //////////////////////////////////////////////////////////////////////
  // Merge vertices that are still "close". JMTBAD this doesn't do anything currently.
  //////////////////////////////////////////////////////////////////////

  if (verbose)
    printf("fun2!\n");

  for (v[0] = vertices->begin(); v[0] != vertices->end(); ++v[0]) {
    ivtx[0] = v[0] - vertices->begin();

    bool merge = false;
    for (v[1] = v[0] + 1; v[1] != vertices->end(); ++v[1]) {
      ivtx[1] = v[1] - vertices->begin();

      if (verbose)
        printf("close-merge: # vertices = %lu. considering vertices #%lu (ntk = %i) and #%lu (ntk = %i):", vertices->size(), ivtx[0], v[0]->nTracks(), ivtx[1], v[1]->nTracks());

      Measurement1D v_dist = vertex_dist(*v[0], *v[1]);
      if (verbose)
        printf("   vertex dist (2d? %i) %7.3f  sig %7.3f\n", use_2d_vertex_dist, v_dist.value(), v_dist.significance());
  
      if (v_dist.value() < merge_anyway_dist || v_dist.significance() < merge_anyway_sig) {
        if (verbose)
          printf("          dist < %7.3f || sig < %7.3f, breaking to merge\n", merge_anyway_dist, merge_anyway_sig);
        merge = true;
        break;
      }
    }

    if (merge) {
      std::vector<reco::TransientTrack> ttks;
      for (int i = 0; i < 2; ++i)
        for (auto tk : vertex_track_set(*v[i]))
          ttks.push_back(tt_builder->build(tk));
      
      reco::VertexCollection new_vertices;
      for (const TransientVertex& tv : kv_reco_dropin(ttks))
        new_vertices.push_back(reco::Vertex(tv));
      
      if (verbose) {
        printf("      got %lu new vertices out of the av fit\n", new_vertices.size());
        printf("      these track sets:");
        for (const auto& nv : new_vertices) {
          printf(" (");
          print_track_set(nv);
          printf(" ),");
        }
        printf("\n");
      }
    }
  }
 
  //////////////////////////////////////////////////////////////////////
  // Put the output.
  //////////////////////////////////////////////////////////////////////

  finish(event, vertices, pt_quantiles);
}

DEFINE_FWK_MODULE(MFVVertexer);
