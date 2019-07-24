# File exported from the postgres database
## Link to files: https://drive.google.com/open?id=1RTJ1d-wUKp98q-d3W95_Rb6rJ7yrNu85

### *bicicas-nov-dec-jan.csv*  
####Attributes: 
- id: id generated 
- time_scrape:  timestamp when the data was collected
- feature_colection: retrieved (raw) data stored in geoJSON format containing the  data seen in https://ws2.bicicas.es/bench_status_map 

# Files obtained using the format-and-cleaning.py script.

### *stations_info_nov-dec-jan.csv*
Obtained with the function get_stations_info
#### Attributes:
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


### *records_nov-dec-jan_original.csv*
Obtained with the function obtain_records
####Attributes:
- time_scraped: timestamp tz= “UTC” when the data was collected
- bicycle: the number of bicycle parked or NULL if it is empty.
- station_id: station id number
- name: station name
- long: station longitude coordinate
- lat: station latitude coordinate
- anchor: anchor id number
- incident: [ ] if there is no incident or [ 0 ] if the bicycle or the anchor cannot be used.

### *bikes_numbers.csv*
Created by the obtain_records function. 

### *records_nov-dec-jan_cleaned.csv*
Obtained with the function delete_duplicated_records (after 4 iterations)
Contain unnecessary indexes columns. 

### failing_anchors.csv 
Created by the function delete_duplicated_records.
(4 files were created during the iterations, already merged in this file)

### bike_movements_nov-dec-jan 
Obtained with the function get_movements.
####Attributes:
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
- anchor_end: ending anchor id


