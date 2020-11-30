# -*- coding: utf-8 -*-
"""
Count the number of routes of TAZ file generated with 0d2trips
"""

import pandas as pd
import os
import sumolib  # noqa


def readValues(file, measure):
    print("Reading '%s'..." % file)
    # vehicles  firts level in .rou.xml structure
    ret = sumolib.output.parse_sax__asList(file, "vehicle", measure)
    return ret
  
    
   
if __name__ == "__main__":
    # Read files
    sumo_files_location = '/root/Documents/SUMO_SEM/CATALUNYA/sim_files/'
    routes_file = os.path.join(sumo_files_location,'dua.rou.xml')
    
    # Define measured attributes
    measure = ['id','fromTaz', 'toTaz']
    summary = readValues(routes_file, measure)   
    
    # process summary
    results = pd.DataFrame(summary)
    results = results.groupby(['fromTaz', 'toTaz']).count()
    print(results)
    