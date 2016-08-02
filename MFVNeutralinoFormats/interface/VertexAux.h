#ifndef JMTucker_MFVNeutralinoFormats_interface_VertexAux_h
#define JMTucker_MFVNeutralinoFormats_interface_VertexAux_h

#include <vector>
#include "TLorentzVector.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "JMTucker/MFVNeutralinoFormats/interface/JetVertexAssociation.h"

struct MFVVertexAux {
  typedef unsigned char uchar;
  typedef unsigned short ushort;
  typedef unsigned int uint;

  MFVVertexAux() {
    which = ndof_ = jetpairdrmin_ = jetpairdrmax_ = jetpairdravg_ = jetpairdrrms_ = costhtkmomvtxdispmin_ = costhtkmomvtxdispmax_ = costhtkmomvtxdispavg_ = costhtkmomvtxdisprms_ = costhjetmomvtxdispmin_ = costhjetmomvtxdispmax_ = costhjetmomvtxdispavg_ = costhjetmomvtxdisprms_ = 0;
    x = y = z = cxx = cxy = cxz = cyy = cyz = czz = chi2 = gen2ddist = gen2derr = gen3ddist = gen3derr = bs2ddist = bs2derr = pv2ddist = pv2derr = pv3ddist = pv3derr = 0;
    for (int i = 0; i < mfv::NJetsByUse; ++i)
      njets[i] = 0;
    for (int i = 0; i < mfv::NMomenta; ++i) {
      costhmombs_[i] = costhmompv2d_[i] = costhmompv3d_[i] = 0;
      pt[i] = eta[i] = phi[i] = mass[i] = missdistpv[i] = missdistpverr[i] = 0;
    }
  }

  uchar which;
  std::vector<uchar> which_lep; // electrons have 7th bit set

  float x;
  float y;
  float z;

  float cxx;
  float cxy;
  float cxz;
  float cyy;
  float cyz;
  float czz;

  float chi2;
  uchar ndof_; // may not be = ntracks - 3 if weights used in vtx fit
  float ndof() const { return float(ndof_); }
  float chi2dof() const { return chi2 / ndof(); }

  uchar njets[mfv::NJetsByUse];

  float pt  [mfv::NMomenta];
  float eta [mfv::NMomenta];
  float phi [mfv::NMomenta];
  float mass[mfv::NMomenta];

  TLorentzVector p4(int w=0) const {
    TLorentzVector v;
    v.SetPtEtaPhiM(pt[w], eta[w], phi[w], mass[w]);
    return v;
  }

  double betagamma(int w=0) const {
    TLorentzVector v = p4(w);
    return v.Beta() * v.Gamma();
  }

  uchar jetpairdetamin_;
  uchar jetpairdetamax_;
  uchar jetpairdetaavg_;
  uchar jetpairdetarms_;

  uchar jetpairdrmin_;
  uchar jetpairdrmax_;
  uchar jetpairdravg_;
  uchar jetpairdrrms_;

  uchar costhtkmomvtxdispmin_;
  uchar costhtkmomvtxdispmax_;
  uchar costhtkmomvtxdispavg_;
  uchar costhtkmomvtxdisprms_;

  uchar costhjetmomvtxdispmin_;
  uchar costhjetmomvtxdispmax_;
  uchar costhjetmomvtxdispavg_;
  uchar costhjetmomvtxdisprms_;

  static uchar bin(float x, float min, float max) {
    if (x <= min)
      return 0;
    else if (x >= max)
      return 255;
    const float r = (x - min)/(max - min);
    if (r <= 0)
      return 0;
    else if (r >= 1)
      return 255;
    return r * 255;
  }

  static float unbin(uchar x, float min, float max) {
    return x/255.f * (max - min) + min;
  }

  // max deta ~= 5, max dr = sqrt(5**2 + pi**2) ~= 6 -> precision on deta/dr = 6/255 = 0.024
  float jetpairdetamin() const { return unbin(jetpairdetamin_, 0, 6); }
  float jetpairdetamax() const { return unbin(jetpairdetamax_, 0, 6); }
  float jetpairdetaavg() const { return unbin(jetpairdetaavg_, 0, 6); }
  float jetpairdetarms() const { return unbin(jetpairdetarms_, 0, 6); }
  void jetpairdetamin(float jetpairdetamin) { jetpairdetamin_ = bin(jetpairdetamin, 0, 6); }
  void jetpairdetamax(float jetpairdetamax) { jetpairdetamax_ = bin(jetpairdetamax, 0, 6); }
  void jetpairdetaavg(float jetpairdetaavg) { jetpairdetaavg_ = bin(jetpairdetaavg, 0, 6); }
  void jetpairdetarms(float jetpairdetarms) { jetpairdetarms_ = bin(jetpairdetarms, 0, 6); }

  float jetpairdrmin() const { return unbin(jetpairdrmin_, 0, 6); }
  float jetpairdrmax() const { return unbin(jetpairdrmax_, 0, 6); }
  float jetpairdravg() const { return unbin(jetpairdravg_, 0, 6); }
  float jetpairdrrms() const { return unbin(jetpairdrrms_, 0, 6); }
  void jetpairdrmin(float jetpairdrmin) { jetpairdrmin_ = bin(jetpairdrmin, 0, 6); }
  void jetpairdrmax(float jetpairdrmax) { jetpairdrmax_ = bin(jetpairdrmax, 0, 6); }
  void jetpairdravg(float jetpairdravg) { jetpairdravg_ = bin(jetpairdravg, 0, 6); }
  void jetpairdrrms(float jetpairdrrms) { jetpairdrrms_ = bin(jetpairdrrms, 0, 6); }

  // precision on costh = 2/256 = 0.0078
  float costhtkmomvtxdispmin() const { return unbin(costhtkmomvtxdispmin_, -1, 1); }
  float costhtkmomvtxdispmax() const { return unbin(costhtkmomvtxdispmax_, -1, 1); }
  float costhtkmomvtxdispavg() const { return unbin(costhtkmomvtxdispavg_, -1, 1); }
  float costhtkmomvtxdisprms() const { return unbin(costhtkmomvtxdisprms_, -1, 1); }
  void costhtkmomvtxdispmin(float costhtkmomvtxdispmin) { costhtkmomvtxdispmin_ = bin(costhtkmomvtxdispmin, -1, 1); }
  void costhtkmomvtxdispmax(float costhtkmomvtxdispmax) { costhtkmomvtxdispmax_ = bin(costhtkmomvtxdispmax, -1, 1); }
  void costhtkmomvtxdispavg(float costhtkmomvtxdispavg) { costhtkmomvtxdispavg_ = bin(costhtkmomvtxdispavg, -1, 1); }
  void costhtkmomvtxdisprms(float costhtkmomvtxdisprms) { costhtkmomvtxdisprms_ = bin(costhtkmomvtxdisprms, -1, 1); }

  float costhjetmomvtxdispmin() const { return unbin(costhjetmomvtxdispmin_, -1, 1); }
  float costhjetmomvtxdispmax() const { return unbin(costhjetmomvtxdispmax_, -1, 1); }
  float costhjetmomvtxdispavg() const { return unbin(costhjetmomvtxdispavg_, -1, 1); }
  float costhjetmomvtxdisprms() const { return unbin(costhjetmomvtxdisprms_, -1, 1); }
  void costhjetmomvtxdispmin(float costhjetmomvtxdispmin) { costhjetmomvtxdispmin_ = bin(costhjetmomvtxdispmin, -1, 1); }
  void costhjetmomvtxdispmax(float costhjetmomvtxdispmax) { costhjetmomvtxdispmax_ = bin(costhjetmomvtxdispmax, -1, 1); }
  void costhjetmomvtxdispavg(float costhjetmomvtxdispavg) { costhjetmomvtxdispavg_ = bin(costhjetmomvtxdispavg, -1, 1); }
  void costhjetmomvtxdisprms(float costhjetmomvtxdisprms) { costhjetmomvtxdisprms_ = bin(costhjetmomvtxdisprms, -1, 1); }

  float sig(float val, float err) const {
    return err <= 0 ? 0 : val/err;
  }

  float geo2ddist() const { return sqrt(x*x + y*y); }
  float geo3ddist() const { return sqrt(x*x + y*y + z*z); }

  float gen2ddist;
  float gen2derr;
  float gen2dsig() const { return sig(gen2ddist, gen2derr); }

  float gen3ddist;
  float gen3derr;
  float gen3dsig() const { return sig(gen3ddist, gen3derr); }

  float bs2ddist;
  float bs2derr;
  float bs2dsig() const { return sig(bs2ddist, bs2derr); }
  float bs2dctau() const { return bs2ddist / betagamma(); }

  float pv2ddist;
  float pv2derr;
  float pv2dsig() const { return sig(pv2ddist, pv2derr); }
  float pv2dctau() const { return pv2ddist / betagamma(); }

  float pv3ddist;
  float pv3derr;
  float pv3dsig() const { return sig(pv3ddist, pv3derr); }
  float pv3dctau() const { return pv3ddist / betagamma(); }

  float pvdz() const { return sqrt(pv3ddist*pv3ddist - pv2ddist*pv2ddist); }
  float pvdzerr() const {
    // JMTBAD
    float z = pvdz();
    if (z == 0)
      return -1;
    return sqrt(pv3ddist*pv3ddist*pv3derr*pv3derr + pv2ddist*pv2ddist*pv2derr*pv2derr)/z;
  }
  float pvdzsig() const { return sig(pvdz(), pvdzerr()); }

  uchar costhmombs_  [mfv::NMomenta];
  uchar costhmompv2d_[mfv::NMomenta];
  uchar costhmompv3d_[mfv::NMomenta];
  float costhmombs  (size_t i) const { return unbin(costhmombs_  [i], -1, 1); }
  float costhmompv2d(size_t i) const { return unbin(costhmompv2d_[i], -1, 1); }
  float costhmompv3d(size_t i) const { return unbin(costhmompv3d_[i], -1, 1); }
  void costhmombs  (size_t i, float x) { costhmombs_  [i] = bin(x, -1, 1); }
  void costhmompv2d(size_t i, float x) { costhmompv2d_[i] = bin(x, -1, 1); }
  void costhmompv3d(size_t i, float x) { costhmompv3d_[i] = bin(x, -1, 1); }

  float missdistpv   [mfv::NMomenta];
  float missdistpverr[mfv::NMomenta];
  float missdistpvsig(int w) const { return sig(missdistpv[w], missdistpverr[w]); }


  std::vector<uchar> track_w;
  static uchar make_track_weight(float weight) { assert(weight >= 0 && weight <= 1); return uchar(weight*255); }
  float track_weight(int i) const { return float(track_w[i])/255.f; }
  std::vector<float> track_qpt;
  float track_q(int i) const { return track_qpt[i] > 0 ? 1 : -1; }
  float track_pt(int i) const { return fabs(track_qpt[i]); }
  std::vector<float> track_eta;
  std::vector<float> track_phi;
  std::vector<float> track_dxy;
  std::vector<float> track_dz;
  std::vector<uchar> track_pt_err_; // relative to pt, rest are absolute values
  std::vector<uchar> track_eta_err_;
  std::vector<uchar> track_phi_err_;
  std::vector<uchar> track_dxy_err_;
  std::vector<uchar> track_dz_err_;
  std::vector<uchar> track_chi2dof_;
  std::vector<ushort> track_hitpattern;
  static ushort make_track_hitpattern(int npx, int nst, int nbehind, int nlost) {
    assert(npx >= 0 && nst >= 0 && nbehind >= 0 && nlost >= 0);
    if (npx > 7) npx = 7;
    if (nst > 31) nst = 31;
    if (nbehind > 15) nbehind = 15;
    if (nlost > 15) nlost = 15;
    return (nlost << 12) | (nbehind << 8) | (nst << 3) | npx;
  }
  int track_npxhits(int i) const { return track_hitpattern[i] & 0x7; }
  int track_nsthits(int i) const { return (track_hitpattern[i] >> 3) & 0x1F; }
  int track_nhitsbehind(int i) const { return (track_hitpattern[i] >> 8) & 0xF; }
  int track_nhitslost(int i) const { return (track_hitpattern[i] >> 12) & 0xF; }
  int track_nhits(int i) const { return track_npxhits(i) + track_nsthits(i); }
  std::vector<bool> track_injet;
  std::vector<short> track_inpv;

  static void _set(std::vector<uchar>& v, int i, uchar x) {
    if (i < 0) v.push_back(x);
    else       v[i] = x;
  }

  void  track_pt_err(int i, float x) {         _set(track_pt_err_, i , bin(x, 0, 2)); }
  float track_pt_err(int i) const    { return unbin(track_pt_err_ [i],        0, 2); }

  void  track_eta_err(int i, float x) {         _set(track_eta_err_, i , bin(x, 0, 0.02)); }
  float track_eta_err(int i) const    { return unbin(track_eta_err_ [i],        0, 0.02); }

  void  track_phi_err(int i, float x) {         _set(track_phi_err_, i , bin(x, 0, 0.02)); }
  float track_phi_err(int i) const    { return unbin(track_phi_err_ [i],        0, 0.02); }

  void  track_dxy_err(int i, float x) {         _set(track_dxy_err_, i , bin(x, 0, 0.1)); }
  float track_dxy_err(int i) const    { return unbin(track_dxy_err_ [i],        0, 0.1); }

  void  track_dz_err(int i, float x) {         _set(track_dz_err_, i , bin(x, 0, 0.1)); }
  float track_dz_err(int i) const    { return unbin(track_dz_err_ [i],        0, 0.1); }

  void  track_chi2dof(int i, float x) {         _set(track_chi2dof_, i , bin(x, 0, 10)); }
  float track_chi2dof(int i) const    { return unbin(track_chi2dof_ [i],        0, 10); }

  void insert_track() {
    track_w.push_back(0);
    track_qpt.push_back(0);
    track_eta.push_back(0);
    track_phi.push_back(0);
    track_dxy.push_back(0);
    track_dz.push_back(0);
    track_pt_err_.push_back(0);
    track_eta_err_.push_back(0);
    track_phi_err_.push_back(0);
    track_dxy_err_.push_back(0);
    track_dz_err_.push_back(0);
    track_chi2dof_.push_back(0);
    track_hitpattern.push_back(0);
    track_injet.push_back(0);
    track_inpv.push_back(0);
  }

  bool tracks_ok() const {
    const size_t n = ntracks();
    return
      n == track_w.size() &&
      n == track_qpt.size() &&
      n == track_eta.size() &&
      n == track_phi.size() &&
      n == track_dxy.size() &&
      n == track_dz.size() &&
      n == track_pt_err_.size() &&
      n == track_eta_err_.size() &&
      n == track_phi_err_.size() &&
      n == track_dxy_err_.size() &&
      n == track_dz_err_.size() &&
      n == track_chi2dof_.size() &&
      n == track_hitpattern.size() &&
      n == track_injet.size() &&
      n == track_inpv.size();
  }

  TLorentzVector track_p4(int i, float mass=0) const {
    TLorentzVector v;
    v.SetPtEtaPhiM(track_pt(i), track_eta[i], track_phi[i], mass);
    return v;
  }

  int ntracks() const {
    return int(track_w.size());
  }

  bool use_track(size_t i) const {
    static const float pt_err_thr = 0.5;
    return track_pt_err(i) / track_pt(i) <= pt_err_thr;
  }

  int nbadtracks() const {
    int c = 0;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (!use_track(i))
        ++c;
    return c;
  }

  int ngoodtracks() const {
    return ntracks() - nbadtracks();
  }

  int ntracksptgt(float thr) const {
    int c = 0;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i) && track_pt(i) > thr)
        ++c;
    return c;
  }

  int trackminnhits() const {
    int m = 255, m2;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i) && (m2 = track_nhits(i)) < m)
        m = m2;
    return m;
  }

  int trackmaxnhits() const {
    int m = 0, m2;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i) && (m2 = track_nhits(i)) > m)
        m = m2;
    return m;
  }

  float sumpt2() const {
    float sum = 0;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        sum += pow(track_pt(i), 2);
    return sum;
  }

  int sumnhitsbehind() const {
    int c = 0;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        c += track_nhitsbehind(i);
    return c;
  }

  int maxnhitsbehind() const {
    int m = 0, m2;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i) && (m2 = track_nhitsbehind(i)) > m)
        m = m2;
    return m;
  }

  int ntrackssharedwpv() const {
    int c = 0;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i) && track_inpv[i] == 0)
        ++c;
    return c;
  }

  int ntrackssharedwpvs() const {
    int c = 0;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i) && track_inpv[i] >= 0)
        ++c;
    return c;
  }

  std::map<int,int> pvswtracksshared() const {
    std::map<int,int> m;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        ++m[track_inpv[i]];
    return m;
  }

  int npvswtracksshared() const {
    std::map<int,int> m = pvswtracksshared();
    int c = int(m.size());
    if (m.find(-1) != m.end())
      --c;
    return c;
  }

  int pvmosttracksshared() const {
    std::map<int,int> m = pvswtracksshared();
    int mi = -1, mc = 0;
    for (std::map<int,int>::const_iterator it = m.begin(), ite = m.end(); it != ite; ++it)
      if (it->first != -1 && it->second > mc) {
        mc = it->second;
        mi = it->first;
      }
    return mi;
  }

  float _min(const std::vector<float>& v, const bool filter=true) const {
    float m = 1e99;
    for (size_t i = 0, ie = v.size(); i < ie; ++i)
      if (!filter || use_track(i))
        if (v[i] < m)
          m = v[i];
    return m;
  }

  float _max(const std::vector<float>& v, const bool filter=true) const {
    float m = -1e99;
    for (size_t i = 0, ie = v.size(); i < ie; ++i)
      if (!filter || use_track(i))
        if (v[i] > m)
          m = v[i];
    return m;
  }

  float _avg(const std::vector<float>& v, const bool filter=true) const {
    float a = 0.f;
    int c = 0;
    for (size_t i = 0, ie = v.size(); i < ie; ++i)
      if (!filter || use_track(i)) {
        a += v[i];
        ++c;
      }
    return a / c;
  }

  float _rms(const std::vector<float>& v, const bool filter=true) const {
    if (v.size() == 0) return 0.f;
    float avg = _avg(v, filter);
    std::vector<float> v2;
    for (size_t i = 0, ie = v.size(); i < ie; ++i)
      if (!filter || use_track(i))
        v2.push_back(pow(v[i] - avg, 2));
    return sqrt(std::accumulate(v2.begin(), v2.end(), 0.f)/v2.size());
  }

  struct stats {
    float min, max, avg, rms;
    stats(const MFVVertexAux* a, const std::vector<float>& v, const bool filter=false)
      : min(a->_min(v, filter)),
        max(a->_max(v, filter)),
        avg(a->_avg(v, filter)),
        rms(a->_rms(v, filter))
    {}
  };


  std::vector<float> track_pts() const {
    std::vector<float> v;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        v.push_back(track_pt(i));
    return v;
  }

  std::vector<float> track_pt_errs() const {
    std::vector<float> v;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        v.push_back(track_pt_err(i));
    return v;
  }

  std::vector<float> track_eta_errs() const {
    std::vector<float> v;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        v.push_back(track_eta_err(i));
    return v;
  }

  std::vector<float> track_phi_errs() const {
    std::vector<float> v;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        v.push_back(track_phi_err(i));
    return v;
  }

  std::vector<float> track_dxy_errs() const {
    std::vector<float> v;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        v.push_back(track_dxy_err(i));
    return v;
  }

  std::vector<float> track_dz_errs() const {
    std::vector<float> v;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        v.push_back(track_dz_err(i));
    return v;
  }

  float mintrackpt() const { return _min(track_pts(), false); } // already filtered
  float maxtrackpt() const { return _max(track_pts(), false); }

  float maxmntrackpt(int n) const {
    std::vector<float> pt = track_pts();
    int nt = int(pt.size());
    if (n > nt - 1)
      return -1;
    std::sort(pt.begin(), pt.end());
    return pt[nt-1-n];
  }

  float trackptavg() const { return _avg(track_pts(), false); }
  float trackptrms() const { return _rms(track_pts(), false); }

  float trackdxymin() const { return _min(track_dxy); }
  float trackdxymax() const { return _max(track_dxy); }
  float trackdxyavg() const { return _avg(track_dxy); }
  float trackdxyrms() const { return _rms(track_dxy); }

  float trackdzmin() const { return _min(track_dz); }
  float trackdzmax() const { return _max(track_dz); }
  float trackdzavg() const { return _avg(track_dz); }
  float trackdzrms() const { return _rms(track_dz); }

  float trackpterrmin() const { return _min(track_pt_errs()); }
  float trackpterrmax() const { return _max(track_pt_errs()); }
  float trackpterravg() const { return _avg(track_pt_errs()); }
  float trackpterrrms() const { return _rms(track_pt_errs()); }

  float tracketaerrmin() const { return _min(track_eta_errs()); }
  float tracketaerrmax() const { return _max(track_eta_errs()); }
  float tracketaerravg() const { return _avg(track_eta_errs()); }
  float tracketaerrrms() const { return _rms(track_eta_errs()); }

  float trackphierrmin() const { return _min(track_phi_errs()); }
  float trackphierrmax() const { return _max(track_phi_errs()); }
  float trackphierravg() const { return _avg(track_phi_errs()); }
  float trackphierrrms() const { return _rms(track_phi_errs()); }

  float trackdxyerrmin() const { return _min(track_dxy_errs()); }
  float trackdxyerrmax() const { return _max(track_dxy_errs()); }
  float trackdxyerravg() const { return _avg(track_dxy_errs()); }
  float trackdxyerrrms() const { return _rms(track_dxy_errs()); }

  float trackdzerrmin() const { return _min(track_dz_errs()); }
  float trackdzerrmax() const { return _max(track_dz_errs()); }
  float trackdzerravg() const { return _avg(track_dz_errs()); }
  float trackdzerrrms() const { return _rms(track_dz_errs()); }

  std::vector<float> trackpairdetas() const {
    std::vector<float> v;
    size_t n = ntracks();
    if (n >= 2)
      for (size_t i = 0, ie = n-1; i < ie; ++i)
        if (use_track(i))
          for (size_t j = i+1, je = n; j < je; ++j)
            if (use_track(j))
              v.push_back(fabs(track_eta[i] - track_eta[j]));
    return v;
  }

  float trackpairdetamin() const { return stats(this, trackpairdetas()).min; }
  float trackpairdetamax() const { return stats(this, trackpairdetas()).max; }
  float trackpairdetaavg() const { return stats(this, trackpairdetas()).avg; }
  float trackpairdetarms() const { return stats(this, trackpairdetas()).rms; }

  std::vector<float> trackpairdphis() const {
    std::vector<float> v;
    size_t n = ntracks();
    if (n >= 2)
      for (size_t i = 0, ie = n-1; i < ie; ++i)
        if (use_track(i))
          for (size_t j = i+1, je = n; j < je; ++j)
            if (use_track(j))
              v.push_back(reco::deltaPhi(track_phi[i], track_phi[j]));
    return v;
  }

  float trackpairdphimin() const { return stats(this, trackpairdphis()).min; }
  float trackpairdphimax() const { return stats(this, trackpairdphis()).max; }
  float trackpairdphiavg() const { return stats(this, trackpairdphis()).avg; }
  float trackpairdphirms() const { return stats(this, trackpairdphis()).rms; }

  std::vector<float> trackpairdrs() const {
    std::vector<float> v;
    size_t n = ntracks();
    if (n >= 2)
      for (size_t i = 0, ie = n-1; i < ie; ++i)
        if (use_track(i))
          for (size_t j = i+1, je = n; j < je; ++j)
            if (use_track(j))
              v.push_back(reco::deltaR(track_eta[i], track_phi[i],
                                       track_eta[j], track_phi[j]));
    return v;
  }

  float trackpairdrmin() const { return stats(this, trackpairdrs()).min; }
  float trackpairdrmax() const { return stats(this, trackpairdrs()).max; }
  float trackpairdravg() const { return stats(this, trackpairdrs()).avg; }
  float trackpairdrrms() const { return stats(this, trackpairdrs()).rms; }

  float drmin() const { return trackpairdrmin(); }
  float drmax() const { return trackpairdrmax(); }
  float dravg() const { return trackpairdravg(); }
  float drrms() const { return trackpairdrrms(); }

  std::vector<float> trackpairmasses(float mass=0) const {
    std::vector<float> v;
    size_t n = ntracks();
    if (n >= 2)
      for (size_t i = 0, ie = n-1; i < ie; ++i)
        if (use_track(i))
          for (size_t j = i+1, je = n; j < je; ++j)
            if (use_track(j))
              v.push_back((track_p4(i, mass) + track_p4(j, mass)).M());
    return v;
  }

  float trackpairmassmin() const { return stats(this, trackpairmasses()).min; }
  float trackpairmassmax() const { return stats(this, trackpairmasses()).max; }
  float trackpairmassavg() const { return stats(this, trackpairmasses()).avg; }
  float trackpairmassrms() const { return stats(this, trackpairmasses()).rms; }

  std::vector<float> tracktripmasses(float mass=0) const {
    std::vector<float> v;
    size_t n = ntracks();
    if (n >= 3)
      for (size_t i = 0, ie = n-2; i < ie; ++i)
        if (use_track(i))
          for (size_t j = i+1, je = n-1; j < je; ++j)
            if (use_track(j))
              for (size_t k = j+1, ke = n; k < ke; ++k)
                if (use_track(k))
                  v.push_back((track_p4(i, mass) + track_p4(j, mass) + track_p4(k, mass)).M());
    return v;
  }

  float tracktripmassmin() const { return stats(this, tracktripmasses()).min; }
  float tracktripmassmax() const { return stats(this, tracktripmasses()).max; }
  float tracktripmassavg() const { return stats(this, tracktripmasses()).avg; }
  float tracktripmassrms() const { return stats(this, tracktripmasses()).rms; }

  std::vector<float> trackquadmasses(float mass=0) const {
    std::vector<float> v;
    size_t n = ntracks();
    if (n >= 4)
      for (size_t i = 0, ie = n-3; i < ie; ++i)
        if (use_track(i))
          for (size_t j = i+1, je = n-2; j < je; ++j)
            if (use_track(j))
              for (size_t k = j+1, ke = n-1; k < ke; ++k)
                if (use_track(k))
                  for (size_t l = k+1, le = n; l < le; ++l)
                    if (use_track(l))
                      v.push_back((track_p4(i, mass) + track_p4(j, mass) + track_p4(k, mass) + track_p4(l, mass)).M());
    return v;
  }

  float trackquadmassmin() const { return stats(this, trackquadmasses()).min; }
  float trackquadmassmax() const { return stats(this, trackquadmasses()).max; }
  float trackquadmassavg() const { return stats(this, trackquadmasses()).avg; }
  float trackquadmassrms() const { return stats(this, trackquadmasses()).rms; }

  float sumpt() const {
    float sum = 0;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i)
      if (use_track(i))
        sum += track_pt(i);
    return sum;
  }

  float trackST() const {
    float sum = 0;
    for (size_t i = 0, ie = ntracks(); i < ie; ++i) {
      if (use_track(i)) {
        float px_i = track_pt(i) * cos(track_phi[i]);
        float py_i = track_pt(i) * sin(track_phi[i]);
        for (size_t j = 0, je = ntracks(); j < je; ++j) {
          if (use_track(j)) {
            float px_j = track_pt(j) * cos(track_phi[j]);
            float py_j = track_pt(j) * sin(track_phi[j]);
            sum += (px_i*px_i * py_j*py_j - px_i*py_i * px_j*py_j) / (track_pt(i) * track_pt(j));
          }
        }
      }
    }
    return 1 - sqrt(1 - 4/(sumpt() * sumpt()) * sum);
  }
};

typedef std::vector<MFVVertexAux> MFVVertexAuxCollection;

#endif
