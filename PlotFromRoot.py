import numpy as np
import ROOT
import os
import sys
import getopt
import copy

def Get_New_Binning(xl,xu,nb):
  return np.linspace(xl, xu, num=nb)

def main(argv):
  inputroot = ''
  outputdir = ''
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
  if not all([inputroot, outputdir]):
        print('Make_Gridpack_Plots.py -i <input_root> -o <output_directory>')
        sys.exit(2)

  print(inputroot[0])
  f = ROOT.TFile.Open(inputroot[0])

  if outputdir.endswith("/"):
    pass
  else:
    outputdir=outputdir+"/"

  leaves_to_plot = ["costheta1","costheta2","Phi1","costhetastar","Phi","M4L","MZ1","MZ2","costheta1d","costheta2d","Phid","costhetastard","Phi1d","q2V1","q2V2"]
  for observable in leaves_to_plot: 
    xRangeUpper = 1
    xRangeLower = 0
    Nbins = 10
    f.tree.Draw(observable)
    hist = copy.deepcopy(ROOT.gPad.GetPrimitive("htemp"))
    c1 = ROOT.TCanvas("","",900,900)
    if "cos" in observable.lower() or "phi" in observable.lower() :
      xRangeUpper = 1
      xRangeLower = -1
      Nbins = 15
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
    new_bin_range = Get_New_Binning(xRangeLower,xRangeUpper,Nbins+1)
    hist = hist.Rebin(Nbins,"",new_bin_range)
    hist.Scale(1/hist.Integral())
    hist.Draw("hist")
    c1.SaveAs(outputdir+observable+".pdf")
    c1.SaveAs(outputdir+observable+".png")
if __name__ == "__main__":
    main(sys.argv[1:])