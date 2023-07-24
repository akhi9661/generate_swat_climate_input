[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![NASA POWER LARC](https://img.shields.io/badge/NASA_POWER_LARC-blue)](https://power.larc.nasa.gov/data-access-viewer/)
[![SWAT](https://img.shields.io/badge/SWAT-gray)](https://swat.tamu.edu/)

## About
This user interface helps download the climate data from [NASA POWER LARC](https://power.larc.nasa.gov/data-access-viewer/) for use in SWAT Model. 
An index file is also created for each parameter. The generated weather files can be used directly in ArcSWAT model. 

---
## How to use
- Download the requirements.txt file

- Install the required libraries

```bash
 pip install -r requirements.txt
```

- Download the `swat_input.py` file and run it.

---

GUI Window

![image](https://github.com/akhi9661/generate_swat_climate_input/assets/63473666/ae249ff6-0e66-4727-a088-e3823bad916a)

---

## Known Issue
The 'elevation' column in index files is set to -999 (missing). It will be resolved shortly.


