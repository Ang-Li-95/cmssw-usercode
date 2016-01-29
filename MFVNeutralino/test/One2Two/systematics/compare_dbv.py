#!/usr/bin/env python

from JMTucker.Tools.ROOTTools import *
import JMTucker.Tools.Samples as Samples
import JMTucker.MFVNeutralino.AnalysisConstants as ac

set_style()
ps = plot_saver('plots/bkgest/MinitreeV6/dbv', root=False)
trees = '~/crabdirs/MinitreeV6'

def book_dbv(n):
    return ROOT.TH1F(n, '', 20, 0, 0.1)

sc = ac.int_lumi * ac.scale_factor

h_dbv_sum = book_dbv('dbv_sum')
h_dbv_nob = book_dbv('dbv_nob')
h_dbv_b = book_dbv('dbv_b')
h_dbv_qcdb = book_dbv('dbv_qcdb')

hs_nob = []
for sn in 'qcdht0500 qcdht0700 qcdht1000 qcdht1500 qcdht2000 ttbar'.split():
    f = ROOT.TFile('%s/%s.root' % (trees,sn))
    t = f.Get('mfvMiniTree/t')
    s = getattr(Samples, sn)

    n = sn + ', no b quarks'
    h_dbv = book_dbv(n)
    t.Draw('dist0>>%s' % n, 'nvtx == 1 && gen_flavor_code != 2')
    h_dbv_sum.Add(h_dbv, sc * s.partial_weight_orig)
    h_dbv_nob.Add(h_dbv, sc * s.partial_weight_orig)
    ps.save(n)

    h = h_dbv.Clone()
    h.SetDirectory(0)
    hs_nob.append(h)

hs_b = []
for sn in 'qcdht0500 qcdht0700 qcdht1000 qcdht1500 qcdht2000 ttbar'.split():
    f = ROOT.TFile('%s/%s.root' % (trees,sn))
    t = f.Get('mfvMiniTree/t')
    s = getattr(Samples, sn)

    if sn != 'ttbar':
        n = sn + ', b quarks'
    else:
        n = sn
    h_dbv = book_dbv(n)
    t.Draw('dist0>>%s' % n, 'nvtx == 1 && gen_flavor_code == 2')
    h_dbv_sum.Add(h_dbv, sc * s.partial_weight_orig)
    h_dbv_b.Add(h_dbv, sc * s.partial_weight_orig)
    if sn != 'ttbar':
        h_dbv_qcdb.Add(h_dbv, sc * s.partial_weight_orig)
    ps.save(n)

    h = h_dbv.Clone()
    h.SetDirectory(0)
    hs_b.append(h)

h_dbv_sum.Draw()
ps.save('dbv_sum')


h_dbv_sum.SetTitle('only-one-vertex events;d_{BV} (cm);arb. units')
h_dbv_sum.SetStats(0)
h_dbv_sum.SetLineColor(ROOT.kBlack)
h_dbv_sum.SetLineWidth(3)
h_dbv_sum.Scale(1./h_dbv_sum.Integral())
h_dbv_sum.SetMaximum(1)
h_dbv_sum.Draw()

l = ROOT.TLegend(0.3,0.6,0.9,0.9)
l.AddEntry(h_dbv_sum, 'total background: mean d_{BV} = %4.1f +/- %2.1f #mum' % (10000*h_dbv_sum.GetMean(), 10000*h_dbv_sum.GetRMS()/h_dbv_sum.GetEntries()**0.5))

for i,h in enumerate(hs_nob):
    h.SetStats(0)
    h.SetLineColor(ROOT.kBlue + i)
    h.SetLineWidth(3)
    if h.GetEntries() != 0:
        h.DrawNormalized('sames')
        l.AddEntry(h, '%s: mean d_{BV} = %4.1f +/- %2.1f #mum' % (h.GetName(), 10000*h.GetMean(), 10000*h.GetRMS()/h.GetEntries()**0.5))

for i,h in enumerate(hs_b):
    h.SetStats(0)
    h.SetLineColor(ROOT.kPink + i)
    h.SetLineWidth(3)
    if h.GetEntries() != 0:
        h.DrawNormalized('sames')
        l.AddEntry(h, '%s: mean d_{BV} = %4.1f +/- %2.1f #mum' % (h.GetName(), 10000*h.GetMean(), 10000*h.GetRMS()/h.GetEntries()**0.5))

l.SetFillColor(0)
l.Draw()
ps.save('dbv')


h_dbv_sum.Draw()
l = ROOT.TLegend(0.3,0.78,0.9,0.9)
l.AddEntry(h_dbv_sum, 'total background: mean d_{BV} = %4.1f +/- %2.1f #mum' % (10000*h_dbv_sum.GetMean(), 10000*h_dbv_sum.GetRMS()/h_dbv_sum.GetEntries()**0.5))
h_dbv_nob.SetStats(0)
h_dbv_nob.SetLineColor(ROOT.kBlue)
h_dbv_nob.SetLineWidth(3)
h_dbv_nob.DrawNormalized('sames')
l.AddEntry(h_dbv_nob, 'qcd, no b quarks: mean d_{BV} = %4.1f +/- %2.1f #mum' % (10000*h_dbv_nob.GetMean(), 10000*h_dbv_nob.GetRMS()/h_dbv_nob.GetEntries()**0.5))
h_dbv_qcdb.SetStats(0)
h_dbv_qcdb.SetLineColor(ROOT.kPink)
h_dbv_qcdb.SetLineWidth(3)
h_dbv_qcdb.DrawNormalized('sames')
l.AddEntry(h_dbv_qcdb, 'qcd, b quarks: mean d_{BV} = %4.1f +/- %2.1f #mum' % (10000*h_dbv_qcdb.GetMean(), 10000*h_dbv_qcdb.GetRMS()/h_dbv_qcdb.GetEntries()**0.5))
hs_b[5].DrawNormalized('sames')
l.AddEntry(hs_b[5], 'ttbar: mean d_{BV} = %4.1f +/- %2.1f #mum' % (10000*hs_b[5].GetMean(), 10000*hs_b[5].GetRMS()/hs_b[5].GetEntries()**0.5))
l.SetFillColor(0)
l.Draw()
ps.save('dbv_qcdb')


h_dbv_sum.Draw()
l = ROOT.TLegend(0.3,0.81,0.9,0.9)
l.AddEntry(h_dbv_sum, 'total background: mean d_{BV} = %4.1f +/- %2.1f #mum' % (10000*h_dbv_sum.GetMean(), 10000*h_dbv_sum.GetRMS()/h_dbv_sum.GetEntries()**0.5))
h_dbv_nob.SetStats(0)
h_dbv_nob.SetLineColor(ROOT.kBlue)
h_dbv_nob.SetLineWidth(3)
h_dbv_nob.DrawNormalized('sames')
l.AddEntry(h_dbv_nob, 'background, no b quarks: mean d_{BV} = %4.1f +/- %2.1f #mum' % (10000*h_dbv_nob.GetMean(), 10000*h_dbv_nob.GetRMS()/h_dbv_nob.GetEntries()**0.5))
h_dbv_b.SetStats(0)
h_dbv_b.SetLineColor(ROOT.kPink)
h_dbv_b.SetLineWidth(3)
h_dbv_b.DrawNormalized('sames')
l.AddEntry(h_dbv_b, 'background, b quarks: mean d_{BV} = %4.1f +/- %2.1f #mum' % (10000*h_dbv_b.GetMean(), 10000*h_dbv_b.GetRMS()/h_dbv_b.GetEntries()**0.5))
l.SetFillColor(0)
l.Draw()
ps.save('dbv_b')
