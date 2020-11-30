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
import sys, os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom
import seaborn as sns
from sklearn.preprocessing import scale
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from utils import xml2csv, lanes_counter_taz_locations, avrg_speed_and_geo_positions, veh_trip_info, remove_outage_points, encode_data, remove_features, add_features, feature_importance
from keras.callbacks import EarlyStopping
from sklearn.metrics import mean_squared_error
 

def get_options(args=None):
    ## Command line options ##
    parser = argparse.ArgumentParser(prog='SUMO Statistics', usage='%(prog)s -c <sumo sim files directory> -s <sumo output files directory>' )
    parser.add_argument('-c', '--sim dir', type=directory_exist, dest='simfiles', help='SUMO simulation files directory (rou/TAZ)')
    parser.add_argument('-s', '--output dir', type=directory_exist, dest='sumofiles', help='SUMO output files directory (tripinfo/summary/emission/...)')
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
    
    """
    # Process SUMO output files to build the dataset
    sumo_dic = xml2csv(options)                                                                   # Get sumo output files into a dictionary of dataframes
    taz_locations_edgenum_df = lanes_counter_taz_locations(sumo_dic['vehroute'])                  # Count edges on route from vehroute file and get from/to TAZ locations
    veh_speed_positions_df = avrg_speed_and_geo_positions(sumo_dic['fcd'])                        # Get average speed and initial/end positions (x,y)
    tripinfo_df = veh_trip_info(sumo_dic['tripinfo']) 
    
    # find/convert sumo simulation .rou/taz files
    #rou, taz = sim_files_search(options.simfiles)
    
    # merge dataframes
    data = taz_locations_edgenum_df.merge(veh_speed_positions_df,on='ID').merge(tripinfo_df,on='ID')
    data.to_csv(os.path.join(options.sumofiles,'../parsed', 'data.csv'), index=False, header=True)
    print('Parsed --> data.csv')
    """
    
    # Just read not process sumo files
    data = pd.read_csv(os.path.join(options.sumofiles,'../parsed', 'data.csv'))
    data.drop(columns='Unnamed: 0', inplace=True)
    #################################################################################
    
    # Preprocess data
    data = remove_outage_points(data) 
    data = encode_data(data)   
    data = remove_features(data)                                                                  # remove unused features
    data = add_features(data)                                                                     # add new problem features / based on what we know of the problem / we can add 15min restrictions here
    
    # Save preprocess data
    data.to_csv(os.path.join(options.sumofiles,'../parsed', 'preprocess_data.csv'), index=False, header=True)
    
    # Scale preprocess values
    explored_variable = 'tripinfo_duration'     #************************************************************
    pre_scaled = data.copy()
    df_scaled = pre_scaled.drop([explored_variable], axis=1)                                    # before scaling we should remove the output
    df_scaled = scale(df_scaled)

    # concat scaled and output ('trip_duration')
    col = data.columns.tolist()
    col.remove(explored_variable)
    
    df_scaled = pd.DataFrame(df_scaled, columns=col, index=data.index)
    df_scaled = pd.concat([df_scaled, data[explored_variable]], axis=1)
    
    # Save scaled data
    df_scaled.to_csv(os.path.join(options.sumofiles,'../parsed','scaled_data.csv'), index=False, header=True)            
 
  
    # # Split the dataframe into a training and testing set
    df = df_scaled.copy()
    
    X = df.loc[:, df.columns != explored_variable] 
    y = df[explored_variable]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)


    X.to_csv(os.path.join(options.sumofiles,'../parsed','x.csv'), index=False, header=True)        
    y.to_csv(os.path.join(options.sumofiles,'../parsed','y.csv'), index=False, header=True)        
    X_train.to_csv(os.path.join(options.sumofiles,'../parsed','X_train.csv'), index=False, header=True)
    y_train.to_csv(os.path.join(options.sumofiles,'../parsed','Y_train.csv'), index=False, header=True)


    # asses feature importance with random forest
    #feature_importance(df, X_train, y_train)
        
        
    # Build neural network in Keras
  
    model=Sequential()
    model.add(Dense(128, activation= 'relu', input_dim=X_train.shape[1]))
    model.add(Dense(64, activation= 'relu'))
    model.add(Dense(32, activation= 'relu'))
    model.add(Dense(8, activation= 'relu'))
    model.add(Dense(1))
    #print(model.summary())
    model.compile(loss='mse', optimizer='adam', metrics=['mse'])
    model.fit(X_train, y_train, epochs=50)
    
    # overfitting
    #early_stopping = EarlyStopping(monitor='val_loss', patience=3)
    #model.fit(X_train, y_train, epochs=200,validation_split=0.2,callbacks=[early_stopping])
    
    
    # Test model
    train_pred = model.predict(X_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    test_pred = model.predict(X_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    print("Train RMSE: {:0.2f}".format(train_rmse))
    print("Test RMSE: {:0.2f}".format(test_rmse))
    print('------------------------')
    scores = model.evaluate(X_train, y_train)
    print('Training accuracy: ' , (scores))
    scores = model.evaluate(X_test, y_test)
    print('Testing accuracy: ' , (scores))
    
    
    

if __name__ == "__main__":
    main()