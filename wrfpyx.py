#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

===============================================================================

wrfpyx: A Python Toolkit for Manipulating WRF Outputs and others

wrfpyx is a lightweight and user-friendly Python  package  designed to simplify 
working with Weather Research and Forecasting (WRF)  model outputs. The toolkit 
offers a collection of functions to preprocess, modify, and adapt WRF-generated 
NetCDF files for seamless integration with ocean models as WW3 and NEMO.

Key Features:
--------------
- **Metadata Transformation**: Convert WRF NetCDF outputs to  formats  (to GFS) 
    compatible with models like NEMO and WW3.
- **Utility Functions**: A growing set of utilities for working with WRF outputs,
    such as renaming variables, changing attributes, and   handling  coordinate
    systems.

Quick Start:
-------------
Import the package and call the desired functions:

    
    import wrfpyx as wpx

    # Example: Convert WRF metadata to GFS format
    ds = wpx.wrf2gfs_params("my/directory/wrfout_d01_yyyy-mm-dd-hh.nc", "u10", *args, **kwargs)


Contributing:
--------------
This package is under active development. Contributions,   suggestions, and bug
reports are welcome on the GitHub repository (link here).

License:
---------
wrfpyx is open-source software released under the MIT License.

@author: Jose Luis Rodriguez Solis




"""


#%%   ~ ~ ~ ~ ~ ~ 
#     import modules section
#     ~ ~ ~ ~ ~ ~ 

import numpy as np
import xarray as xr
import datetime
from metpy.calc import relative_humidity_from_specific_humidity as sh2rh
from metpy.units import units


#%%
def element_exists(lst, element):
    """
    
    Try to get the index of the element in the list
        
    Parameters
    ----------
    lst: list
        List of elements 
    element: str
        element or string
    """
    
    try:
        lst.index(element)
        return True
    except ValueError:
        return False
    

def wrf2gfs_params(namefile, varname, *args, **kwargs):
    """
    
    wrf2gfs_params is a fuction to change global attributes from WRF outputs
    into GFS global attributes. GFS netcdf metadata is easy to read for ocean
    models as NEMO or WW3 (just u10 and v10)
    
    Parameters
    ----------
    namefile : str
        Path or name for file in netcdf.
    varname : str
        Valid values 
        'u10', 'v10', 't2', 'rh', 'ps', 'cldfra', 'pr', 'sw', 'lw'
    *args : TYPE
        DESCRIPTION.
    **kwargs : TYPE
        DESCRIPTION.

    Returns
    -------
    ds, xarray netcdf format 

    """
    
    nc = xr.open_dataset(namefile)
                   
    #                           read time
    #
    # data from CDO outputs --> uncomment
    #
    
    #a  = nc['Times'].data[0].squeeze()
    #hours = str(int((a - int(a))*24)).zfill(2)
    #fc = str(int(a))
    #b  = datetime.datetime.strptime(fc+' '+hr,'%Y%m%d %H')
    
    #
    # data from WRF outputs --> uncomment
    #
    
    a = nc['Times'].data[0].squeeze().decode()
    b  = datetime.datetime.strptime(a,'%Y-%m-%d_%H:00:00')
    start_date = datetime.datetime.strptime(nc.START_DATE ,'%Y-%m-%d_%H:%M:%S')
    c = b - start_date
    hours = c.seconds/(60*60)


    yearsice = kwargs.get('yearsince', None)
    if yearsice:
        print ('')
        print ('* Times units variable was set by user  -> yearsince:' +str(yearsice))
        print ('')
    elif yearsice == None:
        yearsice = start_date.year
    
    
    #    ~ ~ ~ ~ ~ ~ 
    #
    #    read lat, lon, t
    
    
    #
    #                days from     year_from_start_date - mm - dd hh

    date_sice  = datetime.datetime.strptime(str(yearsice)+'0101 00','%Y%m%d %H') #since
    lon = nc['XLONG'].data[:].squeeze()
    lat = nc['XLAT'].data[:].squeeze()

    if len(lon.shape) == 2:
        lon = lon[0,:].copy()
    if len(lat.shape) == 2:
        lat = lat[:,0].copy()
    

    delta = b - date_sice # hours since
    hours_since = delta.days*24 + int(b.hour)



    #    ~ ~ ~ ~ ~ ~ 
    #
    #    attrs time [dynamic values]
    
    #
    # format time as:      hours since 2023-12-25T00:00:00Z    

    attrs_time =  {"units" : "hours since "+date_sice.strftime('%Y-%m-%dT%H:00:00Z'),
                   "calendar" : "proleptic_gregorian"
                   }    
    


    #    ~ ~ ~ ~ ~ ~ 
    #
    #    variable general attributes [static values]


    #
    # attrs geo
    #
     
    # attrs height
    attrs_ground = {"units" : "m",
                    "long_name" : "Specified height level above ground",
                    "standard_name":"depth",
                    "axis" : "Z",
                    "positive" : "up",
                    "_CoordinateAxisType" : "Height",
                    "_CoordinateZisPositive" : "up",
                    "datum" : "ground"
                    }
    
    # attrs lat
    attrs_lat    = {"units":"degrees_north",
                    "_CoordinateAxisType":"Lat",
                    "axis":"Y",
                    "standard_name":"latitude"
                    }
    
    # attrs lon
    attrs_lon    = {"units":"degrees_east",
                    "_CoordinateAxisType":"Lon",
                    "axis":"X",
                    "standard_name":"longitude"
                    }
    
    #
    # attrs variables
    #
    
    
    # attrs u
    attrs_u = {"units" : "meter_second-1",
               "long_name" : "u-component of wind @ Specified height level above ground",
               "standard_name" : "x_wind",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "UGRD"
               }
    
    # attrs v
    attrs_v = {"units" : "meter_second-1",
               "long_name" : "v-component of wind @ Specified height level above ground",
               "standard_name" : "y_wind",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "VGRD"
               }

    # attrs t2
    attrs_t2 = {"units" : "Celsius",
               "long_name" : "Temperature @ Specified height level above ground",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "TMP"
               }

    # attrs rh
    attrs_rh = {"units" : "percentage",
               "long_name" : "Relative humidity @ Specified height level above ground",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "RH"
               }

    # attrs ps
    attrs_ps = {"units" : "millibar",
               "long_name" : "Pressure @ Ground or water surface",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "PRES"
               }

    # attrs cl
    attrs_cl = {"units" : "nondimensional",
               "long_name" : "Total cloud cover @ Entire atmosphere",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "TCDC"
               }

    # attrs pr
    attrs_pr = {"units" : "kilogram_meter-2_second-1",
               "long_name" : "Precipitation rate @ Ground or water surface",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "PRATE"
               }

    # attrs lw
    attrs_lw = {"units" : "watt_meter-2",
               "long_name" : "Downward Long-Wave Rad. Flux (Mixed_intervals Average) @ Ground or water surface",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "DLWRF"
               }

    # attrs sw
    attrs_sw = {"units" : "watt_meter-2",
               "long_name" : "Downward Short-Wave Radiation Flux (Mixed_intervals Average) @ Ground or water surface",
               "_FillValue" : "NaN",
               "missing_value" : "NaN",
               "abbreviation" : "DSWRF"
               }




    
    #    ~ ~ ~ ~ ~ ~ 
    #
    #  read and save var
    #
    #
    
    
    var = varname.upper()



    # search variable
    # match (var):
    
        
    
    # 
    #                         >>>>>>>>>>>>
    #                             u10
    #
    if var == "U10":    
        ncvar = nc[var].data[:].squeeze()
        
        ds = xr.Dataset(
            
            {"Uwind": (("time", "height_above_ground2", "lat", "lon"), ncvar[np.newaxis,np.newaxis,:,:],attrs_u)
            },                            
            coords={
                "time": ("time", [hours_since], attrs_time),
                "height_above_ground2": ("height_above_ground2", [10], attrs_ground),
                "lat": ("lat", lat, attrs_lat),
                "lon": ("lon", lon, attrs_lon),
                },
            
                        ) 



# 
#                         >>>>>>>>>>>>
#                             v10
#
    elif var == "V10":    
        ncvar = nc[var].data[:].squeeze()
        
        ds = xr.Dataset(
            
            {"Vwind": (("time", "height_above_ground2", "lat", "lon"), ncvar[np.newaxis,np.newaxis,:,:],attrs_v)
            },                            
            coords={
                "time": ("time", [hours_since], attrs_time),
                "height_above_ground2": ("height_above_ground2", [10], attrs_ground),
                "lat": ("lat", lat, attrs_lat),
                "lon": ("lon", lon, attrs_lon),
                },
            
                        )
 


# 
#                         >>>>>>>>>>>>
#                              t2m
#
    elif var == "T2":    
        ncvar = nc[var].data[:].squeeze() -273.15 # to celcius
        
        ds = xr.Dataset(
            
            {"Tair": (("time", "lat", "lon"), ncvar[np.newaxis,:,:],attrs_t2)
            },                            
            coords={
                "time": ("time", [hours_since], attrs_time),
                "lat": ("lat", lat, attrs_lat),
                "lon": ("lon", lon, attrs_lon),
                },
            
                        )
 


# 
#                         >>>>>>>>>>>>
#                             rh
#
    elif var == "RH":    

        # all variables available
        var_elements = ['PSFC', 'T2', 'Q2']
        var_keys = list(nc.variables.keys())
        
        counter = 0
        not_key = []
        for n in var_elements:
            if element_exists(var_keys,n):
                counter = counter + 1
            else:
                not_key.append(n)
        
        

        if counter == 3:       
            pvar = nc['PSFC'].data[:].squeeze()/100 # hPa
            tvar = nc['T2'].data[:].squeeze()- 273.15 # C
            qvar = nc['Q2'].data[:].squeeze()
            
            # humedad relativa
            rhvar = sh2rh (pvar * units.hPa, tvar * units.degC,qvar).to('percent')
            
            ds = xr.Dataset(
                
                {"Qair": (("time", "lat", "lon"), rhvar[np.newaxis,:,:],attrs_rh)
                },                            
                coords={
                    "time": ("time", [hours_since], attrs_time),
                    "lat": ("lat", lat, attrs_lat),
                    "lon": ("lon", lon, attrs_lon),
                    },
            
                            )       
        elif counter != 3:
            print ('')
            print (' - - - - - - - - - - - - - - -')
            print ('not all variables available')
            print ('program looking in file for : ')
            print (not_key)
            print (' - - - - - - - - - - - - - - -')

       

# 
#                         >>>>>>>>>>>>
#                              press
#
    elif var ==  "PS":    
        ncvar = nc['PSFC'].data[:].squeeze()/100 # hPa
        
        ds = xr.Dataset(
            
            {"Pair": (("time", "lat", "lon"), ncvar[np.newaxis,:,:],attrs_ps)
            },                            
            coords={
                "time": ("time", [hours_since], attrs_time),
                "lat": ("lat", lat, attrs_lat),
                "lon": ("lon", lon, attrs_lon),
                },
            
                        )

   

# 
#                         >>>>>>>>>>>>
#                           cloud frc
#
    elif var == "CLDFRA":    
        # total cloud fraction
        ncvar=nc.CLDFRA.max(dim='bottom_top').to_dataset()
        ncvar = ncvar['CLDFRA'].data[:].squeeze()
        
        ds = xr.Dataset(
            
            {"cloud": (("time", "lat", "lon"), ncvar[np.newaxis,:,:],attrs_cl)
            },                            
            coords={
                "time": ("time", [hours_since], attrs_time),
                "lat": ("lat", lat, attrs_lat),
                "lon": ("lon", lon, attrs_lon),
                },
            
                        )
  


# 
#                         >>>>>>>>>>>>
#                             pre
#
    elif var == "PR":    
        
        step_b = kwargs.get('step_b', None)

        
        if step_b:
                
            if hours == 0:
                rainnc = nc['RAINNC'].data[:].squeeze()
                rainc  = nc['RAINC'].data[:].squeeze()
                ncvar = rainnc + rainc
            elif hours>0:
                rainnc = nc['RAINNC'].data[:].squeeze()
                rainc  = nc['RAINC'].data[:].squeeze()
                ncvar_now = rainnc + rainc
                #call time step before
                nc = xr.open_dataset(step_b)
                rainnc = nc['RAINNC'].data[:].squeeze()
                rainc  = nc['RAINC'].data[:].squeeze()
                ncvar_before = rainnc + rainc
                ncvar = ncvar_now - ncvar_before
                
            ds = xr.Dataset(
                
                {"rain": (("time", "lat", "lon"), ncvar[np.newaxis,:,:],attrs_pr)
                },                            
                coords={
                    "time": ("time", [hours_since], attrs_time),
                    "lat": ("lat", lat, attrs_lat),
                    "lon": ("lon", lon, attrs_lon),
                    },
                            )                        
                
        elif step_b == None:
            print ('')
            print ('- - - - ERROR - - - - ')
            print ('must be defined step_b')
            print ('- - - - - - - - - - - ')
            print ('')
            
            ds = xr.Dataset()



# 
#                         >>>>>>>>>>>>
#                            lwrad
#
    elif var == "LW":    
        ncvar = nc['GLW'].data[:].squeeze()
        
        ds = xr.Dataset(
            
            {"lwrad_down": (("time", "lat", "lon"), ncvar[np.newaxis,:,:],attrs_lw)
            },                            
            coords={
                "time": ("time", [hours_since], attrs_time),
                "lat": ("lat", lat, attrs_lat),
                "lon": ("lon", lon, attrs_lon),
                },
            
                        )
 


# 
#                         >>>>>>>>>>>>
#                            swrad
#
    elif var == "SW":    
         ncvar = nc['SWDOWN'].data[:].squeeze()
         
         ds = xr.Dataset(
             
             {"swrad": (("time", "lat", "lon"), ncvar[np.newaxis,:,:],attrs_sw)
             },                            
             coords={
                 "time": ("time", [hours_since], attrs_time),
                 "lat": ("lat", lat, attrs_lat),
                 "lon": ("lon", lon, attrs_lon),
                 },
             
                         )



# 
#                         >>>>>>>>>>>>
#                            empty
#
    elif var ==  []:
        
        print ('')
        print ('- - - - ERROR - - - - ')
        print ('Not a valid variable')
        print ('valid values : u10, v10, t2, rh, ps, cldfra, rain, sw, lw')
        print ('variable given:'+var)
        print ('- - - - - - - - - - - ')
        print ('')
        ds = xr.Dataset()




    return ds
   


#%%   ~ ~ ~ ~ ~ ~ 
#
#     
#

  
   
