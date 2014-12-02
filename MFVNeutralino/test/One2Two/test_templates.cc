#include "TH1.h"
#include "TFile.h"
#include "TRandom3.h"

#include "Random.h"
#include "ROOTTools.h"

#include "ToyThrower.h"
#include "Templates.h"
#include "ClearedJetsTemplater.h"

int main() {
  jmt::set_root_style();

  for (int seed = 0; seed < 10; ++seed) {
    TFile* out_f = new TFile("test_templates.root", "recreate");
    TRandom3* rand = new TRandom3(jmt::seed_base + seed);
    mfv::ToyThrower* tt = new mfv::ToyThrower("", "trees", out_f, rand);
    mfv::Templater* ter = new mfv::ClearedJetsTemplater("", out_f, rand);

    ter->process(tt->data);

    std::vector<double> a_bkg(6+2,0.);
    mfv::TemplateInterpolator* interp = new mfv::TemplateInterpolator(ter->get_templates(), mfv::Template::binning().size()-1, ter->par_info(), a_bkg);

    mfv::Template* t = interp->get_Q(std::vector<double>({0.032283, 0.010945}));
    //mfv::Template* t = interp->get_Q(std::vector<double>({0.032, 0.011}));

    printf("%4s %12s %12s %12s %12s %12s %12s\n", "ibin", "val", "err", "val*251", "err*251", "norig", "rel err");
    for (int i = 1; i <= 6; ++i) {
      double c = t->h->GetBinContent(i);
      double e = t->h->GetBinError(i);
      printf("%4i %12.6e %12.6e %12.6e %12.6e %12.6e %12.6e\n", i, c, e, c*251, e*251, c*c/e/e, e/c);
    }

    out_f->Write();
    out_f->Close();
    delete out_f;
    delete tt;
    delete ter;
    delete interp;
  }


  /*
  mfv::TemplateInterpolator::extra_prints=1;

  printf("0.029500,0.0455:\n");
  interp->interpolate(0.029500,0.0455);
  for (int i = 1; i <= 6; ++i)
    printf(" %.6f", a_bkg[i]);
  printf("\n");

  printf("0.029500,0.046:\n");
  interp->interpolate(0.029500,0.046);
  for (int i = 1; i <= 6; ++i)
    printf(" %.6f", a_bkg[i]);
  printf("\n");

  printf("0.029500,0.0465\n");
  interp->interpolate(0.029500,0.0465);
  for (int i = 1; i <= 6; ++i)
    printf(" %.6f", a_bkg[i]);
  printf("\n");

  return 1;
  */

  /*
  printf("%i %f %f %i %f %f\n", ter->par_info()[0].nsteps, ter->par_info()[0].start, ter->par_info()[0].step, ter->par_info()[1].nsteps, ter->par_info()[1].start, ter->par_info()[1].step);
  mfv::Templates* ts = ter->get_templates();
  for (mfv::Template* t : *ts) { 
    printf("%.6f %.6f", t->par(0), t->par(1));
    for (int i = 1; i <= 6; ++i)
      printf(" %.6f", t->h->GetBinContent(i));
    printf("\n");
  }

  printf("interp:\n");

  for (int imu = 0; imu < 180; ++imu) {
    double mu = 0 + 0.0005 * imu;
    for (int isig = 0; isig < 100; ++isig) {
      double sig = 0.0005 + 0.0005 * isig;
      interp->interpolate(mu, sig);

      printf("%.6f %.6f", mu, sig);
      for (int i = 1; i <= 6; ++i)
        printf(" %.6f", a_bkg[i]);
      printf("\n");
    }
  }
  */
}
