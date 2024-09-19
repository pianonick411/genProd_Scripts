import numpy as np
import ROOT
import os
import sys
import getopt
import copy
import uproot 
import matplotlib.pyplot as plt
import mplhep as hep 
import vector 
import awkward as ak 

make_cuts = True 
hep.style.use("CMS")

def Get_New_Binning(xl,xu,nb):
  return np.linspace(xl, xu, num=nb)

def Couplings_Parser(rundir):
  prod_coupling_names = ["Prod: "]
  dec_coupling_names = ["Dec: "]
  with open(rundir + '/JHUGen.input', 'r') as file:
     prod_text = file.read()
  #print("This is prod_text", prod_text)
  prod_text_split = prod_text.split()
  for item in prod_text_split:
     if "gh" not in item:
      continue
     prod_coupling_names.append(item)
  
#  print("This is coupling_names first time: ", coupling_names)

  with open(rundir + '/JHUGen_decay.input', 'r') as file:
     dec_text = file.read()
  dec_text_split = dec_text.split()
  for item in dec_text_split:
     if "gh" not in item:
      continue
     dec_coupling_names.append(item)
  
  couplings = ""
  for item in prod_coupling_names:
     couplings += item + " "
  for item in dec_coupling_names: 
     couplings += item + " "
  
  return couplings

def main(argv):
  inputroot = ''
  outputdir = ''
  rundir = ''
  try:
    opts, args = getopt.getopt(argv,"hi:o:r:",["ifile=","ofile="])
  except getopt.GetoptError:
    print('Make_Gridpack_Plots.py -i <input_root> -o <output_directory>')
    sys.exit(2)
  for opt, arg, in opts:
    if opt == '-h':
      print('Make_Gridpack_Plots.py -i <input_root> -o <output_directory>')
      sys.exit()
    elif opt in ("-i", "--ifile"):
        split_names = arg.split(" ")
        inputroot = []
        for name in split_names:
          inputroot.append(name)
    elif opt in ("-o", "--ofile"):
        outputdir = arg
    elif opt in ("-r", "--runfile"):
        rundir = arg 
  if not all([inputroot, outputdir]):
        print('Make_Gridpack_Plots.py -i <input_root> -o <output_directory>')
        sys.exit(2)

  print(inputroot[0])
  f = uproot.open(inputroot[0])
  tree = f["tree;1"].arrays(library = 'pd')
  # print(tree)

  if make_cuts: 
     tree = tree[tree["DRjj"] > 0.3]
     tree = tree[tree["ptj1"] > 15]
     tree = tree[tree["ptj2"] > 15]
   
    
     



  if outputdir.endswith("/"):
    pass
  else:
    outputdir=outputdir+"/"

  leaves_to_plot = ["costheta1","costheta2","Phi1","costhetastar","Phi","M4L","MZ1","MZ2","costheta1d","costheta2d","Phid","costhetastard","Phi1d","q2V1","q2V2"]
  for observable in leaves_to_plot:
    xRangeUpper = 1
    xRangeLower = 0
    #yRangeLower = 0
    Nbins = 10
    # f.tree.Draw(observable)
    # hist = copy.deepcopy(ROOT.gPad.GetPrimitive("htemp"))
    # c1 = ROOT.TCanvas("","",900,900)
    if "cos" in observable.lower():
      xRangeUpper = 1
      xRangeLower = -1
      yRangeLower = 0 
      Nbins = 40
    elif "mz1" in observable.lower():
      xRangeUpper = 120
      xRangeLower = 0  
      Nbins = 30
    elif "mz2" in observable.lower():
      xRangeUpper = 90
      xRangeLower = 0  
      Nbins = 30    
    elif "m4l" in observable.lower():
      xRangeUpper = 126
      xRangeLower = 124
      Nbins = 30
    elif "q2" in observable.lower():
      xRangeUpper = 100000
      xRangeLower = 0
      Nbins = 50
    elif "phi" in observable.lower():
       xRangeUpper = np.pi
       xRangeLower = -1*np.pi
       Nbins = 40 

    new_bin_range = np.linspace(xRangeLower,xRangeUpper,Nbins+1)
    if "q2" in observable.lower(): 
       hist, _ = np.histogram(tree[observable], bins = new_bin_range)
       sqrt_hist, sqrt_bins = np.histogram(np.sqrt(tree[observable]), bins = np.linspace(0, 600, 51))
       
    else:
      hist, _ = np.histogram(tree[observable], bins = new_bin_range)
      # if "phi" in observable.lower(): 
        #  print(new_bin_range)
    hist = hist.astype("float64")
    #hist.SetMinimum(0)
    hist *= 1/hist.sum()
   

    
    couplings_text = Couplings_Parser(rundir)
    #print(couplings_text)

    plt.figure(figsize = (10,10), dpi=100)
    hep.histplot(hist, new_bin_range, color = 'r')
    hep.cms.text(couplings_text, exp = 'CMS (Simulation)',fontsize = 12, italic = (True, True, True), loc = 0)
    plt.xlabel(observable, fontsize=15)
    plt.savefig(outputdir+observable+".pdf", format="pdf")
    plt.savefig(outputdir+observable+".png", format="png")
    if "v1" in observable.lower():
      sqrt_hist.astype("float64")
      sqrt_hist = sqrt_hist * 1/sqrt_hist.sum()
      plt.figure(figsize = (10,10), dpi=100)
      hep.histplot(sqrt_hist, sqrt_bins, color = 'r')
      hep.cms.text(couplings_text, exp = 'CMS (Simulation)',fontsize = 12, italic = (True, True, True), loc = 0)
      plt.xlabel("qV1", fontsize=15)
      plt.savefig(outputdir+"qV1.pdf", format="pdf")
      plt.savefig(outputdir+"qV1.png", format="png")
    elif "v2" in observable.lower():
      sqrt_hist.astype("float64")
      sqrt_hist = sqrt_hist * 1/sqrt_hist.sum()
      plt.figure(figsize = (10,10), dpi=100)
      hep.histplot(sqrt_hist, sqrt_bins, color = 'r')
      hep.cms.text(couplings_text, exp = 'CMS (Simulation)',fontsize = 12, italic = (True, True, True), loc = 0)
      plt.xlabel("qV2", fontsize=15)
      plt.savefig(outputdir+"qV2.pdf", format="pdf")
      plt.savefig(outputdir+"qV2.png", format="png")
if __name__ == "__main__":
    main(sys.argv[1:])
