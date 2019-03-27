#ifndef JMTucker_Tools_Ntuple_h
#define JMTucker_Tools_Ntuple_h

#include <cassert>
#include <numeric>
#include <vector>
#include "TLorentzVector.h"
#include "TTree.h"
#include "TVector3.h"

namespace jmt {
  class INtuple {
  public:
    const char* pfx() const { return pfx_; }
    void set_pfx(const char* p) { pfx_ = p; }

  protected:
    typedef unsigned char uchar;
    typedef unsigned short ushort;
    typedef std::vector<bool> vbool;
    typedef std::vector<float> vfloat;
    typedef std::vector<uchar> vuchar;
    typedef std::vector<ushort> vushort;
    typedef std::vector<unsigned> vunsigned;
    typedef std::vector<int> vint;

    template <typename T> static int p_size(const std::vector<T>& v, const std::vector<T>* p) { return int(p ? p->size() : v.size()); }
    template <typename T> static T p_get(int i, const std::vector<T>& v, const std::vector<T>* p) { return p ? p->at(i) : v.at(i); }

    template <typename T> static bool test_bit(T v, size_t i) { return bool((v >> i) & 1); }
    template <typename T> static void set_bit(T& v, size_t i, bool x) { v ^= (-T(x) ^ v) & (T(1) << i); }

    static TVector3 p3_(double pt, double eta, double phi) { TVector3 v; v.SetPtEtaPhi(pt, eta, phi); return v; }
    static TLorentzVector p4_e(double pt, double eta, double phi, double e) { TLorentzVector v; v.SetPtEtaPhiE(pt, eta, phi, e); return v; }
    static TLorentzVector p4_m(double pt, double eta, double phi, double m) { TLorentzVector v; v.SetPtEtaPhiM(pt, eta, phi, m); return v; }

    virtual void clear() = 0;
    virtual void write_to_tree(TTree*) = 0;
    virtual void read_from_tree(TTree*) = 0;

    const char* pfx_;
  };

  ////

  class BaseSubNtuple : public INtuple {
  public:
    BaseSubNtuple();
    virtual void clear();
    virtual void write_to_tree(TTree*);
    virtual void read_from_tree(TTree*);

    void set_weight(float x) { weight_ = x; }
    float weight() const { return weight_; }
    void set_event(unsigned r, unsigned l, unsigned long long e) { run_ = r; lumi_ = l; event_ = e; }
    unsigned run() const { return run_; }
    unsigned lumi() const { return lumi_; }
    unsigned long long event() const { return event_; }
    void set_pass(uchar x) { pass_ = x; }
    uchar pass() const { return pass_; }
    void set_npu(uchar x) { npu_ = x; }
    uchar npu() const { return npu_; }
    void set_rho(float x) { rho_ = x; }
    float rho() const { return rho_; }
    void set_nallpv(uchar x) { nallpv_ = x; }
    uchar nallpv() const { return nallpv_; }

  private:
    float weight_;
    unsigned run_;
    unsigned lumi_;
    unsigned long long event_;
    uchar pass_;
    uchar npu_;
    float rho_;
    uchar nallpv_;
  };

  ////

  class BeamspotSubNtuple : public INtuple {
  public:
    BeamspotSubNtuple();
    virtual void clear();
    virtual void write_to_tree(TTree* tree);
    virtual void read_from_tree(TTree* tree);

    void set(float x, float y, float z, float sigmaz, float dxdz, float dydz, float width,
             float err_x, float err_y, float err_z, float err_sigmaz, float err_dxdz, float err_dydz, float err_width) {
      x_ = x;
      y_ = y;
      z_ = z;
      sigmaz_ = sigmaz;
      dxdz_ = dxdz;
      dydz_ = dydz;
      width_ = width;
      err_x_ = err_x;
      err_y_ = err_y;
      err_z_ = err_z;
      err_sigmaz_ = err_sigmaz;
      err_dxdz_ = err_dxdz;
      err_dydz_ = err_dydz;
      err_width_ = err_width;
    }

    float x() const { return x_; }
    float y() const { return y_; }
    float z() const { return z_; }
    float sigmaz() const { return sigmaz_; }
    float dxdz() const { return dxdz_; }
    float dydz() const { return dydz_; }
    float width() const { return width_; }
    float err_x() const { return err_x_; }
    float err_y() const { return err_y_; }
    float err_z() const { return err_z_; }
    float err_sigmaz() const { return err_sigmaz_; }
    float err_dxdz() const { return err_dxdz_; }
    float err_dydz() const { return err_dydz_; }
    float err_width() const { return err_width_; }

    float x(float zp) const { return x() + dxdz() * (zp - z()); }
    float y(float zp) const { return y() + dydz() * (zp - z()); }

  private:
    float x_;
    float y_;
    float z_;
    float sigmaz_;
    float dxdz_;
    float dydz_;
    float width_;
    float err_x_;
    float err_y_;
    float err_z_;
    float err_sigmaz_;
    float err_dxdz_;
    float err_dydz_;
    float err_width_;
  };

  ////

  class VerticesSubNtuple : public INtuple {
  public:
    VerticesSubNtuple();
    virtual void clear();
    virtual void write_to_tree(TTree* tree);
    virtual void read_from_tree(TTree* tree);

    void add(float x, float y, float z, float chi2, float ndof, int ntracks, float score,
             float cxx, float cxy, float cxz, float cyy, float cyz, float czz,
             unsigned misc) {
      x_.push_back(x);
      y_.push_back(y);
      z_.push_back(z);
      chi2_.push_back(chi2);
      ndof_.push_back(ndof);
      ntracks_.push_back(ntracks);
      score_.push_back(score);
      cxx_.push_back(cxx);
      cxy_.push_back(cxy);
      cxz_.push_back(cxz);
      cyy_.push_back(cyy);
      cyz_.push_back(cyz);
      czz_.push_back(czz);
      misc_.push_back(misc);
    }

    int n() const { return p_size(x_, p_x_); }
    float x      (int i) const { return p_get(i, x_,       p_x_       ); }
    float y      (int i) const { return p_get(i, y_,       p_y_       ); }
    float z      (int i) const { return p_get(i, z_,       p_z_       ); }
    float chi2   (int i) const { return p_get(i, chi2_,    p_chi2_    ); }
    float ndof   (int i) const { return p_get(i, ndof_,    p_ndof_    ); }
    uchar ntracks(int i) const { return p_get(i, ntracks_, p_ntracks_ ); }
    float score  (int i) const { return p_get(i, score_,   p_score_   ); }
    float cxx    (int i) const { return p_get(i, cxx_,     p_cxx_     ); }
    float cxy    (int i) const { return p_get(i, cxy_,     p_cxy_     ); }
    float cxz    (int i) const { return p_get(i, cxz_,     p_cxz_     ); }
    float cyy    (int i) const { return p_get(i, cyy_,     p_cyy_     ); }
    float cyz    (int i) const { return p_get(i, cyz_,     p_cyz_     ); }
    float czz    (int i) const { return p_get(i, czz_,     p_czz_     ); }
    unsigned misc(int i) const { return p_get(i, misc_,    p_misc_    ); }

    void set_misc(int i, unsigned x) { assert(0 == p_misc_); misc_[i] = x; }

    float chi2dof(int i) const { return chi2(i) / ndof(i); }
    float rho(int i) const { return std::hypot(x(i), y(i)); }
    TVector3 pos(int i) const { return TVector3(x(i), y(i), z(i)); }

  private:
    vfloat x_;           vfloat* p_x_;
    vfloat y_;           vfloat* p_y_;
    vfloat z_;           vfloat* p_z_;
    vfloat chi2_;        vfloat* p_chi2_;
    vfloat ndof_;        vfloat* p_ndof_;
    vuchar ntracks_;     vuchar* p_ntracks_;
    vfloat score_;       vfloat* p_score_;
    vfloat cxx_;         vfloat* p_cxx_;
    vfloat cxy_;         vfloat* p_cxy_;
    vfloat cxz_;         vfloat* p_cxz_;
    vfloat cyy_;         vfloat* p_cyy_;
    vfloat cyz_;         vfloat* p_cyz_;
    vfloat czz_;         vfloat* p_czz_;
    vunsigned misc_;     vunsigned* p_misc_;
  };

  class PrimaryVerticesSubNtuple   : public VerticesSubNtuple { public: PrimaryVerticesSubNtuple  () { set_pfx("pv"); }};
  class SecondaryVerticesSubNtuple : public VerticesSubNtuple { public: SecondaryVerticesSubNtuple() { set_pfx("sv"); }};

  ////

  class TracksSubNtuple : public INtuple {
  public:
    TracksSubNtuple();
    virtual void clear();
    virtual void write_to_tree(TTree* tree);
    virtual void read_from_tree(TTree* tree);

    void add(int q, float pt, float eta, float phi, float dxybs, float dxypv, float dzpv, float vx, float vy, float vz,
             float err_pt, float err_eta, float err_phi, float err_dxy, float err_dz, float chi2dof,
             int npxh, int nsth, int npxl, int nstl,
             int minhit_r, int minhit_z, int maxhit_r, int maxhit_z, int maxpxhit_r, int maxpxhit_z,
             int which_jet, int which_pv, int which_sv,
             unsigned misc) {
      qpt_.push_back(q*pt);
      eta_.push_back(eta);
      phi_.push_back(phi);
      dxybs_.push_back(dxybs);
      dxypv_.push_back(dxypv);
      dzpv_.push_back(dzpv);
      vx_.push_back(vx);
      vy_.push_back(vy);
      vz_.push_back(vz);
      err_pt_.push_back(err_pt);
      err_eta_.push_back(err_eta);
      err_phi_.push_back(err_phi);
      err_dxy_.push_back(err_dxy);
      err_dz_.push_back(err_dz);
      chi2dof_.push_back(chi2dof);

      assert(npxh >= 0 && nsth >= 0 && npxl >= 0 && nstl >= 0);
      if (npxh > 15) npxh = 15;
      if (nsth > 31) nsth = 31;
      if (npxl > 15) npxl = 15;
      if (nstl > 31) nstl = 31;
      hp_.push_back((nstl << 13) | (npxl << 9) | (nsth << 4) | npxh);
      assert(minhit_r >= 0 && minhit_r <= 15);
      assert(minhit_z >= 0 && minhit_z <= 15);
      minhit_.push_back((uchar(minhit_z) << 4) | uchar(minhit_r));
      assert(maxhit_r >= 0 && maxhit_r <= 15);
      assert(maxhit_z >= 0 && maxhit_z <= 15);
      maxhit_.push_back((uchar(maxhit_z) << 4) | uchar(maxhit_r));
      assert(maxpxhit_r >= 0 && maxpxhit_r <= 15);
      assert(maxpxhit_z >= 0 && maxpxhit_z <= 15);
      maxpxhit_.push_back((uchar(maxpxhit_z) << 4) | uchar(maxpxhit_r));

      which_jet_.push_back(which_jet < 0 || which_jet > 255 ? 255 : which_jet);
      which_pv_.push_back(which_pv < 0 || which_pv > 255 ? 255 : which_pv);
      which_sv_.push_back(which_sv < 0 || which_sv > 255 ? 255 : which_sv);
      misc_.push_back(misc);
    }

    int n() const { return p_size(qpt_, p_qpt_); }
    float    qpt      (int i) const { return p_get(i, qpt_,       p_qpt_       ); }
    float    eta      (int i) const { return p_get(i, eta_,       p_eta_       ); }
    float    phi      (int i) const { return p_get(i, phi_,       p_phi_       ); }
    float    dxybs    (int i) const { return p_get(i, dxybs_,     p_dxybs_     ); }
    float    dxypv    (int i) const { return p_get(i, dxypv_,     p_dxypv_     ); }
    float    dzpv     (int i) const { return p_get(i, dzpv_,      p_dzpv_      ); }
    float    vx       (int i) const { return p_get(i, vx_,        p_vx_        ); }
    float    vy       (int i) const { return p_get(i, vy_,        p_vy_        ); }
    float    vz       (int i) const { return p_get(i, vz_,        p_vz_        ); }
    float    err_pt   (int i) const { return p_get(i, err_pt_,    p_err_pt_    ); }
    float    err_eta  (int i) const { return p_get(i, err_eta_,   p_err_eta_   ); }
    float    err_phi  (int i) const { return p_get(i, err_phi_,   p_err_phi_   ); }
    float    err_dxy  (int i) const { return p_get(i, err_dxy_,   p_err_dxy_   ); }
    float    err_dz   (int i) const { return p_get(i, err_dz_,    p_err_dz_    ); }
    float    chi2dof  (int i) const { return p_get(i, chi2dof_,   p_chi2dof_   ); }
    unsigned hp       (int i) const { return p_get(i, hp_,        p_hp_        ); }
    uchar    minhit   (int i) const { return p_get(i, minhit_,    p_minhit_    ); }
    uchar    maxhit   (int i) const { return p_get(i, maxhit_,    p_maxhit_    ); }
    uchar    maxpxhit (int i) const { return p_get(i, maxpxhit_,  p_maxpxhit_  ); }
    uchar    which_jet(int i) const { return p_get(i, which_jet_, p_which_jet_ ); }
    uchar    which_pv (int i) const { return p_get(i, which_pv_,  p_which_pv_  ); }
    uchar    which_sv (int i) const { return p_get(i, which_sv_,  p_which_sv_  ); }
    unsigned misc     (int i) const { return p_get(i, misc_,      p_misc_      ); }

    void set_which_jet(int i, uchar x) { assert(0 == p_which_jet_); which_jet_[i] = x; }
    void set_which_pv(int i, uchar x) { assert(0 == p_which_pv_); which_pv_[i] = x; }
    void set_which_sv(int i, uchar x) { assert(0 == p_which_sv_); which_sv_[i] = x; }
    void set_misc(int i, unsigned x) { assert(0 == p_misc_); misc_[i] = x; }

    int q(int i) const { return qpt(i) > 0 ? 1 : -1; }
    float pt(int i) const { return std::abs(qpt(i)); }
    float px(int i) const { return p3(i).X(); }
    float py(int i) const { return p3(i).Y(); }
    float pz(int i) const { return p3(i).Z(); }
    float nsigmadxybs(int i) const { return std::abs(dxybs(i) / err_dxy(i)); }
    float dxy(int i) const { return (vy(i) * px(i) - vx(i) * py(i)) / pt(i); }
    float dxy(int i, float x, float y) const { return ((vy(i) - y) * px(i) - (vx(i) - x) * py(i)) / pt(i); }
    float dz(int i) const { return vz(i) - (vx(i) * px(i) + vy(i) * py(i)) / pt(i) * pz(i) / pt(i); }
    float dz(int i, float x, float y, float z) const { return (vz(i) - z) - ((vx(i) - x) * px(i) + (vy(i) - y) * py(i)) / pt(i) * pz(i) / pt(i); }
    int npxhits(int i) const { return hp(i) & 0xf; }
    int nsthits(int i) const { return (hp(i) >> 4) & 0x1f; }
    int npxlayers(int i) const { return (hp(i) >> 9) & 0xf; }
    int nstlayers(int i) const { return (hp(i) >> 13) & 0x1f; }
    int nhits(int i) const { return npxhits(i) + nsthits(i); }
    int nlayers(int i) const { return npxlayers(i) + nstlayers(i); }
    int min_r(int i) const { return minhit(i) & 0xF; }
    int min_z(int i) const { return minhit(i) >> 4; }
    int max_r(int i) const { return maxhit(i) & 0xF; }
    int max_z(int i) const { return maxhit(i) >> 4; }
    int maxpx_r(int i) const { return maxpxhit(i) & 0xF; }
    int maxpx_z(int i) const { return maxpxhit(i) >> 4; }
    TVector3 p3(int i) const { return p3_(pt(i), eta(i), phi(i)); }
    TLorentzVector p4(int i, double m=0) const { return p4_m(pt(i), eta(i), phi(i), m); }
    bool pass_sel(int i) const { return pt(i) > 1 && min_r(i) <= 1 && npxlayers(i) >= 2 && nstlayers(i) >= 6; }
    bool pass_seed(int i) const { return pass_sel(i) && nsigmadxybs(i) > 4; }

    std::vector<int> tks_for_jet(uchar i) const { return tks_for_x_(0, i); }
    std::vector<int> tks_for_pv (uchar i) const { return tks_for_x_(1, i); }
    std::vector<int> tks_for_sv (uchar i) const { return tks_for_x_(2, i); }

  private:
    std::vector<int> tks_for_x_(int wi, uchar i) const {
      std::vector<int> v;
      for (int j = 0, je = n(); j < je; ++j)
        if ((wi == 0 && which_jet(j) == i) ||
            (wi == 1 && which_pv (j) == i) ||
            (wi == 2 && which_sv (j) == i))
          v.push_back(j);
      return v;
    }

    vfloat qpt_;         vfloat* p_qpt_;
    vfloat eta_;         vfloat* p_eta_;
    vfloat phi_;         vfloat* p_phi_;
    vfloat dxybs_;       vfloat* p_dxybs_; // JMTBAD drop/recalculate these three
    vfloat dxypv_;       vfloat* p_dxypv_;
    vfloat dzpv_;        vfloat* p_dzpv_;
    vfloat vx_;          vfloat* p_vx_;
    vfloat vy_;          vfloat* p_vy_;
    vfloat vz_;          vfloat* p_vz_;
    vfloat err_pt_;      vfloat* p_err_pt_;
    vfloat err_eta_;     vfloat* p_err_eta_;
    vfloat err_phi_;     vfloat* p_err_phi_;
    vfloat err_dxy_;     vfloat* p_err_dxy_;
    vfloat err_dz_;      vfloat* p_err_dz_;
    vfloat chi2dof_;     vfloat* p_chi2dof_;
    vunsigned hp_;       vunsigned* p_hp_;
    vuchar minhit_;      vuchar* p_minhit_;
    vuchar maxhit_;      vuchar* p_maxhit_;
    vuchar maxpxhit_;    vuchar* p_maxpxhit_;
    vuchar which_jet_;   vuchar* p_which_jet_;
    vuchar which_pv_;    vuchar* p_which_pv_;
    vuchar which_sv_;    vuchar* p_which_sv_;
    vunsigned misc_;     vunsigned* p_misc_;
  };

  class RefitTracksSubNtuple : public TracksSubNtuple { public: RefitTracksSubNtuple  () { set_pfx("rftk"); }};

  ////

  class JetsSubNtuple : public INtuple {
  public:
    JetsSubNtuple();
    virtual void clear();
    virtual void write_to_tree(TTree*);
    virtual void read_from_tree(TTree*);

    void add(float pt, float eta, float phi, float energy, float uncorr, uchar ntracks, float bdisc, uchar genflavor, unsigned misc) {
      pt_.push_back(pt);
      eta_.push_back(eta);
      phi_.push_back(phi);
      energy_.push_back(energy);
      uncorr_.push_back(uncorr);
      ntracks_.push_back(ntracks);
      bdisc_.push_back(bdisc);
      genflavor_.push_back(genflavor);
      misc_.push_back(misc);
    }

    int n() const { return p_size(pt_, p_pt_); }
    float pt        (int i) const { return p_get(i, pt_,        p_pt_);        }
    float eta       (int i) const { return p_get(i, eta_,       p_eta_);       }
    float phi       (int i) const { return p_get(i, phi_,       p_phi_);       }
    float energy    (int i) const { return p_get(i, energy_,    p_energy_);    }
    float uncorr    (int i) const { return p_get(i, uncorr_,    p_uncorr_);    }
    uchar ntracks   (int i) const { return p_get(i, ntracks_,   p_ntracks_);   }
    float bdisc     (int i) const { return p_get(i, bdisc_,     p_bdisc_);     }
    uchar genflavor (int i) const { return p_get(i, genflavor_, p_genflavor_); }
    unsigned misc   (int i) const { return p_get(i, misc_,      p_misc_);      }

    void set_misc(int i, unsigned x) { assert(0 == p_misc_); misc_[i] = x; }

    vfloat::const_iterator pt_begin() const { return p_pt_ ? p_pt_->begin() : pt_.begin(); }
    vfloat::const_iterator pt_end()   const { return p_pt_ ? p_pt_->end()   : pt_.end();   }
    int nminpt(float minpt=20.f) const { return std::count_if(pt_begin(), pt_end(), [minpt](float pt) { return pt > minpt; }); }
    float ht(float minpt=40.f) const { return std::accumulate(pt_begin(), pt_end(), 0.f, [minpt](float init, float pt) { if (pt > minpt) init += pt; return init; }); }
    TVector3 p3(int i) const { return p3_(pt(i), eta(i), phi(i)); }
    TLorentzVector p4(int i) const { return p4_e(pt(i), eta(i), phi(i), energy(i)); }

  private:
    vfloat pt_;          vfloat* p_pt_;
    vfloat eta_;         vfloat* p_eta_;
    vfloat phi_;         vfloat* p_phi_;
    vfloat energy_;      vfloat* p_energy_;
    vfloat uncorr_;      vfloat* p_uncorr_;
    vuchar ntracks_;     vuchar* p_ntracks_;
    vfloat bdisc_;       vfloat* p_bdisc_;
    vuchar genflavor_;   vuchar* p_genflavor_;
    vunsigned misc_;     vunsigned* p_misc_;
  };

  ////

  class TrackingNtuple : public INtuple {
  public:
    TrackingNtuple() { clear(); }

    virtual void clear() {
      base().clear();
      bs().clear();
      pvs().clear();
      tracks().clear();
    }

    virtual void write_to_tree(TTree* t) {
      base().write_to_tree(t);
      bs().write_to_tree(t);
      pvs().write_to_tree(t);
      tracks().write_to_tree(t);
    }

    virtual void read_from_tree(TTree* t) {
      base().read_from_tree(t);
      bs().read_from_tree(t);
      pvs().read_from_tree(t);
      tracks().read_from_tree(t);
    }

    BaseSubNtuple& base() { return base_; }
    BeamspotSubNtuple& bs() { return bs_; }
    PrimaryVerticesSubNtuple& pvs() { return pvs_; }
    TracksSubNtuple& tracks() { return tracks_; }
    const BaseSubNtuple& base() const { return base_; }
    const BeamspotSubNtuple& bs() const { return bs_; }
    const PrimaryVerticesSubNtuple& pvs() const { return pvs_; }
    const TracksSubNtuple& tracks() const { return tracks_; }

  private:
    BaseSubNtuple base_;
    BeamspotSubNtuple bs_;
    PrimaryVerticesSubNtuple pvs_;
    TracksSubNtuple tracks_;
  };


  class TrackingAndJetsNtuple : public TrackingNtuple {
  public:
    TrackingAndJetsNtuple() { clear(); }

    virtual void clear() {
      TrackingNtuple::clear();
      jets().clear();
    }

    virtual void write_to_tree(TTree* t) {
      TrackingNtuple::write_to_tree(t);
      jets().write_to_tree(t);
    }

    virtual void read_from_tree(TTree* t) {
      TrackingNtuple::read_from_tree(t);
      jets().read_from_tree(t);
    }

    JetsSubNtuple& jets() { return jets_; }
    const JetsSubNtuple& jets() const { return jets_; }

  private:
    JetsSubNtuple jets_;
  };
}

#endif