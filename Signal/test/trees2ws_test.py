import pandas as pd
import numpy as np
import ROOT
import json

from root_numpy import tree2array

from optparse import OptionParser

recobins = [
    "DoubleHTag_0",
    "DoubleHTag_1",
    "DoubleHTag_2",
    "DoubleHTag_3",
    "DoubleHTag_4",
    "DoubleHTag_5",
    "DoubleHTag_6",
    "DoubleHTag_7",
    "DoubleHTag_8",
    "DoubleHTag_9",
    "DoubleHTag_10",
    "DoubleHTag_11"
]

#-------------------------------------------------------------------------------
def add_mc_vars_to_workspace(ws=None):
   IntLumi = ROOT.RooRealVar("IntLumi","IntLumi",1000)
   IntLumi.setConstant(True)
   getattr(ws,'import')(IntLumi)

   weight = ROOT.RooRealVar("weight","weight",1)
   weight.setConstant(False)
   getattr(ws,'import')(weight)

   CMS_hgg_mass = ROOT.RooRealVar("CMS_hgg_mass","CMS_hgg_mass",125,100,180)
   CMS_hgg_mass.setConstant(False)
   CMS_hgg_mass.setBins(160)
   getattr(ws,'import')(CMS_hgg_mass)

   dZ = ROOT.RooRealVar("dZ","dZ",0.0,-20,20)
   dZ.setConstant(False)
   dZ.setBins(40)
   getattr(ws,'import')(dZ)

   ttHScore = ROOT.RooRealVar("ttHScore","ttHScore",0.5,0.,1.)
   ttHScore.setConstant(False)
   ttHScore.setBins(40)
   getattr(ws,'import')(ttHScore)

   rrv = ROOT.RooRealVar("centralObjectWeight","centralObjectWeight", -1000, 1000)
   rrv.setConstant(False)
   rrv.setBins(40)
   getattr(ws, 'import')(rrv)
#---------------------------------------------------------------------------------------
def apply_selection(data=None,reco_name=None):

    #Split by mva and MX
    # mva boundaries: (0)0.23, (1)0.455, (2)0.709 : size=3
    # mx boundaries: (0)250., (1)336., (2)411., (3)556 : size=4
    # mjj boundaries : 70-190

    # for mva boundaries
    # n=0 -> mvavalue>mva[2], mvaCat = 0
    #n=1 -> mvavalue>mva[1], mvaCat = 1
    #n=2 -> mvavalue>mva[0], mvaCat = 2

    # for mx boundaries
    #n=0 -> mxvalue>mx[3], mxCat = 0
    #n=1 -> mxvalue>mx[2], mxCat = 1
    #n=2 -> mxvalue>mx[1], mxCat = 2
    #n=3 -> mxvalue>mx[0], mxCat = 3

    # mvacat*mxboundary+mxcat
   if 'DoubleHTag_0' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.709) & (data['MX']>556))]
   elif 'DoubleHTag_1' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.709) & (data['MX']>411))]
   elif 'DoubleHTag_2' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.709) & (data['MX']>336))]
   elif 'DoubleHTag_3' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.709) & (data['MX']>250))]
   elif 'DoubleHTag_4' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.455) & (data['MX']>556))]
   elif 'DoubleHTag_5' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.455) & (data['MX']>411))]
   elif 'DoubleHTag_6' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.455) & (data['MX']>336))]
   elif 'DoubleHTag_7' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.455) & (data['MX']>250))]
   elif 'DoubleHTag_8' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.23) & (data['MX']>556))]
   elif 'DoubleHTag_9' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.23) & (data['MX']>411))]
   elif 'DoubleHTag_10' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.23) & (data['MX']>336))]
   elif 'DoubleHTag_11' in reco_name: recobin_data = data[((data['HHbbggMVA']>0.23) & (data['MX']>250))]
   else:
      raise ValueError("Reco bin not recognised")
   
   return recobin_data

#---------------------------------------------------------------------------------------
def add_recobin_dataset_to_workspace(data=None,ws=None,reco_name=None,proc=None):

    #apply selection to extract correct recobin
    recobin_data = apply_selection(data, reco_name)

    print 'define argument set'
    
    #define argument set
    arg_set = ROOT.RooArgSet(ws.var("weight"))
    variables = ["CMS_hgg_mass","dZ","ttHScore","centralObjectWeight"]
    for var in variables:
       arg_set.add(ws.var(var))

    #define roodataset to add to workspace
    dataset_name = '_'.join([proc,'13TeV',mass,reco_name])
    print dataset_name
#    print arg_set
    recobin_roodataset = ROOT.RooDataSet (dataset_name, dataset_name, arg_set, "weight" )
    
    #Fill the dataset with values
    for index,row in recobin_data.iterrows():
        for var in variables:
            if var=='dZ' :  #to ensure only one fit (i.e. all RV fit)
                ws.var(var).setVal( 0. )
                ws.var(var).setConstant()
            else : 
                ws.var(var).setVal( row[ var ] )

        w_val = row['weight']
        recobin_roodataset.add( arg_set, w_val)

    getattr(ws, 'import')(recobin_roodataset)

    return [dataset_name]
#---------------------------------------------------------------------------------------
def get_options():

    parser = OptionParser()
    parser.add_option('--inp-files',
                      dest='inp_files',
                      default='ttHToGG_M125_13TeV_powheg_pythia8_v2')
#                      default='GluGluHToGG_M-125_13TeV_powheg_pythia8,GluGluToHHTo2B2G_node_SM_13TeV-madgraph,VBFHToGG_M-125_13TeV_powheg_pythia8,VHToGG_M125_13TeV_amcatnloFXFX_madspin_pythia8,bbHToGG_M-125_4FS_yb2_13TeV_amcatnlo,ttHToGG_M125_13TeV_powheg_pythia8_v2,bbHToGG_M-125_4FS_ybyt_13TeV_amcatnlo')
    parser.add_option('--inp-dir',
                      dest='inp_dir',
                      default='/eos/cms/store/group/phys_higgs/HiggsExo/HH_bbgg/Run2_legacy/flat_trees_from_ETH_MVA_10_12_2018_commonTraining/')
    parser.add_option('--process_id',
                      dest='process_id',
                      default='tth')
#                          default='ggh,gghh,vbf,vh,bbh_v1,tth,bbh_v2')
    parser.add_option('--out-dir',
                      dest='out_dir',
                      default='/afs/cern.ch/work/g/gbyu/private/CMGTools/ws_made/')
    parser.add_option('--M',
                      dest='mass',
                      default='125')
    parser.add_option('--year',
                      dest='year',
                      default='2016')

    return parser.parse_args()

#---------------------------------------------------------------------------------------

(opt,args) = get_options()
processID = opt.process_id.split(',')
year=opt.year
mass = '125'
masses = [-5,0,5]
input_files = opt.inp_files.split(',')

ws=ROOT.RooWorkspace("cms_hgg_13TeV","cms_hgg_13TeV")
for num,f in enumerate(input_files):
   print 'doing file', f
   name='bbggtrees'
   tfile=ROOT.TFile(opt.inp_dir+"/"+year+"/output_"+f+".root")
   data=pd.DataFrame(tree2array(tfile.Get("tagsDumper/trees/%s"%name)))
   
   add_mc_vars_to_workspace( ws )
   ws.Print()
   
   dataset_names = []
   for recobin in recobins:
      print 'For tags : ',recobin
      dataset_names += add_recobin_dataset_to_workspace( data, ws, recobin ,processID[num])
      
   for name in dataset_names:
      print name, "::: Entries = ",ws.data(name).numEntries(),", SumEntries = ",ws.data(name).sumEntries()
      
      #export ws to file
   f_out = ROOT.TFile.Open("%s/output_%s_M125_13TeV_%s.root"%(opt.out_dir,processID[num],year),"RECREATE")
   dir_ws = f_out.mkdir("tagsDumper")
   
   dir_ws.cd()
   ws.Write()
   dir_ws.Close()
   f_out.Close()

   


         
