import matplotlib
matplotlib.use("TkAgg")
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('/root/Documents/SUMO_SEM/CATALUNYA/parsed/data.csv')

def plot_route_points():
    # plot vehicle origin/destination points
    #plot accidents locations
    plt.figure(figsize = (6,6)) # set figure size
    plt.plot(list(df.ini_x_pos), list(df.ini_y_pos), '.', markersize=1)
    plt.title('Emergency vehicles locations in Catalunya')
    plt.grid(None)
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    plt.savefig('/root/Documents/SUMO_SEM/CATALUNYA/plots/hospital_locations.pdf')
    # plot ambulance locations
    plt.figure(figsize = (7,7)) # set figure size
    plt.plot(list(df.end_x_pos), list(df.end_y_pos), '.', markersize=1)
    
    #from taz
    #x=[168540.05, 168217.84, 171375.51, 170408.87, 168153.40, 168411.17, 168540.05]
    #y=[154471.10, 154857.75, 154922.19, 152795.60, 153246.70, 154664.42, 154471.10]
    #plt.plot(x, y)
 
    plt.title('Accident location in Catalunya')
    plt.grid(None)
    plt.xlabel("Longitud")
    plt.ylabel("Latitud")
    plt.savefig('/root/Documents/SUMO_SEM/CATALUNYA/plots/accidents_locations.pdf')


def plot_box():
    df.plot.box(figsize=(24,5))
    plt.savefig('/root/Documents/SUMO_SEM/CATALUNYA/plots/box.pdf')
   
    
def plot_histogram():   
    plt.rcParams.update({'font.size': '8'})
    #filtered_data.hist()
    df.hist(figsize=(10, 12))
    plt.savefig('/root/Documents/SUMO_SEM/CATALUNYA/plots/hist.pdf')
   
def scatterplot():
    plt.rcParams.update({'font.size': '10'})
    markers=['o','+','x','^','<']
    #ax = plt.axes()
    for i, hospital in enumerate(df['vehicle_toTaz'].unique()):
        new_df = df[df['vehicle_toTaz'] == hospital]
        new_df.plot.scatter(x='tripinfo_duration',y='tripinfo_routeLength', marker=markers[i], label=hospital)
    plt.savefig('/root/Documents/SUMO_SEM/CATALUNYA/plots/scatterplot.pdf')


if __name__ == "__main__":
    plot_route_points()
    plot_box()
    plot_histogram()
    scatterplot()
    plt.show()

