#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 20:54:57 2020

@author: root
"""

import pandas as pd
import sys, os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import scale
import matplotlib.pyplot as plt

parsed_dir = '/root/Documents/SUMO_SEM/CATALUNYA/parsed/'

# import sumo tool xmltocsv
if 'SUMO_HOME' in os.environ:
    tools = os.path.join('/opt/sumo-1.5.0/', 'tools')
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.join(tools))
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")



def save_file(df, name):
    if 'ID' in df.keys():
        df.sort_values(by=['ID'], inplace=True)
    df.to_csv(os.path.join(parsed_dir, f'{name}.csv'), index=False, header=True)
    return df
    
    
def SUMO_preprocess(options):
    # Process SUMO output files to build the dataset
    def xml2csv(options): 
        # convert xml to csv
        files_list = os.listdir(options.sumofiles)
        if files_list:
            print('\nGenerating csv files .........')
            converted_files_dic = {}
            for f in files_list:
                # output directory
                output = os.path.join(options.sumofiles,'..','xmltocsv', f'{f.strip(".xml")}.csv')
                # SUMO tool xml into csv
                sumo_tool = os.path.join(tools, 'xml', 'xml2csv.py')
                # Run sumo tool with sumo output file as input
                cmd = 'python {} {} -s , -o {}'.format(sumo_tool, os.path.join(options.sumofiles,f), output)
                os.system(cmd)
                print(f'{f} -->  {f.strip(".xml")}.csv')
                converted_files_dic[f.strip('.xml')] = pd.read_csv(output)  
            return converted_files_dic
        else:
            sys.exit(f"Empty or missing output data files: {options.sumofiles}")


    def veh_trip_info(df):
        # filter know features
        df = df.filter(items=['tripinfo_duration', 
                              'tripinfo_routeLength', 
                              'tripinfo_timeLoss', 
                              'tripinfo_waitingCount', 
                              'tripinfo_waitingTime', 
                              'tripinfo_arrivalLane', 
                              'tripinfo_departLane',
                              'tripinfo_id']).rename(columns={'tripinfo_id':'ID'})
        return save_file(df, 'tripinfo_df')
    																	      
        
    def lanes_counter_taz_locations(df):
        # contador de edges en ruta
        df['lane_count'] = df['route_edges'].apply(lambda x: len(x.split()))
        df = df.filter(items=['vehicle_id', 'lane_count', 'vehicle_fromTaz', 'vehicle_toTaz']).rename(columns={'vehicle_id':'ID'})
        return save_file(df, 'taz_locations_edgenum_df' )


    def get_positions(df, id,min,max):
        # get initial and end positions based on ini/end time of vehicle id
        ini_pos =  df.loc[(df['vehicle_id'] == id) & (df['timestep_time'] == min)].iloc[0]
        end_pos =  df.loc[(df['vehicle_id'] == id) & (df['timestep_time'] == max)].iloc[0]
        return id, min, max, ini_pos.vehicle_x, ini_pos.vehicle_y, end_pos.vehicle_x, end_pos.vehicle_y 
        
       
    def avrg_speed_and_geo_positions(df):
        # get average speed
        speed_df = df.groupby(['vehicle_id']).mean().reset_index()
        speed_df = speed_df.filter(items=['vehicle_id','vehicle_speed']).rename(columns={'vehicle_id':'ID','vehicle_speed':'avrg_speed'})
        # Prepare df with ini end times of vehicles 
        df = df.filter(items=['vehicle_id', 'timestep_time','vehicle_x', 'vehicle_y'])
        df.dropna(subset = ["vehicle_id"], inplace=True)
        # get initial end times of vechiel
        time_df = df.groupby(['vehicle_id']).timestep_time.agg(['min','max']).reset_index()
        # Get positions df
        positions_list = [get_positions(df,id,min,max) for id,min,max in zip(time_df['vehicle_id'], time_df['min'], time_df['max'])]
        positions_df = pd.DataFrame(positions_list, columns=['ID', 'ini_time', 'end_time', 'ini_x_pos', 'ini_y_pos','end_x_pos', 'end_y_pos'])
        # Merge speed and positions df
        speed_and_positions = speed_df.merge(positions_df, on='ID')
        return save_file(speed_and_positions, 'avrg_speed_positions_df')
    
    
    sumo_dic = xml2csv(options)                                                                   # Get sumo output files into a dictionary of dataframes
    taz_locations_edgenum_df = lanes_counter_taz_locations(sumo_dic['vehroute'])                  # Count edges on route from vehroute file and get from/to TAZ locations
    veh_speed_positions_df = avrg_speed_and_geo_positions(sumo_dic['fcd'])                        # Get average speed and initial/end positions (x,y)
    tripinfo_df = veh_trip_info(sumo_dic['tripinfo']) 
    
    # find/convert sumo simulation .rou/taz files
    #rou, taz = sim_files_search(options.simfiles)
    
    # merge dataframes
    data = taz_locations_edgenum_df.merge(veh_speed_positions_df,on='ID').merge(tripinfo_df,on='ID')
    print('Parsed --> data.csv')
    return save_file(data, 'data.csv')
    
    
    
def preprocess(df):
    def remove_outage_points(df):
        # filter unfinished trips or teleported vehicles
        df = df.loc[df['tripinfo_timeLoss'] < 200]     # From the histogram analysis we cas see 200s
        #df = df[(df['tripinfo_duration'] >= 2000) & (df['tripinfo_duration'] <= 3500)]
        return df
        
    
    def encode_data(df):
        # data encoder  string to numeric
        df = pd.get_dummies(df, columns=['vehicle_fromTaz', 'vehicle_toTaz'])
        return df
        
    
    def fill_na_tripduration_value(df):
         # missing values 
        if True in pd.array(df.isnull().any()):
           print ('\nMissing values:\n',df.isnull().any())
           #filtered_data = filtered_data.dropna()
           # fill missing values with mean value e.g. tripinfo duration
           df['tripinfo_duration'] = df['tripinfo_duration'].fillna(df['tripinfo_duration'].mean())
           return df
    
    def remove_features(df):
        # remove no relevant features
        df = df.drop([
            'ID',
            'ini_x_pos',
            'ini_y_pos',
            'end_x_pos',
            'end_y_pos',
            'ini_time',	
            'end_time',
            'lane_count',
        #    'tripinfo_routeLength'	
        #    'tripinfo_timeLoss'	,
            'tripinfo_waitingCount'	,
            'tripinfo_waitingTime'	,
            'vehicle_fromTaz_HospitalViladecans',	
            'vehicle_fromTaz_HospitaldeBarcelona',	
            'vehicle_toTaz_Barcelona'	,
            'vehicle_toTaz_Sitges'	,
            'vehicle_toTaz_Terrasa'	,
            'tripinfo_arrivalLane',	
            'tripinfo_departLane'
                        ],axis=1)
        return df
    
    def add_features(df):
        # add features (know the problmem)
        # speed
        df['Speed'] = df['tripinfo_routeLength'] / df['tripinfo_duration']
        return df
    
    df = remove_outage_points(df) 
    df = encode_data(df) 
    #df = fill_na_tripduration_value(df)
    df = remove_features(df)                                                                  # remove unused features
    #df = add_features(df)  
    return save_file(df,'preprocess_data')       


def scale_df(df, v_predicted): 
    # Scale preprocess values
    pre_scaled = df.copy()
    df_scaled = pre_scaled.drop([v_predicted], axis=1)                                    # before scaling we should remove the output
    df_scaled = scale(df_scaled)
    # concat scaled and output 
    col = df.columns.tolist()
    col.remove(v_predicted)
    df_scaled = pd.DataFrame(df_scaled, columns=col, index=df.index)
    df_scaled = pd.concat([df_scaled, df[v_predicted]], axis=1)
    return save_file(df_scaled,'scaled_data')           
     

def feature_importance(df, X_train, y_train):
    # Assessing feature importance with random forests
    feat_labels = df.columns[:]
    forest = RandomForestClassifier(n_estimators=500,random_state=0,n_jobs=-1)
    forest.fit(X_train, y_train)
    importances = forest.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    #for f in range(X_train.shape[1]):
    #    print("%2d) %-*s %f" % (f + 1, 30, feat_labels[indices[f]], importances[indices[f]]))
    
    plt.title('Feature Importances')
    plt.bar(range(X_train.shape[1]), importances[indices], color='lightblue',align='center')
    plt.xticks(range(X_train.shape[1]),feat_labels[indices], rotation=90)
    plt.xlim([-1, X_train.shape[1]])
    plt.tight_layout()
    plt.savefig('/root/Documents/SUMO_SEM/CATALUNYA/plots/feature_importance.pdf')  
    
    
def plot_predict_vs_real(predicted, real, samples):    
    y_real = real.to_numpy()
    y_predicted = predicted
    
    plt.plot(y_real[:samples]/60,'o-', label='Real')
    plt.plot(y_predicted[:samples]/60, 'o-', label='Predicted')
    plt.title('Trip time prediction')
    plt.grid(None)
    plt.xlabel('Samples')
    plt.ylabel("Trip time [min]")
    plt.legend()
    plt.show()
    
    
    
    
    
    
    
    
    
    
    