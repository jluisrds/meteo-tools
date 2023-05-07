#/bin/bash
# 
# Version: 0.1 date: 2023/05/05
#          -.- date: 202-/--/--
# 
# Script to download selected GFS 0.25 data for a forecast 
# period from the NCEP NOAA database
# 
#
# Author: Jose Luis Rodriguez-Solis
#         jrodriguez@cicese.edu.mx
#         
#
#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                      begin user section
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
#
# enclose your subregion
# choose your latitude and longitude coordinates
# description:
#                bottomlat: south latitude
#                toplat   : north latitude
#                rightlon : west longitude
#                leftlon  : east longitude
#
# FORMAT: integer

bottomlat=5
toplat=45
rightlon=-140
leftlon=-30

#
# The first version just  00z or 12z   run  is donwloaded.
# At 08:00 hrs [PST UTC-8]  the 00z run is desire, but  if 
# it is not available  the  12z run of the day before will
# be instead. Also  option run can be changed for the 00z, 
# 06z,12z and 18z.
# FORMAT: integer
#

run=00

#
# Date is choosen by user or automatically. If option -on-
# is selected user must especify the date of the data re--
# quired. Option -off- let the script download the 00z run 
# data if it is available, otherwise  the  12z run of  the
# day before will be download.
# FORMAT: character
#


user_date='off'

# 
# Path directory where data will be stored. A folder  will
# be created with the format yyyymmdd_rr. This option  can
# be turned -off-  and  then  the script  creates a folder 
# where it is running
# FORMAT: character

path_to_store='off'

#
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#                      end user section
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# _______________
#
#  Begin program
# _______________
#
#
# variables
# 

#    >> text color
#
r='\033[0;31m' # rojo
N='\033[0m'    # No Color

#    >> what day is today
today=`date -d" 0 days" +%Y%m%d`
ti=`date -d" 0 days" +%k| sed 's/[^0-9]//g'`


# let me know the data storing directory
if [ $path_to_store -qe 'off' ]; then
  mkdir -p 
fi

# 
directorio=`pwd`

#rm $directorio/data/*.grb2

echo --------------------------
echo  ${r}borrando archivos grb2 en el directorio data...${N}
echo --------------------------


#rm /home/clima/Documents/forecast/GFS_grib025/viento/*.png

echo --------------------------
echo -e ${r}comienza la descarga de datos del ncdc...${N}
echo --------------------------

ni=6
np=6
nf=168

f=`date -d" 0 days" +%Y%m%d`
ti=`date -d" 0 days" +%k| sed 's/[^0-9]//g'`

if [ $ti -lt 11 ]; then
  run="00"
  ni=18
  np=6
  nf=180  
fi
#-------------------------------------------------------------------------------------

for i in $(seq -f "%03g" $ni $np $nf)
  do
  echo -e ${r}grib $i${N}
  url="https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl?file=gfs.t"$run"z.pgrb2.0p25.anl&all_lev=on&all_var=on&leftlon="$leftlon"&rightlon="$rightlon"&toplat="$toplat"&bottomlat="$bottomlat"&dir=%2Fgfs.20230504%2F12%2Fatmos"
  wget  $url 
done




