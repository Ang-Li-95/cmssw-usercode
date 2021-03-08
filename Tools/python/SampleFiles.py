import os, base64, zlib, cPickle as pickle
from collections import defaultdict
from fnmatch import fnmatch
from itertools import chain
from pprint import pprint
from JMTucker.Tools.CRAB3ToolsBase import decrabify_list
from JMTucker.Tools.CMSSWTools import cmssw_base

_d = {}
_added_from_enc = {}

def _enc(d):
    return base64.b64encode(zlib.compress(pickle.dumps(d)))

def _denc(encd):
    return pickle.loads(zlib.decompress(base64.b64decode(encd)))

def _add(d, allow_overwrite=False, _enced_call=[0]):
    global _d
    enced = type(d) == str
    if enced:
        d = _denc(d)
        _enced_call[0] += 1
    if not allow_overwrite:
        for k in d:
            if _d.has_key(k):
                raise ValueError('already have key %s' % repr(k))
            if len(d[k][1]) != d[k][0]:
                raise ValueError('length check problem: %s %s supposed to be %i but is %i' % (k[0], k[1], d[k][0], len(d[k][1])))
    _d.update(d)
    if enced:
        for k in d.keys():
            _added_from_enc[k] = _enced_call[0]

def _remove_file(sample, ds, fn):
    n, fns = _d[(sample,ds)]
    fns.remove(fn)
    _d[(sample,ds)] = (n-1, fns)

def _replace_file(sample, ds, fn, fn2):
    n, fns = _d[(sample,ds)]
    fns.remove(fn)
    fns.append(fn2)
    _d[(sample,ds)] = (n, fns)

def _add_ds(ds, d, allow_overwrite=False):
    d2 = {}
    for k in d:
        d2[(k,ds)] = d[k]
    _add(d2, allow_overwrite)

def _add_single_files(ds, path, l, allow_overwrite=False):
    d = {}
    for sample in l:
        d[(sample,ds)] = (1, [os.path.join(path, sample + '.root')])
    _add(d, allow_overwrite)

def _fromnumlist(path, numlist, but=[], fnbase='ntuple', add=[], numbereddirs=True):
    return add + [path + ('/%04i' % (i/1000) if numbereddirs else '') + '/%s_%i.root' % (fnbase, i) for i in numlist if i not in but]

def _fromnum1(path, n, but=[], fnbase='ntuple', add=[], numbereddirs=True): # crab starts job numbering at 1
    l = _fromnumlist(path, xrange(1,n+1), but, fnbase, add, numbereddirs)
    return (len(l), l)

def _fromnum0(path, n, but=[], fnbase='ntuple', add=[], numbereddirs=True): # condorsubmitter starts at 0
    l = _fromnumlist(path, xrange(n), but, fnbase, add, numbereddirs)
    return (len(l), l)

def _frommerge(path, n):
    assert path.endswith('/merge') and path.count('/merge') == 1
    return (n, [path.replace('/merge', '/merge%s_0.root') % s for s in [''] + ['%03i' % x for x in xrange(1,n)]])

def _join(*l):
    ns, ls = zip(*l)
    return (sum(ns), sum(ls, []))

def keys():
    return _d.keys()

def dump():
    pprint(_d)

def allfiles():
    return (fn for (sample, ds), (n, fns) in _d.iteritems() for fn in fns)

def summary():
    d = defaultdict(list)
    for k in _d.iterkeys():
        a,b = k
        d[a].append((b, _d[k][0]))
    for a in sorted(d.keys()):
        for b,n in d[a]:
            print a.ljust(40), b.ljust(20), '%5i' % n

def has(name, ds):
    return _d.has_key((name, ds))

def get(name, ds):
    return _d.get((name, ds), None)

def get_fns(name, ds):
    return _d[(name,ds)][1]

def get_local_fns(name, ds, num=-1):
    #print(_d.keys())
    fns = _d[(name, ds)][1]
    if num > 0:
        fns = fns[:num]
    return [('root://cmseos.fnal.gov/' + fn) if fn.startswith('/store/user') else fn for fn in fns]

def set_process(process, name, ds, num=-1):
    process.source.fileNames = get_local_fns(name, ds, num)

def who(name, ds):
    nfns, fns = _d[(name,ds)]
    users = set()
    for fn in fns:
        assert fn.startswith('/store')
        if fn.startswith('/store/user'):
            users.add(fn.split('/')[3])
    return tuple(sorted(users))

__all__ = [
    'dump',
    'get',
    'summary',
    ]

################################################################################

execfile(cmssw_base('src/JMTucker/Tools/python/enc_SampleFiles.py'))

_removed = [
    ('ttbarht0800_2017', 'miniaod', ['/store/mc/RunIIFall17MiniAODv2/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/40000/225CD078-B3A4-E811-AA74-001E67DDC254.root',
                                     '/store/mc/RunIIFall17MiniAODv2/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/60000/BC22A92A-7BBA-E811-8A2B-0242AC1C0501.root',]),
    ]

for name, ds, fns in _removed:
    for fn in fns:
        _remove_file(name, ds, fn)

################################################################################

_add_ds("nr_trackingtreerv23mv3", {
'qcdht0700_2017': (48, ['/store/user/wsun/croncopyeos/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/TrackingTreerV23mv3_2017/190329_154545/0000/trackingtreer_%i.root' % i for i in [25, 46]] + ['/store/user/wsun/croncopyeos/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/TrackingTreerV23mv3_2017/190329_150253/0000/trackingtreer_%i.root' % i for i in chain(xrange(22), xrange(23,25), xrange(26,46), [47])] + ['/store/user/wsun/croncopyeos/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/TrackingTreerV23mv3_2017/190401_120003/0000/trackingtreer_22.root']),
'qcdht1000_2017': _fromnum1("/store/user/wsun/croncopyeos/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/TrackingTreerV23mv3_2017/190329_200142", 22, fnbase="trackingtreer"),
'qcdht1500_2017': (11, ['/store/user/wsun/croncopyeos/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/TrackingTreerV23mv3_2017/190329_150254/0000/trackingtreer_%i.root' % i for i in chain(xrange(7), xrange(13,16), [11])]),
'qcdht2000_2017': _fromnum0("/store/user/wsun/croncopyeos/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/TrackingTreerV23mv3_2017/190329_150255", 10, fnbase="trackingtreer"),
'qcdht0700_2018': (72, ['/store/user/wsun/croncopyeos/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/TrackingTreerV23mv3_2018/190329_153344/0000/trackingtreer_%i.root' % i for i in chain(xrange(3), xrange(4,72))] + ['/store/user/wsun/croncopyeos/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/TrackingTreerV23mv3_2018/190329_154546/0000/trackingtreer_3.root']),
'qcdht1000_2018': (26, ['/store/user/wsun/croncopyeos/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/TrackingTreerV23mv3_2018/190402_070940/0000/trackingtreer_%i.root' % i for i in [2, 13]] + ['/store/user/wsun/croncopyeos/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/TrackingTreerV23mv3_2018/190329_153345/0000/trackingtreer_%i.root' % i for i in chain(xrange(2), xrange(3,13), xrange(14,16), xrange(17,22), xrange(23,26))] + ['/store/user/wsun/croncopyeos/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/TrackingTreerV23mv3_2018/190401_120016/0000/trackingtreer_%i.root' % i for i in [16, 22]]),
'qcdht1500_2018': (1, ['/store/user/wsun/croncopyeos/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/TrackingTreerV23mv3_2018/190329_203300/0000/trackingtreer_18.root']),
'qcdht2000_2018': (9, ['/store/user/wsun/croncopyeos/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/TrackingTreerV23mv3_2018/190401_120017/0000/trackingtreer_0.root'] + ['/store/user/wsun/croncopyeos/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/TrackingTreerV23mv3_2018/190329_153346/0000/trackingtreer_%i.root' % i for i in chain(xrange(1,4), xrange(7,11), [5])]),
'JetHT2017B': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2017/190329_200156", 12, fnbase="trackingtreer"),
'JetHT2017C': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2017/190329_200207", 26, fnbase="trackingtreer"),
'JetHT2017D': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2017/190329_200224", 12, fnbase="trackingtreer"),
'JetHT2017E': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2017/190329_200239", 22, fnbase="trackingtreer"),
'JetHT2017F': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2017/190329_200252", 29, fnbase="trackingtreer"),
'JetHT2018A': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2018/190329_203312", 30, fnbase="trackingtreer"),
'JetHT2018B': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2018/190329_203322", 24, fnbase="trackingtreer"),
'JetHT2018C': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2018/190329_203332", 14, fnbase="trackingtreer"),
'JetHT2018D': _fromnum1("/store/user/wsun/croncopyeos/JetHT/TrackingTreerV23mv3_2018/190329_203343", 64, fnbase="trackingtreer"),
})


_add_ds("ntuplev27m_norescaling", {
'mfv_neu_tau000100um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142025/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142025/0000/merge001_0.root']),
'mfv_neu_tau000100um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142026/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142026/0000/merge001_0.root']),
'mfv_neu_tau000100um_M0800_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142027/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142027/0000/merge001_0.root']),
'mfv_neu_tau000100um_M1200_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142028/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142028/0000/merge001_0.root']),
'mfv_neu_tau000100um_M1600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142029/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142029/0000/merge001_0.root']),
'mfv_neu_tau000100um_M3000_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142030/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142030/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142031/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142031/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142032/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142032/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0800_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142033/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142033/0000/merge001_0.root']),
'mfv_neu_tau000300um_M1200_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142034/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142034/0000/merge001_0.root']),
'mfv_neu_tau000300um_M1600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142035/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142035/0000/merge001_0.root']),
'mfv_neu_tau000300um_M3000_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142036/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142036/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142036/0000/merge002_0.root']),
'mfv_neu_tau001000um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142037/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142037/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142038/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142038/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0800_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142039/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142039/0000/merge001_0.root']),
'mfv_neu_tau001000um_M1200_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142040/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142040/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142040/0000/merge002_0.root']),
'mfv_neu_tau001000um_M1600_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142041/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142041/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142041/0000/merge002_0.root']),
'mfv_neu_tau001000um_M3000_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142042/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142042/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142042/0000/merge002_0.root']),
'mfv_neu_tau010000um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142043/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142043/0000/merge001_0.root']),
'mfv_neu_tau010000um_M0600_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142044/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142044/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142044/0000/merge002_0.root']),
'mfv_neu_tau010000um_M0800_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142045/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142045/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142045/0000/merge002_0.root']),
'mfv_neu_tau010000um_M1200_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142046/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142046/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142046/0000/merge002_0.root']),
'mfv_neu_tau010000um_M1600_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142047/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142047/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142047/0000/merge002_0.root']),
'mfv_neu_tau010000um_M3000_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142048/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142048/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142048/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142048/0000/merge003_0.root']),
'mfv_neu_tau030000um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142049/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142049/0000/merge001_0.root']),
'mfv_neu_tau030000um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142050/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142050/0000/merge001_0.root']),
'mfv_neu_tau030000um_M0800_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142051/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142051/0000/merge001_0.root']),
'mfv_neu_tau030000um_M1200_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142052/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142052/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142052/0000/merge002_0.root']),
'mfv_neu_tau030000um_M1600_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142053/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142053/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142053/0000/merge002_0.root']),
'mfv_neu_tau030000um_M3000_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142054/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142054/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142054/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M0400_2017': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142055/0000/merge_0.root']),
'mfv_stopdbardbar_tau000100um_M0600_2017': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142056/0000/merge_0.root']),
'mfv_stopdbardbar_tau000100um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142057/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142057/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M1200_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142058/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142058/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M1600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142059/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142059/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M3000_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142100/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142100/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0400_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142101/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142101/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142102/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142102/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142103/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142103/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M1200_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142104/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142104/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M1600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142105/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142105/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M3000_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142106/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142106/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142106/0000/merge002_0.root']),
'mfv_stopdbardbar_tau001000um_M0400_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142107/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142107/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142108/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142108/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142109/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142109/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M1200_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142110/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142110/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M1600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142111/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142111/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142111/0000/merge002_0.root']),
'mfv_stopdbardbar_tau001000um_M3000_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142112/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142112/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142112/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M0400_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142113/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142113/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M0600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142114/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142114/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142115/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142115/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M1200_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142116/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142116/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142116/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M1600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142117/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142117/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142117/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M3000_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142118/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142118/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142118/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M0400_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142119/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142119/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M0600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142120/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142120/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142121/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142121/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M1200_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142122/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142122/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M1600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142123/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142123/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M3000_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142124/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142124/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_norescaling_2017/200614_142124/0000/merge002_0.root']),
'mfv_neu_tau000100um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141715/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141715/0000/merge001_0.root']),
'mfv_neu_tau000100um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141716/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141716/0000/merge001_0.root']),
'mfv_neu_tau000100um_M0800_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141717/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141717/0000/merge001_0.root']),
'mfv_neu_tau000100um_M1200_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141718/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141718/0000/merge001_0.root']),
'mfv_neu_tau000100um_M1600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141719/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141719/0000/merge001_0.root']),
'mfv_neu_tau000100um_M3000_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141720/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141720/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141721/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141721/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141722/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141722/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0800_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141723/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141723/0000/merge001_0.root']),
'mfv_neu_tau000300um_M1200_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141724/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141724/0000/merge001_0.root']),
'mfv_neu_tau000300um_M1600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141725/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141725/0000/merge001_0.root']),
'mfv_neu_tau000300um_M3000_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141726/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141726/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141726/0000/merge002_0.root']),
'mfv_neu_tau001000um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141727/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141727/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141728/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141728/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0800_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141729/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141729/0000/merge001_0.root']),
'mfv_neu_tau001000um_M1200_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141730/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141730/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141730/0000/merge002_0.root']),
'mfv_neu_tau001000um_M1600_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141731/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141731/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141731/0000/merge002_0.root']),
'mfv_neu_tau001000um_M3000_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141732/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141732/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141732/0000/merge002_0.root']),
'mfv_neu_tau010000um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141733/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141733/0000/merge001_0.root']),
'mfv_neu_tau010000um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141734/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141734/0000/merge001_0.root']),
'mfv_neu_tau010000um_M0800_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141735/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141735/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141735/0000/merge002_0.root']),
'mfv_neu_tau010000um_M1200_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141736/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141736/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141736/0000/merge002_0.root']),
'mfv_neu_tau010000um_M1600_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141737/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141737/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141737/0000/merge002_0.root']),
'mfv_neu_tau010000um_M3000_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141738/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141738/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141738/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141738/0000/merge003_0.root']),
'mfv_neu_tau030000um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141739/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141739/0000/merge001_0.root']),
'mfv_neu_tau030000um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141740/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141740/0000/merge001_0.root']),
'mfv_neu_tau030000um_M0800_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141741/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141741/0000/merge001_0.root']),
'mfv_neu_tau030000um_M1200_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141742/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141742/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141742/0000/merge002_0.root']),
'mfv_neu_tau030000um_M1600_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141743/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141743/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141743/0000/merge002_0.root']),
'mfv_neu_tau030000um_M3000_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141744/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141744/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141744/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M0400_2018': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141745/0000/merge_0.root']),
'mfv_stopdbardbar_tau000100um_M0600_2018': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141746/0000/merge_0.root']),
'mfv_stopdbardbar_tau000100um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141747/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141747/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141748/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141748/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M1600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141749/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141749/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M3000_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141750/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141750/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0400_2018': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141751/0000/merge_0.root']),
'mfv_stopdbardbar_tau000300um_M0600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141752/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141752/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141753/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141753/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141754/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141754/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M1600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141755/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141755/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M3000_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141756/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141756/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0400_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141757/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141757/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141758/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141758/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141759/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141759/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141800/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141800/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M1600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141801/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141801/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M3000_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141802/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141802/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141802/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M0400_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141803/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141803/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M0600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141804/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141804/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141805/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141805/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M1200_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141806/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141806/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141806/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M1600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141807/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141807/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141807/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M3000_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141808/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141808/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141808/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M0400_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141809/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141809/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M0600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141810/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141810/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141811/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141811/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141812/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141812/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M1600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141813/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141813/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M3000_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141814/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141814/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_norescaling_2018/200614_141814/0000/merge002_0.root']),
})


_add_ds("ntuplev27m_wgen", {
'mfv_neu_tau000100um_M0400_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135609/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135609/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135609/0000/merge002_0.root']),
'mfv_neu_tau000100um_M0600_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135610/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135610/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135610/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135610/0000/merge003_0.root']),
'mfv_neu_tau000100um_M0800_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135610/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135610/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135610/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135610/0000/merge003_0.root']),
'mfv_neu_tau000100um_M1200_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103420/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103420/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103420/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103420/0000/merge003_0.root']),
'mfv_neu_tau000100um_M1600_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103421/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103421/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103421/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103421/0000/merge003_0.root']),
'mfv_neu_tau000100um_M3000_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135611/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135611/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135611/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135611/0000/merge003_0.root']),
'mfv_neu_tau000300um_M0400_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103423/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103423/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103423/0000/merge002_0.root']),
'mfv_neu_tau000300um_M0600_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135612/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135612/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135612/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135612/0000/merge003_0.root']),
'mfv_neu_tau000300um_M0800_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135613/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135613/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135613/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135613/0000/merge003_0.root']),
'mfv_neu_tau000300um_M1200_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135614/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135614/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135614/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135614/0000/merge003_0.root']),
'mfv_neu_tau000300um_M1600_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135614/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135614/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135614/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135614/0000/merge003_0.root']),
'mfv_neu_tau000300um_M3000_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103428/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103428/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103428/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103428/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103428/0000/merge004_0.root']),
'mfv_neu_tau001000um_M0400_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103429/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103429/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103429/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103429/0000/merge003_0.root']),
'mfv_neu_tau001000um_M0600_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103430/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103430/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103430/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103430/0000/merge003_0.root']),
'mfv_neu_tau001000um_M0800_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135616/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135616/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135616/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135616/0000/merge003_0.root']),
'mfv_neu_tau001000um_M1200_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103432/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103432/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103432/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103432/0000/merge003_0.root']),
'mfv_neu_tau001000um_M1600_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103433/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103433/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103433/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103433/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103433/0000/merge004_0.root']),
'mfv_neu_tau001000um_M3000_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103434/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103434/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103434/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103434/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103434/0000/merge004_0.root']),
'mfv_neu_tau010000um_M0400_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135616/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135616/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135616/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135616/0000/merge003_0.root']),
'mfv_neu_tau010000um_M0600_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135617/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135617/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135617/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135617/0000/merge003_0.root']),
'mfv_neu_tau010000um_M0800_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103437/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103437/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103437/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103437/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103437/0000/merge004_0.root']),
'mfv_neu_tau010000um_M1200_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135618/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135618/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135618/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135618/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135618/0000/merge004_0.root']),
'mfv_neu_tau010000um_M1600_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103439/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103439/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103439/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103439/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103439/0000/merge004_0.root']),
'mfv_neu_tau010000um_M3000_2017': (6, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101048/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101048/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101048/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101048/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101048/0000/merge004_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101048/0000/merge005_0.root']),
'mfv_neu_tau030000um_M0400_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135619/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135619/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135619/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135619/0000/merge003_0.root']),
'mfv_neu_tau030000um_M0600_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103441/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103441/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103441/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103441/0000/merge003_0.root']),
'mfv_neu_tau030000um_M0800_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103442/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103442/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103442/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103442/0000/merge003_0.root']),
'mfv_neu_tau030000um_M1200_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135620/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135620/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135620/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135620/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135620/0000/merge004_0.root']),
'mfv_neu_tau030000um_M1600_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103444/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103444/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103444/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103444/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103444/0000/merge004_0.root']),
'mfv_neu_tau030000um_M3000_2017': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101054/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101054/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101054/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101054/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101054/0000/merge004_0.root']),
'mfv_stopdbardbar_tau000100um_M0400_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135621/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135621/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135621/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M0600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135622/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135622/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135622/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M0800_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135623/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135623/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135623/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M1200_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135624/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135624/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135624/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M1600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135625/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135625/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135625/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M3000_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103450/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103450/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103450/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103450/0000/merge003_0.root']),
'mfv_stopdbardbar_tau000300um_M0400_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135626/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135626/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135626/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M0600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103452/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103452/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103452/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M0800_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135627/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135627/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135627/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M1200_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103454/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103454/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103454/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M1600_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135627/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135627/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135627/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135627/0000/merge003_0.root']),
'mfv_stopdbardbar_tau000300um_M3000_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103456/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103456/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103456/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103456/0000/merge003_0.root']),
'mfv_stopdbardbar_tau001000um_M0400_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135628/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135628/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135628/0000/merge002_0.root']),
'mfv_stopdbardbar_tau001000um_M0600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135629/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135629/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135629/0000/merge002_0.root']),
'mfv_stopdbardbar_tau001000um_M0800_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103459/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103459/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103459/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103459/0000/merge003_0.root']),
'mfv_stopdbardbar_tau001000um_M1200_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103500/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103500/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103500/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103500/0000/merge003_0.root']),
'mfv_stopdbardbar_tau001000um_M1600_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135630/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135630/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135630/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135630/0000/merge003_0.root']),
'mfv_stopdbardbar_tau001000um_M3000_2017': (5, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101112/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101112/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101112/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101112/0000/merge003_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101112/0000/merge004_0.root']),
'mfv_stopdbardbar_tau010000um_M0400_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103502/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103502/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103502/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M0600_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135631/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135631/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135631/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135631/0000/merge003_0.root']),
'mfv_stopdbardbar_tau010000um_M0800_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135632/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135632/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135632/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135632/0000/merge003_0.root']),
'mfv_stopdbardbar_tau010000um_M1200_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135633/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135633/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135633/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135633/0000/merge003_0.root']),
'mfv_stopdbardbar_tau010000um_M1600_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103506/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103506/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103506/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103506/0000/merge003_0.root']),
'mfv_stopdbardbar_tau010000um_M3000_2017': (5, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101118/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101118/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101118/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101118/0000/merge003_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200420_101118/0000/merge004_0.root']),
'mfv_stopdbardbar_tau030000um_M0400_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103507/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103507/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103507/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M0600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135634/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135634/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135634/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M0800_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103509/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103509/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103509/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103509/0000/merge003_0.root']),
'mfv_stopdbardbar_tau030000um_M1200_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103510/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103510/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103510/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103510/0000/merge003_0.root']),
'mfv_stopdbardbar_tau030000um_M1600_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135635/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135635/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135635/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_135635/0000/merge003_0.root']),
'mfv_stopdbardbar_tau030000um_M3000_2017': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103512/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103512/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103512/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_WGen_2017/200417_103512/0000/merge003_0.root']),
'mfv_neu_tau000100um_M0400_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114244/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114244/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114244/0000/merge002_0.root']),
'mfv_neu_tau000100um_M0600_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114245/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114245/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114245/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114245/0000/merge003_0.root']),
'mfv_neu_tau000100um_M0800_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180319/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180319/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180319/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180319/0000/merge003_0.root']),
'mfv_neu_tau000100um_M1200_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180320/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180320/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180320/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180320/0000/merge003_0.root']),
'mfv_neu_tau000100um_M1600_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180321/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180321/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180321/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180321/0000/merge003_0.root']),
'mfv_neu_tau000100um_M3000_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180322/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180322/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180322/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180322/0000/merge003_0.root']),
'mfv_neu_tau000300um_M0400_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114246/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114246/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114246/0000/merge002_0.root']),
'mfv_neu_tau000300um_M0600_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180323/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180323/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180323/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180323/0000/merge003_0.root']),
'mfv_neu_tau000300um_M0800_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114247/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114247/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114247/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114247/0000/merge003_0.root']),
'mfv_neu_tau000300um_M1200_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180324/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180324/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180324/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180324/0000/merge003_0.root']),
'mfv_neu_tau000300um_M1600_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180325/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180325/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180325/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180325/0000/merge003_0.root']),
'mfv_neu_tau000300um_M3000_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180326/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180326/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180326/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180326/0000/merge003_0.root']),
'mfv_neu_tau001000um_M0400_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180327/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180327/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180327/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180327/0000/merge003_0.root']),
'mfv_neu_tau001000um_M0600_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180328/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180328/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180328/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180328/0000/merge003_0.root']),
'mfv_neu_tau001000um_M0800_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180329/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180329/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180329/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180329/0000/merge003_0.root']),
'mfv_neu_tau001000um_M1200_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180330/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180330/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180330/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180330/0000/merge003_0.root']),
'mfv_neu_tau001000um_M3000_2018': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114248/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114248/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114248/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114248/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114248/0000/merge004_0.root']),
'mfv_neu_tau010000um_M0400_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114249/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114249/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114249/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114249/0000/merge003_0.root']),
'mfv_neu_tau010000um_M0600_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114250/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114250/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114250/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114250/0000/merge003_0.root']),
'mfv_neu_tau010000um_M0800_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180331/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180331/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180331/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180331/0000/merge003_0.root']),
'mfv_neu_tau010000um_M1200_2018': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114251/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114251/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114251/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114251/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114251/0000/merge004_0.root']),
'mfv_neu_tau010000um_M1600_2018': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180332/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180332/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180332/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180332/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180332/0000/merge004_0.root']),
'mfv_neu_tau010000um_M3000_2018': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132553/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132553/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132553/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132553/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132553/0000/merge004_0.root']),
'mfv_neu_tau030000um_M0400_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114252/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114252/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114252/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114252/0000/merge003_0.root']),
'mfv_neu_tau030000um_M0600_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114253/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114253/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114253/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114253/0000/merge003_0.root']),
'mfv_neu_tau030000um_M0800_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114254/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114254/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114254/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114254/0000/merge003_0.root']),
'mfv_neu_tau030000um_M1200_2018': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114255/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114255/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114255/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114255/0000/merge003_0.root']),
'mfv_neu_tau030000um_M1600_2018': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114256/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114256/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114256/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114256/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114256/0000/merge004_0.root']),
'mfv_neu_tau030000um_M3000_2018': (5, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114257/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114257/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114257/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114257/0000/merge003_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114257/0000/merge004_0.root']),
'mfv_stopdbardbar_tau000100um_M0400_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114258/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114258/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114258/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M0600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114259/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114259/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114259/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M0800_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114300/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114300/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114300/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M1200_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114301/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114301/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114301/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M1600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180333/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180333/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180333/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M3000_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180334/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180334/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180334/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180334/0000/merge003_0.root']),
'mfv_stopdbardbar_tau000300um_M0400_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180335/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180335/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180335/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M0600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180336/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180336/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180336/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M0800_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114302/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114302/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114302/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M1200_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114303/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114303/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114303/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M1600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180337/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180337/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180337/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000300um_M3000_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180338/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180338/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180338/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180338/0000/merge003_0.root']),
'mfv_stopdbardbar_tau001000um_M0400_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114304/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114304/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114304/0000/merge002_0.root']),
'mfv_stopdbardbar_tau001000um_M0600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114305/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114305/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114305/0000/merge002_0.root']),
'mfv_stopdbardbar_tau001000um_M1200_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114306/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114306/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114306/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114306/0000/merge003_0.root']),
'mfv_stopdbardbar_tau001000um_M1600_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114307/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114307/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114307/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114307/0000/merge003_0.root']),
'mfv_stopdbardbar_tau001000um_M3000_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180339/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180339/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180339/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180339/0000/merge003_0.root']),
'mfv_stopdbardbar_tau010000um_M0400_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114308/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114308/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114308/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M0600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114309/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114309/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114309/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M0800_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114310/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114310/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114310/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114310/0000/merge003_0.root']),
'mfv_stopdbardbar_tau010000um_M1200_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180340/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180340/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180340/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180340/0000/merge003_0.root']),
'mfv_stopdbardbar_tau010000um_M1600_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114311/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114311/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114311/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114311/0000/merge003_0.root']),
'mfv_stopdbardbar_tau010000um_M3000_2018': (5, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180341/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180341/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180341/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180341/0000/merge003_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180341/0000/merge004_0.root']),
'mfv_stopdbardbar_tau030000um_M0400_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180342/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180342/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180342/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M0600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180343/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180343/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180343/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M0800_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114312/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114312/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114312/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M1200_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114313/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114313/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114313/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_114313/0000/merge003_0.root']),
'mfv_stopdbardbar_tau030000um_M1600_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180344/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180344/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180344/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200415_180344/0000/merge003_0.root']),
'mfv_stopdbardbar_tau030000um_M3000_2018': (4, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132616/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132616/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132616/0000/merge002_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_WGen_2018/200411_132616/0000/merge003_0.root']),
})


_add_ds("ntuplev27m", {
'qcdht0700_2017': _fromnum0("/store/user/tucker/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_2017/190802_112506", 16),
'qcdht1000_2017': _fromnum0("/store/user/tucker/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_2017/190802_112507", 31),
'qcdht1500_2017': _fromnum0("/store/user/tucker/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_2017/190802_112508", 63),
'qcdht2000_2017': _fromnum0("/store/user/tucker/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_2017/190802_112509", 30),
'ttbarht0600_2017': _fromnum0("/store/user/tucker/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2017/190802_112510", 4),
'ttbarht0800_2017': _fromnum0("/store/user/tucker/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2017/190802_112511", 3),
'ttbarht1200_2017': (1, ['/store/user/tucker/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2017/190802_112512/0000/ntuple_0.root']),
'ttbarht2500_2017': (1, ['/store/user/tucker/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2017/190802_112513/0000/ntuple_0.root']),
'qcdht0700_2018': _fromnum0("/store/user/tucker/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2018/190802_113539", 23),
'qcdht1000_2018': _fromnum0("/store/user/tucker/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2018/190802_113540", 37),
'qcdht1500_2018': _fromnum0("/store/user/tucker/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2018/190802_113541", 76),
'qcdht2000_2018': _fromnum0("/store/user/tucker/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2018/190802_113542", 34),
'ttbarht0600_2018': _fromnum0("/store/user/tucker/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2018/190802_113543", 5),
'ttbarht0800_2018': _fromnum0("/store/user/tucker/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2018/190802_113544", 4),
'ttbarht1200_2018': (1, ['/store/user/tucker/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2018/190802_113545/0000/ntuple_0.root']),
'ttbarht2500_2018': (1, ['/store/user/tucker/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_2018/190802_113546/0000/ntuple_0.root']),
'mfv_neu_tau000100um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133743/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133743/0000/merge001_0.root']),
'mfv_neu_tau000100um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133744/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133744/0000/merge001_0.root']),
'mfv_neu_tau000100um_M0800_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133745/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133745/0000/merge001_0.root']),
'mfv_neu_tau000100um_M1200_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133746/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133746/0000/merge001_0.root']),
'mfv_neu_tau000100um_M1600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133747/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133747/0000/merge001_0.root']),
'mfv_neu_tau000100um_M3000_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133748/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133748/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133749/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133749/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133750/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133750/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0800_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133751/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133751/0000/merge001_0.root']),
'mfv_neu_tau000300um_M1200_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133752/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133752/0000/merge001_0.root']),
'mfv_neu_tau000300um_M1600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133753/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133753/0000/merge001_0.root']),
'mfv_neu_tau000300um_M3000_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133754/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133754/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133754/0000/merge002_0.root']),
'mfv_neu_tau001000um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133755/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133755/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133756/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133756/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0800_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133757/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133757/0000/merge001_0.root']),
'mfv_neu_tau001000um_M1200_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133758/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133758/0000/merge001_0.root']),
'mfv_neu_tau001000um_M1600_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150922/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150922/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150922/0000/merge002_0.root']),
'mfv_neu_tau001000um_M3000_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133800/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133800/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133800/0000/merge002_0.root']),
'mfv_neu_tau010000um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133801/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133801/0000/merge001_0.root']),
'mfv_neu_tau010000um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133802/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133802/0000/merge001_0.root']),
'mfv_neu_tau010000um_M0800_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133803/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133803/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133803/0000/merge002_0.root']),
'mfv_neu_tau010000um_M1200_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133804/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133804/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133804/0000/merge002_0.root']),
'mfv_neu_tau010000um_M1600_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133805/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133805/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133805/0000/merge002_0.root']),
'mfv_neu_tau010000um_M3000_2017': (4, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133806/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133806/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133806/0000/merge002_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133806/0000/merge003_0.root']),
'mfv_neu_tau030000um_M0400_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133807/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133807/0000/merge001_0.root']),
'mfv_neu_tau030000um_M0600_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133808/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133808/0000/merge001_0.root']),
'mfv_neu_tau030000um_M0800_2017': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133809/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133809/0000/merge001_0.root']),
'mfv_neu_tau030000um_M1200_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133810/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133810/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133810/0000/merge002_0.root']),
'mfv_neu_tau030000um_M1600_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150924/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150924/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150924/0000/merge002_0.root']),
'mfv_neu_tau030000um_M3000_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133812/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133812/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133812/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M0400_2017': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133813/0000/merge_0.root']),
'mfv_stopdbardbar_tau000100um_M0600_2017': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133814/0000/merge_0.root']),
'mfv_stopdbardbar_tau000100um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133815/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133815/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M1200_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133816/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133816/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M1600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133817/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133817/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M3000_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133818/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133818/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0400_2017': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133819/0000/merge_0.root']),
'mfv_stopdbardbar_tau000300um_M0600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133820/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133820/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133821/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133821/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M1200_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133822/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133822/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M1600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150929/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150929/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M3000_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133824/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133824/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0400_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150931/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150931/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133826/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133826/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133827/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133827/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M1200_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133828/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133828/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M1600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133829/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133829/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133829/0000/merge002_0.root']),
'mfv_stopdbardbar_tau001000um_M3000_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133830/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133830/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133830/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M0400_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133831/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133831/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M0600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150933/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150933/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150934/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150934/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M1200_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150935/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150935/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_150935/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M1600_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133835/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133835/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133835/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M3000_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133836/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133836/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133836/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M0400_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133837/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133837/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M0600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133838/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133838/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M0800_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133839/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133839/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M1200_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133840/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133840/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M1600_2017': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133841/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133841/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M3000_2017': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133842/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133842/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV27m_2017/190808_133842/0000/merge002_0.root']),
'mfv_neu_tau000100um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133748/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133748/0000/merge001_0.root']),
'mfv_neu_tau000100um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133749/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133749/0000/merge001_0.root']),
'mfv_neu_tau000100um_M0800_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133750/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133750/0000/merge001_0.root']),
'mfv_neu_tau000100um_M1200_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133751/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133751/0000/merge001_0.root']),
'mfv_neu_tau000100um_M1600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133752/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133752/0000/merge001_0.root']),
'mfv_neu_tau000100um_M3000_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133753/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133753/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133754/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133754/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133755/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133755/0000/merge001_0.root']),
'mfv_neu_tau000300um_M0800_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133756/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133756/0000/merge001_0.root']),
'mfv_neu_tau000300um_M1200_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133757/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133757/0000/merge001_0.root']),
'mfv_neu_tau000300um_M1600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133758/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133758/0000/merge001_0.root']),
'mfv_neu_tau000300um_M3000_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133759/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133759/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133800/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133800/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133801/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133801/0000/merge001_0.root']),
'mfv_neu_tau001000um_M0800_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133802/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133802/0000/merge001_0.root']),
'mfv_neu_tau001000um_M1200_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133803/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133803/0000/merge001_0.root']),
'mfv_neu_tau001000um_M1600_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150925/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150925/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150925/0000/merge002_0.root']),
'mfv_neu_tau001000um_M3000_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094900/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094900/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094900/0000/merge002_0.root']),
'mfv_neu_tau010000um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133805/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133805/0000/merge001_0.root']),
'mfv_neu_tau010000um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133806/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133806/0000/merge001_0.root']),
'mfv_neu_tau010000um_M0800_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133807/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133807/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133807/0000/merge002_0.root']),
'mfv_neu_tau010000um_M1200_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150926/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150926/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150926/0000/merge002_0.root']),
'mfv_neu_tau010000um_M1600_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150927/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150927/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150927/0000/merge002_0.root']),
'mfv_neu_tau010000um_M3000_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133810/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133810/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133810/0000/merge002_0.root']),
'mfv_neu_tau030000um_M0400_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133811/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133811/0000/merge001_0.root']),
'mfv_neu_tau030000um_M0600_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133812/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133812/0000/merge001_0.root']),
'mfv_neu_tau030000um_M0800_2018': (2, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133813/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133813/0000/merge001_0.root']),
'mfv_neu_tau030000um_M1200_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133814/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133814/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133814/0000/merge002_0.root']),
'mfv_neu_tau030000um_M1600_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150930/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150930/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150930/0000/merge002_0.root']),
'mfv_neu_tau030000um_M3000_2018': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133816/0000/merge_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133816/0000/merge001_0.root', '/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133816/0000/merge002_0.root']),
'mfv_stopdbardbar_tau000100um_M0400_2018': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133817/0000/merge_0.root']),
'mfv_stopdbardbar_tau000100um_M0600_2018': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133818/0000/merge_0.root']),
'mfv_stopdbardbar_tau000100um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133819/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133819/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133820/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133820/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M1600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133821/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133821/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000100um_M3000_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133822/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133822/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0400_2018': (1, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150932/0000/merge_0.root']),
'mfv_stopdbardbar_tau000300um_M0600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133824/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133824/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133825/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133825/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150936/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150936/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M1600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150937/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150937/0000/merge001_0.root']),
'mfv_stopdbardbar_tau000300um_M3000_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133828/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133828/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0400_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133829/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133829/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133830/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133830/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150938/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150938/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133832/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133832/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M1600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094929/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094929/0000/merge001_0.root']),
'mfv_stopdbardbar_tau001000um_M3000_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094930/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094930/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094930/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M0400_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133833/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133833/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M0600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133834/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133834/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133835/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133835/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_033121/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_033121/0000/merge001_0.root']),
'mfv_stopdbardbar_tau010000um_M1600_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094935/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094935/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094935/0000/merge002_0.root']),
'mfv_stopdbardbar_tau010000um_M3000_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094936/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094936/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094936/0000/merge002_0.root']),
'mfv_stopdbardbar_tau030000um_M0400_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133837/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133837/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M0600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133838/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133838/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M0800_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150940/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_150940/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M1200_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133840/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133840/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M1600_2018': (2, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133841/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190808_133841/0000/merge001_0.root']),
'mfv_stopdbardbar_tau030000um_M3000_2018': (3, ['/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094942/0000/merge_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094942/0000/merge001_0.root', '/store/user/tucker/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV_2018-pythia8/NtupleV27m_2018/190809_094942/0000/merge002_0.root']),
'JetHT2017B': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_2017/190802_112514", 25),
'JetHT2017C': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_2017/190802_112515", 38),
'JetHT2017D': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_2017/190802_112516", 18),
'JetHT2017E': (42, ['/store/user/tucker/JetHT/NtupleV27m_2017/190802_112517/0000/ntuple_%i.root' % i for i in chain(xrange(2,42), [0])] + ['/store/user/tucker/JetHT/NtupleV27m_2017/190806_004211/0000/ntuple_1.root']),
'JetHT2017F': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_2017/190802_112518", 51),
'JetHT2018A': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_2018/190802_113547", 115),
'JetHT2018B': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_2018/190802_113548", 58),
'JetHT2018C': (107, ['/store/user/tucker/JetHT/NtupleV27m_2018/190803_214147/0000/ntuple_%i.root' % i for i in chain(xrange(68), xrange(69,107))] + ['/store/user/tucker/JetHT/NtupleV27m_2018/190805_064028/0000/ntuple_68.root']),
'JetHT2018D': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_2018/190802_113550", 207),
})

_add_ds("ntuplev27m_ntkseeds", {
'qcdht0700_2017': _fromnum0("/store/user/tucker/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_NTkSeeds_2017/190802_115905", 16, fnbase="ntkseeds"),
'qcdht1000_2017': _fromnum0("/store/user/tucker/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_NTkSeeds_2017/190802_115906", 31, fnbase="ntkseeds"),
'qcdht1500_2017': _fromnum0("/store/user/tucker/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_NTkSeeds_2017/190802_115907", 63, fnbase="ntkseeds"),
'qcdht2000_2017': _fromnum0("/store/user/tucker/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_NTkSeeds_2017/190802_115908", 30, fnbase="ntkseeds"),
'ttbarht0600_2017': _fromnum0("/store/user/tucker/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2017/190802_115909", 4, fnbase="ntkseeds"),
'ttbarht0800_2017': _fromnum0("/store/user/tucker/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2017/190802_115910", 3, fnbase="ntkseeds"),
'ttbarht1200_2017': (1, ['/store/user/tucker/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2017/190802_115911/0000/ntkseeds_0.root']),
'ttbarht2500_2017': (1, ['/store/user/tucker/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2017/190802_115912/0000/ntkseeds_0.root']),
'qcdht0700_2018': _fromnum0("/store/user/tucker/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2018/190802_115936", 23, fnbase="ntkseeds"),
'qcdht1000_2018': _fromnum0("/store/user/tucker/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2018/190802_115937", 37, fnbase="ntkseeds"),
'qcdht1500_2018': _fromnum0("/store/user/tucker/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2018/190802_115938", 76, fnbase="ntkseeds"),
'qcdht2000_2018': _fromnum0("/store/user/tucker/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2018/190802_115939", 34, fnbase="ntkseeds"),
'ttbarht0600_2018': _fromnum0("/store/user/tucker/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2018/190802_115940", 5, fnbase="ntkseeds"),
'ttbarht0800_2018': _fromnum0("/store/user/tucker/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2018/190802_115941", 4, fnbase="ntkseeds"),
'ttbarht1200_2018': (1, ['/store/user/tucker/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2018/190802_115942/0000/ntkseeds_0.root']),
'ttbarht2500_2018': (1, ['/store/user/tucker/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NTkSeeds_2018/190802_115943/0000/ntkseeds_0.root']),
'JetHT2017B': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2017/190802_115913", 62, fnbase="ntkseeds"),
'JetHT2017C': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2017/190802_115914", 95, fnbase="ntkseeds"),
'JetHT2017D': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2017/190802_115915", 44, fnbase="ntkseeds"),
'JetHT2017E': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2017/190802_115916", 103, fnbase="ntkseeds"),
'JetHT2017F': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2017/190802_115917", 127, fnbase="ntkseeds"),
'JetHT2018A': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2018/190802_115944", 286, fnbase="ntkseeds"),
'JetHT2018B': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2018/190802_115945", 145, fnbase="ntkseeds"),
'JetHT2018C': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2018/190802_115946", 107, fnbase="ntkseeds"),
'JetHT2018D': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NTkSeeds_2018/190802_115947", 516, fnbase="ntkseeds"),
})


_add_ds("ntuplev27m_norefitdzcut", {
'qcdht0700_2017': _fromnum0("/store/user/tucker/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_NoRefitDzCut_2017/190819_163618", 16),
'qcdht1000_2017': _fromnum0("/store/user/tucker/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_NoRefitDzCut_2017/190819_163619", 31),
'qcdht1500_2017': _fromnum0("/store/user/tucker/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_NoRefitDzCut_2017/190819_163620", 63),
'qcdht2000_2017': _fromnum0("/store/user/tucker/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV27m_NoRefitDzCut_2017/190819_163621", 30),
'ttbarht0600_2017': _fromnum0("/store/user/tucker/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2017/190819_163622", 4),
'ttbarht0800_2017': _fromnum0("/store/user/tucker/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2017/190819_163623", 3),
'ttbarht1200_2017': (1, ['/store/user/tucker/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2017/190819_163624/0000/ntuple_0.root']),
'ttbarht2500_2017': (1, ['/store/user/tucker/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2017/190819_163625/0000/ntuple_0.root']),
'mfv_neu_tau010000um_M0800_2017': (3, ['/store/user/tucker/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV27m_NoRefitDzCut_2017/merge/%s.root' % x for x in 'mrg', 'mrg001', 'mrg002']),
'qcdht0700_2018': _fromnum0("/store/user/tucker/QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2018/190819_163623", 23),
'qcdht1000_2018': _fromnum0("/store/user/tucker/QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2018/190819_163624", 37),
'qcdht1500_2018': _fromnum0("/store/user/tucker/QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2018/190819_163625", 76),
'qcdht2000_2018': _fromnum0("/store/user/tucker/QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2018/190819_163626", 34),
'ttbarht0600_2018': _fromnum0("/store/user/tucker/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2018/190819_163627", 5),
'ttbarht0800_2018': _fromnum0("/store/user/tucker/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2018/190819_163628", 4),
'ttbarht1200_2018': (1, ['/store/user/tucker/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2018/190819_163629/0000/ntuple_0.root']),
'ttbarht2500_2018': (1, ['/store/user/tucker/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV27m_NoRefitDzCut_2018/190819_163630/0000/ntuple_0.root']),
'JetHT2017B': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2017/190819_163626", 41),
'JetHT2017C': (63, ['/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2017/190820_080617/0000/ntuple_%i.root' % i for i in [42, 51]] + ['/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2017/190819_163627/0000/ntuple_%i.root' % i for i in chain(xrange(42), xrange(43,51), xrange(52,63))]),
'JetHT2017D': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2017/190819_163628", 30),
'JetHT2017E': (69, ['/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2017/190819_163629/0000/ntuple_%i.root' % i for i in chain(xrange(3), xrange(4,53), xrange(54,69))] + ['/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2017/190820_080619/0000/ntuple_%i.root' % i for i in [3, 53]]),
'JetHT2017F': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2017/190819_163630", 85),
'JetHT2018A': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2018/190819_163631", 191),
'JetHT2018B': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2018/190819_163632", 97),
'JetHT2018C': (72, ['/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2018/190819_163633/0000/ntuple_%i.root' % i for i in chain(xrange(6), xrange(8,11), xrange(12,14), xrange(16,31), xrange(32,35), xrange(39,45), xrange(46,52), xrange(53,59), xrange(60,72), [37])] + ['/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2018/190820_080621/0000/ntuple_%i.root' % i for i in chain(xrange(6,8), xrange(14,16), xrange(35,37), [11, 31, 38, 45, 52, 59])]),
'JetHT2018D': _fromnum0("/store/user/tucker/JetHT/NtupleV27m_NoRefitDzCut_2018/190819_163634", 344),
})

_add_ds("ntuplev29metm", {
  'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV29METm_2017/201016_131638", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleV29METm_2017/201016_131639", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleV29METm_2017/201016_131640", 50),
  'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleV29METm_2017/201016_131641", 50),
  'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleV29METm_2017/201016_131642", 50),
  'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV29METm_2017/201016_131643", 50),
  'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV29METm_2017/201016_131644", 50),
  'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV29METm_2017/201016_131645", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleV29METm_2017/201016_131646", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleV29METm_2017/201016_131647", 49),
  'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleV29METm_2017/201016_131648", 49),
  'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleV29METm_2017/201016_131649", 49),
  'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV29METm_2017/201016_131650", 49),
  'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV29METm_2017/201016_131651", 49),
  'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV29METm_2017/201016_131652", 50),
  'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleV29METm_2017/201016_131653", 50),
  'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleV29METm_2017/201016_131654", 50),
  'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleV29METm_2017/201016_131655", 50),
  'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleV29METm_2017/201016_131656", 50),
  'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV29METm_2017/201016_131657", 49),
  'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV29METm_2017/201016_131658", 49),
  'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV29METm_2017/201016_131659", 50),
  'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleV29METm_2017/201016_131700", 49),
  'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleV29METm_2017/201016_131701", 50),
  'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleV29METm_2017/201016_131702", 50),
  'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleV29METm_2017/201016_131703", 49),
  'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV29METm_2017/201016_131704", 49),
  'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV29METm_2017/201016_131705", 50),
})

_add_ds("ntuplev30m", {
  'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV30m_2017/201019_162445", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleV30m_2017/201019_162446", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleV30m_2017/201019_162447", 50),
  'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleV30m_2017/201019_162448", 50),
  'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleV30m_2017/201019_162449", 50),
  'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV30m_2017/201019_162450", 50),
  'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV30m_2017/201019_162451", 50),
  'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV30m_2017/201019_162452", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleV30m_2017/201019_162453", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleV30m_2017/201019_162454", 49),
  'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleV30m_2017/201019_162455", 49),
  'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleV30m_2017/201019_162456", 49),
  'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV30m_2017/201019_162457", 49),
  'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV30m_2017/201019_162458", 49),
  'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV30m_2017/201019_162459", 50),
  'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleV30m_2017/201019_162500", 50),
  'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleV30m_2017/201019_162501", 50),
  'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleV30m_2017/201019_162502", 50),
  'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleV30m_2017/201019_162503", 50),
  'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV30m_2017/201019_162504", 49),
  'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV30m_2017/201019_162505", 49),
  'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV30m_2017/201019_162506", 50),
  'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleV30m_2017/201019_162507", 49),
  'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleV30m_2017/201019_162508", 50),
  'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleV30m_2017/201019_162509", 50),
  'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleV30m_2017/201019_162510", 49),
  'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV30m_2017/201019_162511", 49),
  'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV30m_2017/201019_162512", 50),
})

_add_ds("ntuplev32m", {
'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV32m_2017/201019_223730", 16),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV32m_2017/201019_223731", 31),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV32m_2017/201019_223732", 63),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV32m_2017/201019_223733", 30),
'ttbarht0600_2017': _fromnum0("/store/user/ali/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV32m_2017/201019_223734", 4),
'ttbarht0800_2017': _fromnum0("/store/user/ali/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV32m_2017/201019_223735", 3),
'ttbarht1200_2017': (1, ['/store/user/ali/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV32m_2017/201019_223736/0000/ntuple_0.root']),
'ttbarht2500_2017': (1, ['/store/user/ali/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV32m_2017/201019_223737/0000/ntuple_0.root']),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV32m_2017/201019_223738", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleV32m_2017/201019_223739", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleV32m_2017/201019_223740", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleV32m_2017/201019_223741", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleV32m_2017/201019_223742", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV32m_2017/201019_223743", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV32m_2017/201019_223744", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV32m_2017/201019_223745", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleV32m_2017/201019_223746", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleV32m_2017/201019_223747", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleV32m_2017/201019_223748", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleV32m_2017/201019_223749", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV32m_2017/201019_223750", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV32m_2017/201019_223751", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV32m_2017/201019_223752", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleV32m_2017/201019_223753", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleV32m_2017/201019_223754", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleV32m_2017/201019_223755", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleV32m_2017/201019_223756", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV32m_2017/201019_223757", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV32m_2017/201019_223758", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV32m_2017/201019_223759", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleV32m_2017/201019_223800", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleV32m_2017/201019_223801", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleV32m_2017/201019_223802", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleV32m_2017/201019_223803", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV32m_2017/201019_223804", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV32m_2017/201019_223805", 50),
})

_add_ds("ntuplev33metm", {
'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV33METm_2017/201019_223835", 16),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV33METm_2017/201019_223836", 31),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV33METm_2017/201019_223837", 63),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV33METm_2017/201019_223838", 30),
'ttbarht0600_2017': _fromnum0("/store/user/ali/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV33METm_2017/201019_223839", 4),
'ttbarht0800_2017': _fromnum0("/store/user/ali/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV33METm_2017/201019_223840", 3),
'ttbarht1200_2017': (1, ['/store/user/ali/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV33METm_2017/201019_223841/0000/ntuple_0.root']),
'ttbarht2500_2017': (1, ['/store/user/ali/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV33METm_2017/201019_223842/0000/ntuple_0.root']),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV33METm_2017/201019_223843", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleV33METm_2017/201019_223844", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleV33METm_2017/201019_223845", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleV33METm_2017/201019_223846", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleV33METm_2017/201019_223847", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV33METm_2017/201019_223848", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV33METm_2017/201019_223849", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV33METm_2017/201019_223850", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleV33METm_2017/201019_223851", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleV33METm_2017/201019_223852", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleV33METm_2017/201019_223853", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleV33METm_2017/201019_223854", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV33METm_2017/201019_223855", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV33METm_2017/201019_223856", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV33METm_2017/201019_223857", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleV33METm_2017/201019_223858", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleV33METm_2017/201019_223859", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleV33METm_2017/201019_223900", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleV33METm_2017/201019_223901", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV33METm_2017/201019_223902", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV33METm_2017/201019_223903", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV33METm_2017/201019_223904", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleV33METm_2017/201019_223905", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleV33METm_2017/201019_223906", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleV33METm_2017/201019_223907", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleV33METm_2017/201019_223908", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV33METm_2017/201019_223909", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV33METm_2017/201019_223910", 50),
})

_add_ds("miniaod", {
  'mfv_splitSUSY_tau000001000um_M1200_1100_2017':_fromnum1("/store/user/ali/splitSUSY_M1200_1100_ctau1p0_17Fall/CRAB_splitSUSY_M1200_1100_ctau1p0_17Fall_MINIAOD/210226_002951/0000", 40, fnbase="MiniAOD", numbereddirs=False),
  'mfv_splitSUSY_tau000010000um_M1200_1100_2017':_fromnum1("/store/user/ali/splitSUSY_M1200_1100_ctau10p0_17Fall/CRAB_splitSUSY_M1200_1100_ctau10p0_17Fall_MINIAOD/210226_000236/0000", 40, fnbase="MiniAOD", numbereddirs=False),
  'mfv_splitSUSY_tau000001000um_M1200_1200_2017':_fromnum1("/store/user/ali/splitSUSY_M1200_1200_ctau1p0_17Fall/CRAB_splitSUSY_M1200_1200_ctau1p0_17Fall_MINIAOD/210226_002736/0000", 40, fnbase="MiniAOD", numbereddirs=False),
  'mfv_splitSUSY_tau000010000um_M1200_1200_2017':_fromnum1("/store/user/ali/splitSUSY_M1200_1200_ctau10p0_17Fall/CRAB_splitSUSY_M1200_1200_ctau10p0_17Fall_MINIAOD/210226_024923/0000", 40, fnbase="MiniAOD", numbereddirs=False),
  'mfv_splitSUSY_tau000001000um_M1400_1200_2017':_fromnum1("/store/user/ali/splitSUSY_M1400_1200_ctau1p0_17Fall/CRAB_splitSUSY_M1400_1200_ctau1p0_17Fall_MINIAOD/210219_181045/0000", 40, fnbase="MiniAOD", numbereddirs=False),
  'mfv_splitSUSY_tau000010000um_M1400_1200_2017':_fromnum1("/store/user/ali/splitSUSY_M1400_1200_ctau10p0_17Fall/CRAB_splitSUSY_M1400_1200_ctau10p0_17Fall_MINIAOD/210218_230424/0000", 40, fnbase="MiniAOD", numbereddirs=False),
  'mfv_splitSUSY_tau000000000um_M2000_1800_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1800_ctau0p1_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000000300um_M2000_1800_2017':_fromnum1("/store/user/ali/splitSUSY_M2000_1800_ctau0p3_17Fall/CRAB_splitSUSY_M2000_1800_ctau0p3_17Fall_MINIAOD/201225_221847/0000", 20, fnbase="splitSUSY_ctau0p3_MINIAOD", numbereddirs=False),
  'mfv_splitSUSY_tau100000000um_M2000_1800_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1800_ctau100000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau010000000um_M2000_1800_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1800_ctau10000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau001000000um_M2000_1800_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1800_ctau1000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000100000um_M2000_1800_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1800_ctau100p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000010000um_M2000_1800_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1800_ctau10p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000001000um_M2000_1800_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1800_ctau1p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000000000um_M2000_1900_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1900_ctau0p1_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000000300um_M2000_1900_2017':_fromnum1("/store/user/ali/splitSUSY_M2000_1900_ctau0p3_17Fall/CRAB_splitSUSY_M2000_1900_ctau0p3_17Fall_MINIAOD/201229_190939/0000", 20, fnbase="splitSUSY_ctau0p3_MINIAOD", numbereddirs=False),
  'mfv_splitSUSY_tau100000000um_M2000_1900_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1900_ctau100000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau010000000um_M2000_1900_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1900_ctau10000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 39, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau001000000um_M2000_1900_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1900_ctau1000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 39, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000100000um_M2000_1900_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1900_ctau100p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 39, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000010000um_M2000_1900_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1900_ctau10p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 39, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000001000um_M2000_1900_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2000_1900_ctau1p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 39, fnbase="output", numbereddirs=False),

  'mfv_splitSUSY_tau000000000um_M2400_100_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_100_ctau0p1_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000000300um_M2400_100_2017':_fromnum1("/store/user/ali/splitSUSY_M2400_100_ctau0p3_17Fall/CRAB_splitSUSY_M2400_100_ctau0p3_17Fall_MINIAOD/201230_152551/0000", 20, fnbase="splitSUSY_ctau0p3_MINIAOD", numbereddirs=False),
  'mfv_splitSUSY_tau100000000um_M2400_100_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_100_ctau100000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau010000000um_M2400_100_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_100_ctau10000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau001000000um_M2400_100_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_100_ctau1000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000100000um_M2400_100_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_100_ctau100p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000010000um_M2400_100_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_100_ctau10p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000001000um_M2400_100_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_100_ctau1p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000000000um_M2400_2300_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_2300_ctau0p1_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000000300um_M2400_2300_2017':_fromnum1("/store/user/ali/splitSUSY_M2400_2300_ctau0p3_17Fall/CRAB_splitSUSY_M2400_2300_ctau0p3_17Fall_MINIAOD/201230_011838/0000", 20, fnbase="splitSUSY_ctau0p3_MINIAOD", numbereddirs=False),
  'mfv_splitSUSY_tau100000000um_M2400_2300_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_2300_ctau100000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 39, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau010000000um_M2400_2300_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_2300_ctau10000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau001000000um_M2400_2300_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_2300_ctau1000p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000100000um_M2400_2300_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_2300_ctau100p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 39, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000010000um_M2400_2300_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_2300_ctau10p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 39, fnbase="output", numbereddirs=False),
  'mfv_splitSUSY_tau000001000um_M2400_2300_2017':_fromnum1("/store/user/ali/splitSUSY/splitSUSY_M2400_2300_ctau1p0_TuneCP2_13TeV_pythia8_RunIIFall17_MINIAODSIM_v2_summaryProd", 40, fnbase="output", numbereddirs=False),
})

_add_single_files('nr_k0ntuplev25mv1', '/store/user/wsun/croncopyeos/hadded/K0NtupleV25mv1', \
                      ['qcdht%04i_%i' % (x,y) for y in (2017,2018) for x in (700,1000,1500,2000)] + \
                      ['JetHT%i%s' % (y,x) for y in (2017,2018) for x in ('BCDEF' if y == 2017 else 'ABCD')])

for xx in '', '_NoRefitDzCut':
    _add_single_files('nr_trackmoverv27mv1' + xx.lower(), '/store/user/%s/hadded/TrackMoverV27mv1' % ('shogan/croncopyeos' if not xx else 'tucker') + xx, \
                          ['qcdht%04i_%i' % (x,y) for y in (2017,2018) for x in (700,1000,1500,2000)] + \
                          ['ttbarht%04i_%i' % (x,y) for y in (2017,2018) for x in (600,800,1200,2500)] + \
                          ['JetHT%i%s' % (y,x) for y in (2017,2018) for x in ('BCDEF' if y == 2017 else 'ABCD')])

    _add_single_files('nr_trackmovermctruthv27mv1' + xx.lower(), '/store/user/shogan/croncopyeos/hadded/TrackMoverMCTruthV27mv1' + xx, \
                          ['mfv_%s_tau%06ium_M%04i_%i' % (a,b,c,y) for y in (2017,2018) for a in ('neu','stopdbardbar') for b in (100,300,1000,10000,30000) for c in (400,600,800,1200,1600,3000)])

_add_single_files('nr_trackmovermctruthv27mv2', '/store/user/tucker/hadded/TrackMoverMCTruthV27mv2', \
                      ['mfv_%s_tau%06ium_M%04i_%i' % (a,b,c,y) for y in (2017,2018) for a in ('neu','stopdbardbar') for b in (100,300,1000,10000,30000) for c in (400,600,800,1200,1600,3000)])

_add_ds("ntuplev28bm", {
'qcdht0700_2017': _fromnum0("/store/user/joeyr/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201011_185109", 16),
'qcdht1000_2017': _fromnum0("/store/user/joeyr/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201009_175424", 31),
'qcdht1500_2017': _fromnum0("/store/user/joeyr/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201009_175425", 63),
'qcdht2000_2017': _fromnum0("/store/user/joeyr/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201009_175426", 30),
'qcdht0300_2017': (935, ['/store/user/joeyr/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201014_163310/0000/ntuple_%i.root' % i for i in [20, 91, 666, 698]] + ['/store/user/joeyr/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201014_111712/0000/ntuple_%i.root' % i for i in chain(xrange(11), xrange(12,20), xrange(21,91), xrange(92,254), xrange(255,666), xrange(667,694), xrange(695,698), xrange(699,747), xrange(748,820), xrange(821,863), xrange(864,935))] + ['/store/user/joeyr/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201014_133237/0000/ntuple_%i.root' % i for i in [254, 694, 747, 820, 863]] + ['/store/user/joeyr/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201014_120451/0000/ntuple_11.root']),
'qcdht0500_2017': (21, ['/store/user/joeyr/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201011_185214/0000/ntuple_%i.root' % i for i in chain(xrange(15), xrange(16,21))] + ['/store/user/joeyr/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_2017/201013_094444/0000/ntuple_15.root']),
'ttbar_2017': _fromnum0("/store/user/joeyr/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV28Bm_2017/201009_175529", 51),
'ttHbb_2017': _fromnum0("/store/user/joeyr/ttHJetTobb_M125_TuneCP5_13TeV_amcatnloFXFX_madspin_pythia8/NtupleV28Bm_2017/201009_175530", 5),
'ttZ_2017': _fromnum0("/store/user/joeyr/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/NtupleV28Bm_2017/201009_175531", 4),
'ttZext_2017': _fromnum0("/store/user/joeyr/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/NtupleV28Bm_2017/201009_175532", 4),
'singletop_tchan_top_2017': _fromnum1("/store/user/jreicher/ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/NtupleV28Bm_2017/201009_215408", 2),
'singletop_tchan_antitop_2017': _fromnum1("/store/user/jreicher/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/NtupleV28Bm_2017/201009_215422", 2),
'mfv_neu_tau000100um_M0400_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175427", 480),
'mfv_neu_tau000100um_M0600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175428", 500),
'mfv_neu_tau000100um_M0800_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175429", 500),
'mfv_neu_tau000100um_M1200_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175430", 500),
'mfv_neu_tau000100um_M1600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175431", 500),
'mfv_neu_tau000100um_M3000_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175432", 500),
'mfv_neu_tau000300um_M0400_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175433", 500),
'mfv_neu_tau000300um_M0600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175434", 490),
'mfv_neu_tau000300um_M0800_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175435", 500),
'mfv_neu_tau000300um_M1200_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175436", 500),
'mfv_neu_tau000300um_M1600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175437", 500),
'mfv_neu_tau000300um_M3000_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175438", 490),
'mfv_neu_tau001000um_M0400_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175439", 500),
'mfv_neu_tau001000um_M0600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175440", 500),
'mfv_neu_tau001000um_M0800_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175441", 500),
'mfv_neu_tau001000um_M1200_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175442", 480),
'mfv_neu_tau001000um_M1600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175443", 500),
'mfv_neu_tau001000um_M3000_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175444", 490),
'mfv_neu_tau010000um_M0400_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175445", 500),
'mfv_neu_tau010000um_M0600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175446", 500),
'mfv_neu_tau010000um_M0800_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175447", 500),
'mfv_neu_tau010000um_M1200_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175448", 500),
'mfv_neu_tau010000um_M1600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175449", 500),
'mfv_neu_tau010000um_M3000_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175450", 490),
'mfv_neu_tau030000um_M0400_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175451", 500),
'mfv_neu_tau030000um_M0600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175452", 500),
'mfv_neu_tau030000um_M0800_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175453", 500),
'mfv_neu_tau030000um_M1200_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175454", 500),
'mfv_neu_tau030000um_M1600_2017': _fromnum0("/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201012_152949", 500),
'mfv_neu_tau030000um_M3000_2017': (499, ['/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175456/0000/ntuple_%i.root' % i for i in chain(xrange(130), xrange(131,154), xrange(155,191), xrange(192,205), xrange(206,273), xrange(274,288), xrange(289,345), xrange(346,446), xrange(447,478), xrange(479,498), [499])] + ['/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201012_094401/0000/ntuple_%i.root' % i for i in [130, 154, 191, 205, 288, 345, 478, 498]] + ['/store/user/joeyr/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201013_094448/0000/ntuple_446.root']),
'mfv_stopdbardbar_tau000100um_M0400_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175457", 500),
'mfv_stopdbardbar_tau000100um_M0600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175458", 480),
'mfv_stopdbardbar_tau000100um_M0800_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175459", 500),
'mfv_stopdbardbar_tau000100um_M1200_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201012_152954", 500),
'mfv_stopdbardbar_tau000100um_M1600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175501", 500),
'mfv_stopdbardbar_tau000100um_M3000_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175502", 475),
'mfv_stopdbardbar_tau000300um_M0400_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175503", 500),
'mfv_stopdbardbar_tau000300um_M0600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201012_152958", 500),
'mfv_stopdbardbar_tau000300um_M0800_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175505", 500),
'mfv_stopdbardbar_tau000300um_M1200_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175506", 500),
'mfv_stopdbardbar_tau000300um_M1600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175507", 500),
'mfv_stopdbardbar_tau000300um_M3000_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175508", 500),
'mfv_stopdbardbar_tau001000um_M0400_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175509", 500),
'mfv_stopdbardbar_tau001000um_M0600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175510", 485),
'mfv_stopdbardbar_tau001000um_M0800_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175511", 500),
'mfv_stopdbardbar_tau001000um_M1200_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175512", 495),
'mfv_stopdbardbar_tau001000um_M1600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175513", 500),
'mfv_stopdbardbar_tau001000um_M3000_2017': (499, ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201012_152844/0000/ntuple_%i.root' % i for i in [26, 353, 429]] + ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201013_094443/0000/ntuple_%i.root' % i for i in [80, 166]] + ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201012_094355/0000/ntuple_%i.root' % i for i in chain(xrange(342,344), [36, 66, 74, 85, 128, 148, 170, 206, 243, 253, 336, 356, 463, 469, 473])] + ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175514/0000/ntuple_%i.root' % i for i in chain(xrange(20), xrange(21,26), xrange(27,36), xrange(37,66), xrange(67,74), xrange(75,80), xrange(81,85), xrange(86,128), xrange(129,148), xrange(149,166), xrange(167,170), xrange(171,206), xrange(207,234), xrange(235,243), xrange(244,253), xrange(254,298), xrange(299,336), xrange(337,342), xrange(344,353), xrange(354,356), xrange(357,429), xrange(430,463), xrange(464,469), xrange(470,473), xrange(474,500))] + ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201014_163308/0000/ntuple_%i.root' % i for i in [234, 298]]),
'mfv_stopdbardbar_tau010000um_M0400_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175515", 500),
'mfv_stopdbardbar_tau010000um_M0600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175516", 500),
'mfv_stopdbardbar_tau010000um_M0800_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175517", 490),
'mfv_stopdbardbar_tau010000um_M1200_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175518", 500),
'mfv_stopdbardbar_tau010000um_M1600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175519", 500),
'mfv_stopdbardbar_tau010000um_M3000_2017': (498, ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201013_094446/0000/ntuple_%i.root' % i for i in [12, 30, 180, 268, 304, 496, 499]] + ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175520/0000/ntuple_%i.root' % i for i in chain(xrange(12), xrange(13,30), xrange(31,33), xrange(34,42), xrange(44,53), xrange(54,76), xrange(77,80), xrange(81,83), xrange(84,92), xrange(93,114), xrange(115,117), xrange(118,138), xrange(139,153), xrange(154,162), xrange(163,174), xrange(175,180), xrange(181,183), xrange(184,190), xrange(191,199), xrange(200,259), xrange(260,268), xrange(269,304), xrange(305,322), xrange(323,365), xrange(366,372), xrange(373,377), xrange(378,425), xrange(426,464), xrange(467,481), xrange(482,496), xrange(497,499), [465])] + ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201014_163306/0000/ntuple_%i.root' % i for i in [33, 43]] + ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201012_094358/0000/ntuple_%i.root' % i for i in [53, 80, 92, 117, 138, 162, 174, 183, 199, 259, 322, 365, 372, 377, 425, 464, 481]] + ['/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201012_152847/0000/ntuple_%i.root' % i for i in [42, 76, 83, 114, 190]]),
'mfv_stopdbardbar_tau030000um_M0400_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175521", 500),
'mfv_stopdbardbar_tau030000um_M0600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175522", 500),
'mfv_stopdbardbar_tau030000um_M0800_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175523", 500),
'mfv_stopdbardbar_tau030000um_M1200_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175524", 490),
'mfv_stopdbardbar_tau030000um_M1600_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175525", 500),
'mfv_stopdbardbar_tau030000um_M3000_2017': _fromnum0("/store/user/joeyr/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV28Bm_2017/201009_175526", 500),
})

_add_ds("ntuplev28bm_ntkseeds", {
'qcdht0700_2017': (16, ['/store/user/joeyr/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_NTkSeeds_2017/201013_094444/0000/ntkseeds_%i.root' % i for i in [8, 13]] + ['/store/user/joeyr/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_NTkSeeds_2017/201011_185037/0000/ntkseeds_%i.root' % i for i in chain(xrange(8), xrange(9,13), xrange(14,16))]),
'qcdht1000_2017': (30, ['/store/user/joeyr/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_NTkSeeds_2017/201009_180012/0000/ntkseeds_%i.root' % i for i in chain(xrange(12), xrange(13,31))]),
'qcdht1500_2017': _fromnum0("/store/user/joeyr/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_NTkSeeds_2017/201009_180013", 63, fnbase="ntkseeds"),
'qcdht2000_2017': _fromnum0("/store/user/joeyr/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_NTkSeeds_2017/201009_180014", 30, fnbase="ntkseeds"),
'qcdht0300_2017': _fromnum0("/store/user/joeyr/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_NTkSeeds_2017/201014_132043", 935, fnbase="ntkseeds"),
'qcdht0500_2017': _fromnum0("/store/user/joeyr/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV28Bm_NTkSeeds_2017/201011_185042", 21, fnbase="ntkseeds"),
'ttbar_2017': (51, ['/store/user/joeyr/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV28Bm_NTkSeeds_2017/201009_180017/0000/ntkseeds_%i.root' % i for i in chain(xrange(16), xrange(18,32), xrange(33,39), xrange(40,51))] + ['/store/user/joeyr/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV28Bm_NTkSeeds_2017/201013_094440/0000/ntkseeds_17.root'] + ['/store/user/joeyr/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV28Bm_NTkSeeds_2017/201012_094410/0000/ntkseeds_%i.root' % i for i in [16, 32, 39]]),
'ttHbb_2017': _fromnum0("/store/user/joeyr/ttHJetTobb_M125_TuneCP5_13TeV_amcatnloFXFX_madspin_pythia8/NtupleV28Bm_NTkSeeds_2017/201009_180018", 5, fnbase="ntkseeds"),
'ttZ_2017': _fromnum0("/store/user/joeyr/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/NtupleV28Bm_NTkSeeds_2017/201009_180019", 4, fnbase="ntkseeds"),
'ttZext_2017': _fromnum0("/store/user/joeyr/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/NtupleV28Bm_NTkSeeds_2017/201009_180020", 4, fnbase="ntkseeds"),
'singletop_tchan_top_2017': _fromnum1("/store/user/jreicher/ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/NtupleV28Bm_NTkSeeds_2017/201009_215957", 2, fnbase="ntkseeds"),
'singletop_tchan_antitop_2017': _fromnum1("/store/user/jreicher/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/NtupleV28Bm_NTkSeeds_2017/201009_220010", 2, fnbase="ntkseeds"),
})

_add_ds("ntuplev36metm", {
'qcdht0700_2017': (16, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201025_105948/0000/ntuple_%i.root' % i for i in chain(xrange(3), xrange(5,7), xrange(8,16))] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201026_111820/0000/ntuple_%i.root' % i for i in chain(xrange(3,5), [7])]),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201025_105949", 31),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201025_105950", 63),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201025_105951", 30),
'ttbarht0600_2017': _fromnum0("/store/user/ali/TTJets_HT-600to800_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_105952", 4),
'ttbarht0800_2017': _fromnum0("/store/user/ali/TTJets_HT-800to1200_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_105953", 3),
'ttbarht1200_2017': (1, ['/store/user/ali/TTJets_HT-1200to2500_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_105954/0000/ntuple_0.root']),
'ttbarht2500_2017': (1, ['/store/user/ali/TTJets_HT-2500toInf_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_105955/0000/ntuple_0.root']),
'ttHbb_2017': _fromnum0("/store/user/ali/ttHJetTobb_M125_TuneCP5_13TeV_amcatnloFXFX_madspin_pythia8/NtupleV36METm_2017/201025_110004", 5),
'ttZ_2017': _fromnum0("/store/user/ali/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/NtupleV36METm_2017/201025_110005", 4),
'ttZext_2017': (4, ['/store/user/ali/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/NtupleV36METm_2017/201026_111818/0000/ntuple_2.root'] + ['/store/user/ali/ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8/NtupleV36METm_2017/201025_110006/0000/ntuple_%i.root' % i for i in chain(xrange(2), [3])]),
'singletop_tchan_top_2017': _fromnum1("/store/user/lian/ST_t-channel_top_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/NtupleV36METm_2017/201025_155934", 2),
'singletop_tchan_antitop_2017': _fromnum1("/store/user/lian/ST_t-channel_antitop_4f_inclusiveDecays_TuneCP5_13TeV-powhegV2-madspin-pythia8/NtupleV36METm_2017/201025_155947", 2),
'dyjetstollM10_2017': _fromnum0("/store/user/ali/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_105958", 10),
'dyjetstollM50_2017': _fromnum1("/store/user/lian/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_155908", 12),
'dyjetstollM50ext_2017': _fromnum1("/store/user/lian/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_155921", 12),
'qcdmupt15_2017': _fromnum0("/store/user/ali/QCD_Pt-20toInf_MuEnrichedPt15_TuneCP5_13TeV_pythia8/NtupleV36METm_2017/201025_105959", 6),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_105956", 11),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV36METm_2017/201025_105957", 15),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201025_110000", 15),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201025_110001", 19),
'qcdht0500_2017': (21, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201025_110002/0000/ntuple_%i.root' % i for i in chain(xrange(2), xrange(3,6), xrange(7,10), xrange(11,13), xrange(15,17), xrange(19,21))] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV36METm_2017/201026_111815/0000/ntuple_%i.root' % i for i in chain(xrange(13,15), xrange(17,19), [2, 6, 10])]),
'ttbar_2017': (51, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV36METm_2017/201025_110003/0000/ntuple_%i.root' % i for i in chain(xrange(8), xrange(9,21), xrange(22,51))] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV36METm_2017/201026_111808/0000/ntuple_%i.root' % i for i in [8, 21]]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleV36METm_2017/201025_110035", 6),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleV36METm_2017/201025_110036", 6),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleV36METm_2017/201025_110037", 4),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleV36METm_2017/201025_110038", 2),
'zjetstonunuht0800_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleV36METm_2017/201025_110039/0000/ntuple_0.root']),
'zjetstonunuht1200_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleV36METm_2017/201025_110040/0000/ntuple_0.root']),
'zjetstonunuht2500_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleV36METm_2017/201025_110041/0000/ntuple_0.root']),
'mfv_neu_tau000100um_M0400_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101638", 480),
'mfv_neu_tau000100um_M0600_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101639", 500),
'mfv_neu_tau000100um_M0800_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101640", 500),
'mfv_neu_tau000100um_M1200_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101641", 500),
'mfv_neu_tau000100um_M1600_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101642", 500),
'mfv_neu_tau000100um_M3000_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101643", 500),
'mfv_neu_tau000300um_M0400_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101644", 500),
'mfv_neu_tau000300um_M0600_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101645", 490),
'mfv_neu_tau000300um_M0800_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101646", 500),
'mfv_neu_tau000300um_M1200_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101647", 500),
'mfv_neu_tau000300um_M1600_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101648", 500),
'mfv_neu_tau000300um_M3000_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101649", 490),
'mfv_neu_tau001000um_M0400_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101650", 500),
'mfv_neu_tau001000um_M0600_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101651", 500),
'mfv_neu_tau001000um_M0800_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101652", 500),
'mfv_neu_tau001000um_M1200_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101653", 480),
'mfv_neu_tau001000um_M1600_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101654", 500),
'mfv_neu_tau001000um_M3000_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101655", 490),
'mfv_neu_tau010000um_M0400_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101656", 500),
'mfv_neu_tau010000um_M0600_2017': (500, ['/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201031_104617/0000/ntuple_319.root'] + ['/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101657/0000/ntuple_%i.root' % i for i in chain(xrange(319), xrange(320,500))]),
'mfv_neu_tau010000um_M0800_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101658", 500),
'mfv_neu_tau010000um_M1200_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101659", 500),
'mfv_neu_tau010000um_M1600_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101700", 500),
'mfv_neu_tau010000um_M3000_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101701", 490),
'mfv_neu_tau030000um_M0400_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101702", 500),
'mfv_neu_tau030000um_M0600_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101703", 500),
'mfv_neu_tau030000um_M0800_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101704", 500),
'mfv_neu_tau030000um_M1200_2017': _fromnum0("/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101705", 500),
'mfv_neu_tau030000um_M1600_2017': (500, ['/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201031_104613/0000/ntuple_%i.root' % i for i in [138, 418, 447, 467, 477]] + ['/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101706/0000/ntuple_%i.root' % i for i in chain(xrange(138), xrange(139,418), xrange(419,447), xrange(448,467), xrange(468,477), xrange(478,500))]),
'mfv_neu_tau030000um_M3000_2017': (499, ['/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201031_104614/0000/ntuple_443.root'] + ['/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101707/0000/ntuple_%i.root' % i for i in chain(xrange(138), xrange(139,205), xrange(206,443), xrange(444,446), xrange(447,500))] + ['/store/user/ali/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201225_182740/0000/ntuple_%i.root' % i for i in [205, 446]]),
'mfv_stopdbardbar_tau000100um_M0400_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-400_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101708", 500),
'mfv_stopdbardbar_tau000100um_M0600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101709", 480),
'mfv_stopdbardbar_tau000100um_M0800_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-800_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101710", 500),
'mfv_stopdbardbar_tau000100um_M1200_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-1200_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101711", 500),
'mfv_stopdbardbar_tau000100um_M1600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-1600_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101712", 500),
'mfv_stopdbardbar_tau000100um_M3000_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-100um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101713", 475),
'mfv_stopdbardbar_tau000300um_M0400_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-400_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101714", 500),
'mfv_stopdbardbar_tau000300um_M0600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101715", 500),
'mfv_stopdbardbar_tau000300um_M0800_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-800_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101716", 500),
'mfv_stopdbardbar_tau000300um_M1200_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-1200_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101717", 500),
'mfv_stopdbardbar_tau000300um_M1600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101718", 500),
'mfv_stopdbardbar_tau000300um_M3000_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-300um_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101719", 500),
'mfv_stopdbardbar_tau001000um_M0400_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-400_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101720", 500),
'mfv_stopdbardbar_tau001000um_M0600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101721", 485),
'mfv_stopdbardbar_tau001000um_M0800_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-800_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101722", 500),
'mfv_stopdbardbar_tau001000um_M1200_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-1200_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101723", 495),
'mfv_stopdbardbar_tau001000um_M1600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-1600_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101724", 500),
'mfv_stopdbardbar_tau001000um_M3000_2017': (499, ['/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201225_182736/0000/ntuple_336.root'] + ['/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201031_104601/0000/ntuple_%i.root' % i for i in [234, 278, 460]] + ['/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-1mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101725/0000/ntuple_%i.root' % i for i in chain(xrange(234), xrange(235,268), xrange(269,278), xrange(279,336), xrange(337,460), xrange(461,500))]),
'mfv_stopdbardbar_tau010000um_M0400_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-400_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101726", 500),
'mfv_stopdbardbar_tau010000um_M0600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101727", 500),
'mfv_stopdbardbar_tau010000um_M0800_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-800_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101728", 490),
'mfv_stopdbardbar_tau010000um_M1200_2017': (500, ['/store/user/ali/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201031_104557/0000/ntuple_%i.root' % i for i in chain(xrange(375,378), xrange(382,500), [258, 320, 352, 361, 373, 379])] + ['/store/user/ali/StopStopbarTo2Dbar2D_M-1200_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101729/0000/ntuple_%i.root' % i for i in chain(xrange(258), xrange(259,320), xrange(321,352), xrange(353,361), xrange(362,373), xrange(380,382), [374, 378])]),
'mfv_stopdbardbar_tau010000um_M1600_2017': (500, ['/store/user/ali/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201031_104606/0000/ntuple_%i.root' % i for i in chain(xrange(272,285), xrange(287,429), xrange(430,447), [244, 267, 453])] + ['/store/user/ali/StopStopbarTo2Dbar2D_M-1600_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101730/0000/ntuple_%i.root' % i for i in chain(xrange(244), xrange(245,267), xrange(268,272), xrange(285,287), xrange(447,453), xrange(454,500), [429])]),
'mfv_stopdbardbar_tau010000um_M3000_2017': (499, ['/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201225_182733/0000/ntuple_%i.root' % i for i in [33, 39, 83, 241, 372]] + ['/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101731/0000/ntuple_%i.root' % i for i in chain(xrange(33), xrange(34,39), xrange(40,76), xrange(77,83), xrange(84,165), xrange(166,214), xrange(215,224), xrange(225,241), xrange(242,256), xrange(257,268), xrange(269,322), xrange(323,372), xrange(373,403), xrange(404,466), xrange(467,492), xrange(493,499))] + ['/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-10mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201031_104605/0000/ntuple_%i.root' % i for i in [165, 214, 224, 256, 268, 322, 403, 466, 492, 499]]),
'mfv_stopdbardbar_tau030000um_M0400_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-400_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101732", 500),
'mfv_stopdbardbar_tau030000um_M0600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101733", 500),
'mfv_stopdbardbar_tau030000um_M0800_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-800_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101734", 500),
'mfv_stopdbardbar_tau030000um_M1200_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-1200_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101735", 490),
'mfv_stopdbardbar_tau030000um_M1600_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-1600_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101736", 500),
'mfv_stopdbardbar_tau030000um_M3000_2017': _fromnum0("/store/user/ali/StopStopbarTo2Dbar2D_M-3000_CTau-30mm_TuneCP2_13TeV-pythia8/NtupleV36METm_2017/201030_101737", 500),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV36METm_2017/201025_110007", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': (50, ['/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleV36METm_2017/201225_181824/0000/ntuple_%i.root' % i for i in chain(xrange(8,31), xrange(32,37), xrange(40,45), xrange(46,50), [2, 4, 38])] + ['/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleV36METm_2017/201225_182745/0000/ntuple_%i.root' % i for i in chain(xrange(2), xrange(5,8), [3, 31, 37, 39, 45])]),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleV36METm_2017/201025_110008", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleV36METm_2017/201025_110009", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleV36METm_2017/201025_110010", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleV36METm_2017/201025_110011", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV36METm_2017/201025_110012", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV36METm_2017/201025_110013", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV36METm_2017/201025_110014", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleV36METm_2017/201230_192035", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleV36METm_2017/201025_110015", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleV36METm_2017/201025_110016", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleV36METm_2017/201025_110017", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleV36METm_2017/201025_110018", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV36METm_2017/201025_110019", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV36METm_2017/201025_110020", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV36METm_2017/201025_110021", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleV36METm_2017/201230_192043", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleV36METm_2017/201025_110022", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleV36METm_2017/201025_110023", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleV36METm_2017/201025_110024", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleV36METm_2017/201025_110025", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV36METm_2017/201025_110026", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV36METm_2017/201025_110027", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV36METm_2017/201025_110028", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleV36METm_2017/201230_192051", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleV36METm_2017/201025_110029", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleV36METm_2017/201025_110030", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleV36METm_2017/201025_110031", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleV36METm_2017/201025_110032", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV36METm_2017/201025_110033", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV36METm_2017/201025_110034", 50),
})

_add_ds("ntuplevvtxplotmetm", {
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVvtxplotMETm_2017/201113_210934", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVvtxplotMETm_2017/201113_210935", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVvtxplotMETm_2017/201113_210936", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVvtxplotMETm_2017/201113_210937", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVvtxplotMETm_2017/201113_210938", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVvtxplotMETm_2017/201113_210939", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVvtxplotMETm_2017/201113_210940", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVvtxplotMETm_2017/201113_210941", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVvtxplotMETm_2017/201113_210942", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVvtxplotMETm_2017/201113_210943", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVvtxplotMETm_2017/201113_210944", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVvtxplotMETm_2017/201113_210945", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVvtxplotMETm_2017/201113_210946", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVvtxplotMETm_2017/201113_210947", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVvtxplotMETm_2017/201113_210948", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVvtxplotMETm_2017/201113_210949", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVvtxplotMETm_2017/201113_210950", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVvtxplotMETm_2017/201113_210951", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVvtxplotMETm_2017/201113_210952", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVvtxplotMETm_2017/201113_210953", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVvtxplotMETm_2017/201113_210954", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVvtxplotMETm_2017/201113_210955", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVvtxplotMETm_2017/201113_210956", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVvtxplotMETm_2017/201113_210957", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVvtxplotMETm_2017/201113_210958", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVvtxplotMETm_2017/201113_210959", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVvtxplotMETm_2017/201113_211000", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVvtxplotMETm_2017/201113_211001", 50),
})

_add_ds("ntuplevnsigmadxy2_v2metm", {
'qcdht0700_2017': (1, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy2_v2METm_2017/201122_103334/0000/ntuple_15.root']),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084439", 31),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084440", 63),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084441", 30),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084517", 11),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084518", 15),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084519", 15),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084520", 19),
'qcdht0500_2017': (1, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084521/0000/ntuple_20.root']),
'ttbar_2017': (51, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVnsigmadxy2_v2METm_2017/201121_084522/0000/ntuple_%i.root' % i for i in chain(xrange(10), xrange(11,51))] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVnsigmadxy2_v2METm_2017/201122_103343/0000/ntuple_10.root']),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVnsigmadxy2_v2METm_2017/201121_084510", 6),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVnsigmadxy2_v2METm_2017/201121_084511", 6),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVnsigmadxy2_v2METm_2017/201121_084512", 4),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVnsigmadxy2_v2METm_2017/201121_084513", 2),
'zjetstonunuht0800_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVnsigmadxy2_v2METm_2017/201121_084514/0000/ntuple_0.root']),
'zjetstonunuht1200_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVnsigmadxy2_v2METm_2017/201121_084515/0000/ntuple_0.root']),
'zjetstonunuht2500_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVnsigmadxy2_v2METm_2017/201121_192800/0000/ntuple_0.root']),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084442", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084443", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084444", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084445", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084446", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084447", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084448", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084449", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084450", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084451", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084452", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084453", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084454", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084455", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084456", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084457", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084458", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084459", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084500", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084501", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084502", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084503", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084504", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084505", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084506", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084507", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084508", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVnsigmadxy2_v2METm_2017/201121_084509", 50),
})

_add_ds("ntuplevnsigmadxy_1_100ummetm", {
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVnsigmadxy_1_100umMETm_2017/201123_204826", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVnsigmadxy_1_100umMETm_2017/201123_204827", 50),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVnsigmadxy_1_100umMETm_2017/201123_204828", 50),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVnsigmadxy_1_100umMETm_2017/201123_204829", 50),
})

_add_ds("ntuplevnsigmadxy_1_100um_genmetm", {
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVnsigmadxy_1_100um_genMETm_2017/201125_140454", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVnsigmadxy_1_100um_genMETm_2017/201125_140455", 50),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVnsigmadxy_1_100um_genMETm_2017/201125_140456", 50),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVnsigmadxy_1_100um_genMETm_2017/201125_140457", 50),
})

_add_ds("ntuplevnsigmadxy_no_100um_genmetm", {
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201127_143857", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125834", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125835", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125836", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125837", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125838", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201127_143901", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201127_143858", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125841", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125842", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125843", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125844", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125845", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201127_143902", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201127_143859", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125848", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125849", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125850", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125851", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125852", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201127_143903", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201127_143900", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125855", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125856", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125857", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125858", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201210_125859", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVnsigmadxy_no_100um_genMETm_2017/201127_143904", 50),
})


_add_ds("ntuplevnsigmadxy_1_ml_genmetm", {
'qcdht0700_2017': (16, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131632/0000/ntuple_%i.root' % i for i in chain(xrange(6,9), xrange(10,15), [0, 3])] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093917/0000/ntuple_%i.root' % i for i in chain(xrange(1,3), xrange(4,6), [9, 15])]),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131633", 31),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131634", 63),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131635", 30),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131711", 11),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131712", 15),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131713", 15),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131714", 19),
'qcdht0500_2017': (105, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093307/0000/ntuple_%i.root' % i for i in chain(xrange(1,3), xrange(4,20), xrange(21,42), xrange(43,73), xrange(74,96), xrange(99,103), [97, 104])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201214_065229/0000/ntuple_%i.root' % i for i in [0, 3, 20, 42, 73, 96, 98, 103]]),
'ttbar_2017': (51, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131716/0000/ntuple_%i.root' % i for i in chain(xrange(36), xrange(37,44), xrange(45,51))] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093913/0000/ntuple_%i.root' % i for i in [36, 44]]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093256", 29),
'zjetstonunuht0200_2017': (30, ['/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093257/0000/ntuple_%i.root' % i for i in chain(xrange(25), xrange(26,30))] + ['/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVnsigmadxy_1_ML_genMETm_2017/201214_065229/0000/ntuple_25.root']),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093258", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093259", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093300", 5),
'zjetstonunuht1200_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093301/0000/ntuple_0.root']),
'zjetstonunuht2500_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVnsigmadxy_1_ML_genMETm_2017/201213_093302/0000/ntuple_0.root']),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131636", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131637", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131638", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131639", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131640", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131641", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131642", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131643", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131644", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131645", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131646", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131647", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131648", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131649", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131650", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131651", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131652", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131653", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131654", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131655", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131656", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131657", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131658", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131659", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131700", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131701", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131702", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVnsigmadxy_1_ML_genMETm_2017/201210_131703", 50),
})

_add_ds("ntuplevnsigmadxy_2_ml_genmetm", {
'qcdht0700_2017': (16, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201212_093332/0000/ntuple_%i.root' % i for i in chain(xrange(1,3), xrange(5,7), xrange(13,15), [11])] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131842/0000/ntuple_%i.root' % i for i in chain(xrange(3,5), xrange(7,11), [0, 12, 15])]),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131843", 31),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131844", 63),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131845", 30),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131921", 11),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131922", 15),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131923", 15),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131924", 19),
'qcdht0500_2017': (105, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201215_124332/0000/ntuple_58.root'] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201213_092906/0000/ntuple_%i.root' % i for i in chain(xrange(3), xrange(4,10), xrange(11,15), xrange(18,22), xrange(23,25), xrange(28,36), xrange(37,42), xrange(43,58), xrange(59,64), xrange(65,69), xrange(70,77), xrange(78,81), xrange(82,85), xrange(87,89), xrange(90,93), xrange(94,102), xrange(103,105), [16, 26])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201214_065306/0000/ntuple_%i.root' % i for i in chain(xrange(85,87), [3, 10, 15, 17, 22, 27, 64, 69, 77, 81, 89, 93, 102])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201214_121003/0000/ntuple_%i.root' % i for i in [25, 42]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201215_075803/0000/ntuple_36.root']),
'ttbar_2017': (51, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131926/0000/ntuple_%i.root' % i for i in chain(xrange(1,4), xrange(5,29), xrange(31,51))] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVnsigmadxy_2_ML_genMETm_2017/201212_093334/0000/ntuple_%i.root' % i for i in chain(xrange(29,31), [0, 4])]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131914", 6),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131915", 6),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131916", 4),
'zjetstonunuht0600_2017': (2, ['/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVnsigmadxy_2_ML_genMETm_2017/201212_093336/0000/ntuple_0.root'] + ['/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131917/0000/ntuple_1.root']),
'zjetstonunuht0800_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131918/0000/ntuple_0.root']),
'zjetstonunuht1200_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131919/0000/ntuple_0.root']),
'zjetstonunuht2500_2017': (1, ['/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131920/0000/ntuple_0.root']),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131846", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131847", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131848", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131849", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131850", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131851", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131852", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131853", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131854", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131855", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131856", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131857", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131858", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131859", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131900", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131901", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131902", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131903", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131904", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131905", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131906", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131907", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131908", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131909", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131910", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131911", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131912", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVnsigmadxy_2_ML_genMETm_2017/201210_131913", 50),
})

_add_ds("ntuplevtracktreev1metm", {
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtracktreev1METm_2017/210106_215204", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtracktreev1METm_2017/210106_215205", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtracktreev1METm_2017/210106_215206", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtracktreev1METm_2017/210106_215207", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtracktreev1METm_2017/210106_215208", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtracktreev1METm_2017/210106_215209", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtracktreev1METm_2017/210106_215210", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtracktreev1METm_2017/210106_215211", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtracktreev1METm_2017/210106_215212", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtracktreev1METm_2017/210106_215213", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtracktreev1METm_2017/210106_215214", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtracktreev1METm_2017/210106_215215", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtracktreev1METm_2017/210106_215216", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtracktreev1METm_2017/210106_215217", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtracktreev1METm_2017/210106_215218", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtracktreev1METm_2017/210106_215219", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtracktreev1METm_2017/210106_215220", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtracktreev1METm_2017/210106_215221", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtracktreev1METm_2017/210106_215222", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtracktreev1METm_2017/210106_215223", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtracktreev1METm_2017/210106_215224", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtracktreev1METm_2017/210106_215225", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtracktreev1METm_2017/210106_215226", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtracktreev1METm_2017/210106_215227", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtracktreev1METm_2017/210106_215228", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtracktreev1METm_2017/210106_215229", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtracktreev1METm_2017/210106_215230", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtracktreev1METm_2017/210106_215231", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtracktreev1METm_2017/210106_215232", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtracktreev1METm_2017/210106_215233", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtracktreev1METm_2017/210106_215234", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtracktreev1METm_2017/210106_215235", 50),
})

_add_ds("ntuplevtrackpt0p5_dxy2_2metm", {
  'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212414", 77),
  'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212415", 113),
  'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212416", 250),
  'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212417", 147),
  'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212457", 52),
  'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212458", 74),
  'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212459", 75),
  'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212500", 94),
  'qcdht0500_2017': (103, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212501/0000/ntuple_%i.root' % i for i in chain(xrange(28), xrange(29,43), xrange(44,54), xrange(55,84), xrange(85,94), xrange(95,105))] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210113_082242/0000/ntuple_%i.root' % i for i in [28, 43, 54]]),
  'ttbar_2017': _fromnum0("/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212502", 254),
  'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212450", 29),
  'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212451", 30),
  'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212452", 16),
  'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212453", 9),
  'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212454", 5),
  'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212455", 4),
  'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212456", 2),
  'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212418", 50),
  'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212419", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212420", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212421", 50),
  'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212422", 50),
  'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212423", 50),
  'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212424", 50),
  'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212425", 50),
  'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212426", 50),
  'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212427", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212428", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212429", 49),
  'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212430", 49),
  'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212431", 49),
  'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212432", 49),
  'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212433", 49),
  'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212434", 50),
  'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212435", 50),
  'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212436", 50),
  'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212437", 50),
  'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212438", 50),
  'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212439", 50),
  'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212440", 49),
  'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212441", 49),
  'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212442", 50),
  'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212443", 50),
  'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212444", 49),
  'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212445", 50),
  'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212446", 50),
  'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212447", 49),
  'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212448", 49),
  'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2_2METm_2017/210112_212449", 50),
})

_add_ds("ntuplevtrackpt0p5_2metm", {
  'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212606", 77),
  'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212607", 113),
  'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212608", 250),
  'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212609", 147),
  'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212649", 52),
  'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212650", 74),
  'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212651", 75),
  'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212652", 94),
  'qcdht0500_2017': (103, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210113_122834/0000/ntuple_91.root'] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210113_082142/0000/ntuple_%i.root' % i for i in [47, 71]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210114_204242/0000/ntuple_5.root'] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212653/0000/ntuple_%i.root' % i for i in chain(xrange(5), xrange(6,47), xrange(48,71), xrange(72,84), xrange(85,91), xrange(92,94), xrange(95,105))]),
  'ttbar_2017': _fromnum0("/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackpt0p5_2METm_2017/210112_212654", 254),
  'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackpt0p5_2METm_2017/210112_212642", 29),
  'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackpt0p5_2METm_2017/210112_212643", 30),
  'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackpt0p5_2METm_2017/210112_212644", 16),
  'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackpt0p5_2METm_2017/210112_212645", 9),
  'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackpt0p5_2METm_2017/210112_212646", 5),
  'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackpt0p5_2METm_2017/210112_212647", 4),
  'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackpt0p5_2METm_2017/210112_212648", 2),
  'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackpt0p5_2METm_2017/210112_212610", 50),
  'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackpt0p5_2METm_2017/210112_212611", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtrackpt0p5_2METm_2017/210112_212612", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtrackpt0p5_2METm_2017/210112_212613", 50),
  'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtrackpt0p5_2METm_2017/210112_212614", 50),
  'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtrackpt0p5_2METm_2017/210112_212615", 50),
  'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackpt0p5_2METm_2017/210112_212616", 50),
  'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackpt0p5_2METm_2017/210112_212617", 50),
  'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackpt0p5_2METm_2017/210112_212618", 50),
  'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackpt0p5_2METm_2017/210112_212619", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtrackpt0p5_2METm_2017/210112_212620", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtrackpt0p5_2METm_2017/210112_212621", 49),
  'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtrackpt0p5_2METm_2017/210112_212622", 49),
  'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtrackpt0p5_2METm_2017/210112_212623", 49),
  'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackpt0p5_2METm_2017/210112_212624", 49),
  'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackpt0p5_2METm_2017/210112_212625", 49),
  'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackpt0p5_2METm_2017/210112_212626", 50),
  'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackpt0p5_2METm_2017/210112_212627", 50),
  'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtrackpt0p5_2METm_2017/210112_212628", 50),
  'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtrackpt0p5_2METm_2017/210112_212629", 50),
  'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtrackpt0p5_2METm_2017/210112_212630", 50),
  'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtrackpt0p5_2METm_2017/210112_212631", 50),
  'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackpt0p5_2METm_2017/210112_212632", 49),
  'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackpt0p5_2METm_2017/210112_212633", 49),
  'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210112_212634", 50),
  'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210112_212635", 50),
  'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210112_212636", 49),
  'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210112_212637", 50),
  'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210112_212638", 50),
  'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210112_212639", 49),
  'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210112_212640", 49),
  'mfv_splitSUSY_tau000001000um_M2400_2300_2017': (50, ['/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210113_082148/0000/ntuple_43.root'] + ['/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackpt0p5_2METm_2017/210112_212641/0000/ntuple_%i.root' % i for i in chain(xrange(43), xrange(44,50))]),
})

_add_ds("ntuplevtracktreev3metm", {
  'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtracktreev3METm_2017/210114_162758", 50),
  'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtracktreev3METm_2017/210114_162759", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtracktreev3METm_2017/210114_162800", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtracktreev3METm_2017/210114_162801", 50),
  'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtracktreev3METm_2017/210114_162802", 50),
  'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtracktreev3METm_2017/210114_162803", 50),
  'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtracktreev3METm_2017/210114_162804", 50),
  'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtracktreev3METm_2017/210114_162805", 50),
  'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtracktreev3METm_2017/210114_162806", 50),
  'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtracktreev3METm_2017/210114_162807", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtracktreev3METm_2017/210114_162808", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtracktreev3METm_2017/210114_162809", 49),
  'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtracktreev3METm_2017/210114_162810", 49),
  'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtracktreev3METm_2017/210114_162811", 49),
  'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtracktreev3METm_2017/210114_162812", 49),
  'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtracktreev3METm_2017/210114_162813", 49),
  'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtracktreev3METm_2017/210114_162814", 50),
  'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtracktreev3METm_2017/210114_162815", 50),
  'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtracktreev3METm_2017/210114_162816", 50),
  'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtracktreev3METm_2017/210114_162817", 50),
  'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtracktreev3METm_2017/210114_162818", 50),
  'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtracktreev3METm_2017/210114_162819", 50),
  'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtracktreev3METm_2017/210114_162820", 49),
  'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtracktreev3METm_2017/210114_162821", 49),
  'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtracktreev3METm_2017/210114_162822", 50),
  'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtracktreev3METm_2017/210114_162823", 50),
  'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtracktreev3METm_2017/210114_162824", 49),
  'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtracktreev3METm_2017/210114_162825", 50),
  'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtracktreev3METm_2017/210114_162826", 50),
  'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtracktreev3METm_2017/210114_162827", 49),
  'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtracktreev3METm_2017/210114_162828", 49),
  'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtracktreev3METm_2017/210114_162829", 50),
})

_add_ds("ntuplevtracktreev4metm", {
  'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtracktreev4METm_2017/210116_220129", 50),
  'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtracktreev4METm_2017/210116_220130", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtracktreev4METm_2017/210116_220131", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtracktreev4METm_2017/210116_220132", 50),
  'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtracktreev4METm_2017/210116_220133", 50),
  'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtracktreev4METm_2017/210116_220134", 50),
  'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtracktreev4METm_2017/210116_220135", 50),
  'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtracktreev4METm_2017/210116_220136", 50),
  'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtracktreev4METm_2017/210116_220137", 50),
  'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtracktreev4METm_2017/210116_220138", 50),
  'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtracktreev4METm_2017/210116_220139", 50),
  'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtracktreev4METm_2017/210116_220140", 49),
  'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtracktreev4METm_2017/210116_220141", 49),
  'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtracktreev4METm_2017/210116_220142", 49),
  'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtracktreev4METm_2017/210116_220143", 49),
  'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtracktreev4METm_2017/210116_220144", 49),
  'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtracktreev4METm_2017/210116_220145", 50),
  'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtracktreev4METm_2017/210116_220146", 50),
  'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtracktreev4METm_2017/210116_220147", 50),
  'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtracktreev4METm_2017/210116_220148", 50),
  'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtracktreev4METm_2017/210116_220149", 50),
  'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtracktreev4METm_2017/210116_220150", 50),
  'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtracktreev4METm_2017/210116_220151", 49),
  'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtracktreev4METm_2017/210116_220152", 49),
  'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtracktreev4METm_2017/210116_220153", 50),
  'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtracktreev4METm_2017/210116_220154", 50),
  'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtracktreev4METm_2017/210116_220155", 49),
  'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtracktreev4METm_2017/210116_220156", 50),
  'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtracktreev4METm_2017/210116_220157", 50),
  'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtracktreev4METm_2017/210116_220158", 49),
  'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtracktreev4METm_2017/210116_220159", 49),
  'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtracktreev4METm_2017/210116_220200", 50),
})

_add_ds("ntuplev37metm", {
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV37METm_2017/210121_214449", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleV37METm_2017/210121_214450", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleV37METm_2017/210121_214451", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleV37METm_2017/210121_214452", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleV37METm_2017/210121_214453", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleV37METm_2017/210121_214454", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV37METm_2017/210121_214455", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV37METm_2017/210121_214456", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV37METm_2017/210121_214457", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleV37METm_2017/210121_214458", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleV37METm_2017/210121_214459", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleV37METm_2017/210121_214500", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleV37METm_2017/210121_214501", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleV37METm_2017/210121_214502", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV37METm_2017/210121_214503", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV37METm_2017/210121_214504", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV37METm_2017/210121_214505", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleV37METm_2017/210121_214506", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleV37METm_2017/210121_214507", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleV37METm_2017/210121_214508", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleV37METm_2017/210121_214509", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleV37METm_2017/210121_214510", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV37METm_2017/210121_214511", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV37METm_2017/210121_214512", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV37METm_2017/210121_214513", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleV37METm_2017/210121_214514", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleV37METm_2017/210121_214515", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleV37METm_2017/210121_214516", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleV37METm_2017/210121_214517", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleV37METm_2017/210121_214518", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV37METm_2017/210121_214519", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV37METm_2017/210121_214520", 50),
})

_add_ds("ntuplevtrackpt0p5_dxy2p5_2metm", {
'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200139", 77),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200140", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200141", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200142", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200222", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200223", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200224", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200225", 94),
'qcdht0500_2017': (209, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210122_131136/0000/ntuple_%i.root' % i for i in chain(xrange(6,10), xrange(11,13), xrange(22,25), xrange(38,40), xrange(51,54), xrange(60,62), xrange(65,67), xrange(71,73), xrange(78,80), xrange(85,88), xrange(95,98), xrange(107,109), xrange(124,126), xrange(127,130), xrange(132,134), xrange(138,142), xrange(143,145), xrange(146,149), xrange(155,160), xrange(171,174), xrange(183,185), xrange(190,192), xrange(196,198), xrange(199,201), xrange(203,205), [2, 18, 26, 30, 32, 34, 36, 44, 48, 58, 74, 76, 81, 83, 89, 93, 101, 103, 105, 112, 116, 118, 120, 136, 151, 161, 163, 165, 167, 169, 176, 181])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210122_214232/0000/ntuple_%i.root' % i for i in [0, 16, 20, 63, 73, 180]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210123_094903/0000/ntuple_%i.root' % i for i in [179, 202]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200226/0000/ntuple_%i.root' % i for i in chain(xrange(3,6), xrange(14,16), xrange(27,30), xrange(40,44), xrange(45,48), xrange(49,51), xrange(54,56), xrange(67,71), xrange(90,93), xrange(98,101), xrange(109,112), xrange(113,115), xrange(121,124), xrange(130,132), xrange(134,136), xrange(149,151), xrange(152,155), xrange(174,176), xrange(177,179), xrange(185,190), xrange(192,196), xrange(205,209), [1, 10, 17, 19, 21, 25, 31, 33, 35, 37, 57, 59, 62, 64, 75, 77, 80, 82, 84, 88, 94, 102, 104, 106, 117, 119, 126, 137, 142, 145, 160, 162, 164, 166, 168, 170, 182, 198, 201])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210123_151504/0000/ntuple_13.root'] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210122_080048/0000/ntuple_%i.root' % i for i in [56, 115]]),
'ttbar_2017': _fromnum0("/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200227", 254),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200215", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200216", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200217", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200218", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200219", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200220", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200221", 2),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200024", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200025", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200026", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200027", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200028", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200029", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200030", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200031", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200032", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200033", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200034", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200035", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200036", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200037", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200038", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200039", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200040", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200041", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200042", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200043", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200044", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200045", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200046", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200047", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200048", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200049", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200050", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200051", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200052", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200053", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200054", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy2p5_2METm_2017/210121_200055", 50),
})

_add_ds("ntuplevtrackpt0p5_dxy3p5_2metm", {
'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200549", 77),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200550", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200551", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200552", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200632", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200633", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200634", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200635", 94),
'qcdht0500_2017': (209, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210122_080147/0000/ntuple_%i.root' % i for i in chain(xrange(109,111), [37, 52, 86, 121, 127, 162, 166, 198])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200636/0000/ntuple_%i.root' % i for i in chain(xrange(1,5), xrange(9,12), xrange(16,19), xrange(22,26), xrange(29,35), xrange(38,40), xrange(43,46), xrange(47,49), xrange(55,58), xrange(59,63), xrange(64,66), xrange(89,91), xrange(98,101), xrange(105,108), xrange(130,132), xrange(133,136), xrange(140,142), xrange(150,152), xrange(157,159), xrange(171,174), xrange(175,179), xrange(180,184), xrange(185,189), xrange(190,196), xrange(205,209), [13, 27, 50, 70, 72, 75, 79, 81, 92, 95, 111, 114, 118, 122, 125, 143, 146, 154, 160, 163, 199])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210123_095106/0000/ntuple_%i.root' % i for i in [69, 74]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210122_214100/0000/ntuple_%i.root' % i for i in [21, 28, 40, 63, 77, 91, 113, 138, 144, 152, 168]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210122_131306/0000/ntuple_%i.root' % i for i in chain(xrange(5,9), xrange(14,16), xrange(19,21), xrange(35,37), xrange(41,43), xrange(53,55), xrange(66,69), xrange(82,86), xrange(87,89), xrange(93,95), xrange(96,98), xrange(101,105), xrange(115,118), xrange(119,121), xrange(123,125), xrange(128,130), xrange(136,138), xrange(147,150), xrange(155,157), xrange(164,166), xrange(169,171), xrange(196,198), xrange(200,205), [0, 12, 26, 46, 49, 51, 58, 71, 73, 76, 78, 80, 108, 112, 126, 132, 139, 142, 145, 153, 159, 161, 167, 174, 179, 184, 189])]),
'ttbar_2017': (254, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200637/0000/ntuple_%i.root' % i for i in chain(xrange(194), xrange(195,252), [253])] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210122_080155/0000/ntuple_252.root'] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210122_131312/0000/ntuple_194.root']),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200625", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200626", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200627", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200628", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200629", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200630", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200631", 2),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200553", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200554", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200555", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200556", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200557", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200558", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200559", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200600", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200601", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200602", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200603", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200604", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200605", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200606", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200607", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200608", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200609", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200610", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200611", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200612", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200613", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200614", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200615", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200616", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200617", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200618", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200619", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200620", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200621", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200622", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200623", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3p5_2METm_2017/210121_200624", 50),
})

_add_ds("ntuplevtrackpt0p5_dxy3_2metm", {
'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200353", 77),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200354", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200355", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200356", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200436", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200437", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200438", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200439", 94),
'qcdht0500_2017': (209, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210122_080124/0000/ntuple_%i.root' % i for i in [10, 37, 131, 162]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210124_094327/0000/ntuple_%i.root' % i for i in [52, 120]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200440/0000/ntuple_%i.root' % i for i in chain(xrange(11,13), xrange(23,26), xrange(29,35), xrange(41,46), xrange(49,51), xrange(56,58), xrange(68,71), xrange(74,76), xrange(89,91), xrange(104,106), xrange(107,109), xrange(125,128), xrange(167,170), xrange(177,181), xrange(186,191), xrange(192,197), xrange(200,202), [0, 2, 5, 15, 18, 38, 53, 59, 72, 79, 92, 98, 100, 111, 121, 139, 143, 146, 150, 158, 164, 173, 175, 182, 205, 208])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210123_095020/0000/ntuple_96.root'] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210122_131231/0000/ntuple_%i.root' % i for i in chain(xrange(3,5), xrange(7,10), xrange(16,18), xrange(19,23), xrange(26,29), xrange(35,37), xrange(46,49), xrange(54,56), xrange(62,68), xrange(80,89), xrange(93,96), xrange(101,104), xrange(109,111), xrange(112,120), xrange(122,125), xrange(128,131), xrange(132,139), xrange(140,143), xrange(144,146), xrange(147,150), xrange(151,158), xrange(160,162), xrange(165,167), xrange(170,173), xrange(183,186), xrange(197,200), xrange(202,205), xrange(206,208), [1, 14, 40, 51, 58, 60, 71, 73, 76, 78, 91, 97, 99, 106, 163, 174, 176, 181, 191])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210122_214152/0000/ntuple_%i.root' % i for i in [6, 13, 39, 61, 77, 159]]),
'ttbar_2017': _fromnum0("/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200441", 254),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200429", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200430", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200431", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200432", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200433", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200434", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200435", 2),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200357", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200358", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200359", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200400", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200401", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200402", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200403", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200404", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200405", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200406", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200407", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200408", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200409", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200410", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200411", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200412", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200413", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200414", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200415", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200416", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200417", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200418", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200419", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200420", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200421", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200422", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200423", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200424", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200425", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200426", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200427", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackpt0p5_dxy3_2METm_2017/210121_200428", 50),
})

_add_ds("ntuplev38metm", {
'qcdht0700_2017': (41, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210130_155203/0000/ntuple_%i.root' % i for i in chain(xrange(8,10), xrange(15,17), xrange(18,21), xrange(22,24), xrange(26,28), xrange(36,40), xrange(41,43), xrange(44,47), xrange(48,51), xrange(52,54), xrange(64,67), [0, 11, 13, 30, 55, 57, 62, 68, 74, 76])] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210131_095244/0000/ntuple_7.root'] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210131_201047/0000/ntuple_%i.root' % i for i in [1, 10]]),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210130_155204", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210130_155205", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210130_155206", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV38METm_2017/210130_155246", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV38METm_2017/210130_155247", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210130_155248", 75),
'qcdht0300_2017': (91, ['/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210130_155249/0000/ntuple_%i.root' % i for i in chain(xrange(12), xrange(13,25), xrange(26,37), xrange(38,44), xrange(45,94))] + ['/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210131_095246/0000/ntuple_25.root']),
'qcdht0500_2017': (131, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210131_201039/0000/ntuple_%i.root' % i for i in chain(xrange(17,19), xrange(99,102), xrange(125,127), xrange(156,158), [2, 9, 14, 21, 26, 41, 49, 68, 108, 110, 129, 139, 143, 192, 201, 203, 207])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210130_155250/0000/ntuple_%i.root' % i for i in chain(xrange(2), xrange(27,30), xrange(36,38), xrange(44,46), xrange(59,62), xrange(72,74), xrange(81,83), xrange(102,104), xrange(166,168), xrange(169,173), xrange(174,176), xrange(180,182), [7, 15, 19, 23, 40, 57, 63, 70, 75, 77, 87, 90, 94, 109, 111, 113, 128, 133, 146, 154, 161, 164, 204, 206, 208])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210131_161844/0000/ntuple_%i.root' % i for i in chain(xrange(91,94), [4, 13, 31, 47, 64, 66, 84, 86, 88, 114, 145, 152, 155, 159, 165, 179, 182])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210131_114904/0000/ntuple_%i.root' % i for i in [52, 104, 119, 124, 142, 148, 196, 200]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210131_111211/0000/ntuple_%i.root' % i for i in [115, 130, 199]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV38METm_2017/210131_095250/0000/ntuple_%i.root' % i for i in chain(xrange(55,57), xrange(150,152), [8, 20, 25, 38, 51, 62, 65, 83, 106, 112, 127, 163, 178, 184, 187, 202, 205])]),
'ttbar_2017': (252, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV38METm_2017/210130_155251/0000/ntuple_%i.root' % i for i in chain(xrange(66), xrange(67,108), xrange(109,234), xrange(235,254))] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV38METm_2017/210131_095242/0000/ntuple_108.root']),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleV38METm_2017/210130_155239", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleV38METm_2017/210130_155240", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleV38METm_2017/210130_155241", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleV38METm_2017/210130_155242", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleV38METm_2017/210130_155243", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleV38METm_2017/210130_155244", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleV38METm_2017/210130_155245", 2),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV38METm_2017/210130_155207", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleV38METm_2017/210130_155208", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleV38METm_2017/210130_155209", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleV38METm_2017/210130_155210", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleV38METm_2017/210130_155211", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleV38METm_2017/210130_155212", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV38METm_2017/210130_155213", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV38METm_2017/210130_155214", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV38METm_2017/210130_155215", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleV38METm_2017/210130_155216", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleV38METm_2017/210130_155217", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleV38METm_2017/210130_155218", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleV38METm_2017/210130_155219", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleV38METm_2017/210130_155220", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV38METm_2017/210130_155221", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV38METm_2017/210130_155222", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV38METm_2017/210130_155223", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleV38METm_2017/210130_155224", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleV38METm_2017/210130_155225", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleV38METm_2017/210130_155226", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleV38METm_2017/210130_155227", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleV38METm_2017/210130_155228", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV38METm_2017/210130_155229", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV38METm_2017/210130_155230", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV38METm_2017/210130_155231", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleV38METm_2017/210130_155232", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleV38METm_2017/210130_155233", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleV38METm_2017/210130_155234", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleV38METm_2017/210130_155235", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleV38METm_2017/210130_155236", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV38METm_2017/210130_155237", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV38METm_2017/210130_155238", 50),
})

_add_ds("ntuplev39metm", {
'mfv_splitSUSY_tau000001000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1400_1200_2017/NtupleV39METm_2017/210220_145922", 50),
'mfv_splitSUSY_tau000010000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1400_1200_2017/NtupleV39METm_2017/210220_145923", 50),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV39METm_2017/210220_145850", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleV39METm_2017/210220_145851", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleV39METm_2017/210220_145852", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleV39METm_2017/210220_145853", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleV39METm_2017/210220_145854", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleV39METm_2017/210220_145855", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV39METm_2017/210220_145856", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV39METm_2017/210220_145857", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV39METm_2017/210220_145858", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleV39METm_2017/210220_145859", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleV39METm_2017/210220_145900", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleV39METm_2017/210220_145901", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleV39METm_2017/210220_145902", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleV39METm_2017/210220_145903", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV39METm_2017/210220_145904", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV39METm_2017/210220_145905", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV39METm_2017/210220_145906", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleV39METm_2017/210220_145907", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleV39METm_2017/210220_145908", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleV39METm_2017/210220_145909", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleV39METm_2017/210220_145910", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleV39METm_2017/210220_145911", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV39METm_2017/210220_145912", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV39METm_2017/210220_145913", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV39METm_2017/210220_145914", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleV39METm_2017/210220_145915", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleV39METm_2017/210220_145916", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleV39METm_2017/210220_145917", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleV39METm_2017/210220_145918", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleV39METm_2017/210220_145919", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV39METm_2017/210220_145920", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV39METm_2017/210220_145921", 50),
})

_add_ds("ntuplevtrackattach_1metm", {
'qcdht0700_2017': (153, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210225_082635/0000/ntuple_%i.root' % i for i in chain(xrange(78,80), [2, 4, 8, 23, 35, 52, 67, 74, 81, 86, 122, 130, 136, 139, 152])] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210224_193557/0000/ntuple_%i.root' % i for i in chain(xrange(2), xrange(5,8), xrange(9,23), xrange(24,35), xrange(36,52), xrange(53,67), xrange(68,74), xrange(75,78), xrange(82,86), xrange(87,122), xrange(123,130), xrange(131,136), xrange(137,139), xrange(140,152), [3, 80])]),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210224_193558", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210224_193559", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210224_193600", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_1METm_2017/210224_193642", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_1METm_2017/210224_193643", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210224_193644", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210224_193645", 187),
'qcdht0500_2017': (347, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210225_134301/0000/ntuple_%i.root' % i for i in [48, 320, 325]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210224_193646/0000/ntuple_%i.root' % i for i in chain(xrange(13), xrange(14,21), xrange(22,48), xrange(51,65), xrange(66,110), xrange(111,114), xrange(115,129), xrange(130,155), xrange(156,164), xrange(165,267), xrange(268,320), xrange(321,325), xrange(326,346), [49])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_1METm_2017/210225_082628/0000/ntuple_%i.root' % i for i in [13, 21, 50, 65, 110, 114, 129, 155, 164, 267, 346]]),
'ttbar_2017': (508, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_1METm_2017/210225_082636/0000/ntuple_185.root'] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_1METm_2017/210224_193647/0000/ntuple_%i.root' % i for i in chain(xrange(185), xrange(186,508))]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackattach_1METm_2017/210224_193635", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackattach_1METm_2017/210224_193636", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackattach_1METm_2017/210224_193637", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackattach_1METm_2017/210224_193638", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackattach_1METm_2017/210224_193639", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackattach_1METm_2017/210224_193640", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackattach_1METm_2017/210224_193641", 2),
'mfv_splitSUSY_tau000001000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1400_1200_2017/NtupleVtrackattach_1METm_2017/210224_193438", 50),
'mfv_splitSUSY_tau000010000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1400_1200_2017/NtupleVtrackattach_1METm_2017/210224_193439", 50),
'mfv_splitSUSY_tau000001000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1100_2017/NtupleVtrackattach_1METm_2017/210226_085123", 50),
'mfv_splitSUSY_tau000010000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1100_2017/NtupleVtrackattach_1METm_2017/210226_085124", 50),
'mfv_splitSUSY_tau000001000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1200_2017/NtupleVtrackattach_1METm_2017/210226_085125", 50),
'mfv_splitSUSY_tau000010000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1200_2017/NtupleVtrackattach_1METm_2017/210226_085126", 50),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackattach_1METm_2017/210224_193406", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackattach_1METm_2017/210224_193407", 50),
'mfv_splitSUSY_tau100000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1800_2017/NtupleVtrackattach_1METm_2017/210224_193408", 50),
'mfv_splitSUSY_tau010000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1800_2017/NtupleVtrackattach_1METm_2017/210224_193409", 50),
'mfv_splitSUSY_tau001000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1800_2017/NtupleVtrackattach_1METm_2017/210224_193410", 50),
'mfv_splitSUSY_tau000100000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1800_2017/NtupleVtrackattach_1METm_2017/210224_193411", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackattach_1METm_2017/210224_193412", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackattach_1METm_2017/210224_193413", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackattach_1METm_2017/210224_193414", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackattach_1METm_2017/210224_193415", 50),
'mfv_splitSUSY_tau100000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2000_1900_2017/NtupleVtrackattach_1METm_2017/210224_193416", 50),
'mfv_splitSUSY_tau010000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2000_1900_2017/NtupleVtrackattach_1METm_2017/210224_193417", 49),
'mfv_splitSUSY_tau001000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2000_1900_2017/NtupleVtrackattach_1METm_2017/210224_193418", 49),
'mfv_splitSUSY_tau000100000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2000_1900_2017/NtupleVtrackattach_1METm_2017/210224_193419", 49),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackattach_1METm_2017/210224_193420", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackattach_1METm_2017/210224_193421", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackattach_1METm_2017/210224_193422", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackattach_1METm_2017/210224_193423", 50),
'mfv_splitSUSY_tau100000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_100_2017/NtupleVtrackattach_1METm_2017/210224_193424", 50),
'mfv_splitSUSY_tau010000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_100_2017/NtupleVtrackattach_1METm_2017/210224_193425", 50),
'mfv_splitSUSY_tau001000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_100_2017/NtupleVtrackattach_1METm_2017/210224_193426", 50),
'mfv_splitSUSY_tau000100000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_100_2017/NtupleVtrackattach_1METm_2017/210224_193427", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackattach_1METm_2017/210224_193428", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackattach_1METm_2017/210224_193429", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackattach_1METm_2017/210224_193430", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackattach_1METm_2017/210224_193431", 50),
'mfv_splitSUSY_tau100000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau100000000um_M2400_2300_2017/NtupleVtrackattach_1METm_2017/210224_193432", 49),
'mfv_splitSUSY_tau010000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau010000000um_M2400_2300_2017/NtupleVtrackattach_1METm_2017/210224_193433", 50),
'mfv_splitSUSY_tau001000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau001000000um_M2400_2300_2017/NtupleVtrackattach_1METm_2017/210224_193434", 50),
'mfv_splitSUSY_tau000100000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000100000um_M2400_2300_2017/NtupleVtrackattach_1METm_2017/210224_193435", 49),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackattach_1METm_2017/210224_193436", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackattach_1METm_2017/210224_193437", 50),
})

_add_ds("ntuplevtrackattach_2metm", {
'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_115821", 153),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_115822", 113),
'qcdht1500_2017': (250, ['/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_115823/0000/ntuple_%i.root' % i for i in chain(xrange(131), xrange(132,250))] + ['/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_212032/0000/ntuple_131.root']),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_115824", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_2METm_2017/210227_115854", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_2METm_2017/210227_115855", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_115856", 75),
'qcdht0300_2017': (187, ['/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_115857/0000/ntuple_%i.root' % i for i in chain(xrange(97), xrange(98,187))] + ['/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_212031/0000/ntuple_97.root']),
'qcdht0500_2017': (347, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_115858/0000/ntuple_%i.root' % i for i in chain(xrange(17), xrange(18,98), xrange(99,340), xrange(341,347))] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210227_212035/0000/ntuple_%i.root' % i for i in [17, 98]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2METm_2017/210228_103206/0000/ntuple_340.root']),
'ttbar_2017': (496, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_2METm_2017/210227_115859/0000/ntuple_%i.root' % i for i in chain(xrange(21), xrange(22,28), xrange(29,44), xrange(45,54), xrange(55,85), xrange(86,88), xrange(89,101), xrange(102,118), xrange(119,211), xrange(214,314), xrange(315,487), xrange(488,508), [212])]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackattach_2METm_2017/210227_115847", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackattach_2METm_2017/210227_115848", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackattach_2METm_2017/210227_115849", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackattach_2METm_2017/210227_115850", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackattach_2METm_2017/210227_115851", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackattach_2METm_2017/210227_115852", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackattach_2METm_2017/210227_115853", 2),
'mfv_splitSUSY_tau000001000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1400_1200_2017/NtupleVtrackattach_2METm_2017/210227_115841", 50),
'mfv_splitSUSY_tau000010000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1400_1200_2017/NtupleVtrackattach_2METm_2017/210227_115844", 50),
'mfv_splitSUSY_tau000001000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1100_2017/NtupleVtrackattach_2METm_2017/210227_115843", 50),
'mfv_splitSUSY_tau000010000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1100_2017/NtupleVtrackattach_2METm_2017/210227_115846", 50),
'mfv_splitSUSY_tau000001000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1200_2017/NtupleVtrackattach_2METm_2017/210227_115842", 50),
'mfv_splitSUSY_tau000010000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1200_2017/NtupleVtrackattach_2METm_2017/210227_115845", 50),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackattach_2METm_2017/210227_115825", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackattach_2METm_2017/210227_115829", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackattach_2METm_2017/210227_115837", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackattach_2METm_2017/210227_115833", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackattach_2METm_2017/210227_115826", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackattach_2METm_2017/210227_115830", 50),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackattach_2METm_2017/210227_115838", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackattach_2METm_2017/210227_115834", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackattach_2METm_2017/210227_115827", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackattach_2METm_2017/210227_115831", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackattach_2METm_2017/210227_115839", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackattach_2METm_2017/210227_115835", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackattach_2METm_2017/210227_115828", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackattach_2METm_2017/210227_115832", 50),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackattach_2METm_2017/210227_115840", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackattach_2METm_2017/210227_115836", 50),
})

_add_ds("ntuplevtrackattach_2p5metm", {
'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120325", 153),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120326", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120327", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120328", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120358", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120359", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120400", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120401", 187),
'qcdht0500_2017': (346, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120402/0000/ntuple_%i.root' % i for i in chain(xrange(67), xrange(70,98), xrange(99,119), xrange(120,125), xrange(126,129), xrange(131,139), xrange(140,142), xrange(144,146), xrange(149,152), xrange(154,156), xrange(157,159), xrange(160,164), xrange(167,172), xrange(174,188), xrange(191,223), xrange(224,226), xrange(232,234), xrange(235,245), xrange(246,257), xrange(258,265), xrange(267,270), xrange(271,273), xrange(281,288), xrange(289,294), xrange(296,299), xrange(304,307), xrange(308,317), xrange(318,320), xrange(321,329), xrange(330,333), xrange(334,342), xrange(343,347), [68, 147, 165, 189, 227, 230, 274, 276, 300, 302])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_2p5METm_2017/210301_080909/0000/ntuple_%i.root' % i for i in chain(xrange(129,131), xrange(142,144), xrange(152,154), xrange(172,174), xrange(228,230), xrange(265,267), xrange(277,281), xrange(294,296), [67, 69, 98, 119, 125, 139, 146, 148, 156, 159, 164, 166, 188, 223, 226, 231, 234, 245, 257, 270, 273, 275, 288, 299, 301, 303, 307, 317, 320, 329, 333, 342])]),
'ttbar_2017': (508, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_2p5METm_2017/210301_080901/0000/ntuple_%i.root' % i for i in [364, 445]] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_2p5METm_2017/210228_103306/0000/ntuple_%i.root' % i for i in [69, 153, 178, 370, 422, 430]] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_2p5METm_2017/210227_120403/0000/ntuple_%i.root' % i for i in chain(xrange(69), xrange(70,153), xrange(154,178), xrange(179,364), xrange(365,370), xrange(371,422), xrange(423,430), xrange(431,445), xrange(446,508))]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackattach_2p5METm_2017/210227_120351", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackattach_2p5METm_2017/210227_120352", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackattach_2p5METm_2017/210227_120353", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackattach_2p5METm_2017/210227_120354", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackattach_2p5METm_2017/210227_120355", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackattach_2p5METm_2017/210227_120356", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackattach_2p5METm_2017/210227_120357", 2),
'mfv_splitSUSY_tau000001000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1400_1200_2017/NtupleVtrackattach_2p5METm_2017/210227_120345", 50),
'mfv_splitSUSY_tau000010000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1400_1200_2017/NtupleVtrackattach_2p5METm_2017/210227_120348", 50),
'mfv_splitSUSY_tau000001000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1100_2017/NtupleVtrackattach_2p5METm_2017/210227_120347", 50),
'mfv_splitSUSY_tau000010000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1100_2017/NtupleVtrackattach_2p5METm_2017/210227_120350", 50),
'mfv_splitSUSY_tau000001000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1200_2017/NtupleVtrackattach_2p5METm_2017/210227_120346", 50),
'mfv_splitSUSY_tau000010000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1200_2017/NtupleVtrackattach_2p5METm_2017/210227_120349", 50),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackattach_2p5METm_2017/210227_120329", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackattach_2p5METm_2017/210227_120333", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackattach_2p5METm_2017/210227_120341", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackattach_2p5METm_2017/210227_120337", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackattach_2p5METm_2017/210227_120330", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackattach_2p5METm_2017/210227_120334", 50),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackattach_2p5METm_2017/210227_120342", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackattach_2p5METm_2017/210227_120338", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackattach_2p5METm_2017/210227_120331", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackattach_2p5METm_2017/210227_120335", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackattach_2p5METm_2017/210227_120343", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackattach_2p5METm_2017/210227_120339", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackattach_2p5METm_2017/210227_120332", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackattach_2p5METm_2017/210227_120336", 50),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackattach_2p5METm_2017/210227_120344", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackattach_2p5METm_2017/210227_120340", 50),
})

_add_ds("ntuplevtrackattach_3metm", {
'qcdht0700_2017': _fromnum0("/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210227_120033", 153),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210227_120034", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210227_120035", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210227_120036", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_3METm_2017/210227_120106", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_3METm_2017/210227_120107", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210227_120108", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210227_120109", 187),
'qcdht0500_2017': (346, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210301_081046/0000/ntuple_%i.root' % i for i in chain(xrange(29,32), xrange(44,46), xrange(47,49), xrange(110,112), xrange(119,121), xrange(127,129), xrange(167,169), xrange(192,194), xrange(195,197), xrange(209,212), xrange(233,235), xrange(247,249), xrange(254,256), xrange(257,259), [9, 20, 33, 36, 52, 57, 61, 66, 74, 96, 98, 116, 138, 152, 156, 158, 160, 171, 173, 179, 185, 187, 199, 216, 223, 228, 231, 236, 244, 264, 266, 277])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210301_123538/0000/ntuple_%i.root' % i for i in [154, 181]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3METm_2017/210227_120110/0000/ntuple_%i.root' % i for i in chain(xrange(9), xrange(10,20), xrange(21,29), xrange(34,36), xrange(37,44), xrange(49,52), xrange(53,57), xrange(58,61), xrange(62,66), xrange(67,74), xrange(75,83), xrange(84,96), xrange(99,110), xrange(112,116), xrange(117,119), xrange(121,127), xrange(129,138), xrange(139,152), xrange(161,167), xrange(169,171), xrange(174,179), xrange(182,185), xrange(188,192), xrange(197,199), xrange(200,209), xrange(212,216), xrange(217,223), xrange(224,228), xrange(229,231), xrange(237,244), xrange(245,247), xrange(249,254), xrange(259,264), xrange(267,277), xrange(278,347), [32, 46, 97, 153, 155, 157, 159, 172, 180, 186, 194, 232, 235, 256, 265])]),
'ttbar_2017': (491, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_3METm_2017/210227_120111/0000/ntuple_%i.root' % i for i in chain(xrange(8), xrange(9,20), xrange(21,41), xrange(42,70), xrange(71,146), xrange(149,152), xrange(153,161), xrange(162,167), xrange(168,178), xrange(181,199), xrange(200,245), xrange(246,260), xrange(261,302), xrange(303,460), xrange(461,508), [179])]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackattach_3METm_2017/210227_120059", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackattach_3METm_2017/210227_120100", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackattach_3METm_2017/210227_120101", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackattach_3METm_2017/210227_120102", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackattach_3METm_2017/210227_120103", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackattach_3METm_2017/210227_120104", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackattach_3METm_2017/210227_120105", 2),
'mfv_splitSUSY_tau000001000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1400_1200_2017/NtupleVtrackattach_3METm_2017/210227_120053", 50),
'mfv_splitSUSY_tau000010000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1400_1200_2017/NtupleVtrackattach_3METm_2017/210227_120056", 50),
'mfv_splitSUSY_tau000001000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1100_2017/NtupleVtrackattach_3METm_2017/210227_120055", 50),
'mfv_splitSUSY_tau000010000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1100_2017/NtupleVtrackattach_3METm_2017/210227_120058", 50),
'mfv_splitSUSY_tau000001000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1200_2017/NtupleVtrackattach_3METm_2017/210227_120054", 50),
'mfv_splitSUSY_tau000010000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1200_2017/NtupleVtrackattach_3METm_2017/210227_120057", 50),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackattach_3METm_2017/210227_120037", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackattach_3METm_2017/210227_120041", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackattach_3METm_2017/210227_120049", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackattach_3METm_2017/210227_120045", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackattach_3METm_2017/210227_120038", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackattach_3METm_2017/210227_120042", 50),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackattach_3METm_2017/210227_120050", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackattach_3METm_2017/210227_120046", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackattach_3METm_2017/210227_120039", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackattach_3METm_2017/210227_120043", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackattach_3METm_2017/210227_120051", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackattach_3METm_2017/210227_120047", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackattach_3METm_2017/210227_120040", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackattach_3METm_2017/210227_120044", 50),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackattach_3METm_2017/210227_120052", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackattach_3METm_2017/210227_120048", 50),
})

_add_ds("ntuplev40metm", {
'qcdht0700_2017': (153, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_110121/0000/ntuple_%i.root' % i for i in chain(xrange(54), xrange(55,153))] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_190702/0000/ntuple_54.root']),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_110122", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_110123", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_110124", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV40METm_2017/210226_110154", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV40METm_2017/210226_110155", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_110156", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_110157", 187),
'qcdht0500_2017': (347, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_110158/0000/ntuple_%i.root' % i for i in chain(xrange(25), xrange(26,67), xrange(68,91), xrange(92,94), xrange(95,192), xrange(193,299), xrange(300,303), xrange(304,347))] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV40METm_2017/210226_190700/0000/ntuple_%i.root' % i for i in [25, 67, 91, 94, 192, 299, 303]]),
'ttbar_2017': (508, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV40METm_2017/210226_190703/0000/ntuple_%i.root' % i for i in chain(xrange(65,67), xrange(227,229), xrange(335,337), xrange(352,354), xrange(480,482), [15, 43, 61, 75, 77, 87, 91, 111, 116, 129, 132, 155, 157, 160, 174, 183, 198, 205, 213, 217, 222, 270, 289, 345, 391, 406, 439, 457, 478, 487, 507])] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV40METm_2017/210226_110159/0000/ntuple_%i.root' % i for i in chain(xrange(15), xrange(16,43), xrange(44,61), xrange(62,65), xrange(67,75), xrange(78,87), xrange(88,91), xrange(92,111), xrange(112,116), xrange(117,129), xrange(130,132), xrange(133,155), xrange(158,160), xrange(161,174), xrange(175,183), xrange(184,198), xrange(199,205), xrange(206,213), xrange(214,217), xrange(218,222), xrange(223,227), xrange(229,270), xrange(271,289), xrange(290,335), xrange(337,345), xrange(346,352), xrange(354,391), xrange(392,406), xrange(407,439), xrange(440,457), xrange(458,478), xrange(482,487), xrange(488,507), [76, 156, 479])]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleV40METm_2017/210226_110147", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleV40METm_2017/210226_110148", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleV40METm_2017/210226_110149", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleV40METm_2017/210226_110150", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleV40METm_2017/210226_110151", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleV40METm_2017/210226_110152", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleV40METm_2017/210226_110153", 2),
'mfv_splitSUSY_tau000001000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1400_1200_2017/NtupleV40METm_2017/210226_110141", 50),
'mfv_splitSUSY_tau000010000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1400_1200_2017/NtupleV40METm_2017/210226_110144", 50),
'mfv_splitSUSY_tau000001000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1100_2017/NtupleV40METm_2017/210226_110143", 50),
'mfv_splitSUSY_tau000010000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1100_2017/NtupleV40METm_2017/210226_110146", 50),
'mfv_splitSUSY_tau000001000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1200_2017/NtupleV40METm_2017/210226_110142", 50),
'mfv_splitSUSY_tau000010000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1200_2017/NtupleV40METm_2017/210226_110145", 50),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV40METm_2017/210226_110125", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleV40METm_2017/210226_110129", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV40METm_2017/210226_110137", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV40METm_2017/210226_110133", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV40METm_2017/210226_110126", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleV40METm_2017/210226_110130", 50),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV40METm_2017/210226_110138", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV40METm_2017/210226_110134", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV40METm_2017/210226_110127", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleV40METm_2017/210226_110131", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV40METm_2017/210226_110139", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV40METm_2017/210226_110135", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV40METm_2017/210226_110128", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleV40METm_2017/210226_110132", 50),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV40METm_2017/210226_110140", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV40METm_2017/210226_110136", 50),
})

_add_ds("ntuplevtrackattach_3p5metm", {
'qcdht0700_2017': (153, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120626/0000/ntuple_%i.root' % i for i in chain(xrange(114), xrange(115,153))] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210301_081057/0000/ntuple_114.root']),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120627", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120628", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120629", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120659", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120700", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120701", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120702", 187),
'qcdht0500_2017': (343, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120703/0000/ntuple_%i.root' % i for i in chain(xrange(20), xrange(21,67), xrange(68,75), xrange(76,83), xrange(84,89), xrange(91,96), xrange(97,110), xrange(111,114), xrange(115,124), xrange(125,127), xrange(130,135), xrange(137,147), xrange(149,152), xrange(154,156), xrange(157,179), xrange(180,182), xrange(184,188), xrange(189,196), xrange(197,201), xrange(202,207), xrange(208,212), xrange(213,228), xrange(232,236), xrange(238,242), xrange(243,245), xrange(246,250), xrange(251,256), xrange(257,262), xrange(272,281), xrange(282,288), xrange(289,292), xrange(297,299), xrange(300,313), xrange(314,317), xrange(318,324), xrange(325,333), xrange(334,338), xrange(341,343), [128, 230, 263, 267, 269, 293, 295, 344, 346])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210301_112446/0000/ntuple_%i.root' % i for i in [317, 345]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleVtrackattach_3p5METm_2017/210301_081042/0000/ntuple_%i.root' % i for i in chain(xrange(89,91), xrange(135,137), xrange(147,149), xrange(152,154), xrange(182,184), xrange(228,230), xrange(236,238), xrange(264,267), xrange(338,341), [20, 67, 75, 96, 110, 114, 124, 127, 129, 156, 179, 188, 196, 201, 207, 212, 231, 242, 245, 250, 256, 262, 270, 281, 292, 294, 296, 299, 313, 324, 333, 343])]),
'ttbar_2017': (507, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_3p5METm_2017/210227_120704/0000/ntuple_%i.root' % i for i in chain(xrange(34), xrange(35,60), xrange(61,354), xrange(355,373), xrange(374,379), xrange(381,396), xrange(399,411), xrange(412,417), xrange(418,447), xrange(449,486), xrange(489,508), [397, 487])] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleVtrackattach_3p5METm_2017/210301_081053/0000/ntuple_%i.root' % i for i in chain(xrange(379,381), xrange(447,449), [34, 354, 373, 396, 398, 411, 417, 486, 488])]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleVtrackattach_3p5METm_2017/210227_120652", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleVtrackattach_3p5METm_2017/210227_120653", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleVtrackattach_3p5METm_2017/210227_120654", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleVtrackattach_3p5METm_2017/210227_120655", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleVtrackattach_3p5METm_2017/210227_120656", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleVtrackattach_3p5METm_2017/210227_120657", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleVtrackattach_3p5METm_2017/210227_120658", 2),
'mfv_splitSUSY_tau000001000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1400_1200_2017/NtupleVtrackattach_3p5METm_2017/210227_120646", 50),
'mfv_splitSUSY_tau000010000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1400_1200_2017/NtupleVtrackattach_3p5METm_2017/210227_120649", 50),
'mfv_splitSUSY_tau000001000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1100_2017/NtupleVtrackattach_3p5METm_2017/210227_120648", 50),
'mfv_splitSUSY_tau000010000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1100_2017/NtupleVtrackattach_3p5METm_2017/210227_120651", 50),
'mfv_splitSUSY_tau000001000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1200_2017/NtupleVtrackattach_3p5METm_2017/210227_120647", 50),
'mfv_splitSUSY_tau000010000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1200_2017/NtupleVtrackattach_3p5METm_2017/210227_120650", 50),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleVtrackattach_3p5METm_2017/210227_120630", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleVtrackattach_3p5METm_2017/210227_120634", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleVtrackattach_3p5METm_2017/210227_120642", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleVtrackattach_3p5METm_2017/210227_120638", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleVtrackattach_3p5METm_2017/210227_120631", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleVtrackattach_3p5METm_2017/210227_120635", 50),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleVtrackattach_3p5METm_2017/210227_120643", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleVtrackattach_3p5METm_2017/210227_120639", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleVtrackattach_3p5METm_2017/210227_120632", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleVtrackattach_3p5METm_2017/210227_120636", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleVtrackattach_3p5METm_2017/210227_120644", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleVtrackattach_3p5METm_2017/210227_120640", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleVtrackattach_3p5METm_2017/210227_120633", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleVtrackattach_3p5METm_2017/210227_120637", 50),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleVtrackattach_3p5METm_2017/210227_120645", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleVtrackattach_3p5METm_2017/210227_120641", 50),
})

_add_ds("ntuplev41metm", {
'qcdht0700_2017': (153, ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_210909/0000/ntuple_43.root'] + ['/store/user/ali/QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_145037/0000/ntuple_%i.root' % i for i in chain(xrange(43), xrange(44,153))]),
'qcdht1000_2017': _fromnum0("/store/user/ali/QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_145038", 113),
'qcdht1500_2017': _fromnum0("/store/user/ali/QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_145039", 250),
'qcdht2000_2017': _fromnum0("/store/user/ali/QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_145040", 147),
'wjetstolnu_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV41METm_2017/210302_145110", 52),
'wjetstolnuext_2017': _fromnum0("/store/user/ali/WJetsToLNu_TuneCP5_13TeV-madgraphMLM-pythia8/NtupleV41METm_2017/210302_145111", 74),
'qcdht0200_2017': _fromnum0("/store/user/ali/QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_145112", 75),
'qcdht0300_2017': _fromnum0("/store/user/ali/QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_145113", 187),
'qcdht0500_2017': (346, ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210303_110058/0000/ntuple_329.root'] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_145114/0000/ntuple_%i.root' % i for i in chain(xrange(31), xrange(32,82), xrange(83,161), xrange(162,190), xrange(191,229), xrange(230,242), xrange(243,264), xrange(265,274), xrange(275,283), xrange(284,294), xrange(297,329), xrange(330,347), [295])] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210303_064613/0000/ntuple_%i.root' % i for i in [161, 190, 229, 242, 264, 274, 283, 294, 296]] + ['/store/user/ali/QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8/NtupleV41METm_2017/210302_210907/0000/ntuple_31.root']),
'ttbar_2017': (508, ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV41METm_2017/210303_064611/0000/ntuple_233.root'] + ['/store/user/ali/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/NtupleV41METm_2017/210302_145115/0000/ntuple_%i.root' % i for i in chain(xrange(233), xrange(234,508))]),
'zjetstonunuht0100_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-100To200_13TeV-madgraph/NtupleV41METm_2017/210302_145103", 29),
'zjetstonunuht0200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-200To400_13TeV-madgraph/NtupleV41METm_2017/210302_145104", 30),
'zjetstonunuht0400_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-400To600_13TeV-madgraph/NtupleV41METm_2017/210302_145105", 16),
'zjetstonunuht0600_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-600To800_13TeV-madgraph/NtupleV41METm_2017/210302_145106", 9),
'zjetstonunuht0800_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-800To1200_13TeV-madgraph/NtupleV41METm_2017/210302_145107", 5),
'zjetstonunuht1200_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-1200To2500_13TeV-madgraph/NtupleV41METm_2017/210302_145108", 4),
'zjetstonunuht2500_2017': _fromnum0("/store/user/ali/ZJetsToNuNu_HT-2500ToInf_13TeV-madgraph/NtupleV41METm_2017/210302_145109", 2),
'mfv_splitSUSY_tau000001000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1400_1200_2017/NtupleV41METm_2017/210302_145057", 50),
'mfv_splitSUSY_tau000010000um_M1400_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1400_1200_2017/NtupleV41METm_2017/210302_145100", 50),
'mfv_splitSUSY_tau000001000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1100_2017/NtupleV41METm_2017/210302_145059", 50),
'mfv_splitSUSY_tau000010000um_M1200_1100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1100_2017/NtupleV41METm_2017/210302_145102", 50),
'mfv_splitSUSY_tau000001000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M1200_1200_2017/NtupleV41METm_2017/210302_145058", 50),
'mfv_splitSUSY_tau000010000um_M1200_1200_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M1200_1200_2017/NtupleV41METm_2017/210302_145101", 50),
'mfv_splitSUSY_tau000000000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1800_2017/NtupleV41METm_2017/210302_145041", 50),
'mfv_splitSUSY_tau000000300um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1800_2017/NtupleV41METm_2017/210302_145045", 50),
'mfv_splitSUSY_tau000010000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1800_2017/NtupleV41METm_2017/210302_145053", 50),
'mfv_splitSUSY_tau000001000um_M2000_1800_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1800_2017/NtupleV41METm_2017/210302_145049", 50),
'mfv_splitSUSY_tau000000000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2000_1900_2017/NtupleV41METm_2017/210302_145042", 50),
'mfv_splitSUSY_tau000000300um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2000_1900_2017/NtupleV41METm_2017/210302_145046", 50),
'mfv_splitSUSY_tau000010000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2000_1900_2017/NtupleV41METm_2017/210302_145054", 49),
'mfv_splitSUSY_tau000001000um_M2000_1900_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2000_1900_2017/NtupleV41METm_2017/210302_145050", 49),
'mfv_splitSUSY_tau000000000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_100_2017/NtupleV41METm_2017/210302_145043", 50),
'mfv_splitSUSY_tau000000300um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_100_2017/NtupleV41METm_2017/210302_145047", 50),
'mfv_splitSUSY_tau000010000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_100_2017/NtupleV41METm_2017/210302_145055", 49),
'mfv_splitSUSY_tau000001000um_M2400_100_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_100_2017/NtupleV41METm_2017/210302_145051", 49),
'mfv_splitSUSY_tau000000000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000000um_M2400_2300_2017/NtupleV41METm_2017/210302_145044", 50),
'mfv_splitSUSY_tau000000300um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000000300um_M2400_2300_2017/NtupleV41METm_2017/210302_145048", 50),
'mfv_splitSUSY_tau000010000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000010000um_M2400_2300_2017/NtupleV41METm_2017/210302_145056", 49),
'mfv_splitSUSY_tau000001000um_M2400_2300_2017': _fromnum0("/store/user/ali/mfv_splitSUSY_tau000001000um_M2400_2300_2017/NtupleV41METm_2017/210302_145052", 50),
})

################################################################################

if __name__ == '__main__':
    import sys, re

    def _printlist(l):
        for x in l:
            print x

    def _args(x, *names):
        n = len(names)
        i = sys.argv.index(x)
        if len(sys.argv) < i+n+1 or sys.argv[i+1] in ('-h','--help','help'):
            sys.exit('usage: %s %s %s' % (sys.argv[0], x, ' '.join(names)))
        return tuple(sys.argv[i+j] for j in xrange(1,n+1))
    def _arg(x,name):
        return _args(x,name)[0]

    if 'enc' in sys.argv:
        dataset, sample, listfn = _args('enc', 'dataset','sample','listfn')
        fns = [x.strip() for x in open(listfn).read().split('\n') if x.strip()]
        n = len(fns)
        print '# %s, %s, %i files' % (sample, dataset, n)
        print '_add(%r)' % _enc({(sample,dataset):(n,fns)})

    elif 'testfiles' in sys.argv:
        dataset, sample = _args('testfiles', 'dataset','sample')
        is_ntuple = dataset.startswith('ntuple')
        from JMTucker.Tools.ROOTTools import ROOT
        print sample, dataset
        nev, nev2 = 0, 0
        def get_n(f,p):
            try:
                return f.Get(p).GetEntries()
            except ReferenceError:
                return 1e99
        for fn in get(sample, dataset)[1]:
            n = get_n(ROOT.TFile.Open('root://cmseos.fnal.gov/' + fn), 'Events')
            nev += n
            if is_ntuple:
                n2 = get_n(ROOT.TFile.Open('root://cmseos.fnal.gov/' + fn.replace('ntuple', 'vertex_histos')), 'mfvVertices/h_n_all_tracks')
                nev2 += n2
                print fn, n, n2
            else:
                print fn, n
        print 'total:', nev, 'events',
        if is_ntuple:
            print nev2, 'in vertex_histos h_n_all_tracks',
        print

    elif 'forcopy' in sys.argv:
        dataset, sample = _args('forcopy', 'dataset','sample')
        if not has(sample, dataset):
            raise KeyError('no key sample = %s dataset = %s' % (sample, dataset))
        print sample, dataset
        from JMTucker.Tools import eos
        out_fn = '%s_%s' % (sample, dataset)
        out_f = open(out_fn, 'wt')
        out_f.write('copy\n')
        for fn in get(sample, dataset)[1]:
            md5sum = eos.md5sum(fn)
            x = '%s  %s\n' % (md5sum, fn)
            out_f.write(x)
            print x,
        out_f.close()

    elif 'fordelete' in sys.argv:
        dataset, sample = _args('fordelete', 'dataset','sample')
        if not has(sample, dataset):
            raise KeyError('no key sample = %s dataset = %s' % (sample, dataset))
        print sample, dataset
        from JMTucker.Tools import eos
        out_fn = '%s_%s' % (sample, dataset)
        out_f = open(out_fn, 'wt')
        out_f.write('delete\n%s\n' % '\n'.join(get(sample, dataset)[1]))
        out_f.close()

    elif 'dump' in sys.argv:
        dump()

    elif 'summary' in sys.argv:
        summary()

    elif 'datasets' in sys.argv:
        _printlist(sorted(set(ds for _, ds in _d.keys())))

    elif 'samples' in sys.argv:
        _printlist(sorted(set(name for name, ds in _d.keys() if ds == _arg('samples', 'dataset'))))

    elif 'files' in sys.argv:
        dataset, sample = _args('files', 'dataset','sample')
        _printlist(sorted(get(sample, dataset)[1]))

    elif 'allfiles' in sys.argv:
        _printlist(sorted(allfiles()))

    elif 'otherfiles' in sys.argv:
        list_fn = _arg('otherfiles', 'list_fn')
        other_fns = set()
        for line in open(list_fn):
            line = line.strip()
            if line.endswith('.root'):
                assert '/store' in line
                other_fns.add(line.replace('/eos/uscms', ''))
        all_fns = set(allfiles())
        print 'root files in %s not in SampleFiles:' % list_fn
        _printlist(sorted(other_fns - all_fns))
        print 'root files in SampleFiles not in %s:' % list_fn
        _printlist(sorted(all_fns - other_fns))

    elif 'filematch' in sys.argv:
        pattern = _arg('filematch', 'pattern')
        for (sample, dataset), (_, fns) in _d.iteritems():
            for fn in fns:
                if fnmatch(fn, pattern):
                    print sample, dataset, fn

    elif 'dirs' in sys.argv:
        dataset, sample = _args('dirs', 'dataset','sample')
        fns = get(sample, dataset)[1]
        path_re = re.compile(r'(/store.*/\d{6}_\d{6})/')
        _printlist(sorted(set(path_re.search(fn).group(1) for fn in fns)))
        # for x in ttbar qcdht0700 qcdht1000 qcdht1500 qcdht2000 wjetstolnu dyjetstollM10 dyjetstollM50 qcdmupt15 ; echo $x $(eosdu $(samplefiles dirs  ntuplev18m ${x}_2017) )

    elif 'whosummary' in sys.argv:
        whosummary = defaultdict(list)
        for k in _d:
            users = who(*k)
            if users:
                whosummary[users].append(k)
        print 'by user(s):'
        for users, dses in whosummary.iteritems():
            dses.sort()
            print ' + '.join(users)
            for ds in dses:
                print '    ', ds

    elif 'who' in sys.argv:
        dataset, sample = _args('who', 'dataset','sample')
        print ' + '.join(who(sample, dataset))

    elif 'sync' in sys.argv:
        from JMTucker.Tools import Samples
        in_sf_not_s = []
        in_s_not_sf = []

        for k in _d.iterkeys():
            name, ds = k
            if not hasattr(Samples, name) or not getattr(Samples, name).has_dataset(ds):
                in_sf_not_s.append(k)

        for s in Samples.registry.all():
            for ds in s.datasets:
                k = s.name, ds
                if not _d.has_key(k):
                    in_s_not_sf.append(k)

        print '%-45s %25s %10s' % ('in SampleFiles but not Samples:', '', 'enced?')
        for k in sorted(in_sf_not_s):
            name, ds = k
            print '%-45s %25s %10i' % (name, ds, _added_from_enc.get(k, -1))
        print
        print '%-45s %25s' % ('in Samples but not SampleFiles:', '')
        for k in sorted(in_s_not_sf):
            print '%-45s %25s' % k

    elif 'removed' in sys.argv:
        import colors
        def ok(fn):
            assert fn.startswith('/store') and fn.endswith('.root')
            ret = os.system('xrdcp -sf root://cmsxrootd-site.fnal.gov/%s /dev/null' % fn)
            if ret != 0:
                ret = os.system('xrdcp -sf root://cmseos.fnal.gov/%s /dev/null' % fn)
            return ret == 0
        print colors.boldred('red means the file is OK,'), colors.green('green means it should stay in the removed list')
        for name, ds, fns in _removed:
            for fn in fns:
                print (colors.boldred if ok(fn) else colors.green)('%s %s %s' % (name, ds, fn))

    else:
        if not (len(sys.argv) == 1 and sys.argv[0].endswith('/SampleFiles.py')):
            sys.exit('did not understand argv %r' % sys.argv)
