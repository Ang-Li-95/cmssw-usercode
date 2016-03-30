#include "CommonTools/Utils/interface/StringCutObjectSelector.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/PatCandidates/interface/MET.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "L1Trigger/GlobalTriggerAnalyzer/interface/L1GtUtils.h"
#include "PhysicsTools/SelectorUtils/interface/JetIDSelectionFunctor.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"
#include "JMTucker/MFVNeutralinoFormats/interface/Event.h"
#include "JMTucker/MFVNeutralino/interface/EventTools.h"
#include "JMTucker/MFVNeutralino/interface/MCInteractionMFV3j.h"
#include "JMTucker/Tools/interface/TriggerHelper.h"
#include "JMTucker/Tools/interface/GenUtilities.h"
#include "JMTucker/Tools/interface/Utilities.h"

class MFVEventProducer : public edm::EDProducer {
public:
  explicit MFVEventProducer(const edm::ParameterSet&);
  void produce(edm::Event&, const edm::EventSetup&);

private:
  const edm::InputTag trigger_results_src;
  const edm::InputTag cleaning_results_src;

  const edm::EDGetTokenT<edm::TriggerResults> trigger_results_token;
  const edm::EDGetTokenT<edm::TriggerResults> cleaning_results_token;
  const edm::EDGetTokenT<reco::BeamSpot> beamspot_token;
  const edm::EDGetTokenT<reco::VertexCollection> primary_vertex_token;
  const edm::EDGetTokenT<GenEventInfoProduct> gen_info_token;
  const edm::EDGetTokenT<reco::GenParticleCollection> gen_particles_token;
  const edm::EDGetTokenT<std::vector<PileupSummaryInfo> > pileup_summary_token;
  const edm::EDGetTokenT<pat::JetCollection> jets_token;
  const edm::EDGetTokenT<pat::METCollection> met_token;
  const edm::EDGetTokenT<pat::MuonCollection> muons_token;
  const edm::EDGetTokenT<pat::ElectronCollection> electrons_token;
  const edm::EDGetTokenT<std::vector<float>> vertex_seed_pt_quantiles_token;
  
  const std::string skip_event_filter;
  const double jet_pt_min;
  const std::string b_discriminator;
  const std::vector<double> b_discriminator_mins;
  const StringCutObjectSelector<pat::Muon> muon_semilep_selector;
  const StringCutObjectSelector<pat::Muon> muon_dilep_selector;
  const StringCutObjectSelector<pat::Electron> electron_semilep_selector;
  const StringCutObjectSelector<pat::Electron> electron_dilep_selector;
  bool warned_non_mfv;

  L1GtUtils l1_cfg;
};

MFVEventProducer::MFVEventProducer(const edm::ParameterSet& cfg)
  : trigger_results_src(cfg.getParameter<edm::InputTag>("trigger_results_src")),
    cleaning_results_src(cfg.getParameter<edm::InputTag>("cleaning_results_src")),

    trigger_results_token(consumes<edm::TriggerResults>(trigger_results_src)),
    cleaning_results_token(consumes<edm::TriggerResults>(cleaning_results_src)),
    
    beamspot_token(consumes<reco::BeamSpot>(cfg.getParameter<edm::InputTag>("beamspot_src"))),
    primary_vertex_token(consumes<reco::VertexCollection>(cfg.getParameter<edm::InputTag>("primary_vertex_src"))),
    gen_info_token(consumes<GenEventInfoProduct>(cfg.getParameter<edm::InputTag>("gen_info_src"))),
    gen_particles_token(consumes<reco::GenParticleCollection>(cfg.getParameter<edm::InputTag>("gen_particles_src"))),
    pileup_summary_token(consumes<std::vector<PileupSummaryInfo> >(edm::InputTag("addPileupInfo"))),
    jets_token(consumes<pat::JetCollection>(cfg.getParameter<edm::InputTag>("jets_src"))),
    met_token(consumes<pat::METCollection>(cfg.getParameter<edm::InputTag>("met_src"))),
    muons_token(consumes<pat::MuonCollection>(cfg.getParameter<edm::InputTag>("muons_src"))),
    electrons_token(consumes<pat::ElectronCollection>(cfg.getParameter<edm::InputTag>("electrons_src"))),
    vertex_seed_pt_quantiles_token(consumes<std::vector<float>>(cfg.getParameter<edm::InputTag>("vertex_seed_pt_quantiles_src"))),

    skip_event_filter(cfg.getParameter<std::string>("skip_event_filter")),
    jet_pt_min(cfg.getParameter<double>("jet_pt_min")),
    b_discriminator(cfg.getParameter<std::string>("b_discriminator")),
    b_discriminator_mins(cfg.getParameter<std::vector<double> >("b_discriminator_mins")),
    muon_semilep_selector(cfg.getParameter<std::string>("muon_semilep_cut")),
    muon_dilep_selector(cfg.getParameter<std::string>("muon_dilep_cut")),
    electron_semilep_selector(cfg.getParameter<std::string>("electron_semilep_cut")),
    electron_dilep_selector(cfg.getParameter<std::string>("electron_dilep_cut")),

    warned_non_mfv(false),

    l1_cfg(cfg, consumesCollector(), false)
{
  produces<MFVEvent>();
}

void MFVEventProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
  if (cleaning_results_src.label() != "" && skip_event_filter != "" && !TriggerHelper(event, cleaning_results_token).pass(skip_event_filter))
    return;

  std::auto_ptr<MFVEvent> mevent(new MFVEvent);

  edm::Handle<reco::BeamSpot> beamspot;
  event.getByToken(beamspot_token, beamspot);
  mevent->bsx = beamspot->x0();
  mevent->bsy = beamspot->y0();
  mevent->bsz = beamspot->z0();
  mevent->bsdxdz = beamspot->dxdz();
  mevent->bsdydz = beamspot->dydz();
  mevent->bswidthx = beamspot->BeamWidthX();
  mevent->bswidthy = beamspot->BeamWidthY();

  edm::Handle<reco::VertexCollection> primary_vertices;
  event.getByToken(primary_vertex_token, primary_vertices);
  const reco::Vertex* primary_vertex = 0;
  if (primary_vertices->size())
    primary_vertex = &primary_vertices->at(0);

  //////////////////////////////////////////////////////////////////////

  mevent->gen_valid = false;

  if (!event.isRealData()) {
    edm::Handle<GenEventInfoProduct> gen_info;
    event.getByToken(gen_info_token, gen_info);

    mevent->gen_weight = gen_info->weight();
    mevent->gen_weightprod = gen_info->weightProduct();

    edm::Handle<reco::GenParticleCollection> gen_particles;
    event.getByToken(gen_particles_token, gen_particles);
    
    const reco::GenParticle& for_vtx = gen_particles->at(2);
    const int for_vtx_id = abs(for_vtx.pdgId());
    die_if_not(for_vtx_id == 21 || (for_vtx_id >= 1 && for_vtx_id <= 5), "gen_particles[2] is not a gluon or udscb: id=%i", for_vtx_id);
    float x0 = for_vtx.vx(), y0 = for_vtx.vy(), z0 = for_vtx.vz();
    
    mevent->gen_flavor_code = 0;
    bool saw_c = false;
    for (const reco::GenParticle& gen : *gen_particles) {
      if (is_bhadron(&gen)) {
	mevent->gen_flavor_code = 2;
	break;
      }
      if (is_chadron(&gen))
	saw_c = true;
    }
    if (saw_c && mevent->gen_flavor_code == 0)
      mevent->gen_flavor_code = 1;

    for (const reco::GenParticle& gen : *gen_particles) {
      if (abs(gen.pdgId()) == 5) {
        bool has_b_dau = false;
        for (size_t i = 0, ie = gen.numberOfDaughters(); i < ie; ++i) {
          if (abs(gen.daughter(i)->pdgId()) == 5) {
            has_b_dau = true;
            break;
          }
        }
        if (!has_b_dau) {
          mevent->gen_bquark_pt.push_back(gen.pt());
          mevent->gen_bquark_eta.push_back(gen.eta());
          mevent->gen_bquark_phi.push_back(gen.phi());
          mevent->gen_bquark_energy.push_back(gen.energy());
        }
      }
    }

    MCInteractionMFV3j mci;
    mci.Init(*gen_particles);
    if (!mci.Valid()) {
      if (!warned_non_mfv) {
        edm::LogWarning("MCInteractionMFV3j") << "invalid! hope this is not an MFV signal file";
        warned_non_mfv = true;
      }
    }
    else {
      mevent->gen_valid = true;
      std::vector<const reco::GenParticle*> lsp_partons;
      for (int i = 0; i < 2; ++i) {
        mevent->gen_lsp_pt  [i] = mci.lsps[i]->pt();
        mevent->gen_lsp_eta [i] = mci.lsps[i]->eta();
        mevent->gen_lsp_phi [i] = mci.lsps[i]->phi();
        mevent->gen_lsp_mass[i] = mci.lsps[i]->mass();
	
        mevent->gen_lsp_decay[i*3+0] = mci.stranges[i]->vx();
        mevent->gen_lsp_decay[i*3+1] = mci.stranges[i]->vy();
        mevent->gen_lsp_decay[i*3+2] = mci.stranges[i]->vz();

        lsp_partons.push_back(mci.stranges[i]);
        lsp_partons.push_back(mci.bottoms[i]);
        lsp_partons.push_back(mci.bottoms_from_tops[i]);

        mevent->gen_decay_type[i] = mci.decay_type[i];
        if (mci.decay_type[i] == 3) {
          lsp_partons.push_back(mci.W_daughters[i][0]);
          lsp_partons.push_back(mci.W_daughters[i][1]);
        }
      } 

      mevent->gen_pv[0] = x0;
      mevent->gen_pv[1] = y0;
      mevent->gen_pv[2] = z0;

      mevent->gen_partons_in_acc = 0;
      for (const reco::GenParticle* p : lsp_partons) 
        if (p->pt() > jet_pt_min && fabs(p->eta()) < 2.5)
          inc_uchar(mevent->gen_partons_in_acc);
    }
  }

  //////////////////////////////////////////////////////////////////////

  TriggerHelper trig_helper(event, trigger_results_token);

  const std::string hlt_paths[mfv::n_hlt_paths] = {
    "HLT_PFHT650_v",
    "HLT_PFHT800_v",
    "HLT_PFHT900_v",
    "HLT_PFHT550_4Jet_v",
    "HLT_PFHT450_SixJet40_PFBTagCSV_v",
    "HLT_PFHT400_SixJet30_BTagCSV0p5_2PFBTagCSV_v",
    "HLT_PFHT450_SixJet40_v",
    "HLT_PFHT400_SixJet30_v",
    "HLT_QuadJet45_TripleCSV0p5_v",
    "HLT_QuadJet45_DoubleCSV0p5_v",
    "HLT_DoubleJet90_Double30_TripleCSV0p5_v",
    "HLT_DoubleJet90_Double30_DoubleCSV0p5_v",
    "HLT_HT650_DisplacedDijet80_Inclusive_v",
    "HLT_HT750_DisplacedDijet80_Inclusive_v",
    "HLT_HT500_DisplacedDijet40_Inclusive_v",
    "HLT_HT550_DisplacedDijet40_Inclusive_v",
    "HLT_HT350_DisplacedDijet40_DisplacedTrack_v",
    "HLT_HT350_DisplacedDijet80_DisplacedTrack_v",
    "HLT_HT350_DisplacedDijet80_Tight_DisplacedTrack_v"
  };
  
  for (size_t i = 0; i < mfv::n_hlt_paths; ++i) {
    auto pass_and_found = trig_helper.pass_and_found_any_version(hlt_paths[i]);
    mevent-> pass_hlt(i, pass_and_found.first);
    mevent->found_hlt(i, pass_and_found.second);
  }


  l1_cfg.getL1GtRunCache(event, setup, true, false);

  const std::string l1_paths[mfv::n_l1_paths] = { "L1_HTT100", "L1_HTT125", "L1_HTT150", "L1_HTT175", "L1_HTT200" };
  for (size_t i = 0; i < mfv::n_l1_paths; ++i) {
    int l1_err = 0;
    bool pass = l1_cfg.decision(event, l1_paths[i], l1_err);
    if (l1_err != 0) {
      mevent-> pass_l1(i, false);
      mevent->found_l1(i, false);
    }
    else {
      mevent-> pass_l1(i, pass);
      mevent->found_l1(i, true);
    }
  }


  if (cleaning_results_src.label() != "") {
    const std::string cleaning_paths[mfv::n_clean_paths] = {
      "Flag_CSCTightHaloFilter",
      "Flag_EcalDeadCellTriggerPrimitiveFilter",
      "Flag_HBHENoiseFilter",
      "Flag_METFilters",
      "Flag_ecalLaserCorrFilter",
      "Flag_eeBadScFilter",
      "Flag_goodVertices",
      "Flag_hcalLaserEventFilter",
      "Flag_trackingFailureFilter",
      "Flag_trkPOGFilters",
      "Flag_trkPOG_logErrorTooManyClusters",
      "Flag_trkPOG_manystripclus53X",
      "Flag_trkPOG_toomanystripclus53X",
    };

    TriggerHelper trig_helper_cleaning(event, cleaning_results_token);

    for (size_t i = 0; i < mfv::n_clean_paths; ++i)
      mevent->pass_clean(i, trig_helper_cleaning.pass(cleaning_paths[i]));
  }

  //////////////////////////////////////////////////////////////////////

  mevent->npu = -1;

  if (!event.isRealData()) {
    edm::Handle<std::vector<PileupSummaryInfo> > pileup;
    event.getByToken(pileup_summary_token, pileup);

    for (std::vector<PileupSummaryInfo>::const_iterator psi = pileup->begin(), end = pileup->end(); psi != end; ++psi)
      if (psi->getBunchCrossing() == 0)
        mevent->npu = psi->getTrueNumInteractions();
  }

  //////////////////////////////////////////////////////////////////////
  
  mevent->npv = int2uchar(primary_vertices->size());

  if (primary_vertex != 0) {
    mevent->pvx = primary_vertex->x();
    mevent->pvy = primary_vertex->y();
    mevent->pvz = primary_vertex->z();
    mevent->pvcxx = primary_vertex->covariance(0,0);
    mevent->pvcxy = primary_vertex->covariance(0,1);
    mevent->pvcxz = primary_vertex->covariance(0,2);
    mevent->pvcyy = primary_vertex->covariance(1,1);
    mevent->pvcyz = primary_vertex->covariance(1,2);
    mevent->pvczz = primary_vertex->covariance(2,2);

    mevent->pv_ntracks = int2uchar_clamp(primary_vertex->nTracks());
    mevent->pv_sumpt2 = 0;
    for (auto trki = primary_vertex->tracks_begin(), trke = primary_vertex->tracks_end(); trki != trke; ++trki) {
      double trkpt = (*trki)->pt();
      mevent->pv_sumpt2 += trkpt * trkpt;
    }
  }

  //////////////////////////////////////////////////////////////////////

  edm::Handle<pat::JetCollection> jets;
  event.getByToken(jets_token, jets);

  edm::Handle<pat::METCollection> mets;
  event.getByToken(met_token, mets);
  const pat::MET& met = mets->at(0);
  mevent->metx = met.px();
  mevent->mety = met.py();

  for (int jjet = 0, jjete = int(jets->size()); jjet < jjete; ++jjet) {
    const pat::Jet& jet = jets->at(jjet);
    if (jet.pt() < jet_pt_min)
      continue;

    mevent->jet_pudisc.push_back(jet.userFloat("pileupJetId:fullDiscriminant")); // to be removed and put into _id when working points defined
    mevent->jet_pt.push_back(jet.pt());
    mevent->jet_raw_pt.push_back(jet.pt()*jet.jecFactor("Uncorrected"));
    mevent->jet_calo_pt.push_back(jet.userFloat("caloJetMap:pt"));
    mevent->jet_eta.push_back(jet.eta());
    mevent->jet_phi.push_back(jet.phi());
    mevent->jet_energy.push_back(jet.energy());

    int bdisc_level = 0;
    for (int i = 0; i < 3; ++i)
      if (jet.bDiscriminator(b_discriminator) > b_discriminator_mins[i])
        bdisc_level = i+1;

    mevent->jet_id.push_back(MFVEvent::encode_jet_id(0, bdisc_level));

    const reco::SecondaryVertexTagInfo* svtag = jet.tagInfoSecondaryVertex("secondaryVertex");
    mevent->jet_svnvertices.push_back(svtag ? svtag->nVertices() : -1);

    if (svtag && svtag->nVertices() > 0) {
      const reco::Vertex &sv = svtag->secondaryVertex(0);
      mevent->jet_svntracks.push_back(sv.nTracks());
      double svsumpt2 = 0;
      for (auto trki = sv.tracks_begin(), trke = sv.tracks_end(); trki != trke; ++trki) {
        double trkpt = (*trki)->pt();
        svsumpt2 += trkpt * trkpt;
      }
      mevent->jet_svsumpt2.push_back(svsumpt2);
      mevent->jet_svx.push_back(sv.x());
      mevent->jet_svy.push_back(sv.y());
      mevent->jet_svz.push_back(sv.z());
      mevent->jet_svcxx.push_back(sv.covariance(0,0));
      mevent->jet_svcxy.push_back(sv.covariance(0,1));
      mevent->jet_svcxz.push_back(sv.covariance(0,2));
      mevent->jet_svcyy.push_back(sv.covariance(1,1));
      mevent->jet_svcyz.push_back(sv.covariance(1,2));
      mevent->jet_svczz.push_back(sv.covariance(2,2));
    }
    else {
      mevent->jet_svntracks.push_back(0);
      mevent->jet_svsumpt2.push_back(0);
      mevent->jet_svx.push_back(0);
      mevent->jet_svy.push_back(0);
      mevent->jet_svz.push_back(0);
      mevent->jet_svcxx.push_back(0);
      mevent->jet_svcxy.push_back(0);
      mevent->jet_svcxz.push_back(0);
      mevent->jet_svcyy.push_back(0);
      mevent->jet_svcyz.push_back(0);
      mevent->jet_svczz.push_back(0);
    }
  }

  //////////////////////////////////////////////////////////////////////

  mevent->lep_id.clear();
  mevent->lep_pt.clear();
  mevent->lep_eta.clear();
  mevent->lep_phi.clear();
  mevent->lep_dxy.clear();
  mevent->lep_dz.clear();
  mevent->lep_iso.clear();

  edm::Handle<pat::MuonCollection> muons;
  event.getByToken(muons_token, muons);

  for (const pat::Muon& muon : *muons) {
    uchar sel = 0;
    if (1)                           sel |= MFVEvent::mu_veto;
    if (muon_semilep_selector(muon)) sel |= MFVEvent::mu_semilep;
    if (muon_dilep_selector  (muon)) sel |= MFVEvent::mu_dilep;

    const float iso = (muon.chargedHadronIso() + std::max(0.f,muon.neutralHadronIso()) + muon.photonIso() - 0.5*muon.puChargedHadronIso())/muon.pt(); // JMTBAD keep in sync with .py

    mevent->lep_id.push_back(MFVEvent::encode_mu_id(sel));
    mevent->lep_pt.push_back(muon.pt());
    mevent->lep_eta.push_back(muon.eta());
    mevent->lep_phi.push_back(muon.phi());
    mevent->lep_dxy.push_back(muon.track()->dxy(beamspot->position()));
    if (primary_vertex != 0)
      mevent->lep_dz.push_back(muon.track()->dz(primary_vertex->position()));
    mevent->lep_iso.push_back(iso);
  }

  edm::Handle<pat::ElectronCollection> electrons;
  event.getByToken(electrons_token, electrons);
  
  for (const pat::Electron& electron : *electrons) {
    uchar sel = 0;
    if (1)                                         sel |= MFVEvent::el_veto;
    if (electron_semilep_selector(electron))       sel |= MFVEvent::el_semilep;
    if (electron_dilep_selector  (electron))       sel |= MFVEvent::el_dilep;
    if (electron.closestCtfTrackRef().isNonnull()) sel |= MFVEvent::el_ctf;

    const float iso = (electron.chargedHadronIso() + std::max(0.f,electron.neutralHadronIso()) + electron.photonIso() - 0.5*electron.puChargedHadronIso())/electron.et();

    mevent->lep_id.push_back(MFVEvent::encode_el_id(sel));
    mevent->lep_pt.push_back(electron.pt());
    mevent->lep_eta.push_back(electron.eta());
    mevent->lep_phi.push_back(electron.phi());
    mevent->lep_dxy.push_back(electron.gsfTrack()->dxy(beamspot->position()));
    if (primary_vertex != 0)
      mevent->lep_dz.push_back(electron.gsfTrack()->dz(primary_vertex->position()));
    mevent->lep_iso.push_back(iso);
  }

  //////////////////////////////////////////////////////////////////////

  edm::Handle<std::vector<float>> vertex_seed_pt_quantiles;
  event.getByToken(vertex_seed_pt_quantiles_token, vertex_seed_pt_quantiles);
  assert(vertex_seed_pt_quantiles->size() == mfv::n_vertex_seed_pt_quantiles);
  for (int i = 0; i < mfv::n_vertex_seed_pt_quantiles; ++i)
    mevent->vertex_seed_pt_quantiles[i] = (*vertex_seed_pt_quantiles)[i];

  //////////////////////////////////////////////////////////////////////

  event.put(mevent);
}

DEFINE_FWK_MODULE(MFVEventProducer);
