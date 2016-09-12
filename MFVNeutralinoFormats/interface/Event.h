#ifndef JMTucker_MFVNeutralinoFormats_interface_Event_h
#define JMTucker_MFVNeutralinoFormats_interface_Event_h

#include <cassert>
#include <numeric>
#include "TLorentzVector.h"

namespace mfv {
  static const int n_hlt_paths = 19;
  static const int n_l1_paths = 5;
  static const int n_clean_paths = 13;
  static const int n_vertex_seed_pt_quantiles = 7;
}

struct MFVEvent {
  typedef unsigned char uchar;
  typedef unsigned short ushort;
  typedef unsigned int uint;

  static bool test_bit(uint64_t v, size_t i) { return bool((v >> i) & 1); }
  static void set_bit(uint64_t& v, size_t i, bool x) { v ^= (-int(x) ^ v) & (1 << i); }

  MFVEvent() {
    gen_valid = 0;
    gen_partons_in_acc = npv = pv_ntracks = 0;
    gen_flavor_code = 0;
    gen_weight = gen_weightprod = npu = bsx = bsy = bsz = bsdxdz = bsdydz = bswidthx = bswidthy = pvx = pvy = pvz = pvcxx = pvcxy = pvcxz = pvcyy = pvcyz = pvczz = pv_sumpt2 = metx = mety = 0;
    for (int i = 0; i < 2; ++i) {
      gen_lsp_pt[i] = gen_lsp_eta[i] = gen_lsp_phi[i] = gen_lsp_mass[i] = 0;
      gen_decay_type[i] = 0;
      for (int j = 0; j < 3; ++j)
        gen_lsp_decay[i*3+j] = 0;
    }
    for (int i = 0; i < 3; ++i) {
      gen_pv[i] = 0;
    }
    pass_ = 0;
    for (int i = 0; i < mfv::n_vertex_seed_pt_quantiles; ++i)
      vertex_seed_pt_quantiles[i] = 0;
  }

  static TLorentzVector p4(float pt, float eta, float phi, float mass) {
    TLorentzVector v;
    v.SetPtEtaPhiM(pt, eta, phi, mass);
    return v;
  }

  template <typename T>
  static T min(T x, T y) {
    return x < y ? x : y;
  }

  template <typename T>
  static T mag(T x, T y) {
    return sqrt(x*x + y*y);
  }

  template <typename T>
  static T mag(T x, T y, T z) {
    return sqrt(x*x + y*y + z*z);
  }

  float gen_weight;
  float gen_weightprod;

  bool gen_valid; // only refers to the next block, not the weights above
  float gen_lsp_pt[2];
  float gen_lsp_eta[2];
  float gen_lsp_phi[2];
  float gen_lsp_mass[2];
  float gen_lsp_decay[2*3];
  float gen_pv[3];
  uchar gen_decay_type[2];
  uchar gen_partons_in_acc;
  uchar gen_flavor_code;
  std::vector<float> gen_bquark_pt;
  std::vector<float> gen_bquark_eta;
  std::vector<float> gen_bquark_phi;
  std::vector<float> gen_bquark_energy;

  TLorentzVector gen_lsp_p4(int w) const {
    return p4(gen_lsp_pt[w], gen_lsp_eta[w], gen_lsp_phi[w], gen_lsp_mass[w]);
  }

  float minlspdist2d() const {
    return min(mag(gen_lsp_decay[0*3+0] - bsx, gen_lsp_decay[0*3+1] - bsy),
               mag(gen_lsp_decay[1*3+0] - bsx, gen_lsp_decay[1*3+1] - bsy));
  }

  float lspdist2d() const {
    return mag(gen_lsp_decay[0*3+0] - gen_lsp_decay[1*3+0],
               gen_lsp_decay[0*3+1] - gen_lsp_decay[1*3+1]);
  }

  float lspdist3d() const {
    return mag(gen_lsp_decay[0*3+0] - gen_lsp_decay[1*3+0],
               gen_lsp_decay[0*3+1] - gen_lsp_decay[1*3+1],
               gen_lsp_decay[0*3+2] - gen_lsp_decay[1*3+2]);
  }

  uint64_t pass_;
  bool pass_hlt(size_t i)           const { assert(i < mfv::n_hlt_paths);                                                return test_bit(pass_, i   ); }
  void pass_hlt(size_t i, bool x)         { assert(i < mfv::n_hlt_paths);                                                        set_bit(pass_, i, x); }
  bool found_hlt(size_t i)          const { assert(i < mfv::n_hlt_paths);   i += mfv::n_hlt_paths;                       return test_bit(pass_, i   ); }
  void found_hlt(size_t i, bool x)        { assert(i < mfv::n_hlt_paths);   i += mfv::n_hlt_paths;                               set_bit(pass_, i, x); }
  bool pass_l1(size_t i)            const { assert(i < mfv::n_l1_paths);    i += 2*mfv::n_hlt_paths;                     return test_bit(pass_, i   ); }
  void pass_l1(size_t i, bool x)          { assert(i < mfv::n_l1_paths);    i += 2*mfv::n_hlt_paths;                             set_bit(pass_, i, x); }
  bool found_l1(size_t i)           const { assert(i < mfv::n_l1_paths);    i += 2*mfv::n_hlt_paths + mfv::n_l1_paths;   return test_bit(pass_, i   ); }
  void found_l1(size_t i, bool x)         { assert(i < mfv::n_l1_paths);    i += 2*mfv::n_hlt_paths + mfv::n_l1_paths;           set_bit(pass_, i, x); }
  bool pass_clean(size_t i)         const { assert(i < mfv::n_clean_paths); i += 2*mfv::n_hlt_paths + 2*mfv::n_l1_paths; return test_bit(pass_, i   ); }
  void pass_clean(size_t i, bool x)       { assert(i < mfv::n_clean_paths); i += 2*mfv::n_hlt_paths + 2*mfv::n_l1_paths;         set_bit(pass_, i, x); }

  bool pass_clean_all() const {
    bool pass = true;
    return pass;
    //const int N_all = 13;
    //const int clean_all[N_all] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 18, 19};
    //for (int i = 0; i < N_all; ++i)
    //  pass = pass && pass_clean(clean_all[i]);
    //return pass;
  }

  float npu;

  float bsx;
  float bsy;
  float bsz;
  float bsdxdz;
  float bsdydz;
  float bswidthx;
  float bswidthy;

  float bsx_at_z(float z) const { return bsx + bsdxdz * (z - bsz); }
  float bsy_at_z(float z) const { return bsy + bsdydz * (z - bsz); }
  float bs2ddist(float x, float y, float z) const { return mag(x - bsx_at_z(z), y - bsy_at_z(z)); }
  template <typename T> float bs2ddist(const T& t) const { return bs2ddist(t.x, t.y, t.z); }

  uchar npv;
  float pvx;
  float pvy;
  float pvz;
  float pvcxx;
  float pvcxy;
  float pvcxz;
  float pvcyy;
  float pvcyz;
  float pvczz;
  uchar pv_ntracks;
  float pv_sumpt2;
  float pv_rho() const { return mag(pvx - bsx_at_z(pvz), pvy - bsy_at_z(pvz)); }

  std::vector<uchar> jet_id;
  std::vector<float> jet_pudisc; // to be removed and put into _id when working points defined
  std::vector<float> jet_pt;
  std::vector<float> jet_raw_pt;
  std::vector<float> jet_calo_pt;
  std::vector<float> jet_eta;
  std::vector<float> jet_phi;
  std::vector<float> jet_energy;
  std::vector<char> jet_svnvertices;
  std::vector<uchar> jet_svntracks;
  std::vector<float> jet_svsumpt2;
  std::vector<float> jet_svx;
  std::vector<float> jet_svy;
  std::vector<float> jet_svz;
  std::vector<float> jet_svcxx;
  std::vector<float> jet_svcxy;
  std::vector<float> jet_svcxz;
  std::vector<float> jet_svcyy;
  std::vector<float> jet_svcyz;
  std::vector<float> jet_svczz;

  TLorentzVector jet_p4(int w) const {
    TLorentzVector v;
    v.SetPtEtaPhiE(jet_pt[w], jet_eta[w], jet_phi[w], jet_energy[w]);
    return v;
  }
    
  int njets() const { return int(jet_id.size()); }
  float jetpt4() const { return njets() >= 4 ? jet_pt[3] : 0.f; }
  float jetpt5() const { return njets() >= 5 ? jet_pt[4] : 0.f; }
  float jetpt6() const { return njets() >= 6 ? jet_pt[5] : 0.f; }
  float jet_ht(float min_jet_pt=0.f) const { return std::accumulate(jet_pt.begin(), jet_pt.end(), 0.f,
                                                                    [min_jet_pt](float init, float b) { if (b > min_jet_pt) init += b; return init; }); }

  float jet_ST_sum() const {
    double sum = 0;
    for (size_t ijet = 0; ijet < jet_id.size(); ++ijet) {
      const double px_i = jet_pt[ijet] * cos(jet_phi[ijet]);
      const double py_i = jet_pt[ijet] * sin(jet_phi[ijet]);
      for (size_t jjet = 0; jjet < jet_id.size(); ++jjet) {
        const double px_j = jet_pt[jjet] * cos(jet_phi[jjet]);
        const double py_j = jet_pt[jjet] * sin(jet_phi[jjet]);
        sum += (px_i*px_i * py_j*py_j - px_i*py_i * px_j*py_j) / (jet_pt[ijet] * jet_pt[jjet]);
      }
    }
    return sum;
  }

  float jet_ST() const {
    return 1 - sqrt(1 - 4 * jet_ST_sum() / pow(jet_ht(), 2));
  }

  static uchar encode_jet_id(int pu_level, int bdisc_level) {
    assert(pu_level == 0);
    uchar id = 0;
    assert(pu_level >= 0 && pu_level <= 3);
    assert(bdisc_level >= 0 && bdisc_level <= 3);
    id = (bdisc_level << 2) | pu_level;
    return id;
  }

  bool pass_nopu(int w, int level) const {
    return false;
    return (jet_id[w] & 3) >= level + 1;
  }
  
  int njetsnopu(int level) const {
    return -1;
    int c = 0;
    for (int i = 0, ie = njets(); i < ie; ++i)
      if (pass_nopu(i, level))
        ++c;
    return c;
  }

  bool is_btagged(int w, int level) const {
    return ((jet_id[w] >> 2) & 3) >= level + 1;
  }

  int nbtags(int level) const {
    int c = 0;
    for (int i = 0, ie = njets(); i < ie; ++i)
      if (is_btagged(i, level))
        ++c;
    return c;
  }

  float jet_svpv2ddist(int w) const {
    return mag(jet_svx[w] - pvx,
               jet_svy[w] - pvy);
  }

  float jet_svpv2derr(int w) const {
    const float d = jet_svpv2ddist(w);
    const float dx = (jet_svx[w] - pvx)/d;
    const float dy = (jet_svy[w] - pvy)/d;
    return sqrt((pvcxx + jet_svcxx[w])*dx*dx +
                (pvcyy + jet_svcyy[w])*dy*dy +
                2*(pvcxy + jet_svcxy[w])*dx*dy);
  }

  float jet_svpv2dsig(int w) const {
    return jet_svpv2ddist(w) / jet_svpv2derr(w);
  }

  float metx;
  float mety;
  float met() const { return mag(metx, mety); }
  float metphi() const { return atan2(mety, metx); }

  enum { lep_mu, lep_el };
  enum { mu_veto = 1, mu_semilep = 2, mu_dilep = 4, max_mu_sel = 8 };
  enum { el_veto = 1, el_semilep = 2, el_dilep = 4, el_ctf = 8, max_el_sel = 16 };
  std::vector<uchar> lep_id; // bit field: bit 7 (msb): 0 = mu, 1 = el, remaining seven bits are el or mu id in order from lsb to msb according to the enums above
  std::vector<float> lep_pt;
  std::vector<float> lep_eta;
  std::vector<float> lep_phi;
  std::vector<float> lep_dxy;
  std::vector<float> lep_dxybs;
  std::vector<float> lep_dz;
  std::vector<float> lep_iso;

  size_t nlep() const { return lep_id.size(); }

  static uchar encode_mu_id(uchar sel) {
    assert(sel < max_mu_sel);
    return sel;
  }

  static uchar encode_el_id(uchar sel) {
    assert(sel < max_el_sel);
    return sel | 0x80;
  }

  bool is_electron(size_t w) const { return lep_id[w] & 0x80; }
  bool is_muon    (size_t w) const { return !is_electron(w); }
  bool pass_lep_sel_bit(size_t w, uchar sel) const { return lep_id[w] & sel; }
  bool pass_lep_sel(size_t w, uchar el_sel, uchar mu_sel) const { 
    return
      (is_electron(w) && (lep_id[w] & el_sel)) || 
      (is_muon    (w) && (lep_id[w] & mu_sel));
  }

  TLorentzVector lep_p4(size_t w) const {
    const float mass = is_electron(w) ? 0.000511 : 0.106;
    return p4(lep_pt[w], lep_eta[w], lep_phi[w], mass);
  }

  int nlep(int type, uchar sel) const {
    int n = 0;
    for (size_t i = 0, ie = nlep(); i < ie; ++i)
      if (((lep_id[i] & 0x80) >> 7) == type && (lep_id[i] & sel))
        ++n;
    return n;
  }

  int nmu (uchar sel) const { return nlep(lep_mu, sel); }
  int nel (uchar sel) const { return nlep(lep_el, sel); }
  int nlep(uchar sel) const { return nmu(sel) + nel(sel); }

  float jetlep_ST(uchar el_sel, uchar mu_sel) const {
    double sum = jet_ST_sum();
    double sum_lep_pt = 0;

    for (size_t ilep = 0; ilep < nlep(); ++ilep) {
      if (pass_lep_sel(ilep, el_sel, mu_sel)) {
        sum_lep_pt += lep_pt[ilep];

        const double px_i = lep_pt[ilep] * cos(lep_phi[ilep]);
        const double py_i = lep_pt[ilep] * sin(lep_phi[ilep]);
        for (size_t jlep = 0; jlep < nlep(); ++jlep) {
          const double px_j = lep_pt[jlep] * cos(lep_phi[jlep]);
          const double py_j = lep_pt[jlep] * sin(lep_phi[jlep]);
          sum += (px_i*px_i * py_j*py_j - px_i*py_i * px_j*py_j) / (lep_pt[ilep] * lep_pt[jlep]);
        }
      }
    }

    return 1 - sqrt(1 - 4 * sum / pow(jet_ht() + sum_lep_pt, 2));
  }

  float vertex_seed_pt_quantiles[mfv::n_vertex_seed_pt_quantiles];
};

#endif
