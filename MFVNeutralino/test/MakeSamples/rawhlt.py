# https://twiki.cern.ch/twiki/bin/view/CMS/PdmVMCcampaignRunIIFall17DRPremix
# https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/EXO-RunIIFall17DRPremix-02035
# 9_4_7 cmsDriver.py step1 --filein "dbs:/GluinoGluinoToNeutralinoNeutralinoTo2T2B2S_M-1600_CTau-300um_TuneCP2_13TeV-pythia8/RunIIFall17GS-93X_mc2017_realistic_v3-v1/GEN-SIM" --fileout file:EXO-RunIIFall17DRPremix-02035_step1.root  --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MCv2_correctPU_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW" --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 94X_mc2017_realistic_v11 --step DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:2e34v40 --nThreads 8 --datamix PreMix --era Run2_2017 --python_filename EXO-RunIIFall17DRPremix-02035_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 1751
# https://twiki.cern.ch/twiki/bin/view/CMS/PdmVCampaignRunIIAutumn18DRPremix
# https://cms-pdmv.cern.ch/mcm/public/restapi/requests/get_test/EXO-RunIIAutumn18DRPremix-00193
# 10_2_6 cmsDriver.py step1 --filein "dbs:/StopStopbarTo2Dbar2D_M-200_CTau-10mm_TuneCP2_13TeV_2018-pythia8/RunIIFall18GS-102X_upgrade2018_realistic_v11-v1/GEN-SIM" --fileout file:EXO-RunIIAutumn18DRPremix-00193_step1.root  --pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-PUAutumn18_102X_upgrade2018_realistic_v15-v1/GEN-SIM-DIGI-RAW" --mc --eventcontent PREMIXRAW --datatier GEN-SIM-RAW --conditions 102X_upgrade2018_realistic_v15 --step DIGI,DATAMIX,L1,DIGI2RAW,HLT:@relval2018 --procModifiers premix_stage2 --nThreads 8 --geometry DB:Extended --datamix PreMix --era Run2_2018 --python_filename EXO-RunIIAutumn18DRPremix-00193_1_cfg.py --no_exec --customise Configuration/DataProcessing/Utils.addMonitoring -n 2626

import sys, FWCore.ParameterSet.Config as cms, dynamicconf

randomize = 'norandomize' not in sys.argv
expectedevents = 100
salt = ''
premix = True
trigfilter = False
trigfilterpath = 'HLT_PFHT1050_v14'
jobnum = 1

for arg in sys.argv:
    if arg.startswith('salt='):
        salt = arg.replace('salt=','')
    elif arg.startswith('jobnum='):
        jobnum = int(arg.replace('jobnum=',''))
    elif arg.startswith('expectedevents='):
        jobnum = int(arg.replace('expectedevents=',''))
    elif arg.startswith('premix='):
        premix = arg.replace('premix=','') == '1'
    elif arg.startswith('trigfilter='):
        trigfilter = arg.replace('trigfilter=','') == '1'

process = dynamicconf.process()

process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
if premix:
    process.load('SimGeneral.MixingModule.mixNoPU_cfi')
    if dynamicconf.year == 2017:
        process.load('Configuration.StandardSequences.DigiDMPreMix_cff')
        process.load('SimGeneral.MixingModule.digi_MixPreMix_cfi')
    else:
        process.load('Configuration.StandardSequences.DigiDM_cff')
    process.load('Configuration.StandardSequences.DataMixerPreMix_cff')
    process.load('Configuration.StandardSequences.SimL1EmulatorDM_cff')
    process.load('Configuration.StandardSequences.DigiToRawDM_cff')
else:
    raise NotImplementedError('need to set up non-premix')

if dynamicconf.year == 2017:
    process.load('HLTrigger.Configuration.HLT_2e34v40_cff')
elif dynamicconf.year == 2018:
    process.load('HLTrigger.Configuration.HLT_2018v32_cff')

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.MessageLogger.cerr.FwkReport.reportEvery = 1000000
process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False))
process.source = cms.Source('PoolSource', fileNames = cms.untracked.vstring('file:gensim.root'))

if 'debug' in sys.argv:
    process.options.wantSummary = True
    process.MessageLogger.cerr.FwkReport.reportEvery = 1
    process.maxEvents.input = 50

import minbias
if premix:
    output_commands = process.PREMIXRAWEventContent.outputCommands
    minbias_input = process.mixData.input
    process.mixData.input.fileNames = minbias.premix_files()
    if dynamicconf.year == 2017:
        process.mix.digitizers = cms.PSet(process.theDigitizersMixPreMix)
else:
    raise NotImplementedError('need to set up non-premix')
    output_commands = process.RAWSIMEventContent.outputCommands
    minbias_input = process.mix.input
    process.mix.input.fileNames = minbias.files()

process.output = cms.OutputModule('PoolOutputModule',
                                  fileName = cms.untracked.string('rawhlt.root'),
                                  outputCommands = output_commands,
                                  splitLevel = cms.untracked.int32(0),
                                  )

if trigfilter:
    process.output.SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring(trigfilterpath))

if not randomize or salt.startswith('fixed'):
    minbias_input.sequential = cms.untracked.bool(True)
    skip = jobnum * expectedevents
    if not premix:
        skip *= 2*23 # 2*average PU
    minbias_input.skipEvents = cms.untracked.uint32(skip)

from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, dynamicconf.globaltag(), '')

process.digitisation_step = cms.Path(process.pdigi)
if premix:
    process.datamixing_step = cms.Path(process.pdatamix)
else:
    raise NotImplementedError('need to set up non-premix')
process.L1simulation_step = cms.Path(process.SimL1Emulator)
process.digi2raw_step = cms.Path(process.DigiToRaw)
process.output_step = cms.EndPath(process.output)

process.schedule = cms.Schedule(process.digitisation_step)
if premix:
    process.schedule.append(process.datamixing_step)
else:
    raise NotImplementedError('need to set up non-premix')
process.schedule.extend([process.L1simulation_step,process.digi2raw_step])
if trigfilter:
    process.HLTSchedule = cms.Schedule(process.HLTriggerFirstPath, getattr(process, trigfilterpath), process.HLTriggerFinalPath, process.HLTAnalyzerEndpath)
process.schedule.extend(process.HLTSchedule)
process.schedule.append(process.output_step)
#task?

from HLTrigger.Configuration.customizeHLTforMC import customizeHLTforMC
process = customizeHLTforMC(process)

if randomize: # for minbias
    from modify import deterministic_seeds
    deterministic_seeds(process, 74205, salt, jobnum)

from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
