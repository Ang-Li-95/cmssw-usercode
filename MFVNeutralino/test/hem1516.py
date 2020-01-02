#!/usr/bin/env python

from JMTucker.Tools.ROOTTools import *
from JMTucker.Tools import Samples
from JMTucker.MFVNeutralino.PerSignal import PerSignal

set_style()
ps = plot_saver(plot_dir('hem1516'), size=(600,600), pdf=True, log=False)

multijet = Samples.mfv_signal_samples_2018
dijet = Samples.mfv_stopdbardbar_samples_2018

for presel in 1,0:
    for gen in 0,1:
        if presel and gen:
            continue
        print 'presel %i gen %i' % (presel, gen)
        for svdist in 0., 0.04, 0.07:
            print 'svdist %.02f' % svdist
            PerSignal.clear_samples(multijet + dijet)
            for sample in multijet + dijet:
                path = '/uscms_data/d2/tucker/crab_dirs/MiniTreeV27m'
                if not presel:
                    path += '_NoPresel'
                fn = os.path.join(path, sample.name + '.root')
                if not os.path.exists(fn):
                    print 'no', fn
                    continue

                f = ROOT.TFile(fn)
                t = f.Get('mfvMiniTree/t')
                hr = draw_hist_register(t, True)
                def n(cut):
                    return get_integral(hr.draw('weight', cut, binning='1,0,1', goff=True))[0]

                if gen:
                    t.SetAlias('gen_is_jet', 'abs(gen_daughter_id) >= 1 && abs(gen_daughter_id) <= 5 && abs(gen_daughters.Eta()) < 2.5')
                    t.SetAlias('jet_hem1516', 'gen_is_jet && gen_daughters.Eta() < -1.3 && gen_daughters.Phi() < -0.87 && gen_daughters.Phi() > -1.57')
                    t.SetAlias('njets_hem1516', 'Sum$(gen_is_jet && !jet_hem1516)')
                    t.SetAlias('jetht_hem1516', 'Sum$(gen_daughters.Pt() * (gen_daughters.Pt() > 40 && gen_is_jet && !jet_hem1516))')
                    t.SetAlias('njets_all', 'Sum$(!!gen_is_jet)') # !! is because ROOT is very stupid and I hate it
                    t.SetAlias('jetht_all', 'Sum$(gen_daughters.Pt() * (gen_is_jet && gen_daughters.Pt() > 40))')
                else:
                    t.SetAlias('jet_hem1516', 'jet_eta < -1.3 && jet_phi < -0.87 && jet_phi > -1.57')
                    t.SetAlias('njets_hem1516', 'Sum$(!jet_hem1516)')
                    t.SetAlias('jetht_hem1516', 'Sum$(jet_pt * (jet_pt > 40 && !jet_hem1516))')
                    t.SetAlias('njets_all', 'njets')
                    t.SetAlias('jetht_all', 'jetht')

                base = 'nvtx>=2 && svdist > %f' % svdist
                if not presel:
                    base += ' && njets_all >= 4 && jetht_all >= 1200'
                den = n(base)
                num = n(base + ' && njets_hem1516 >= 4 && jetht_hem1516 >= 1200')
                sample.y, sample.yl, sample.yh = clopper_pearson(num, den)
                print '%26s: num = %.1f den = %.1f ratio = %.3f (%.3f, %.3f)' % (sample.name, num, den, sample.y, sample.yl, sample.yh)

            per = PerSignal('hem1516%s/nominal' % (' (gen)' if gen else ''), y_range=(0.8,1.01), decay_paves_at_top=False)
            per.add(multijet, title='#tilde{N} #rightarrow tbs')
            per.add(dijet, title='#tilde{t} #rightarrow #bar{d}#bar{d}', color=ROOT.kBlue)
            per.draw(canvas=ps.c)
            ps.save('sigeff_svdist%.2f_presel%i_gen%i' % (svdist, presel, gen))
