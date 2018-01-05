#include "TH2.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/SiPixelDetId/interface/PXBDetId.h"
#include "DataFormats/SiPixelDetId/interface/PXFDetId.h"
#include "DataFormats/SiStripDetId/interface/TIBDetId.h"
#include "DataFormats/SiStripDetId/interface/TOBDetId.h"
#include "DataFormats/SiStripDetId/interface/TIDDetId.h"
#include "DataFormats/SiStripDetId/interface/TECDetId.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "JMTucker/Tools/interface/TrackHistos.h"

namespace jmt {
  TrackHistos::TrackHistos(const char* name, const bool do_2d_, const bool use_rechits_)
    : do_2d(do_2d_), use_rechits(use_rechits_)
  {
    edm::Service<TFileService> fs;
    TFileDirectory d(fs->mkdir(name));

    const char* par_names[9] = {"p", "pt", "eta", "phi", "dxy", "dz", "dxybs", "dxypv", "dzpv"};
    const int par_nbins[9] = {  200, 200,  100,   100, 1000, 1000, 1000, 1000, 1000 };
    const double par_lo[9] = {    0,   0, -2.6, -3.15,   -2,  -20,   -2,   -2,   -2 };
    const double par_hi[9] = {  100, 100,  2.6,  3.15,    2,   20,    2,    2,   -2 };
    const int err_nbins[9] = { 100, 100, 100, 100, 100, 100, 100, 100, 100 };
    const double err_lo[6] = { 0 };
    const double err_hi[6] = { 0.15, 0.15, 0.01, 0.01, 0.2, 0.4 };

    for (int i = 0; i < 9; ++i)
      h_pars[i] = d.make<TH1D>(par_names[i], "", par_nbins[i], par_lo[i], par_hi[i]);
    for (int i = 0; i < 6; ++i)
      h_errs[i] = d.make<TH1D>(TString::Format("err%s", par_names[i]), "", err_nbins[i], err_lo[i], err_hi[i]);
    if (do_2d) {
      for (int i = 0; i < 9; ++i)
        for (int j = i+1; j < 9; ++j)
          h_pars_v_pars[i][j] = d.make<TH2D>(TString::Format("%s_v_%s", par_names[j], par_names[i]), "", par_nbins[i], par_lo[i], par_hi[i], par_nbins[j], par_lo[j], par_hi[j]);
      for (int i = 0; i < 9; ++i)
        for (int j = 0; j < 6; ++j)
          h_errs_v_pars[i][j] = d.make<TH2D>(TString::Format("err%s_v_%s", par_names[j], par_names[i]), "", par_nbins[i], par_lo[i], par_hi[i], err_nbins[j], err_lo[j], err_hi[j]);
    }

    h_dptopt = d.make<TH1D>("dptopt", "", 200, 0, 2);
    h_sigmadxybs = d.make<TH1D>("sigmadxybs", "", 200, -100, 100);

    h_q       = d.make<TH1D>("q", "",  3, -1,   2);
    h_nhits   = d.make<TH1D>("nhits", "", 40,  0,  40);
    h_npxhits = d.make<TH1D>("npxhits", "", 12,  0,  12);
    h_nsthits = d.make<TH1D>("nsthits", "", 28,  0,  28);
    h_npxlayers = d.make<TH1D>("npxlayers", "", 12,  0,  12);
    h_nstlayers = d.make<TH1D>("nstlayers", "", 28,  0,  28);
    h_nlosthits = d.make<TH1D>("nlosthits", "", 10, 0, 10);
    h_nlostlayers = d.make<TH1D>("nlostlayers", "", 10, 0, 10);
    h_chi2    = d.make<TH1D>("chi2", "", 50,  0, 100);
    h_dof     = d.make<TH1D>("dof", "", 50,  0, 100);
    h_chi2dof = d.make<TH1D>("chi2dof", "", 50,  0,  10);
    h_algo    = d.make<TH1D>("algo", "", 30,  0,  30);
    h_quality = d.make<TH1D>("quality", "",  7,  0,   7);
    h_highpurity = d.make<TH1D>("highpurity", "",  2,0,2);
    h_nloops  = d.make<TH1D>("nloops", "", 10,  0,  10);

    if (use_rechits) {
      h_unknown_detid = d.make<TH1D>("unknown_detid", "", 1, 0, 1);

      for (int i = 1; i <= 3; ++i)
        h_pxb_ladder_module[i] = d.make<TH2D>(TString::Format("pxb_layer_%i_ladder_module", i), ";ladder;module", 256, 0, 256, 64, 0, 64);

      for (int i = 1; i <= 2; ++i)
        for (int j = 1; j <= 2; ++j)
          for (int k = 1; k <= 4; ++k)
            h_pxf_panel_module[i][j][k] = d.make<TH2D>(TString::Format("pxf_side_%i_disk_%i_panel_%i_blade_module", i, j, k), ";blade;module", 64, 0, 64, 64, 0, 64);

      for (int i = 1; i <= 2; ++i)
        for (int j = 1; j <= 4; ++j)
          h_tib_layer_string[i][j] = d.make<TH2D>(TString::Format("tib_side_%i_module_%i_layer_string", i, j), ";layer;string", 8, 0, 8, 64, 0, 64);

      for (int i = 1; i <= 2; ++i)
        for (int j = 1; j <= 8; ++j)
          h_tob_rod_module[i][j] = d.make<TH2D>(TString::Format("tob_side_%i_layer_%i_rod_module", i, j), ";rod;module", 128, 0, 128, 8, 0, 8);

      for (int i = 1; i <= 2; ++i)
        for (int j = 1; j <= 4; ++j)
          h_tid_ring_module[i][j] = d.make<TH2D>(TString::Format("tid_side_%i_wheel_%i_ring_module", i, j), ";ring;module", 4, 0, 4, 32, 0, 32);

      for (int i = 1; i <= 2; ++i)
        for (int j = 1; j <= 16; ++j)
          for (int k = 1; k <= 8; ++k)
            h_tec_petal_module[i][j][k] = d.make<TH2D>(TString::Format("tec_side_%i_wheel_%i_ring_%i_petal_module", i, j, k), ";petal;module", 16, 0, 16, 8, 0, 8);
    }
  }

  bool TrackHistos::Fill(const reco::Track& tk, const reco::BeamSpot* bs, const reco::Vertex* pv) {
    bool ok = true;

    const double dxybs = bs ? tk.dxy(*bs) : -1e99;
    const double pars[9] = {
      tk.p(),
      tk.pt(),
      tk.eta(),
      tk.phi(),
      tk.dxy(),
      tk.dz(),
      dxybs,
      pv ? tk.dxy(pv->position()) : -1e99,
      pv ? tk.dz (pv->position()) : -1e99,
    };
    const double errs[6] = { tk.qoverpError() * tk.p() * tk.p(), tk.ptError(), tk.etaError(), tk.phiError(), tk.dxyError(), tk.dzError() };

    for (int i = 0; i < 9; ++i)
      h_pars[i]->Fill(pars[i]);
    for (int i = 0; i < 6; ++i)
      h_errs[i]->Fill(errs[i]);
    if (do_2d) {
      for (int i = 0; i < 9; ++i)
        for (int j = i+1; j < 9; ++j)
          h_pars_v_pars[i][j]->Fill(pars[i], pars[j]);
      for (int i = 0; i < 9; ++i)
        for (int j = 0; j < 6; ++j)
          h_errs_v_pars[i][j]->Fill(pars[i], errs[j]);
    }

    h_dptopt->Fill(tk.pt() > 0 ? tk.ptError() / tk.pt() : -999);
    h_sigmadxybs->Fill(dxybs / tk.dxyError());

    h_q->Fill(tk.charge());
    h_nhits  ->Fill(tk.hitPattern().numberOfValidHits());
    h_npxhits->Fill(tk.hitPattern().numberOfValidPixelHits());
    h_nsthits->Fill(tk.hitPattern().numberOfValidStripHits());
    h_npxlayers->Fill(tk.hitPattern().pixelLayersWithMeasurement());
    h_nstlayers->Fill(tk.hitPattern().stripLayersWithMeasurement());
    h_nlosthits->Fill(tk.numberOfLostHits());
    h_nlostlayers->Fill(tk.hitPattern().trackerLayersWithoutMeasurement(reco::HitPattern::TRACK_HITS));
    h_chi2->Fill(tk.chi2());
    h_dof->Fill(tk.ndof());
    h_chi2dof->Fill(tk.chi2()/tk.ndof());
    h_algo->Fill(int(tk.algo()));
    for (int i = 0; i < reco::TrackBase::qualitySize; ++i)
      if (tk.quality(reco::Track::TrackQuality(i)))
        h_quality->Fill(i);
    h_highpurity->Fill(tk.quality(reco::TrackBase::highPurity));
    h_nloops->Fill(tk.nLoops());

    if (use_rechits) {
      for (int i = 0, ie = int(tk.recHitsSize()); i < ie; ++i) {
        DetId dd = tk.recHit(i)->geographicalId();
        if (dd.det() == DetId::Tracker) {
          if (dd.subdetId() == (int) PixelSubdetector::PixelBarrel) {
            PXBDetId d(dd);
            h_pxb_ladder_module[d.layer()]->Fill(d.ladder(), d.module());
          }
          else if (dd.subdetId() == (int) PixelSubdetector::PixelEndcap) {
            PXFDetId d(dd);
            h_pxf_panel_module[d.side()][d.disk()][d.panel()]->Fill(d.blade(), d.module());
          }
          else if (dd.subdetId() == StripSubdetector::TIB) {
            TIBDetId d(dd);
            h_tib_layer_string[d.side()][d.module()]->Fill(d.layer(), d.stringNumber());
          }
          else if (dd.subdetId() == StripSubdetector::TOB) {
            TOBDetId d(dd);
            h_tob_rod_module[d.side()][d.layer()]->Fill(d.rodNumber(), d.module());
          }
          else if (dd.subdetId() == StripSubdetector::TID) {
            TIDDetId d(dd);
            h_tid_ring_module[d.side()][d.wheel()]->Fill(d.ring(), d.moduleNumber());
          }
          else if (dd.subdetId() == StripSubdetector::TEC) {
            TECDetId d(dd);
            h_tec_petal_module[d.side()][d.wheel()][d.ring()]->Fill(d.petalNumber(), d.module());
          }
          else {
            ok = false;
            h_unknown_detid->Fill(0);
          }
        }
      }
    }

    return ok;
  }
}