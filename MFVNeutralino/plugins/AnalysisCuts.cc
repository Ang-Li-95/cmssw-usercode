#include "DataFormats/Math/interface/deltaPhi.h"
#include "FWCore/Framework/interface/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "JMTucker/Tools/interface/TriggerHelper.h"
#include "JMTucker/MFVNeutralinoFormats/interface/Event.h"
#include "JMTucker/MFVNeutralinoFormats/interface/VertexAux.h"
#include "JMTucker/MFVNeutralino/interface/EventTools.h"

class MFVAnalysisCuts : public edm::EDFilter {
public:
  explicit MFVAnalysisCuts(const edm::ParameterSet&);

private:
  virtual bool filter(edm::Event&, const edm::EventSetup&);

  const edm::InputTag mevent_src;
  const bool use_mevent;
  const int l1_bit;
  const int trigger_bit;
  const bool re_trigger;
  const int clean_bit;
  const bool invert_clean;
  const bool apply_cleaning_filters;
  const bool invert_cleaning_filters;

  const int min_npv;
  const int max_npv;
  const double min_4th_calojet_pt;
  const double min_5th_calojet_pt;
  const double min_4th_jet_pt;
  const double min_5th_jet_pt;
  const int min_njets;
  const int max_njets;
  const std::vector<int> min_nbtags;
  const std::vector<int> max_nbtags;
  const double min_sumht;
  const double max_sumht;
  const double min_sum_other_pv_sumpt2;
  const double max_sum_other_pv_sumpt2;
  const int min_nmuons;
  const int min_nsemilepmuons;
  const int min_nleptons;
  const int min_nsemileptons;

  const bool apply_vertex_cuts;
  const edm::InputTag vertex_src;
  const int min_nvertex;
  const int max_nvertex;
  const int min_ntracks01;
  const int max_ntracks01;
  const double min_maxtrackpt01;
  const double max_maxtrackpt01;
  const int min_njetsntks01;
  const double min_tkonlymass01;
  const double min_jetsntkmass01;
  const double min_tksjetsntkmass01;
  const double min_absdeltaphi01;
  const double min_bs2ddist01;
  const double min_bs2dsig01;
  const double min_pv2ddist01;
  const double min_pv3ddist01;
  const double min_pv2dsig01;
  const double min_pv3dsig01;
  const double min_svdist2d;
  const double max_svdist2d;
  const double min_svdist3d;
  const int max_ntrackssharedwpv01;
  const int max_ntrackssharedwpvs01;
  const int max_fractrackssharedwpv01;
  const int max_fractrackssharedwpvs01;
};

MFVAnalysisCuts::MFVAnalysisCuts(const edm::ParameterSet& cfg) 
  : mevent_src(cfg.getParameter<edm::InputTag>("mevent_src")),
    use_mevent(mevent_src.label() != ""),
    l1_bit(cfg.getParameter<int>("l1_bit")),
    trigger_bit(cfg.getParameter<int>("trigger_bit")),
    re_trigger(cfg.getParameter<bool>("re_trigger")),
    clean_bit(cfg.getParameter<int>("clean_bit")),
    invert_clean(cfg.getParameter<bool>("invert_clean")),
    apply_cleaning_filters(cfg.getParameter<bool>("apply_cleaning_filters")),
    invert_cleaning_filters(cfg.getParameter<bool>("invert_cleaning_filters")),
    min_npv(cfg.getParameter<int>("min_npv")),
    max_npv(cfg.getParameter<int>("max_npv")),
    min_4th_calojet_pt(cfg.getParameter<double>("min_4th_calojet_pt")),
    min_5th_calojet_pt(cfg.getParameter<double>("min_5th_calojet_pt")),
    min_4th_jet_pt(cfg.getParameter<double>("min_4th_jet_pt")),
    min_5th_jet_pt(cfg.getParameter<double>("min_5th_jet_pt")),
    min_njets(cfg.getParameter<int>("min_njets")),
    max_njets(cfg.getParameter<int>("max_njets")),
    min_nbtags(cfg.getParameter<std::vector<int> >("min_nbtags")),
    max_nbtags(cfg.getParameter<std::vector<int> >("max_nbtags")),
    min_sumht(cfg.getParameter<double>("min_sumht")),
    max_sumht(cfg.getParameter<double>("max_sumht")),
    min_sum_other_pv_sumpt2(cfg.getParameter<double>("min_sum_other_pv_sumpt2")),
    max_sum_other_pv_sumpt2(cfg.getParameter<double>("max_sum_other_pv_sumpt2")),
    min_nmuons(cfg.getParameter<int>("min_nmuons")),
    min_nsemilepmuons(cfg.getParameter<int>("min_nsemilepmuons")),
    min_nleptons(cfg.getParameter<int>("min_nleptons")),
    min_nsemileptons(cfg.getParameter<int>("min_nsemileptons")),
    apply_vertex_cuts(cfg.getParameter<bool>("apply_vertex_cuts")),
    vertex_src(cfg.getParameter<edm::InputTag>("vertex_src")),
    min_nvertex(cfg.getParameter<int>("min_nvertex")),
    max_nvertex(cfg.getParameter<int>("max_nvertex")),
    min_ntracks01(cfg.getParameter<int>("min_ntracks01")),
    max_ntracks01(cfg.getParameter<int>("max_ntracks01")),
    min_maxtrackpt01(cfg.getParameter<double>("min_maxtrackpt01")),
    max_maxtrackpt01(cfg.getParameter<double>("max_maxtrackpt01")),
    min_njetsntks01(cfg.getParameter<int>("min_njetsntks01")),
    min_tkonlymass01(cfg.getParameter<double>("min_tkonlymass01")),
    min_jetsntkmass01(cfg.getParameter<double>("min_jetsntkmass01")),
    min_tksjetsntkmass01(cfg.getParameter<double>("min_tksjetsntkmass01")),
    min_absdeltaphi01(cfg.getParameter<double>("min_absdeltaphi01")),
    min_bs2ddist01(cfg.getParameter<double>("min_bs2ddist01")),
    min_bs2dsig01(cfg.getParameter<double>("min_bs2dsig01")),
    min_pv2ddist01(cfg.getParameter<double>("min_pv2ddist01")),
    min_pv3ddist01(cfg.getParameter<double>("min_pv3ddist01")),
    min_pv2dsig01(cfg.getParameter<double>("min_pv2dsig01")),
    min_pv3dsig01(cfg.getParameter<double>("min_pv3dsig01")),
    min_svdist2d(cfg.getParameter<double>("min_svdist2d")),
    max_svdist2d(cfg.getParameter<double>("max_svdist2d")),
    min_svdist3d(cfg.getParameter<double>("min_svdist3d")),
    max_ntrackssharedwpv01(cfg.getParameter<int>("max_ntrackssharedwpv01")),
    max_ntrackssharedwpvs01(cfg.getParameter<int>("max_ntrackssharedwpvs01")),
    max_fractrackssharedwpv01(cfg.getParameter<double>("max_fractrackssharedwpv01")),
    max_fractrackssharedwpvs01(cfg.getParameter<double>("max_fractrackssharedwpvs01"))
{
}

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

bool MFVAnalysisCuts::filter(edm::Event& event, const edm::EventSetup&) {
  edm::Handle<MFVEvent> mevent;

  if (use_mevent) {
    event.getByLabel(mevent_src, mevent);

    if (l1_bit >= 0 || trigger_bit >= 0) {
      if (re_trigger) {
        throw cms::Exception("AnalysisCuts", "L1 part of re_trigger not implemented");
        bool pass_trigger[mfv::n_trigger_paths] = { 0 };
        TriggerHelper trig_helper(event, edm::InputTag("TriggerResults", "", "HLT"));
        mfv::trigger_decision(trig_helper, pass_trigger);
        if (!pass_trigger[trigger_bit])
          return false;
      }
      else if ((trigger_bit >= 0 && !mevent->pass_trigger[trigger_bit]) ||
               (l1_bit      >= 0 && !mevent->l1_pass[l1_bit]))
        return false;
    }

    if (clean_bit >= 0) {
      if (invert_clean == mevent->pass_clean[clean_bit])
        return false;
    }

    if (apply_cleaning_filters && invert_cleaning_filters == mevent->pass_clean_all())
      return false;

    if (mevent->npv < min_npv || mevent->npv > max_npv)
      return false;

    if (mevent->nmu(0) < min_nmuons)
      return false;

    if (mevent->nmu(1) < min_nsemilepmuons)
      return false;

    if (mevent->nlep(0) < min_nleptons)
      return false;

    if (mevent->nlep(1) < min_nsemileptons)
      return false;

    if (mevent->njets() < min_njets || mevent->njets() > max_njets)
      return false;

    if ((min_4th_calojet_pt > 0 && mevent->calojetpt4() < min_4th_calojet_pt) ||
        (min_5th_calojet_pt > 0 && mevent->calojetpt5() < min_5th_calojet_pt))
      return false;

    if ((min_4th_jet_pt > 0 && mevent->jetpt4() < min_4th_jet_pt) ||
        (min_5th_jet_pt > 0 && mevent->jetpt5() < min_5th_jet_pt))
      return false;

    for (int i = 0; i < 3; ++i)
      if (mevent->nbtags(i) < min_nbtags[i] || mevent->nbtags(i) > max_nbtags[i])
        return false;

    if (mevent->jet_sum_ht() < min_sumht)
      return false;

    if (mevent->jet_sum_ht() > max_sumht)
      return false;

    if (min_sum_other_pv_sumpt2 > 0 || max_sum_other_pv_sumpt2 < 1e9) {
      edm::Handle<reco::VertexCollection> primary_vertices;
      event.getByLabel("offlinePrimaryVertices", primary_vertices);
      double other_pv_sumpt2 = 0;
      for (size_t i = 1; i < primary_vertices->size(); ++i) {
        const reco::Vertex& pv = primary_vertices->at(i);
        for (auto trki = pv.tracks_begin(), trke = pv.tracks_end(); trki != trke; ++trki)
          other_pv_sumpt2 += (*trki)->pt() * (*trki)->pt();
      }

      if (other_pv_sumpt2 < min_sum_other_pv_sumpt2 || other_pv_sumpt2 > max_sum_other_pv_sumpt2)
        return false;
    }
  }

  if (apply_vertex_cuts) {
    edm::Handle<MFVVertexAuxCollection> vertices;
    event.getByLabel(vertex_src, vertices);

    const int nsv = int(vertices->size());
    if (nsv < min_nvertex || nsv > max_nvertex)
      return false;

    const bool two_vertex_cuts_on =
      min_ntracks01 > 0 ||
      max_ntracks01 < 100000 || // for ints
      min_maxtrackpt01 > 0 ||
      max_maxtrackpt01 < 1e6 || // for floats
      min_njetsntks01 > 0 ||
      min_tkonlymass01 > 0 ||
      min_jetsntkmass01 > 0 ||
      min_tksjetsntkmass01 > 0 ||
      min_absdeltaphi01 > 0 ||
      min_bs2ddist01 > 0 ||
      min_bs2dsig01 > 0 ||
      min_pv2ddist01 > 0 ||
      min_pv3ddist01 > 0 ||
      min_pv2dsig01 > 0 ||
      min_pv3dsig01 > 0 ||
      min_svdist2d > 0 ||
      max_svdist2d < 1e6 ||
      min_svdist3d > 0 ||
      max_ntrackssharedwpv01 < 100000 ||
      max_ntrackssharedwpvs01 < 100000 ||
      max_fractrackssharedwpv01 < 1e6 ||
      max_fractrackssharedwpvs01 < 1e6;

    if (two_vertex_cuts_on) {
      if (nsv < 2)
        return false;

      const MFVVertexAux& v0 = vertices->at(0);
      const MFVVertexAux& v1 = vertices->at(1);

      if (v0.ntracks() + v1.ntracks() < min_ntracks01)
        return false;
      if (v0.ntracks() + v1.ntracks() > max_ntracks01)
        return false;
      if (v0.maxtrackpt() + v1.maxtrackpt() < min_maxtrackpt01)
        return false;
      if (v0.maxtrackpt() + v1.maxtrackpt() > max_maxtrackpt01)
        return false;
      if (v0.njets[mfv::JByNtracks] + v1.njets[mfv::JByNtracks] < min_njetsntks01)
        return false;
      if (v0.mass[mfv::PTracksOnly] + v1.mass[mfv::PTracksOnly] < min_tkonlymass01)
        return false;
      if (v0.mass[mfv::PJetsByNtracks] + v1.mass[mfv::PJetsByNtracks] < min_jetsntkmass01)
        return false;
      if (v0.mass[mfv::PTracksPlusJetsByNtracks] + v1.mass[mfv::PTracksPlusJetsByNtracks] < min_tksjetsntkmass01)
        return false;

      if (use_mevent) {
        const double phi0 = atan2(v0.y - mevent->bsy, v0.x - mevent->bsx);
        const double phi1 = atan2(v1.y - mevent->bsy, v1.x - mevent->bsx);
        if (fabs(reco::deltaPhi(phi0, phi1)) < min_absdeltaphi01)
          return false;
      }

      if (v0.bs2ddist + v1.bs2ddist < min_bs2ddist01)
        return false;

      if (v0.bs2dsig() + v1.bs2dsig() < min_bs2dsig01)
        return false;

      if (v0.pv2ddist + v1.pv2ddist < min_pv2ddist01)
        return false;

      if (v0.pv3ddist + v1.pv3ddist < min_pv3ddist01)
        return false;

      if (v0.pv2dsig() + v1.pv2dsig() < min_pv2dsig01)
        return false;

      if (v0.pv3dsig() + v1.pv3dsig() < min_pv3dsig01)
        return false;

      const double svdist2d = mag(v0.x - v1.x,
                                  v0.y - v1.y);
      const double svdist3d = mag(v0.x - v1.x,
                                  v0.y - v1.y,
                                  v0.z - v1.z);

      if (svdist2d < min_svdist2d || svdist2d > max_svdist2d)
        return false;

      if (svdist3d < min_svdist3d)
        return false;

      if (v0.ntrackssharedwpv()  + v1.ntrackssharedwpv()  > max_ntrackssharedwpv01)
        return false;
      if (v0.ntrackssharedwpvs() + v1.ntrackssharedwpvs() > max_ntrackssharedwpvs01)
        return false;
      if (float(v0.ntrackssharedwpv()  + v1.ntrackssharedwpv ())/(v0.ntracks() + v1.ntracks()) > max_fractrackssharedwpv01)
        return false;
      if (float(v0.ntrackssharedwpvs() + v1.ntrackssharedwpvs())/(v0.ntracks() + v1.ntracks()) > max_fractrackssharedwpvs01)
        return false;
    }
  }

  return true;
}

DEFINE_FWK_MODULE(MFVAnalysisCuts);
