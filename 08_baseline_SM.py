#!/usr/bin/env python
# coding: utf-8


# Import all of the python packages used in this workflow.
import scipy
import numpy as np
from collections import OrderedDict
import os, sys
from pylab import *
import pandas as pd
import numpy as np
import xarray as xr
import geopandas as gpd
from datetime import date, datetime
from datetime import timedelta  
import json
import itertools
import os
import requests


######## USER INPUT HERE ONLY ##########

# Use this for the 6-year SnowModel run info
#start_years_list = [1988,1993,1998,2003,2008,2013]
#end_years_list = [1994,1999,2004,2009,2014,2019]

# Use this for the 2-year SnowModel run info
# just do start years that have have a second year that overlaps with MODIS data
start_years_list = list(range(2000,2020))
print(start_years_list)

###########################################

# Define some variables that don't change throughout the snowmodel runs
domain = 'BEAU'


# SM filepath
SMpath = '/nfs/attic/dfh/2020_NPRB/domain_'+domain+'/test/'

#path to NPRB domains
domains_resp = requests.get("https://raw.githubusercontent.com/NPRB/02_preprocess_python/main/NPRB_domains.json")
domains = domains_resp.json()

# Other variables
parFile = SMpath+'snowmodel.par'
incFile = SMpath+'code/snowmodel.inc'
compileFile = SMpath+'code/compile_snowmodel.script'
ctlFile = SMpath+'ctl_files/wo_assim/swed.ctl'
codepath = SMpath+'code'
preprocessFile = SMpath+'code/preprocess_code.f'
outputs_user = SMpath+'code/outputs_user.f'
micrometFile = SMpath+'code/micromet_code.f'



# ### Function to edit text files docs


#function to edit SnowModel Files other than .par
def replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num] = text
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()



#Edit the par file to set parameters with new values
def edit_par(par_dict,parameter,new_value,parFile):
    lines = open(parFile, 'r').readlines()
    if par_dict[parameter][2] == 14 or par_dict[parameter][2] == 17     or par_dict[parameter][2] == 18 or par_dict[parameter][2] == 19     or par_dict[parameter][2] == 93 or par_dict[parameter][2] == 95     or par_dict[parameter][2] == 97 or par_dict[parameter][2] == 100     or par_dict[parameter][2] == 102 or par_dict[parameter][2] == 104     or par_dict[parameter][2] == 107 or par_dict[parameter][2] == 108     or par_dict[parameter][2] == 147 or par_dict[parameter][2] == 148     or par_dict[parameter][2] == 149:
        text = str(new_value)+'\n'
    else:
        text = str(new_value)+'\t\t\t!'+par_dict[parameter][1]
    lines[par_dict[parameter][2]] = text
    out = open(parFile, 'w')
    out.writelines(lines)
    out.close()



#import baseline .par parameters
with open('/nfs/attic/dfh/2020_NPRB/data/json/par_base.json') as f:
    base = json.load(f)

base.keys()




#edit snowmodel.par for variables that are constant between runs
edit_par(base,'nx',domains[domain]['ncols'],parFile)
edit_par(base,'ny',domains[domain]['nrows'],parFile)
edit_par(base,'deltax',domains[domain]['cellsize'],parFile)
edit_par(base,'deltay',domains[domain]['cellsize'],parFile)
edit_par(base,'xmn',domains[domain]['xll'],parFile)
edit_par(base,'ymn',domains[domain]['yll'],parFile)
edit_par(base,'dt',21600,parFile) #seconds per model time step
edit_par(base,'ascii_topoveg',1,parFile)
edit_par(base,'topo_ascii_fname','topo_vege/'+domain+'_dem.asc',parFile)
edit_par(base,'veg_ascii_fname','topo_vege/'+domain+'_veg.asc',parFile)
edit_par(base,'lat_file_path','extra_met/'+domain+'_grid_lat.asc',parFile)
edit_par(base,'lon_file_path','extra_met/'+domain+'_grid_lon.asc',parFile)
edit_par(base,'xlat',round(domains[domain]['Bbox']['latmin']+(domains[domain]['Bbox']['latmax']-domains[domain]['Bbox']['latmin'])/2,2),parFile)
edit_par(base,'UTC_flag',1,parFile)
edit_par(base,'run_snowtran',0,parFile)
edit_par(base,'barnes_lg_domain',1,parFile)
edit_par(base,'print_inc',4,parFile)
edit_par(base,'print_var_01','y',parFile)#tair
edit_par(base,'print_var_09','y',parFile)#prec
edit_par(base,'print_var_10','n',parFile)#rain
edit_par(base,'print_var_11','n',parFile)#sprec
edit_par(base,'print_var_12','y',parFile)#swemelt
edit_par(base,'print_var_14','y',parFile)#runoff
edit_par(base,'print_var_16','y',parFile)#snow depth
edit_par(base,'print_var_18','y',parFile)#swed


##edit snowmodel.inc
replace_line(incFile, 12, '      parameter (nx_max='+str(int(domains[domain]['ncols'])+1)+',ny_max='+str(int(domains[domain]['nrows'])+1)+')\n')
replace_line(incFile, 41, '      parameter (nz_max=2)\n') 

##edit compile_snowmodel.script
#replace_line(compileFile, 16, '#pgf77 -O3 -mcmodel=medium -I$path -o ../snowmodel $path$filename1 $path$filename2 $path$filename3 $path$filename4 $path$filename5 $path$filename6 $path$filename7 $path$filename8 $path$filename9 $path$filename10\n')
replace_line(compileFile, 20, 'gfortran -O3 -mcmodel=medium -I$path -o ../snowmodel $path$filename1 $path$filename2 $path$filename3 $path$filename4 $path$filename5 $path$filename6 $path$filename7 $path$filename8 $path$filename9 $path$filename10\n')



#function to edit time-related parameters in .par 
def change_dates(styr):
    st = pd.to_datetime(str(styr)+'-10-01',format="%Y-%m-%d")
    ed = pd.to_datetime(str(styr+2)+'-09-30',format="%Y-%m-%d")
    edit_par(base,'iyear_init',str(st.year),parFile)
    edit_par(base,'imonth_init',str(st.month),parFile)
    edit_par(base,'iday_init',str(st.day),parFile)
    edit_par(base,'xhour_init',str(st.hour),parFile)
    edit_par(base,'max_iter',str((ed-st).days*4+4),parFile)
    edit_par(base,'met_input_fname','../../data/SMinputs/'+domain+'/mm_'+domain+'_'+str(st.year)+'-'+str(ed.year)+'.dat',parFile)
    edit_par(base,'output_path_wo_assim','outputs/wo_assim_'+str(st.year)+'-'+str(ed.year)+'/',parFile)



def compile_snowmodel():
    # Move to code
    get_ipython().run_line_magic('cd', '$codepath')
    # Run compile script 
    get_ipython().system(' ./compile_snowmodel.script')



def run_snowmodel():
    get_ipython().run_line_magic('cd', '$SMpath')
    get_ipython().system(' nohup ./snowmodel')


# styr = start_years_list[-1]
# print(styr)
# change_dates(styr)
# compile_snowmodel()
# run_snowmodel()

for styr in start_years_list:
    print(styr)
    print('editing .par file')
    change_dates(styr)
    
    # Compile snowmodel
    print('compiling snowmodel')
    compile_snowmodel()
    
    # run snowmodel
    print('running rnowmodel')
    run_snowmodel()