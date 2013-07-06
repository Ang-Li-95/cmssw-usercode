#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "RecoVertex/ConfigurableVertexReco/interface/ConfigurableVertexReconstructor.h"
#include "RecoVertex/KalmanVertexFit/interface/KalmanVertexFitter.h"
#include "RecoVertex/VertexTools/interface/VertexDistance3D.h"
#include "TrackingTools/IPTools/interface/IPTools.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrack.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"

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

  const edm::InputTag beamspot_src;
  const edm::InputTag track_src;
  const double min_seed_track_pt;
  const double min_seed_track_dxy;
  const int min_seed_track_nhits;
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
  const bool histos;
  const bool verbose;

  TH1F* h_n_all_tracks;
  TH1F* h_all_track_pt;
  TH1F* h_all_track_dxy;
  TH1F* h_all_track_nhits;
  TH1F* h_n_seed_tracks;
  TH1F* h_seed_track_pt;
  TH1F* h_seed_track_dxy;
  TH1F* h_seed_track_nhits;
  TH1F* h_n_seed_vertices;
  TH1F* h_seed_vertex_track_weights;
  TH1F* h_seed_vertex_chi2;
  TH1F* h_seed_vertex_ndof;
  TH1F* h_seed_vertex_x;
  TH1F* h_seed_vertex_y;
  TH1F* h_seed_vertex_rho;
  TH1F* h_seed_vertex_z;
  TH1F* h_seed_vertex_r;
  TH1F* h_seed_track_multiplicity;
  TH1F* h_max_seed_track_multiplicity;
  TH1F* h_n_resets;
  TH1F* h_n_onetracks;
  TH1F* h_n_noshare_vertices;
  TH1F* h_noshare_vertex_ntracks;
  TH1F* h_noshare_vertex_track_weights;
  TH1F* h_noshare_vertex_chi2;
  TH1F* h_noshare_vertex_ndof;
  TH1F* h_noshare_vertex_x;
  TH1F* h_noshare_vertex_y;
  TH1F* h_noshare_vertex_rho;
  TH1F* h_noshare_vertex_z;
  TH1F* h_noshare_vertex_r;
  TH1F* h_noshare_track_multiplicity;
  TH1F* h_max_noshare_track_multiplicity;
  TH1F* h_n_output_vertices;
};

MFVVertexer::MFVVertexer(const edm::ParameterSet& cfg)
  : kv_reco(new KalmanVertexFitter(cfg.getParameter<edm::ParameterSet>("kvr_params"), cfg.getParameter<edm::ParameterSet>("kvr_params").getParameter<bool>("doSmoothing"))),
    av_reco(new ConfigurableVertexReconstructor(cfg.getParameter<edm::ParameterSet>("avr_params"))),
    beamspot_src(cfg.getParameter<edm::InputTag>("beamspot_src")),
    track_src(cfg.getParameter<edm::InputTag>("track_src")),
    min_seed_track_pt(cfg.getParameter<double>("min_seed_track_pt")),
    min_seed_track_dxy(cfg.getParameter<double>("min_seed_track_dxy")),
    min_seed_track_nhits(cfg.getParameter<int>("min_seed_track_nhits")),
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
    histos(cfg.getUntrackedParameter<bool>("histos", true)),
    verbose(cfg.getUntrackedParameter<bool>("verbose", false))
{
  produces<reco::VertexCollection>();

  if (histos) {
    edm::Service<TFileService> fs;
    h_n_all_tracks                   = fs->make<TH1F>("h_n_all_tracks",                   "", 200,   0,   2000);
    h_all_track_pt                   = fs->make<TH1F>("h_all_track_pt",                   "", 250,   0,    500);
    h_all_track_dxy                  = fs->make<TH1F>("h_all_track_dxy",                  "", 200,  -1,      1);
    h_all_track_nhits                = fs->make<TH1F>("h_all_track_nhits",                "",  40,   0,     40);
    h_n_seed_tracks                  = fs->make<TH1F>("h_n_seed_tracks",                  "", 200,   0,    600);
    h_seed_track_pt                  = fs->make<TH1F>("h_seed_track_pt",                  "", 250,   0,    500);
    h_seed_track_dxy                 = fs->make<TH1F>("h_seed_track_dxy",                 "", 200,  -1,      1);
    h_seed_track_nhits               = fs->make<TH1F>("h_seed_track_nhits",               "",  40,   0,     40);
    h_n_seed_vertices                = fs->make<TH1F>("h_n_seed_vertices",                "", 200,   0,    400);
    h_seed_vertex_track_weights      = fs->make<TH1F>("h_seed_vertex_track_weights",      "",  64,   0,      1);
    h_seed_vertex_chi2               = fs->make<TH1F>("h_seed_vertex_chi2",               "", 100,   0, max_seed_vertex_chi2);
    h_seed_vertex_ndof               = fs->make<TH1F>("h_seed_vertex_ndof",               "", 100,   0,     20);
    h_seed_vertex_x                  = fs->make<TH1F>("h_seed_vertex_x",                  "", 200,  -1,      1);
    h_seed_vertex_y                  = fs->make<TH1F>("h_seed_vertex_y",                  "", 200,  -1,      1);
    h_seed_vertex_rho                = fs->make<TH1F>("h_seed_vertex_rho",                "", 200,   0,      2);
    h_seed_vertex_z                  = fs->make<TH1F>("h_seed_vertex_z",                  "", 200, -20,     20);
    h_seed_vertex_r                  = fs->make<TH1F>("h_seed_vertex_r",                  "", 200,   0,      2);
    h_seed_track_multiplicity        = fs->make<TH1F>("h_seed_track_multiplicity",        "",  40,   0,     40);
    h_max_seed_track_multiplicity    = fs->make<TH1F>("h_max_seed_track_multiplicity",    "",  40,   0,     40);
    h_n_resets                       = fs->make<TH1F>("h_n_resets",                       "", 100,   0,   5000);
    h_n_onetracks                    = fs->make<TH1F>("h_n_onetracks",                    "",  20,   0,     20);
    h_n_noshare_vertices             = fs->make<TH1F>("h_n_noshare_vertices",             "", 200,   0,    200);
    h_noshare_vertex_ntracks         = fs->make<TH1F>("h_noshare_vertex_ntracks",         "",  50, 0, 50);
    h_noshare_vertex_track_weights   = fs->make<TH1F>("h_noshare_vertex_track_weights",   "",  64,   0,      1);
    h_noshare_vertex_chi2            = fs->make<TH1F>("h_noshare_vertex_chi2",            "", 100,   0, max_seed_vertex_chi2);
    h_noshare_vertex_ndof            = fs->make<TH1F>("h_noshare_vertex_ndof",            "", 100,   0,     20);
    h_noshare_vertex_x               = fs->make<TH1F>("h_noshare_vertex_x",               "", 200,  -1,      1);
    h_noshare_vertex_y               = fs->make<TH1F>("h_noshare_vertex_y",               "", 200,  -1,      1);
    h_noshare_vertex_rho             = fs->make<TH1F>("h_noshare_vertex_rho",             "", 200,   0,      2);
    h_noshare_vertex_z               = fs->make<TH1F>("h_noshare_vertex_z",               "", 200, -20,     20);
    h_noshare_vertex_r               = fs->make<TH1F>("h_noshare_vertex_r",               "", 200,   0,      2);
    h_noshare_track_multiplicity     = fs->make<TH1F>("h_noshare_track_multiplicity",     "",  40,   0,     40);
    h_max_noshare_track_multiplicity = fs->make<TH1F>("h_max_noshare_track_multiplicity", "",  40,   0,     40);
    h_n_output_vertices           = fs->make<TH1F>("h_n_output_vertices",           "", 200,   0,    200);
  }
}

void MFVVertexer::produce(edm::Event& event, const edm::EventSetup& setup) {
  if (verbose) {
    printf("------------------------------------------------------------------------\n");
    printf("MFVVertexer::produce: run %u, lumi %u, event %u\n", event.id().run(), event.luminosityBlock(), event.id().event());
  }

  edm::Handle<reco::BeamSpot> beamspot;
  event.getByLabel(beamspot_src, beamspot);
  const double bs_x = beamspot->position().x();
  const double bs_y = beamspot->position().y();
  const double bs_z = beamspot->position().z();

  edm::Handle<reco::TrackCollection> tracks;
  event.getByLabel(track_src, tracks);

  edm::ESHandle<TransientTrackBuilder> tt_builder;
  setup.get<TransientTrackRecord>().get("TransientTrackBuilder", tt_builder);

  //////////////////////////////////////////////////////////////////////
  // Select tracks for seeding passing pt, dxy, nhits cuts.
  //////////////////////////////////////////////////////////////////////

  std::vector<reco::TransientTrack> seed_tracks;
  std::map<reco::TrackRef, size_t> seed_track_ref_map;
  for (size_t i = 0, ie = tracks->size(); i < ie; ++i) {
    reco::TrackRef tk(tracks, i);
    const double pt = tk->pt();
    const double dxy = tk->dxy(beamspot->position());
    const int nhits = tk->hitPattern().numberOfValidHits();

    if (verbose)
      printf("track %5lu: pt: %7.3f dxy: %7.3f nhits %3i ", i, pt, dxy, nhits);

    if (histos) {
      h_all_track_pt->Fill(pt);
      h_all_track_dxy->Fill(dxy);
      h_all_track_nhits->Fill(nhits);
    }

    if (pt > min_seed_track_pt && fabs(dxy) > min_seed_track_dxy && nhits >= min_seed_track_nhits) {
      seed_tracks.push_back(tt_builder->build(tk));
      seed_track_ref_map[tk] = seed_tracks.size() - 1;

      if (histos) {
        h_seed_track_pt->Fill(pt);
        h_seed_track_dxy->Fill(dxy);
        h_seed_track_nhits->Fill(nhits);
      }

      if (verbose)
        printf(" selected for seed! (#%lu)", seed_tracks.size()-1);
    }

    if (verbose)
      printf("\n");
  }
  
  const size_t ntk = seed_tracks.size();

  if (verbose)
    printf("n_all_tracks: %5lu   n_seed_tracks: %5lu\n", tracks->size(), ntk);

  if (histos) {
    h_n_all_tracks->Fill(tracks->size());
    h_n_seed_tracks->Fill(ntk);
  }

  //////////////////////////////////////////////////////////////////////
  // Form seed vertices from all pairs of tracks whose vertex fit
  // passes cuts.
  //////////////////////////////////////////////////////////////////////

  std::auto_ptr<reco::VertexCollection> vertices(new reco::VertexCollection);
  std::vector<std::vector<std::pair<int, int> > > track_use(ntk);

  for (size_t itk = 0; itk < ntk-1; ++itk) {
    for (size_t jtk = itk+1; jtk < ntk; ++jtk) {
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
          const double rho = mag(vx, vy);
          const double r = mag(vx, vy, vz);
          if (verbose)
            printf("from tracks %3lu and %3lu: vertex #%3lu: chi2/dof: %7.3f dof: %7.3f pos: <%7.3f, %7.3f, %7.3f>  rho: %7.3f  r: %7.3f\n", itk, jtk, vertices->size()-1, vchi2, vndof, vx, vy, vz, rho, r);
          if (histos) {
            for (auto it = v.tracks_begin(), ite = v.tracks_end(); it != ite; ++it)
              h_seed_vertex_track_weights->Fill(v.trackWeight(*it));
            h_seed_vertex_chi2->Fill(vchi2);
            h_seed_vertex_ndof->Fill(vndof);
            h_seed_vertex_x->Fill(vx);
            h_seed_vertex_y->Fill(vy);
            h_seed_vertex_rho->Fill(rho);
            h_seed_vertex_z->Fill(vz);
            h_seed_vertex_r->Fill(r);
          }
        }
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
        printf("track-sharing: # vertices = %lu. considering vertices #%lu (track set", vertices->size(), ivtx[0]);
        print_track_set(tracks[0], *v[0]);
        printf(") and #%lu (track set", ivtx[1]);
        print_track_set(tracks[1], *v[1]);
        printf("):\n");
      }

      if (is_track_subset(tracks[0], tracks[1])) {
        if (verbose)
          printf("   subset/duplicate vertices %lu and %lu, erasing second and starting over\n", ivtx[0], ivtx[1]);
        duplicate = true;
        break;
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
        printf("      these track sets:");
        for (const auto& nv : new_vertices) {
          printf(" (");
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
      const double r = mag(vx, vy, vz);
      for (const auto& r : vertex_track_set(v)) {
        if (track_use.find(r) != track_use.end())
          track_use[r] += 1;
        else
          track_use[r] = 1;
      }

      if (verbose)
        printf("no-share vertex #%3lu: ntracks: %i chi2/dof: %7.3f dof: %7.3f pos: <%7.3f, %7.3f, %7.3f>  rho: %7.3f  r: %7.3f\n", i, ntracks, vchi2, vndof, vx, vy, vz, rho, r);

      if (histos) {
        h_noshare_vertex_ntracks->Fill(ntracks);
        for (auto it = v.tracks_begin(), ite = v.tracks_end(); it != ite; ++it)
          h_noshare_vertex_track_weights->Fill(v.trackWeight(*it));
        h_noshare_vertex_chi2->Fill(vchi2);
        h_noshare_vertex_ndof->Fill(vndof);
        h_noshare_vertex_x->Fill(vx);
        h_noshare_vertex_y->Fill(vy);
        h_noshare_vertex_rho->Fill(rho);
        h_noshare_vertex_z->Fill(vz);
        h_noshare_vertex_r->Fill(r);
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
  // Merge vertices that are still "close".
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

  if (verbose)
    printf("n_output_vertices: %lu\n", vertices->size());
  if (histos)
    h_n_output_vertices->Fill(vertices->size());

  event.put(vertices);
}

DEFINE_FWK_MODULE(MFVVertexer);
