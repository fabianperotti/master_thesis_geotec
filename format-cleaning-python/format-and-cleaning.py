#####################################################################
########                                                     ########
########                  Libraries                          ########
########                                                     ########
#####################################################################
import os
import pandas as pd
import json
import datetime
import csv
import numpy as np

#####################################################################
######## Creates dataset with the stations data from         ########
######## the json column, considering each time of           ########
########  the data collected                                 ########
#####################################################################

def get_stations_info(file, fileoutput):
    df = pd.read_csv(file)
    stdf = df['feature_collection'].apply(json.loads)
    time_scrape = df['time_scrape']

    rows_stations = []
    for time in range(len(time_scrape)):
        t = time_scrape[time]
        record = stdf[time]
        stations = record["features"]
        for station in stations:
            long = station["geometry"]["coordinates"][0]
            lat =  station["geometry"]["coordinates"][1]
            name = station["properties"]["name"]
            station_id = int(name.split(".")[0])
            bikes_total = station["properties"]["bikes_total"]
            bikes_available = station["properties"]["bikes_available"]
            last_seen = station["properties"]["last_seen"]
            number_loans = station["properties"]["number_loans"]
            incidents = station["properties"]["incidents"]
            online = station["properties"]["online"]
            row = [t,station_id, name, long, lat,bikes_total, bikes_available, number_loans, incidents, last_seen, online ]
            rows_stations.append(row)

    rows_df = pd.DataFrame(rows_stations, columns=["time_scraped","station_id", "name",  "long", "lat", "bikes_total", "bikes_available",  "number_loans", "incidents", "last_seen", "online"])
    rows_df.to_csv(fileoutput, encoding = "utf-8")

#####################################################################
######## Creates dataset with the bikes numbers from         ########
######## the json, considering each time of the data         ########
######## collected, also a file with the list of bikes       ########
#####################################################################

def obtain_records(file, fileoutput):
    df = pd.read_csv(file)
    stdf = df['feature_collection'].apply(json.loads)
    time_scrape = df['time_scrape']
    # print(time_scrape)
    df_bikes_raw = pd.DataFrame(columns=["time_scraped", "bicycle", "station_id", "name", "long", "lat", "anchor", "incident"])
    rows = []
    bikes_numbers = []
    for time in range(len(time_scrape)):
        t = time_scrape[time]
        record = stdf[time]
        stations = record["features"]
        for station in stations:
            long = station["geometry"]["coordinates"][0]
            lat =  station["geometry"]["coordinates"][1]
            name = station["properties"]["name"]
            station_id = int(name.split(".")[0])
            anchors = station["properties"]["anchors"]
            for anchor in anchors:
                number = anchor["number"]
                bicycle = anchor["bicycle"]
                incident = anchor["incidents"]
                row =[t, bicycle, station_id, name, long, lat, number, incident]
                rows.append(row)
                ######## Get bikes numbers  ########
                if bicycle is not None:
                    if not bicycle in bikes_numbers:
                        bikes_numbers.append(bicycle)
                #####################################
        print("ready ", time, "of ", len(time_scrape))

    rows_df = pd.DataFrame(rows, columns=["time_scraped", "bicycle", "station_id", "name", "long", "lat", "anchor", "incident"] )
    bikes_raw  = pd.concat([df_bikes_raw, rows_df], ignore_index=True)
    bikes_numbers = pd.DataFrame(sorted(bikes_numbers), columns=["bicycle"] )
    bikes_numbers.to_csv("bikes_numbers.csv", encoding = "utf-8")
    bikes_raw.to_csv(fileoutput, encoding = "utf-8")


#####################################################################
######## Split list according to elements in other list      ########
########  function used in delete_duplicated_records         ########
#####################################################################
#adapted from https://stackoverflow.com/questions/32618390/python-split-list-in-to-sublists-based-on-another-list
def split_list(a, b):
    it = iter(b)
    start, sub = next(it), []
    append = sub.append
    for ele in a:
        if start <= ele:
            yield sub
            start, sub = next(it), []
            append = sub.append
        append(ele)
    yield sub

def split_list_index_based(a, b):
    it = iter(b)
    start, sub = next(it), []
    append = sub.append
    for i in range(len(a)):
        ele = a[i]
        if start <= i:
            yield sub
            start, sub = next(it), []
            append = sub.append
        append(ele)
    yield sub



#####################################################################
######## Check for duplicated times in data due to errors    ########
######## in anchors of bicicas                               ########
########                                                     ########
#####################################################################
# Some stations(anchors) keep recording the bike as parked after it was taken,
# creating a fake record of that bike that moves around the city
# and changes position. This results in a bike at 2 positions at the
#same time, one "still parked" at the wrong station and the real one.
#  The number of observations produced by the "broken" station is usually  higher
# than the stations where the bikes moves.
# time  station anchor
# t0      1       3
# t1      1       3
# t1      2       5
# t2      1       3
# t2      6       1
# t3      1       3
# t4      9       2
# t4      1       3

def delete_duplicated_records(file, bike_numbers_file,  fileoutput, fileoutput_nw):
    df_st = pd.read_csv(file, encoding = "ISO-8859-1")
    print('len orginal', len(df_st))
    df_bikes = pd.read_csv(bike_numbers_file, encoding = "ISO-8859-1")
    bikes_numbers = df_bikes['bicycle']
    rows_nw = []
    frames = []
    na_subset = df_st[df_st.bicycle.isna()]
    na_subset = na_subset.reset_index(drop=True)
    frames.append(na_subset)

    # Counts how many times the time is repeated, mostly 2 but sometimes up to 4 or 5
    count_times = df_st.groupby(['time_scraped', 'bicycle']).size().reset_index(name='counts')
    print(max(count_times.counts))
    max_repeated_date = max(count_times.counts)

    for i in range(len(bikes_numbers)):
        position = i+1 # to print
        bike = bikes_numbers[i]
        subset = df_st[df_st.bicycle.isin([bike])]
        #print(type(subset))
        #print(len(subset))
        temp_index = list(range(len(subset)))
        subset = subset.reset_index(drop=True)
        subset = pd.DataFrame(data = subset, index= temp_index)

        wrong_times = [] #the duplicated times
        breaks_index = [] #the position of the jumps between dates greater than 12 minutes
        first_sub_index = []
        stations_in_conflict = [] #stations that share the same time "%Y-%m-%d %H:%M"
        anchors_conflict = [] #anchotrs that share the same time

        # for every record compares it with the next one, if the time is the same
        #the time is stored in wrong_times, and the stations and anchors for these
        #times are stored in  stations_in_conflict and anchors_conflict
        count_times2 = subset.groupby(['time_scraped']).size().reset_index(name='counts')
        wrong_times_unique = []
        wrong_times_str =  []
        for ct in (range(len(count_times2))):
            n = count_times2.loc[ct,'counts']
            t = count_times2.loc[ct,'time_scraped']
            if (n > 1):
                t2 = datetime.datetime.strptime(t[:16], "%Y-%m-%d %H:%M")
                wrong_times.extend([t2] * n)
                wrong_times_unique.append(t)
                wrong_times_str.extend([t] * n)
        #print(wrong_times)

        for wt in wrong_times_unique:
             wrong_ind = subset.index[subset['time_scraped'] == wt].tolist()
             first_sub_index.extend(wrong_ind)
             wrong_rec = subset[subset.time_scraped.isin([wt])]
             for e in range(len(wrong_rec)):
                 record = wrong_rec.iloc[e, :]
                 # print(record)
                 stations_in_conflict.append(record.station_id)
                 anchors_conflict.append(record.anchor)

        st_with_anchors =  list(zip(stations_in_conflict,anchors_conflict))
        # print(st_with_anchors)
        # print(stations_in_conflict)
        # print(anchors_conflict)
        # print(first_sub_index)
        # print(len(wrong_times))
        # print(len(stations_in_conflict))
        # print(len(anchors_conflict))
        # print(len(first_sub_index))

        #if there is no duplicated times the records are stored
        if (len(wrong_times) == 0):
            subset = subset.reset_index(drop=True)
            frames.append(subset)
            print('correct!')
        #else, the times are grouped divided when a break higher than 12 minutes
        #is detected. This breaks are produced when a journey lasted more than 10
        #minutes or the station stoped recording wrong values and other station
        #begun to fail.
        else:
            # print(subset)
            # print(len(subset))
            #Detects when the breaks happens
            for i in range(len(wrong_times)-1):
                t0 = wrong_times[i]
                t1 = wrong_times[i+1]
                if ((t1 - t0) > datetime.timedelta(minutes=15)) :
                    breaks_index.append(i+1)
            breaks_index.append(len(stations_in_conflict)) #add to cut at the last break

            #group the wrong_times by interlvals considering the breaks
            #group the stations in conlfict by interlvals considering the breaks
            broken_list2 = (list(split_list_index_based(wrong_times,breaks_index)))
            stations_split = (list(split_list_index_based(stations_in_conflict,breaks_index)))

            st_with_anchors_sp = (list(split_list_index_based(st_with_anchors,breaks_index)))
            print("st with anc sp", st_with_anchors_sp)

            #See the stations in common between one group and the next one
            #when there is no common station among breaks, here the error of
            #one station stopped and other station started to fail
            l3 = []
            for i in range(len(st_with_anchors_sp)-1):
                l1 = st_with_anchors_sp[i]
                l2 = st_with_anchors_sp[i+1]
                l3.append(list(set(l1).intersection(l2)))
            change_error = []
            print(l3)

            for i in range(len(l3)):
                l4 = l3[i]
                if len(l4) == 0:
                    change_error.append(breaks_index[i])
            change_error.append(len(stations_in_conflict))  #add to cut at the last break
            print('change_error', change_error)

            #The station is grouped with their anchor and then
            # divided according where the error changes

            anchors_split =  (list(split_list_index_based(st_with_anchors,change_error)))
            # print("anc split ", anchors_split)

            wt_sp =  (list(split_list_index_based(wrong_times_str,change_error)))
            # print('wt_sp', wt_sp)
            # print(len(wt_sp))
            # print(len(anchors_split))
            # Detect which station (anchor) is the one not working
            anchors_detected = []
            conflict_detected = []

            for g in range(len(anchors_split)):
                gr_times = wt_sp[g]
                n = {x:gr_times.count(x) for x in gr_times}
                n_values = n.values()
                # print('n_val', n_values )
                n_mean  = np.mean(sorted(n.values(), reverse=True))
                # print(n_mean)
                group = anchors_split[g]
                d = {x:group.count(x) for x in group }
                # print('d', d)
                d_values = sorted(d.values(), reverse=True)
                # print('d_values', d_values)
                if (d_values[0] != d_values[1] and n_mean == 2) :
                    detected = max(d, key=lambda key: d[key])
                    anchors_detected.append(detected[1])
                    conflict_detected.append(detected[0])

                else:# elif (d_values[0] == d_values[1] and n_mean == 2) :
                    group_ind = anchors_split.index(group)
                    # print("first_sub_index", first_sub_index)
                    first_sub_index_splited = (list(split_list_index_based(first_sub_index, change_error)))[group_ind]
                    # check for the station in time before
                    index_of_time_before_duplicated = (first_sub_index_splited[0]-1)
                    record_before = subset.iloc[index_of_time_before_duplicated,:]
                    st_anc_before = (record_before.station_id, record_before.anchor)
                    # print(st_anc_before)
                    if st_anc_before in d:
                        anchors_detected.append(st_anc_before[1])
                        conflict_detected.append(st_anc_before[0])
                    else:
                        detected = max(d, key=lambda key: d[key])
                        anchors_detected.append(detected[1])
                        conflict_detected.append(detected[0])
                        # print('detected', detected)
            # print(anchors_detected)
            # print(conflict_detected)

            # Get the gap time where the station must be removed from
            wrong_times_split2 = []
            wrong_times_split2.append(min(wrong_times))
            for i in change_error:
                wrong_times_split2.append(wrong_times[i-1])
            #avoid the  records with  the station (anchor) in conflict
            #valuated on the times

            st_anc_detected =  list(zip(conflict_detected,anchors_detected))
            # print('st anc dete', st_anc_detected)
            # print('wrt2', wrong_times_split2)
            for i in (range(len(subset))):
                record = subset.iloc[i,:]
                station = record.station_id
                anchor =  record.anchor
                st_anc = (station, anchor)
                if st_anc in st_anc_detected:
                    time1 = record.time_scraped
                    time2 = datetime.datetime.strptime(time1[:16], "%Y-%m-%d %H:%M")
                    # anchor = record.anchor
                    ind = st_anc_detected.index(st_anc)
                    # anc = anchors_detected[ind]
                    t0 = wrong_times_split2[ind]
                    t1 = wrong_times_split2[ind+1]
                    if time2 >= t0 and time2 <=t1:
                        # print('ind', ind, 'station', station, 'anchor', anchor, 'time', time2 )
                        row =[record.time_scraped, record.bicycle, record.station_id, record.name, record.long, record.lat, record.anchor, record.incident]
                        rows_nw.append(row)
                        subset.loc[i,'bicycle'] = None
                        # print(subset.loc[i,:])
            # print(rows_to_be_deleted)
            # print(len(rows_to_be_deleted))
            # print(subset)
            # print(len(subset))
            subset = subset.reset_index(drop=True)
            # print(subset)
            # print(len(subset))
            frames.append(subset)

        print("finished bicycle ", bike, " - ", position, " of ", len(bikes_numbers))

    finalcleaned = pd.concat(frames)
    finalcleaned = finalcleaned.reset_index(drop=True)
    final_index = list(range(len(finalcleaned)))
    finalcleaned = pd.DataFrame(data = finalcleaned, index= final_index)
    print(len(finalcleaned))
    finalcleaned.to_csv(fileoutput, encoding = "utf-8")
    rows_df = pd.DataFrame(rows_nw, columns=["time_scraped", "bicycle", "station_id", "name", "long", "lat", "anchor", "incident"] )
    rows_df.to_csv(fileoutput_nw, encoding = "utf-8")

#####################################################################
########                                                     ########
########    bikes movement from one station to other         ########
########                                                     ########
#####################################################################

def get_movements(file,  bike_numbers_file,  fileoutput):
    df_movement = pd.DataFrame(columns=["bicycle", "time_start", "station_start", "st_name_start", "long_start", "lat_start", "anchor_start","time_end", "station_end", "st_name_end", "long_end", "lat_end", "anchor_end"])
    df_st  = pd.read_csv(file, encoding = "ISO-8859-1")
    df_bikes = pd.read_csv(bike_numbers_file, encoding = "ISO-8859-1")
    
    frames = []
    bikes_numbers = df_bikes['bicycle']
    for i in range(len(bikes_numbers)):
        rows = []
        bike = bikes_numbers[i]
        position = i+1
        subset = df_st[df_st.bicycle.isin([bike])]
        subset = subset.sort_values(by=['time_scraped'])
        for j in (range(len(subset)-1)):
            record_start = subset.iloc[j,:]
            station_start = record_start.station_id
            anchor_start = record_start.anchor
            record_end = subset.iloc[j+1,:]
            station_end = record_end.station_id
            anchor_end = record_end.anchor

            if station_start != station_end or anchor_start != anchor_end :
                st_name_start = subset.iloc[j].loc['name']
                time_start = record_start.time_scraped
                long_start = record_start.long
                lat_start = record_start.lat
                anchor_start = record_start.anchor
                st_name_end =  subset.iloc[j+1].loc['name']
                time_end = record_end.time_scraped
                long_end = record_end.long
                lat_end = record_end.lat
                anchor_end = record_end.anchor
                row = [bike, time_start, station_start, st_name_start, long_start, lat_start, anchor_start,time_end, station_end, st_name_end, long_end, lat_end, anchor_end ]
                rows.append(row)

        rows_df = pd.DataFrame(rows, columns=["bicycle", "datetime_start", "station_start", "st_name_start", "long_start", "lat_start", "anchor_start","datetime_end", "station_end", "st_name_end", "long_end", "lat_end", "anchor_end"])
        frames.append(rows_df)
        print("finished bicycle ", bike, " - ", position, " of ", len(bikes_numbers))

    bikes_movement = pd.concat(frames)

    bikes_movement = bikes_movement.reset_index(drop=True)
    final_index = list(range(len(bikes_movement)))
    bikes_movement = pd.DataFrame(data = bikes_movement, index= final_index)
    print(len(bikes_movement))
    # print(bikes_movement)
    bikes_movement.to_csv(fileoutput, encoding = "utf-8")
