#include "TH1F.h"
#include "TH2F.h"
#include "TLorentzVector.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "JMTucker/MFVNeutralino/interface/MCInteractionMFV3j.h"
#include "JMTucker/MFVNeutralinoFormats/interface/Event.h"
#include "JMTucker/MFVNeutralinoFormats/interface/VertexAux.h"
#include "JMTucker/Tools/interface/GenUtilities.h"
#include "JMTucker/Tools/interface/Utilities.h"

class MFVResolutions : public edm::EDAnalyzer {
 public:
  explicit MFVResolutions(const edm::ParameterSet&);
  void analyze(const edm::Event&, const edm::EventSetup&);

 private:
  const std::string mode;
  const bool doing_h2xqq;
  const bool doing_mfv2j;
  const bool doing_mfv3j;
  const bool doing_mfv4j;
  const bool doing_mfv5j;

  const edm::InputTag vertex_src;
  const edm::InputTag mevent_src;
  const int which_mom;
  const double max_dr;
  const double max_dist;

  const edm::InputTag gen_src;
  bool mci_warned;
  const edm::InputTag gen_jet_src;

  TH1F* h_dist;

  TH1F* h_lspsnmatch;

  TH1F* h_rec_dxy;
  TH1F* h_rec_ntracks;
  TH1F* h_rec_bs2derr;
  TH1F* h_rec_drmin;
  TH1F* h_rec_drmax;
  TH1F* h_rec_dravg;
  TH1F* h_rec_drrms;
  TH1F* h_rec_njetsntks;
  TH1F* h_rec_ntracksptgt3;
  TH1F* h_rec_dbv;
  TH1F* h_rec_betagamma;
  TH1F* h_rec_dirrms;
  TH1F* h_rec_tracks_qpt;
  TH1F* h_rec_tracks_eta;
  TH1F* h_rec_tracks_phi;
  TH1F* h_rec_trackpair_deta;
  TH1F* h_rec_trackpair_dphi;
  TH1F* h_rec_trackpair_dr;
  TH1F* h_rec_tracks_deta;
  TH1F* h_rec_tracks_dphi;
  TH1F* h_rec_tracks_dr;
  TH2F* h_rec_drrms_ntracks;
  TH2F* h_rec_drrms_dravg;
  TH2F* h_rec_dirrms_dravg;
  TH1F* h_rec_dvv;

  TH1F* h_rec_bs2derr_betagamma0p00to0p25;
  TH1F* h_rec_bs2derr_betagamma0p25to0p50;
  TH1F* h_rec_bs2derr_betagamma0p50to0p75;
  TH1F* h_rec_bs2derr_betagamma0p75to1p00;
  TH1F* h_rec_bs2derr_betagamma1p00to1p25;
  TH1F* h_rec_bs2derr_betagamma1p25to1p50;
  TH1F* h_rec_bs2derr_betagamma1p50to1p75;
  TH1F* h_rec_bs2derr_betagamma1p75to2p00;
  TH1F* h_rec_bs2derr_betagamma2p00to2p25;
  TH1F* h_rec_bs2derr_betagamma2p25to2p50;
  TH1F* h_rec_bs2derr_betagamma2p50to2p75;
  TH1F* h_rec_bs2derr_betagamma2p75to3p00;
  TH2F* h_rec_bs2derr_gen_betagamma;

  TH1F* h_gen_jetpt4;
  TH1F* h_gen_sumht;
  TH1F* h_gen_dxy;
  TH1F* h_gen_ntracks;
  TH1F* h_gen_nquarks;
  TH1F* h_gen_sumpt;
  TH1F* h_gen_drmin;
  TH1F* h_gen_drmax;
  TH1F* h_gen_betagamma;

  TH1F* h_gen_dbv;
  TH1F* h_gen_dvv;

  TH2F* h_lsp_ntracks0_ntracks1;
};

MFVResolutions::MFVResolutions(const edm::ParameterSet& cfg)
  : mode(cfg.getParameter<std::string>("mode")),
    doing_h2xqq(mode == "h2xqq"),
    doing_mfv2j(mode == "mfv2j"),
    doing_mfv3j(mode == "mfv3j"),
    doing_mfv4j(mode == "mfv4j"),
    doing_mfv5j(mode == "mfv5j"),
    vertex_src(cfg.getParameter<edm::InputTag>("vertex_src")),
    mevent_src(cfg.getParameter<edm::InputTag>("mevent_src")),
    which_mom(cfg.getParameter<int>("which_mom")),
    max_dr(cfg.getParameter<double>("max_dr")),
    max_dist(cfg.getParameter<double>("max_dist")),
    gen_src(cfg.getParameter<edm::InputTag>("gen_src")),
    gen_jet_src(cfg.getParameter<edm::InputTag>("gen_jet_src"))
{
  if (!(doing_h2xqq || doing_mfv2j || doing_mfv3j || doing_mfv4j || doing_mfv5j))
    throw cms::Exception("Configuration") << "mode must be h2xqq, mfv2j, mfv3j, mfv4j, or mfv5j, got " << mode;

  die_if_not(which_mom >= 0 && which_mom < mfv::NMomenta, "invalid which_mom");

  edm::Service<TFileService> fs;

  h_dist = fs->make<TH1F>("h_dist", ";distance to closest lsp;number of vertices", 100, 0, 0.02);

  h_lspsnmatch = fs->make<TH1F>("h_lspsnmatch", ";number of vertices that match LSP;LSPs", 15, 0, 15);

  h_rec_dxy = fs->make<TH1F>("h_rec_dxy", ";reconstructed d_{xy} (cm);tracks", 100, 0, 1);
  h_rec_ntracks = fs->make<TH1F>("h_rec_ntracks", ";number of tracks/vertex;vertices", 40, 0, 40);
  h_rec_bs2derr = fs->make<TH1F>("h_rec_bs2derr", ";#sigma(d_{BV}) (cm);vertices", 25, 0, 0.0025);
  h_rec_drmin = fs->make<TH1F>("h_rec_drmin", ";min{#Delta R{track i,j}};vertices", 50, 0, 0.5);
  h_rec_drmax = fs->make<TH1F>("h_rec_drmax", ";max{#Delta R{track i,j}};vertices", 50, 0, 5);
  h_rec_dravg = fs->make<TH1F>("h_rec_dravg", ";avg{#Delta R{track i,j}};vertices", 50, 0, 5);
  h_rec_drrms = fs->make<TH1F>("h_rec_drrms", ";rms{#Delta R{track i,j}};vertices", 50, 0, 5);
  h_rec_njetsntks = fs->make<TH1F>("h_rec_njetsntks", ";number of associated jets;vertices", 10, 0, 10);
  h_rec_ntracksptgt3 = fs->make<TH1F>("h_rec_ntracksptgt3", ";number of tracks with p_{T} > 3 GeV/vertex;vertices", 40, 0, 40);
  h_rec_dbv = fs->make<TH1F>("h_rec_dbv", ";reconstructed d_{BV} (cm);vertices", 250, 0, 2.5);
  h_rec_betagamma = fs->make<TH1F>("h_rec_betagamma", ";reconstructed #beta#gamma;vertices", 20, 0, 10);
  h_rec_dirrms = fs->make<TH1F>("h_rec_dirrms", ";rms{direction{track i}} w.r.t. direction of net momentum by tracks only;vertices", 50, 0, 5);
  h_rec_tracks_qpt = fs->make<TH1F>("h_rec_tracks_qpt", ";reconstructed track q*p_{T} (GeV);tracks", 100, -150, 150);
  h_rec_tracks_eta = fs->make<TH1F>("h_rec_tracks_eta", ";reconstructed track #eta;tracks", 50, -4, 4);
  h_rec_tracks_phi = fs->make<TH1F>("h_rec_tracks_phi", ";reconstructed track #phi;tracks", 50, -3.15, 3.15);
  h_rec_trackpair_deta = fs->make<TH1F>("h_rec_trackpair_deta", ";reconstructed track pair #Delta#eta;track pairs", 50, 0, 5);
  h_rec_trackpair_dphi = fs->make<TH1F>("h_rec_trackpair_dphi", ";reconstructed track pair #Delta#phi;track pairs", 32, 0, 3.2);
  h_rec_trackpair_dr = fs->make<TH1F>("h_rec_trackpair_dr", ";reconstructed track pair #DeltaR;track pairs", 50, 0, 5);
  h_rec_tracks_deta = fs->make<TH1F>("h_rec_tracks_deta", ";reconstructed track #Delta#eta w.r.t. direction of net momentum by tracks only;tracks", 50, 0, 5);
  h_rec_tracks_dphi = fs->make<TH1F>("h_rec_tracks_dphi", ";reconstructed track #Delta#phi w.r.t. direction of net momentum by tracks only;tracks", 32, 0, 3.2);
  h_rec_tracks_dr = fs->make<TH1F>("h_rec_tracks_dr", ";reconstructed track #DeltaR w.r.t. direction of net momentum by tracks only;tracks", 50, 0, 5);
  h_rec_drrms_ntracks = fs->make<TH2F>("h_rec_drrms_ntracks", ";ntracks;drrms", 40, 0, 40, 50, 0, 5);
  h_rec_drrms_dravg = fs->make<TH2F>("h_rec_drrms_dravg", ";dravg;drrms", 50, 0, 5, 50, 0, 5);
  h_rec_dirrms_dravg = fs->make<TH2F>("h_rec_dirrms_dravg", ";dravg;dirrms", 50, 0, 5, 50, 0, 5);
  h_rec_dvv = fs->make<TH1F>("h_rec_dvv", ";reconstructed d_{VV} (cm);events", 500, 0, 5);

  h_rec_bs2derr_betagamma0p00to0p25 = fs->make<TH1F>("h_rec_bs2derr_betagamma0p00to0p25", "0.00 < generated #beta#gamma < 0.25;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma0p25to0p50 = fs->make<TH1F>("h_rec_bs2derr_betagamma0p25to0p50", "0.25 < generated #beta#gamma < 0.50;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma0p50to0p75 = fs->make<TH1F>("h_rec_bs2derr_betagamma0p50to0p75", "0.50 < generated #beta#gamma < 0.75;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma0p75to1p00 = fs->make<TH1F>("h_rec_bs2derr_betagamma0p75to1p00", "0.75 < generated #beta#gamma < 1.00;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma1p00to1p25 = fs->make<TH1F>("h_rec_bs2derr_betagamma1p00to1p25", "1.00 < generated #beta#gamma < 1.25;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma1p25to1p50 = fs->make<TH1F>("h_rec_bs2derr_betagamma1p25to1p50", "1.25 < generated #beta#gamma < 1.50;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma1p50to1p75 = fs->make<TH1F>("h_rec_bs2derr_betagamma1p50to1p75", "1.50 < generated #beta#gamma < 1.75;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma1p75to2p00 = fs->make<TH1F>("h_rec_bs2derr_betagamma1p75to2p00", "1.75 < generated #beta#gamma < 2.00;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma2p00to2p25 = fs->make<TH1F>("h_rec_bs2derr_betagamma2p00to2p25", "2.00 < generated #beta#gamma < 2.25;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma2p25to2p50 = fs->make<TH1F>("h_rec_bs2derr_betagamma2p25to2p50", "2.25 < generated #beta#gamma < 2.50;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma2p50to2p75 = fs->make<TH1F>("h_rec_bs2derr_betagamma2p50to2p75", "2.50 < generated #beta#gamma < 2.75;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_betagamma2p75to3p00 = fs->make<TH1F>("h_rec_bs2derr_betagamma2p75to3p00", "2.75 < generated #beta#gamma < 3.00;reconstructed bs2derr;vertices", 25, 0, 0.0025);
  h_rec_bs2derr_gen_betagamma = fs->make<TH2F>("h_rec_bs2derr_gen_betagamma", ";generated #beta#gamma;reconstructed bs2derr", 20, 0, 10, 25, 0, 0.0025);

  h_gen_jetpt4 = fs->make<TH1F>("h_gen_jetpt4", ";p_{T} of 4th accepted quark (GeV);events", 200, 0, 200);
  h_gen_sumht = fs->make<TH1F>("h_gen_sumht", ";#SigmaH_{T} of accepted quarks (GeV);events", 200, 0, 2000);
  h_gen_dxy = fs->make<TH1F>("h_gen_dxy", ";generated d_{xy} (cm);LSP daughter particles", 100, 0, 1);
  h_gen_ntracks = fs->make<TH1F>("h_gen_ntracks", ";number of accepted displaced daughter particles;LSPs", 10, 0, 10);
  h_gen_nquarks = fs->make<TH1F>("h_gen_nquarks", ";number of accepted displaced quarks;LSPs", 10, 0, 10);
  h_gen_sumpt = fs->make<TH1F>("h_gen_sumpt", ";#Sigmap_{T} of accepted displaced daughter particles (GeV);LSPs", 100, 0, 1000);
  h_gen_drmin = fs->make<TH1F>("h_gen_drmin", ";min #DeltaR between accepted displaced daughter particles;LSPs", 100, 0, 5);
  h_gen_drmax = fs->make<TH1F>("h_gen_drmax", ";max #DeltaR between accepted displaced daughter particles;LSPs", 100, 0, 5);
  h_gen_betagamma = fs->make<TH1F>("h_gen_betagamma", ";generated #beta#gamma;LSPs", 20, 0, 10);

  h_gen_dbv = fs->make<TH1F>("h_gen_dbv", ";generated d_{BV} (cm);LSPs", 250, 0, 2.5);
  h_gen_dvv = fs->make<TH1F>("h_gen_dvv", ";generated d_{VV} (cm);events", 500, 0, 5);

  h_lsp_ntracks0_ntracks1 = fs->make<TH2F>("h_lsp_ntracks0_ntracks1", ";ntracks of vtx0 matched to LSP;ntracks of vtx1 matched to LSP", 40, 0, 40, 40, 0, 40);
}

namespace {
  float mag(float x, float y) {
    return sqrt(x*x + y*y);
  }
  
  float mag(float x, float y, float z) {
    return sqrt(x*x + y*y + z*z);
  }
  
  float signed_mag(float x, float y) {
    float m = mag(x,y);
    if (y < 0) return -m;
    return m;
  }
}

void MFVResolutions::analyze(const edm::Event& event, const edm::EventSetup&) {
  edm::Handle<MFVVertexAuxCollection> vertices;
  event.getByLabel(vertex_src, vertices);

  edm::Handle<reco::GenParticleCollection> gen_particles;
  event.getByLabel(gen_src, gen_particles);
  const size_t ngen = gen_particles->size();

  const reco::GenParticle& for_vtx = gen_particles->at(2);
  float x0 = for_vtx.vx(), y0 = for_vtx.vy(), z0 = for_vtx.vz();

  std::vector<const reco::GenParticle*> partons[2];
  double v[2][3] = {{0}};
  TLorentzVector lsp_p4s[2];

  if (doing_h2xqq) {
    for (size_t igen = 0; igen < ngen; ++igen) {
      const reco::GenParticle& gen = gen_particles->at(igen);
      if (gen.status() == 3 && abs(gen.pdgId()) == 35) {
        assert(gen.numberOfDaughters() >= 2);
        for (size_t idau = 0; idau < 2; ++idau) {
          const reco::Candidate* dau = gen.daughter(idau);
          int dauid = dau->pdgId();
          // https://espace.cern.ch/cms-exotica/long-lived/selection/MC2012.aspx
          // 600N114 = quarks where N is 1 2 or 3 for the lifetime selection
          assert(dauid/6000000 == 1);
          dauid %= 6000000;
          const int h2x = dauid / 1000;
          assert(h2x == 1 || h2x == 2 || h2x == 3);
          dauid %= h2x*1000;
          assert(dauid/100 == 1);
          dauid %= 100;
          assert(dauid/10 == 1);
          dauid %= 10;
          assert(dauid == 3 || dauid == 4);

          TLorentzVector v;
          v.SetPtEtaPhiM(dau->pt(), dau->eta(), dau->phi(), dau->mass());
          lsp_p4s[idau] = v;
          const size_t ngdau = dau->numberOfDaughters();
          assert(ngdau >= 2);
          for (size_t igdau = 0; igdau < 2; ++igdau) {
            const reco::Candidate* gdau = dau->daughter(igdau);
            const int id = gdau->pdgId();
            assert(abs(id) >= 1 && abs(id) <= 5);
            partons[idau].push_back(dynamic_cast<const reco::GenParticle*>(gdau));
          }
        }
      }
    }

    for (int i = 0; i < 2; ++i) {
      assert(partons[i].size() == 2);
      assert(partons[i][0]->numberOfDaughters() > 0);
      v[i][0] = partons[i][0]->daughter(0)->vx() - x0;
      v[i][1] = partons[i][0]->daughter(0)->vy() - y0;
      v[i][2] = partons[i][0]->daughter(0)->vz() - z0;
    }
  }

if (doing_mfv2j || doing_mfv3j || doing_mfv4j || doing_mfv5j) {
  edm::Handle<MFVEvent> mevent;
  event.getByLabel(mevent_src, mevent);

  die_if_not(mevent->gen_valid, "not running on signal sample");

  MCInteractionMFV3j mci;
  mci.Init(*gen_particles);

  if (!mci.Valid()) {
    if (!mci_warned)
      edm::LogWarning("Resolutions") << "MCInteractionMFV3j invalid; no further warnings!";
    mci_warned = true;
  }

    for (int i = 0; i < 2; ++i) {
      partons[i].push_back(mci.stranges[i]);
      partons[i].push_back(mci.bottoms[i]);
      if (doing_mfv3j) {
        partons[i].push_back(mci.tops[i]);
      }
      if (doing_mfv4j) {
        partons[i].push_back(mci.tops[i]);
        partons[i].push_back(mci.bottoms_from_tops[i]);
      }
      if (doing_mfv5j) {
        partons[i].push_back(mci.bottoms_from_tops[i]);
        partons[i].push_back(mci.W_daughters[i][0]);
        partons[i].push_back(mci.W_daughters[i][1]);
      }
      v[i][0] = mci.stranges[i]->vx() - x0;
      v[i][1] = mci.stranges[i]->vy() - y0;
      v[i][2] = mci.stranges[i]->vz() - z0;
      TLorentzVector v;
      v.SetPtEtaPhiM(mci.lsps[i]->pt(), mci.lsps[i]->eta(), mci.lsps[i]->phi(), mci.lsps[i]->mass());
      lsp_p4s[i] = v;
    }

}

  const double dbv[2] = {
    mag(v[0][0], v[0][1]),
    mag(v[1][0], v[1][1])
  };

  const double dvv = mag(v[0][0] - v[1][0],
                         v[0][1] - v[1][1]);
  h_gen_dvv->Fill(dvv);

  if (int(vertices->size()) >= 2) {
    h_rec_dvv->Fill(mag(vertices->at(0).x - vertices->at(1).x, vertices->at(0).y - vertices->at(1).y));
  }

  std::vector<float> parton_pt;
  for (int i = 0; i < 2; ++i) {
    for (const reco::GenParticle* p : partons[i]) {
      if (p->pt() > 20 && fabs(p->eta()) < 2.5 && is_quark(p)) {
        parton_pt.push_back(p->pt());
      }
    }
  }
  std::sort(parton_pt.begin(), parton_pt.end(), [](float p1, float p2) { return p1 > p2; } );
  h_gen_jetpt4->Fill(int(parton_pt.size()) >= 4 ? parton_pt.at(3) : 0.f);
  h_gen_sumht->Fill(std::accumulate(parton_pt.begin(), parton_pt.end(), 0.f));

  for (int i = 0; i < 2; ++i) {
    const int ndau = int(partons[i].size());

    int ntracks = 0;
    int nquarks = 0;
    float sumpt = 0;
    float drmin = 1e6;
    float drmax = -1e6;
    for (int j = 0; j < ndau; ++j) {
      const reco::GenParticle* p1 = partons[i][j];
      if (is_neutrino(p1) || p1->pt() < 20 || fabs(p1->eta()) > 2.5 || fabs(dbv[i] * sin(p1->phi() - atan2(v[i][1], v[i][0]))) < 0.01) continue;
      ++ntracks;
      if (!is_lepton(p1)) ++nquarks;
      sumpt += p1->pt();
      for (int k = j+1; k < ndau; ++k) {
        const reco::GenParticle* p2 = partons[i][k];
        if (is_neutrino(p2) || p2->pt() < 20 || fabs(p2->eta()) > 2.5 || fabs(dbv[i] * sin(p2->phi() - atan2(v[i][1], v[i][0]))) < 0.01) continue;
        float dr = reco::deltaR(*p1, *p2);
        if (dr < drmin)
          drmin = dr;
        if (dr > drmax)
          drmax = dr;
      }
    }

    if (dbv[i] > 0.20 && dbv[i] < 0.30) {
      for (int j = 0; j < ndau; ++j)
        h_gen_dxy->Fill(fabs(mag(v[i][0], v[i][1]) * sin(partons[i][j]->phi() - atan2(v[i][1], v[i][0]))));
      h_gen_dbv->Fill(dbv[i]);
      h_gen_ntracks->Fill(ntracks);
      h_gen_drmin->Fill(drmin);
      h_gen_drmax->Fill(drmax);
      h_gen_nquarks->Fill(nquarks);
      h_gen_sumpt->Fill(sumpt);
      h_gen_betagamma->Fill(lsp_p4s[i].Beta() * lsp_p4s[i].Gamma());
    }
  }


  int lsp_nmatch[2] = {0,0};
  int nvtx_match = 0;
  std::vector<int> lsp0_ntracks;
  std::vector<int> lsp1_ntracks;

  //printf("run = %u, luminosity block = %u, event = %u\n", event.id().run(), event.luminosityBlock(), event.id().event());
  for (const MFVVertexAux& vtx : *vertices) {
    double dr = 1e99, dist = 1e99;
    int ilsp = -1;

    if (max_dr > 0) {
      double drs[2] = {
        reco::deltaR(lsp_p4s[0].Eta(), lsp_p4s[0].Phi(), vtx.eta[which_mom], vtx.phi[which_mom]),
        reco::deltaR(lsp_p4s[1].Eta(), lsp_p4s[1].Phi(), vtx.eta[which_mom], vtx.phi[which_mom])
      };

      for (int i = 0; i < 2; ++i) {
        if (drs[i] < max_dr) {
          ++lsp_nmatch[i];
          if (drs[i] < dr) {
            dr = drs[i];
            ilsp = i;
          }
        }
      }
    }
    else if (max_dist > 0) {
      double dists[2] = {
        mag(v[0][0] - (vtx.x - x0),
            v[0][1] - (vtx.y - y0),
            v[0][2] - (vtx.z - z0)),
        mag(v[1][0] - (vtx.x - x0),
            v[1][1] - (vtx.y - y0),
            v[1][2] - (vtx.z - z0)),
      };

      for (int i = 0; i < 2; ++i) {
        if (dists[i] < max_dist) {
          ++lsp_nmatch[i];
          if (i == 0) lsp0_ntracks.push_back(vtx.ntracks());
          if (i == 1) lsp1_ntracks.push_back(vtx.ntracks());
          if (dists[i] < dist) {
            dist = dists[i];
            ilsp = i;
          }
        }
      }
    }

    if (ilsp < 0) {
      continue;
    }

    ++nvtx_match;

    if (lsp_nmatch[ilsp] == 1 && dbv[ilsp] > 0.20 && dbv[ilsp] < 0.30) {
      h_dist->Fill(dist);

      double sum = 0;
      //printf("vertex %d: ntracks = %d, njetsntks = %d, bs2derr = %6.4f, drrms = %5.3f\n", nvtx_match, vtx.ntracks(), vtx.njets[mfv::JByNtracks], vtx.bs2derr, vtx.drrms());
      for (size_t i = 0, n = vtx.ntracks(); i < n; ++i) {
        h_rec_dxy->Fill(vtx.track_dxy[i]);
        sum += reco::deltaR(vtx.track_eta[i], vtx.track_phi[i], vtx.eta[mfv::PTracksOnly], vtx.phi[mfv::PTracksOnly])
             * reco::deltaR(vtx.track_eta[i], vtx.track_phi[i], vtx.eta[mfv::PTracksOnly], vtx.phi[mfv::PTracksOnly]);
        //printf("\ttrack %2d: qpt = %7.3f, eta = %6.3f, phi = %6.3f, dxy = %5.3f, drs = %5.3f\n", int(i), vtx.track_qpt[i], vtx.track_eta[i], vtx.track_phi[i], vtx.track_dxy[i],
        //       reco::deltaR(vtx.track_eta[i], vtx.track_phi[i], vtx.eta[mfv::PTracksOnly], vtx.phi[mfv::PTracksOnly])
        //     * reco::deltaR(vtx.track_eta[i], vtx.track_phi[i], vtx.eta[mfv::PTracksOnly], vtx.phi[mfv::PTracksOnly]));
        //printf("\t");
        for (size_t j = i+1; j < n; ++j) {
        //  printf("\t%5.3f", sqrt((vtx.track_eta[i]-vtx.track_eta[j])*(vtx.track_eta[i]-vtx.track_eta[j]) + (vtx.track_phi[i]-vtx.track_phi[j])*(vtx.track_phi[i]-vtx.track_phi[j])));
          h_rec_trackpair_deta->Fill(fabs(vtx.track_eta[i] - vtx.track_eta[j]));
          h_rec_trackpair_dphi->Fill(fabs(reco::deltaPhi(vtx.track_phi[i], vtx.track_phi[j])));
          h_rec_trackpair_dr->Fill(reco::deltaR(vtx.track_eta[i], vtx.track_phi[i], vtx.track_eta[j], vtx.track_phi[j]));
        }
        //printf("\n");

        h_rec_tracks_qpt->Fill(vtx.track_qpt[i]);
        h_rec_tracks_eta->Fill(vtx.track_eta[i]);
        h_rec_tracks_phi->Fill(vtx.track_phi[i]);
        h_rec_tracks_deta->Fill(fabs(vtx.track_eta[i] - vtx.eta[mfv::PTracksOnly]));
        h_rec_tracks_dphi->Fill(fabs(reco::deltaPhi(vtx.track_phi[i], vtx.phi[mfv::PTracksOnly])));
        h_rec_tracks_dr->Fill(reco::deltaR(vtx.track_eta[i], vtx.track_phi[i], vtx.eta[mfv::PTracksOnly], vtx.phi[mfv::PTracksOnly]));

      }
      h_rec_ntracks->Fill(vtx.ntracks());
      h_rec_bs2derr->Fill(vtx.bs2derr);
      h_rec_drmin->Fill(vtx.drmin());
      h_rec_drmax->Fill(vtx.drmax());
      h_rec_dravg->Fill(vtx.dravg());
      h_rec_drrms->Fill(vtx.drrms());
      h_rec_njetsntks->Fill(vtx.njets[mfv::JByNtracks]);
      h_rec_ntracksptgt3->Fill(vtx.ntracksptgt(3));
      h_rec_dbv->Fill(vtx.bs2ddist);
      h_rec_betagamma->Fill(vtx.p4(which_mom).Beta()*vtx.p4(which_mom).Gamma());
      h_rec_dirrms->Fill(sqrt(1/(vtx.ntracks()-1.0) * sum));
      h_rec_drrms_ntracks->Fill(vtx.ntracks(), vtx.drrms());
      h_rec_drrms_dravg->Fill(vtx.dravg(), vtx.drrms());
      h_rec_dirrms_dravg->Fill(vtx.dravg(), sqrt(1/(vtx.ntracks()-1.0) * sum));

      double betagamma = lsp_p4s[ilsp].Beta() * lsp_p4s[ilsp].Gamma();
      if (betagamma < 0.25) h_rec_bs2derr_betagamma0p00to0p25->Fill(vtx.bs2derr);
      else if (betagamma < 0.50) h_rec_bs2derr_betagamma0p25to0p50->Fill(vtx.bs2derr);
      else if (betagamma < 0.75) h_rec_bs2derr_betagamma0p50to0p75->Fill(vtx.bs2derr);
      else if (betagamma < 1.00) h_rec_bs2derr_betagamma0p75to1p00->Fill(vtx.bs2derr);
      else if (betagamma < 1.25) h_rec_bs2derr_betagamma1p00to1p25->Fill(vtx.bs2derr);
      else if (betagamma < 1.50) h_rec_bs2derr_betagamma1p25to1p50->Fill(vtx.bs2derr);
      else if (betagamma < 1.75) h_rec_bs2derr_betagamma1p50to1p75->Fill(vtx.bs2derr);
      else if (betagamma < 2.00) h_rec_bs2derr_betagamma1p75to2p00->Fill(vtx.bs2derr);
      else if (betagamma < 2.25) h_rec_bs2derr_betagamma2p00to2p25->Fill(vtx.bs2derr);
      else if (betagamma < 2.50) h_rec_bs2derr_betagamma2p25to2p50->Fill(vtx.bs2derr);
      else if (betagamma < 2.75) h_rec_bs2derr_betagamma2p50to2p75->Fill(vtx.bs2derr);
      else if (betagamma < 3.00) h_rec_bs2derr_betagamma2p75to3p00->Fill(vtx.bs2derr);
      h_rec_bs2derr_gen_betagamma->Fill(betagamma, vtx.bs2derr);

    }
  }

  // histogram lsp_nmatch
  for (int i = 0; i < 2; ++i) {
    if (dbv[i] > 0.20 && dbv[i] < 0.30) {
      h_lspsnmatch->Fill(lsp_nmatch[i]);
      if (lsp_nmatch[i] > 1) {
        if (i == 0) h_lsp_ntracks0_ntracks1->Fill(lsp0_ntracks.at(0), lsp0_ntracks.at(1));
        if (i == 1) h_lsp_ntracks0_ntracks1->Fill(lsp1_ntracks.at(0), lsp1_ntracks.at(1));
      }
    }
  }

}

DEFINE_FWK_MODULE(MFVResolutions);
