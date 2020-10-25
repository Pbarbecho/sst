# @file    sumo_statistics.py
# @author  Pablo Barbecho
# @author  Guillem
# @date    2020-10-10

#from collections import defaultdict
import argparse
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from pandasgui import show
import numpy as np
from xml.dom import minidom
import seaborn as sns


if 'SUMO_HOME' in os.environ:
    tools = os.path.join('/opt/sumo-1.5.0/', 'tools')
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(tools))
    #from sumolib.output import parse  # noqa
    #from sumolib.net import readNet  # noqa
    #from sumolib.miscutils import Statistics  # noqa
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


def get_options(args=None):
    ## Command line options ##
    parser = argparse.ArgumentParser(prog='SUMO Statistics', usage='%(prog)s -t <type of file>  -i <sumo output file> -s <sumo sim files directory>' )
    parser.add_argument('-t', '--type', dest='type', help='(tripinfo/summary/emmisions) type of output file', default='tripinfo')
    parser.add_argument('-i', '--input', type=file_exist, dest='input', help='SUMO output file (tripinfo/summary/emmisions)')
    parser.add_argument('-s', '--dir', type=directory_exist, dest='sumofiles', help='Path of SUMO simulation files (.rou, TAZ)')
    options = parser.parse_args(args=args)
    if not options.type in ['tripinfo', 'summary', 'emmisions']:
        sys.exit("Type not valid")
    if not options.input:
        sys.exit("SUMO output file is required as input -i [option]")
    if not options.sumofiles:
        sys.exit("Path to SUMO simfiles is required -s [option]")
    return options


def file_exist(dir_name):
    ## Validate input file ##
    dir, name = os.path.split(dir_name)
    directory_exist(dir)
    dir_files = os.listdir(dir)
    if name in dir_files:
        return dir_name
    else:
        raise argparse.ArgumentTypeError("{}{} file not found".format(dir, name))


def directory_exist(dir):
    ## validate directory ##
    if os.path.isdir(dir):
       return dir
    else:
        raise argparse.ArgumentTypeError("{} invalid directory ".format(dir))


def xml2df(indir, outdir, name):
    # output dir
    output = os.path.join(outdir, 'converted_{}.csv'.format(name.split('.')[0]))
    # SUMO tool xml into csv
    sumo_tool = os.path.join(tools, 'xml', 'xml2csv.py')
    # Run sumo tool with sumo output file as input
    cmd = 'python {} {} -s , -o {}'.format(sumo_tool, os.path.join(indir,name), output)
    os.system(cmd)
    # return dataframe
    return pd.read_csv(output)


def example_plots(data, type, input_dir):
    """
    //  Summary Output file structure
    Index(['step_arrived', 'step_collisions', 'step_duration', 'step_ended',
           'step_halting', 'step_inserted', 'step_loaded', 'step_meanSpeed',
           'step_meanSpeedRelative', 'step_meanTravelTime', 'step_meanWaitingTime',
           'step_running', 'step_teleports', 'step_time', 'step_waiting'],
          dtype='object')

    //  Tripinfo Output file structure
    Index(['tripinfo_arrival', 'tripinfo_arrivalLane', 'tripinfo_arrivalPos',
       'tripinfo_arrivalSpeed', 'tripinfo_depart', 'tripinfo_departDelay',
       'tripinfo_departLane', 'tripinfo_departPos', 'tripinfo_departSpeed',
       'tripinfo_devices', 'tripinfo_duration', 'tripinfo_id',
       'tripinfo_rerouteNo', 'tripinfo_routeLength', 'tripinfo_speedFactor',
       'tripinfo_stopTime', 'tripinfo_timeLoss', 'tripinfo_vType',
       'tripinfo_vaporized', 'tripinfo_waitingCount', 'tripinfo_waitingTime'],
      dtype='object')

    """
    # e.g. plots
    if type == 'summary':
        # Time(min) vs vehicles status (inserted running teleported)
        x= data['step_time']/60
        plt.plot(x, data['step_inserted'], linewidth=1.0, label='Inserted veh')
        plt.plot(x, data['step_running'], color='green', linewidth=1.0,  linestyle='--', label='Running veh')
        plt.plot(x, data['step_teleports'], color='red', linewidth=1.0, linestyle='--', label='Teleported veh')
        plt.legend(loc='best')
        plt.xlabel('Time [min]')
        plt.ylabel('# of vehicles')
        plt.savefig(os.path.join(os.path.split(input_dir)[0], '{}_timeVSvehstatus.pdf'.format(type)), bbox_inches="tight")
    #if type == 'tripinfo':
        # Time(min) vs vehicles status (inserted running teleported)
        # tripinfo_routeLength


def SUMO_files_search(dir):
    # list sumo simulation files
    sumo_files = os.listdir(dir)
    # Find rou and taz files
    rou_file_name = [file for file in sumo_files if 'rou' in file.split('.')][0]
    taz_file_name = [file for file in sumo_files if 'TAZ' in file.split('.')][0]
    return rou_file_name, taz_file_name


def main(args=None):
    # get command line options
    options = get_options(args)
    # tripinfo/summary files
    dir, name = os.path.split(options.input)
    # convert sumo output file to df
    sumo_output_file_df = xml2df(dir, dir, name)

    # Merge tripinfo and route files by vehicleID
    if options.type == 'tripinfo':
        # convert to df .rou/taz files
        rou, taz = SUMO_files_search(options.sumofiles)
        rou_file_df = xml2df(options.sumofiles, dir, rou)
        # Merge dataframes by index "ID"
        rou_file_df.rename(columns={"vehicle_id": "ID"}, inplace=True)
        sumo_output_file_df.rename(columns={"tripinfo_id": "ID"},  inplace=True)
        trip_rou_data = sumo_output_file_df.set_index('ID').join(rou_file_df.set_index('ID'))
        gui = show(trip_rou_data)
        # save merge file
        trip_rou_data.to_csv(os.path.join(dir, 'trip_rou_data.csv'), header=True)
    elif options.type == 'summary':
        # convert summary file to df
        None
    else:
        sys.exit("Type not valid")

    # Plot statistics
    example_plots(sumo_output_file_df, options.type, options.input)



if __name__ == "__main__":
    main()