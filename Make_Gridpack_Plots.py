import ROOT 
import sys
import os
import getopt
import glob
from subprocess import call

def Setup_Condor_Submission_Script():
    return
def Setup_Bash_Script():
    return

def Get_Proc_Name_Gridpack(gridpack_path):
    splits = gridpack_path.split("/")
    gp_name = None
    #print(splits)
    for item in splits:
        if "tgz" in item:
            gp_name = item
    print("This is gp_name: ", gp_name)
    if "VBF" in gp_name:
      return "-p JJVBF --no_mothers"
    elif "WH" in gp_name:
      return "-m wh_withdecay"
    elif "ZH" in gp_name:
      return "-m zh_withdecay -p Had_ZH"
    else:
      raise ValueError("Not a Valid Name")

def Check_CMSSW():
  if len(glob.glob("CMSSW*")) > 0:
    return True, glob.glob("CMSSW*")[0]
  else:
    return False, None

def Check_JHUGen_Repo():
  if os.path.isdir("JHUGen"):
    return True
  else:
    return False

def Download_JHUGen():
  download_command = "wget https://spin.pha.jhu.edu/Generator/JHUGenerator.v7.5.6.tar.gz"
  untar_command = "tar -xf JHUGenerator.v7.5.6.tar.gz && mv JHUGenerator.v7.5.6 JHUGen"
  clean_tar_command = "find \".\" -name *.gz -type f -delete"
  os.system(download_command)
  os.system(untar_command)
  os.system(clean_tar_command)
  print("Finished Downloading JHUGen")
  return

def Install_MELA():
  move_to_MELA_dir = "cd JHUGen/JHUGenMELA/ && pwd"
  setup_command = "&& ./setup.sh"
  os.system(move_to_MELA_dir+setup_command)
  print("Finished Installing JHUGen")
  return

def Install_lhe2root():
  move_to_dir_and_mkdir_for_changes = "cd JHUGen/JHUGenMELA/MELA/python && mkdir lhe2root_fixes && cd lhe2root_fixes &&"
  setup_git_and_pull = "git init && git remote add -f origin https://github.com/hexutils/HexUtils && git config core.sparseCheckout true && echo \"SimulationTools/lhe_tools/\" >> .git/info/sparse-checkout && git pull origin main &&"
  move_changes = "cp SimulationTools/lhe_tools/* ../"
  os.system(move_to_dir_and_mkdir_for_changes + setup_git_and_pull + move_changes)
  print("Updated LHE2ROOT")
  return 

def Install_pymela_fixes():
  move_to_dir_and_mkdir_for_changes = "cd JHUGen/JHUGenMELA/MELA/python && mkdir pymela_fixes && cd pymela_fixes &&"
  setup_git_and_pull = "git init && git remote add -f origin https://github.com/hexutils/JHUGenMELA && echo \"MELA/python/\" >> .git/info/sparse-checkout && git pull origin 8f8585fe5ee90712b9229231bc709352559b0713 &&"
  move_changes = "cp MELA/python/pythonmelautils.py ../ && cp MELA/python/mela.py ../"
  os.system(move_to_dir_and_mkdir_for_changes + setup_git_and_pull + move_changes)
  print("Updated PyMELA")
  return 

def main(argv):
  inputgridpacks = ''
  outputdir = ''
  rundir = ''
  try:
    opts, args = getopt.getopt(argv,"hi:o:r:",["ifile=","ofile=","rfile"])
  except getopt.GetoptError:
    print('Make_Gridpack_Plots.py -i <gridpack_paths> -o <output_directory> -r <run_directory>')
    sys.exit(2)
  for opt, arg, in opts:
    if opt == '-h':
      print('Make_Gridpack_Plots.py -i <gridpack_paths> -o <output_directory> -r <run_directory>')
      sys.exit()
    elif opt in ("-i", "--ifile"):
        split_names = arg.split(" ")
        inputgridpacks = []
        for name in split_names:
          inputgridpacks.append(name)
    elif opt in ("-o", "--ofile"):
        outputdir = arg
    elif opt in ("-r", "--rfile"):
        rundir = arg
  if not all([inputgridpacks, outputdir, rundir]):
        print('Make_Gridpack_Plots.py -i gridpack_paths> -o <output_directory> -r <run_directory>')
        sys.exit(2)

  In_Grid_File = inputgridpacks
  OutDir = outputdir

  Overwrite_Area = False
  try: os.mkdir(OutDir)
  except: 
    ans = input("Path Already Exists. Would you like to overwrite the areas? (y/n) \n")
    if ans == "y":
        Overwrite_Area = True
    else:
        Overwrite_Area = False
        raise ValueError("Please point to a new output directory and run again.")
  else:
    if not os.path.exists(OutDir):
        os.mkdir(OutDir)

  if OutDir.endswith("/"):
    pass
  else:
    OutDir = OutDir + "/"

  # Making the Run Directory #
  if not os.path.exists(rundir):
    os.mkdir(rundir)

  if rundir.endswith("/"):
    pass
  else:
    rundir = rundir + "/"
  # Check if JHUGen Repo is installed or not #
  if not Check_JHUGen_Repo():
    Download_JHUGen()
    Install_MELA()
  else:
    ans = input("Found a JHUGen install, Did you install MELA? (y/n) \n")
    if ans == "y":
        pass
    else: 
        Install_MELA()
  # Check if lhe2root is configured properly #
  ans = input("Did you update the lhe2root and pymela properly? (y/n) \n")
  if ans == "y":
    pass
  else:
    Install_lhe2root()
    Install_pymela_fixes()
  
  print(inputgridpacks)
  gridpack_paths = []
  for file in inputgridpacks:
    with open(file) as f:
        for i in f.readlines():
            gridpack_paths.append(i)
  # Now we will make and submit the plotting as individual jobs #
  job_num = 0
  for gridpack in gridpack_paths:
    # Make the RunDir and Plot Output Dir
    Path_To_Run_Dir = os.path.abspath(rundir+"{}".format(gridpack.split("/")[-1].split(".")[0]))
    print(Path_To_Run_Dir)
    if not os.path.exists(Path_To_Run_Dir):
      os.mkdir(Path_To_Run_Dir)
    Path_To_Plot_Dir = os.path.abspath(OutDir+"{}".format(gridpack.split("/")[-1].split(".")[0]))
    if not os.path.exists(Path_To_Plot_Dir):
      os.mkdir(Path_To_Plot_Dir)
    # Make RunScript #
    if not os.path.exists("RunScripts"):
      os.mkdir("RunScripts")
    Proc_Name = Get_Proc_Name_Gridpack(gridpack)
    RunScript_Name_Temp = "RunScript_{}.sh".format(job_num)
    make_run_script = "cp RunScript_Template_v2.sh RunScripts/{}".format(RunScript_Name_Temp)
    os.system(make_run_script) 
    OutLHEName = "cmsgrid_final_{}.lhe".format(gridpack.split("/")[-1].split(".")[0])
    OutRootName = "out_{}.root".format(gridpack.split("/")[-1].split(".")[0])
    CMSSW_PATH = os.path.abspath(glob.glob("CMSSW*")[0])
    MELA_PY_PATH = os.path.abspath("JHUGen/JHUGenMELA/MELA/python")
    HOME_DIR = os.getcwd()
    PATH_TO_OUT_ROOT = os.path.abspath("JHUGen/JHUGenMELA/MELA/python/"+OutRootName)
    with open("RunScripts/{}".format(RunScript_Name_Temp)) as f:
      text = f.read()
    with open("RunScripts/{}".format(RunScript_Name_Temp),"w") as f:
      text = text.replace("CMSSW",CMSSW_PATH)
      text = text.replace("MELA_PY_PATH",MELA_PY_PATH)
      text = text.replace("OUTLHENAME",OutLHEName)
      text = text.replace("OUTROOT",OutRootName)
      text = text.replace("PROCESS",Proc_Name)
      text = text.replace("GRIDPACK_PATH",gridpack.strip("\n"))
      text = text.replace("PATH_TO_RUN_DIR",Path_To_Run_Dir)
      text = text.replace("HOME",HOME_DIR)
      text = text.replace("PATH_TO_OUT_ROOT",PATH_TO_OUT_ROOT)
      text = text.replace("PATH_TO_PLOTS_DIR",Path_To_Plot_Dir)
      f.write(text)
    # Make_CondorScript #
    CondorScriptTempName = "condor_{}.sub".format(gridpack.split("/")[-1].split(".")[0])
    make_condor_script_command = "cp condor_script_template.sub RunScripts/{}".format(CondorScriptTempName)
    os.system(make_condor_script_command)
    with open("RunScripts/{}".format(CondorScriptTempName)) as f:
      text = f.read()
    with open("RunScripts/{}".format(CondorScriptTempName),"w") as f:
      text = text.replace("OUTOUT","RunScripts/{}.out".format(gridpack.split("/")[-1].split(".")[0]))
      text = text.replace("OUTERR","RunScripts/{}.err".format(gridpack.split("/")[-1].split(".")[0]))
      text = text.replace("OUTLOG","RunScripts/{}.log".format(gridpack.split("/")[-1].split(".")[0]))
      text = text.replace("NAME","executable = "+os.path.abspath("RunScripts/{}".format(RunScript_Name_Temp)))
      f.write(text)
    job_num=job_num+1
  # Submit the Jobs #
  for filename in os.listdir("RunScripts/"):
    f = os.path.join("RunScripts/", filename)
    # checking if it is a file
    if os.path.isfile(f) and f.endswith(".sub"):
      command = "condor_submit {}".format(f)
      os.system(command)
    


if __name__ == "__main__":
    main(sys.argv[1:])
