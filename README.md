[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8180294.svg)](https://doi.org/10.5281/zenodo.8180294)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NASA POWER LARC](https://img.shields.io/badge/NASA_POWER_LARC-blue)](https://power.larc.nasa.gov/data-access-viewer/)
[![SWAT](https://img.shields.io/badge/SWAT-gray)](https://swat.tamu.edu/)
[![NASA_SRTM_Digital_Elevation_30m](https://img.shields.io/badge/NASA_SRTM_Digital_Elevation_30m-goldenrod)](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003)

## About
This user interface helps download the climate data from [NASA POWER LARC](https://power.larc.nasa.gov/data-access-viewer/) for use in SWAT Model. 
An index file is also created for each parameter. The generated weather files can be used directly in ArcSWAT model. 
The elevation information is extracted from [SRTM 30m DEM](https://developers.google.com/earth-engine/datasets/catalog/USGS_SRTMGL1_003) available on Google Earth Engine. 

---
## How to use
- Download the requirements.txt file

- Install the required libraries

```bash
 pip install -r requirements.txt
```

- Download the `swat_input.py` file and run it.
 
- If running it for the first time, GEE authentication will have to be done as well. An authentication window will open and it will redirect you to your gmail account. For repeated runs, unless the application is restarted, GEE authentication will likely won't be required again. 

---

GUI Window

![image](https://github.com/akhi9661/generate_swat_climate_input/assets/63473666/ae249ff6-0e66-4727-a088-e3823bad916a)

---


