from JMTucker.Tools.ROOTTools import *
from limitsinput import name2isample
from signal_efficiency import SignalEfficiencyCombiner

set_style()
ps = plot_saver(plot_dir('pretty_dbv_2017p8'), size=(700,700), pdf_log=True)

f = ROOT.TFile('limitsinput.root')
#raise ValueError('propagate change to use stored rate already normalized to int lumi')
combiner = SignalEfficiencyCombiner()

which = [
    ('mfv_neu_tau000300um_M0800', 'c#tau = 0.3 mm', ROOT.kRed,     2), 
    ('mfv_neu_tau001000um_M0800', 'c#tau = 1.0 mm',   ROOT.kGreen+2, 5), 
    ('mfv_neu_tau010000um_M0800', 'c#tau = 10 mm',  ROOT.kBlue,    7), 
    ]

def fmt(z, title, color, style, save=[]):
    if type(z) == str: # signal name
        name = z
        h = f.Get('h_signal_%i_dbv_2017' % name2isample(f, z))
        h2 = f.Get('h_signal_%i_dbv_2018' % name2isample(f, z))
        h.Add(h2)
    else: # background hist
        name = 'bkg'
        h = z

    h.Sumw2()
    h = cm2mm(h)
    h.SetStats(0)
    h.SetLineStyle(style)
    h.SetLineWidth(3 if name == 'bkg' else 4)
    h.SetLineColor(color)
    h.Rebin(1)
    h.SetTitle(';d_{BV} (mm);Events/0.1 mm')
    h.GetXaxis().SetTitleSize(0.05)
    h.GetXaxis().SetLabelSize(0.045)
    h.GetYaxis().SetTitleSize(0.05)
    h.GetYaxis().SetLabelSize(0.045)
    h.GetYaxis().SetTitleOffset(1.15)
    move_above_into_bin(h, 3.999)
    if title != 'bkg':
        h_dbv_2017 = combiner.combine(name2isample(combiner.inputs[0].f, name)).hs_dbv['2017']
        h_dbv_2018 = combiner.combine(name2isample(combiner.inputs[0].f, name)).hs_dbv['2018']
        total_sig_1v = h_dbv_2017.Integral(0,h_dbv_2017.GetNbinsX()+2)
        total_sig_1v += h_dbv_2018.Integral(0,h_dbv_2018.GetNbinsX()+2)
        norm = total_sig_1v * 0.3
        h.Scale(norm/h.Integral(0,h.GetNbinsX()+2))
    save.append(h)
    return h

hbkg = fmt(f.Get('h_bkg_dbv_2017'), 'bkg', ROOT.kBlack, ROOT.kSolid)
hbkg2 = fmt(f.Get('h_bkg_dbv_2018'), 'bkg', ROOT.kBlack, ROOT.kSolid)
hbkg.Add(hbkg2)
hbkg.Rebin(2)
print hbkg.Integral()
hbkg = poisson_intervalize(hbkg, zero_x=True) #, include_zero_bins='surrounded')
hbkg.SetMarkerStyle(20)
hbkg.SetMarkerSize(1.3)
hbkg.SetLineWidth(3)

leg1 = ROOT.TLegend(0.400, 0.810, 0.909, 0.867)
leg1.AddEntry(hbkg, 'Data', 'PE')
leg2 = ROOT.TLegend(0.383, 0.698, 0.893, 0.815)
leg2.AddEntry(0, '#kern[-0.22]{#splitline{Multijet signals,}{m = 800 GeV, #sigma = 0.3 fb:}}', '')
leg3 = ROOT.TLegend(0.400, 0.572, 0.909, 0.705)
legs = leg1, leg2, leg3

for lg in legs:
    lg.SetBorderSize(0)
    lg.SetTextSize(0.04)

for zzz, (name, title, color, style) in enumerate(which):
    h = fmt(name, title, color, style)
    if zzz == 0:
        h.Draw('hist')
    else:
        h.Draw('hist same')
    h.GetXaxis().SetRangeUser(0,4)
    h.GetYaxis().SetRangeUser(6e-2,3e3)
    leg3.AddEntry(h, title, 'L')
    print name, h.Integral(0,h.GetNbinsX()+2)

hbkg.Draw('PE')

for lg in legs:
    lg.Draw()

def write(font, size, x, y, text):
    w = ROOT.TLatex()
    w.SetNDC()
    w.SetTextFont(font)
    w.SetTextSize(size)
    w.DrawLatex(x, y, text)
    return w

write(61, 0.050, 0.175, 0.825, 'CMS')
write(42, 0.050, 0.595, 0.913, '101 fb^{-1} (13 TeV)')

ps.c.SetBottomMargin(0.11)
ps.c.SetLeftMargin(0.13)
ps.c.SetRightMargin(0.06)

ps.save('dbv')

write(52, 0.047, 0.43, 0.82, 'Preliminary')

ps.save('dbv_prelim')
