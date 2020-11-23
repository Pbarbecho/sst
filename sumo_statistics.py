#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 11:00:34 2020

@author: root
"""

# @file    sumo_statistics.py
# @author  Pablo Barbecho
# @author  Guillem
# @date    2020-10-10

#from collections import defaultdict
import argparse
import os
import sys
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom
import seaborn as sns


if 'SUMO_HOME' in os.environ:
    tools = os.path.join('/opt/sumo-1.5.0/', 'tools')
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(tools))
    #from sumolib.output import parse  # noqa
    #from sumolib.net import readNet  # noqa
    from sumolib.miscutils import Statistics  # noqa
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


def get_options(args=None):
    ## Command line options ##
    parser = argparse.ArgumentParser(prog='SUMO Statistics', usage='%(prog)s -c <sumo sim files directory> -s <sumo output files directory>' )
    parser.add_argument('-c', '--sim dir', type=directory_exist, dest='simfiles', help='SUMO simulation files directory (rou/TAZ)')
    parser.add_argument('-s', '--output dir', type=directory_exist, dest='sumofiles', help='SUMO output files directory (tripinfo/summary)')
    options = parser.parse_args(args=args)
    if not options.sumofiles or not options.sumofiles:
        sys.exit("-s [options] and -c [options] are required, see sumo_statistics --help")
    return options


def directory_exist(dir):
    ## validate directory ##
    if os.path.isdir(dir):
       return dir
    else:
        raise argparse.ArgumentTypeError("{} invalid directory ".format(dir))


def xml2df(in_directory, name):
    # output dir
    output = os.path.join(in_directory,'..','xmltocsv', f'{name.strip(".xml")}.csv')
    # SUMO tool xml into csv
    sumo_tool = os.path.join(tools, 'xml', 'xml2csv.py')
    # Run sumo tool with sumo output file as input
    cmd = 'python {} {} -s , -o {}'.format(sumo_tool, os.path.join(in_directory,name), output)
    print(f'{name} -->  {name.strip(".xml")}.csv')
    os.system(cmd)
    # return dataframe
    return pd.read_csv(output)


def summary_example_plots(data, type, input_dir):
    """
    //  Summary Output file structure
    Index(['step_arrived', 'step_collisions', 'step_duration', 'step_ended',
           'step_halting', 'step_inserted', 'step_loaded', 'step_meanSpeed',
           'step_meanSpeedRelative', 'step_meanTravelTime', 'step_meanWaitingTime',
           'step_running', 'step_teleports', 'step_time', 'step_waiting'],
          dtype='object')
    """
    # e.g. plots

    # Time(min) vs vehicles status (inserted running teleported)
    x= data['step_time']/60
    plt.plot(x, data['step_inserted'], linewidth=1.0, label='Inserted veh')
    plt.plot(x, data['step_running'], color='green', linewidth=1.0,  linestyle='--', label='Running veh')
    plt.plot(x, data['step_teleports'], color='red', linewidth=1.0, linestyle='--', label='Teleported veh')
    plt.legend(loc='best')
    plt.xlabel('Time [min]')
    plt.ylabel('# of vehicles')
    plt.savefig(os.path.join(os.path.split(input_dir)[0], '{}_timeVSvehstatus.pdf'.format(type)), bbox_inches="tight")


def merge_data_plots(merge_data, input_dir):
    """
    merge data structure
    Index(['tripinfo_arrival', 'tripinfo_arrivalLane', 'tripinfo_arrivalPos',
           'tripinfo_arrivalSpeed', 'tripinfo_depart', 'tripinfo_departDelay',
           'tripinfo_departLane', 'tripinfo_departPos', 'tripinfo_departSpeed',
           'tripinfo_devices', 'tripinfo_duration', 'tripinfo_rerouteNo',
           'tripinfo_routeLength', 'tripinfo_speedFactor', 'tripinfo_stopTime',
           'tripinfo_timeLoss', 'tripinfo_vType', 'tripinfo_vaporized',
           'tripinfo_waitingCount', 'tripinfo_waitingTime', 'vehicle_depart',
           'vehicle_departLane', 'vehicle_departSpeed', 'vehicle_fromTaz',
           'vehicle_toTaz', 'route_edges'],
    """

    TAZ_statistics = merge_data.groupby('vehicle_fromTaz').describe()
    TAZ_statistics = TAZ_statistics.reset_index(level=list(range(TAZ_statistics.index.nlevels)))
    TAZ_statistics.to_csv(os.path.join(os.path.split(input_dir)[0], 'TAZ_statistics.csv'), header=True)
    # PLOT 1 -> # Number of routes
    ax1 = sns.barplot(TAZ_statistics['vehicle_fromTaz'], TAZ_statistics['tripinfo_routeLength']['count'])
    ax1.set(xlabel=r"Routes", ylabel=r'# of routes')
    plt.savefig(os.path.join(os.path.split(input_dir)[0], 'route_count.pdf'), bbox_inches='tight')
    plt.clf()
    # PLOT 2 -> # Route distance
    ax2 = sns.barplot(TAZ_statistics['vehicle_fromTaz'], TAZ_statistics['tripinfo_routeLength']['mean']/1000)
    ax2.set(xlabel=r"Routes", ylabel=('Route distance [km]'))
    plt.savefig(os.path.join(os.path.split(input_dir)[0], 'route_distance.pdf'),bbox_inches='tight')
    plt.clf()
    # PLOT 3 -> # Route Time
    ax3 = sns.barplot(TAZ_statistics['vehicle_fromTaz'], TAZ_statistics['tripinfo_duration']['mean']/60)
    ax3.set(xlabel=r"Routes", ylabel=('Route time [min]'))
    plt.savefig(os.path.join(os.path.split(input_dir)[0], 'route_time.pdf'),bbox_inches='tight')


def sim_files_search(dir):
    # list sumo simulation files
    sumo_files = os.listdir(dir)
    # Find rou and taz files
    rou_file_name = [file for file in sumo_files 
                     if 'alt' not in file.split('.')
                     if 'dua' in file.split('.')
                     if 'rou' in file.split('.')][0]
    taz_file_name = [file for file in sumo_files if 'TAZ' in file.split('.')][0]
   
    if rou_file_name and taz_file_name:
        return rou_file_name, taz_file_name
    else:
        sys.exit('.rou or TAZ files not found')


def main(args=None):
    # get command line options
    options = get_options(args)
    
    # read sumo tripinfo and summary files
    sumo_file_list = os.listdir(options.sumofiles)
    if sumo_file_list:
        files_dic = {}
        for f in sumo_file_list:
            files_dic[f.strip('.xml')] = xml2df(options.sumofiles, f)
    else:
         sys.exit(f"Empty folder or tripinfo file missing {options.sumofiles}")

    
    # find/convert sumo simulation .rou/taz files
    rou, taz = sim_files_search(options.simfiles)
    rou_file_df = xml2df(options.simfiles, rou)
    
    # Prepare dataframes to merge tripinfo and route files by vehicleID
    rou_file_df.rename(columns={"vehicle_id": "ID"}, inplace=True)
    tripinfo_df = files_dic['tripinfo']
    tripinfo_df.rename(columns={"tripinfo_id": "ID"},  inplace=True)
    
    # merge dataframes
    merge_data = tripinfo_df.set_index('ID').join(rou_file_df.set_index('ID'))
    
    # filter data
    results_name = 'filter_trip_rou_data.csv'
    filtered_data = merge_data[['tripinfo_arrivalSpeed', 
                               'tripinfo_duration',
                               'tripinfo_rerouteNo',
                               'tripinfo_routeLength', 
                               'tripinfo_speedFactor',
                               'tripinfo_departSpeed',
                               'tripinfo_timeLoss', 
                               'tripinfo_vaporized',
                               'tripinfo_waitingCount', 
                               'tripinfo_waitingTime', 
                               'vehicle_type', 
                               'vehicle_fromTaz',
                               'vehicle_toTaz']]
    
    
    # filter unfinished trips or teleported vehicles
    filtered_data = filtered_data.loc[filtered_data['tripinfo_rerouteNo'] == 0 &
                                      filtered_data['tripinfo_vaporized'].empty]
    filtered_data.drop(columns='tripinfo_vaporized', inplace=True)
    
    print(f'Parsed --> {results_name}')

    
    # get plot insigths
    markers=['o','+','x','^','<']
    ax = plt.axes()
    for i, hospital in enumerate(filtered_data['vehicle_toTaz'].unique()):
        df = filtered_data[filtered_data['vehicle_toTaz'] == hospital]
        df.plot.scatter(x='tripinfo_duration',y='tripinfo_routeLength',marker=markers[i], label=hospital, ax=ax)
    #filtered_data["tripinfo_duration"].plot.hist()
    filtered_data.plot.box(figsize=(20,5))
    plt.savefig('/root/Desktop/test.pdf')
    
    
    # data encoder
    filtered_data = pd.get_dummies(filtered_data, columns=['vehicle_fromTaz', 'vehicle_toTaz'])
    
   
    # missing values 
    if True in pd.array(filtered_data.isnull().any()):
       print ('\nMissing values:\n',filtered_data.isnull().any())
       #filtered_data = filtered_data.dropna()
       # fill missing values with mean value e.g. tripinfo duration
       filtered_data['tripinfo_duration'] = filtered_data['tripinfo_duration'].fillna(filtered_data['tripinfo_duration'].mean())
       
    filtered_data.hist() 
    plt.show()       
    filtered_data.to_csv(os.path.join(options.sumofiles,'../parsed',results_name), header=True)           
    
    
if __name__ == "__main__":
    main()