# 02_preprocess_python

### 01_DomainBounds2json.ipynb

Notebook to create a JSON containing bounding parameters for all modeling domains. The output json file can be referenced by later scripts/notebooks using the requests package.

NOTE: This notebook needs to be run twice. On the first run, the user designates all domains, and includes the following details:
* Domain name
* Bounding box with latmax, latmin, lonmax, lonmin
* Start date
* End date
* Station projection (epsg:4326 in US)
* Model projection
 
After the NPRB_domains.json is pushed to github, 02_GEE_topoveg.ipynb can be run. Ues the DEM or landcover ascii files for each domain to fill in the ncols, nrows, xll, yll values for each domain.


### 02_GEE_topoveg.ipynb

Notebook to pull dem and landcover data from GEE and prep ascii files for input into SnowModel. These ascii files will provide missing information (ncols, nrows, xll, yll) for the json. 


### 03_GEE_lapserates.ipynb

Notebook to compute domain-specific temp and precip lapse rates. 


### 04_met_data.py 

Notebook to pull meteorological data from GEE and prep ascii files for input into SnowModel. 


### 05_Fetch_Station.ipynb

Notebook to get SNOTEL station data within a modeling domain to be used for the calibration.


### 06_snow_course.ipynb

Notebook to convert downloaded snow course data and turn it into the inputs needed for the calibration workflow.

### 07_Build_SnowModel_line_file.ipynb

Notebook to create a file to run SnowModel in line mode for the calibration. This notebook generates input files so that Snowmodel is only run at the cell(s) that correspond to station data. 
