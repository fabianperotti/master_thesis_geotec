# Data formating and cleaning Functions in Python

### *get_stations_info*
Get the information related to the stations. 
Parameters: 
- file: csv file (exported from pgAdmin) containing columns id, time_scrape, feature collection 
- output_file: output file eg. stations_info.csv 

The output file contains the following attributes:
- time_scraped: timestamp tz= “UTC” when the data was collected 
- station_id: station number id 
- name: station name
- long: longitude coordinate
- lat: latitude coordinate
- bikes_total: total number of bikes parked at the station
- bikes_available:number of bikes available to be used
- number_loans: number of loans given from that station. Cumulative number of bikes taken by the users throughout the day. The count re-starts from zero at 5 am every day.  (The number could not re-start some days due to failures)
- incidents:total number of incidents reported by the anchors of the station
- last_seen: last time when the station was accessed 
- online: TRUE if the station is online or FALSE if it is offline. 

### *obtain_records*
Get the information related to the bicycles/anchors and creates a file contining the bicycles Ids called bikes_numbers.csv 
Parameters: 
- file: input csv file (exported from pgAdmin) containing columns id, time_scrape, feature collection 
- output_file: output file eg. records.csv  

The output file contains the following attributes:
- time_scraped: timestamp tz= “UTC” when the data was collected 
- bicycle: the number of bicycle parked or NULL if it is empty. 
- station_id: station id number 
- name: station name
- long: station longitude coordinate
- lat: station latitude coordinate
- anchor: anchor id number 
- incident:  [ ] if there is no incident or [ 0 ] if the bicycle or the anchor cannot be used. 


### *delete_duplicated_records*
Some anchors keep recording the bike as parked after it was taken, creating a fake record of that bike which moves between different stations. This function detects the failing anchors, correct the error generation 2 files: one with the records cleaned and the other one containing the failing anchors/bicycles records.
To obtained the final cleaned dataset the records file need to be processed as many times as the maximum number of “failing anchors” at the same time happens.
The files containing the failing anchors datasets have to be merged later.

Parameters: 
- file: file obtained from the obtain_records function (eg. records.csv)
- bike_numbers_file: file containing the bicycle ids (bikes_numbers.csv)
- fileoutput: output file with the clean records eg. clean-records_1.csv  
- fileoutput_nw: output file with the failing anchors/byclcews eg. not-working_1.csv   

(iterating causes unnecessary indexes columns that should be deleted later)

### *get_movements*
Obtain the trips per bike when a bike changes station or anchor. 
 
Parameters: 
- file: final file obtained from the delete_duplicate_records function (eg. clean-records_n.csv)
- bike_numbers_file: file containing the bicycle ids (bikes_numbers.csv)
- fileoutput:  output file with the bicycles trajectories eg. Bike-movements.csv

The output file contains the bicycles` trips with the following attributes:
- bicycle: bicycle id number
- datetime_start: starting timestamp tz = UTC 
- station_start: starting station ID 
- st_name_start: starting station name
- long_start: starting station longitude
- lat_start: starting station latitude
- anchor_start: starting anchor id
- datetime_end: ending timestamp tz = UTC  
- station_end: ending station id
- st_name_end: ending station name
- long_end: ending station longitude
- lat_end: ending station latitude
- anchor_end:  ending anchor id
