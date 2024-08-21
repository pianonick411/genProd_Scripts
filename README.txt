Repo for OnShell Gridpack Testing and Plotting setups

This script will automatically read in the list of gridpacks and then make plots of all relevant kinematic observables

This should be run in an enviornment with cmsenv enabled like lxplus or local computing cluster with singularity (this may be more difficult)

As an example, here is how to run the tests

python3 Make_Gridpack_Plots.py -i <gridpack path file> -o <Output_Dir> -r <Run Directory>

where the gridpack path file is a txt file where each line is a path to a gridpack.
The output dir should be the path to where you want the plots to be output
The Run Directory should be the path to where you want the gridpacks to be unzipped and run from which may be helpful if the user is low on space