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
import matplotlib.pyplot as plt
import numpy as np
from xml.dom import minidom
import seaborn as sns
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from utils import SUMO_preprocess, preprocess, scale_df, plot_predict_vs_real, feature_importance
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
  
    # SUMO build dataframe Time comsuming process. Once generated comment #
    data = SUMO_preprocess(options)
    
    # Read SUMO database 
    data = pd.read_csv(os.path.join(options.sumofiles,'../parsed', 'data.csv'))
    #data.drop(columns='Unnamed: 0', inplace=True)
        
    # Preprocess data
    data = preprocess(data)                                    
    
    # Scale data
    predicted_variable = 'tripinfo_duration'
    df = scale_df(data, predicted_variable)
   
    # Split the dataframe into a training and testing set
    X = df.loc[:, df.columns != predicted_variable] 
    y = df[predicted_variable]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)        
    
    # asses feature importance with random forest
    #feature_importance(df, X_train, y_train)
        
    # Build neural network in Keras
    model=Sequential()
    activation_f = 'relu'             # 'relu'
    model.add(Dense(128, activation= activation_f, input_dim=X_train.shape[1]))
    model.add(Dense(64, activation= activation_f))
    model.add(Dense(32, activation= activation_f))
    model.add(Dense(8, activation= activation_f))
    model.add(Dense(1))
    #print(model.summary())
    model.compile(loss='mse', optimizer='adam', metrics=['mse'])
    model.fit(X_train, y_train, epochs=2)
    
    # overfitting
    #early_stopping = EarlyStopping(monitor='val_loss', patience=3)
    #model.fit(X_train, y_train, epochs=100,validation_split=0.2,callbacks=[early_stopping])
    
    # Test model
    train_pred = model.predict(X_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    test_pred = model.predict(X_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    print("Train RMSE: {:0.2f}".format(train_rmse))
    print("Test RMSE: {:0.2f}".format(test_rmse))
    print('------------------------')
    scores = model.evaluate(X_train, y_train)
    print('Training accuracy: ' , (scores[1]))
    scores = model.evaluate(X_test, y_test)
    print('Testing accuracy: ' , (scores[1]))
    
    # Plot test real vs predicted
    plot_predict_vs_real(test_pred, y_test, 100)
    
    
if __name__ == "__main__":
    main()