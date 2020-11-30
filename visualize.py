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

"""
    


df = pd.read_csv('NYC_taxi.csv', parse_dates=['pickup_datetime'], nrows=500000)

print(df.head())

## Visualizing Geolocation Data #############################################

# range of longitude for NYC
nyc_min_longitude = -74.05
nyc_max_longitude = -73.75

# range of latitude for NYC
nyc_min_latitude = 40.63
nyc_max_latitude = 40.85

df2 = df.copy(deep=True)
for long in ['pickup_longitude', 'dropoff_longitude']:
    df2 = df2[(df2[long] > nyc_min_longitude) & (df2[long] < nyc_max_longitude)]

for lat in ['pickup_latitude', 'dropoff_latitude']:
    df2 = df2[(df2[lat] > nyc_min_latitude) & (df2[lat] < nyc_max_latitude)]

landmarks = {'JFK Airport': (-73.78,40.643),
             'Laguardia Airport': (-73.87, 40.77),
             'Midtown': (-73.98, 40.76),
             'Lower Manhattan': (-74.00, 40.72),
             'Upper Manhattan': (-73.94, 40.82),
             'Brooklyn': (-73.95, 40.66)}    


def plot_lat_long(df, landmarks, points='Pickup'):
    plt.figure(figsize = (12,12)) # set figure size
    if points == 'pickup':
        plt.plot(list(df.pickup_longitude), list(df.pickup_latitude), '.', markersize=1)
    else:
        plt.plot(list(df.dropoff_longitude), list(df.dropoff_latitude), '.', markersize=1)

    for landmark in landmarks:
        plt.plot(landmarks[landmark][0], landmarks[landmark][1], '*', markersize=15, alpha=1, color='r') # plot landmark location on map
        plt.annotate(landmark, (landmarks[landmark][0]+0.005, landmarks[landmark][1]+0.005), color='r', backgroundcolor='w') # add 0.005 offset on landmark name for aesthetics purposes
  
    plt.title("{} Locations in NYC Illustrated".format(points))
    plt.grid(None)
    plt.xlabel("Latitude")
    plt.ylabel("Longitude")
    plt.show()


plot_lat_long(df2, landmarks, points='Pickup')

plot_lat_long(df2, landmarks, points='Drop Off')



## Ridership by Day and Hour #############################################

df['year'] = df['pickup_datetime'].dt.year
df['month'] = df['pickup_datetime'].dt.month
df['day'] = df['pickup_datetime'].dt.day
df['day_of_week'] = df['pickup_datetime'].dt.dayofweek
df['hour'] = df['pickup_datetime'].dt.hour

df['day_of_week'].plot.hist(bins=np.arange(8)-0.5, ec='black', ylim=(60000,75000))
plt.xlabel('Day of Week (0=Monday, 6=Sunday)')
plt.title('Day of Week Histogram')
plt.show()

df['hour'].plot.hist(bins=24, ec='black')
plt.title('Pickup Hour Histogram')
plt.xlabel('Hour')
plt.show()



## Handling Missing Values and Data Anomalies #############################################

print(df.isnull().sum())
print('')

df = df.dropna()

print(df.describe())

df['fare_amount'].hist(bins=500)
plt.xlabel("Fare")
plt.title("Histogram of Fares")
plt.show()

df = df[(df['fare_amount'] >=0) & (df['fare_amount'] <= 100)]

df['passenger_count'].hist(bins=6, ec='black')
plt.xlabel("Passenger Count")
plt.title("Histogram of Passenger Count")
plt.show()

df.plot.scatter('pickup_longitude', 'pickup_latitude')
plt.show()



## Geolocation Features #############################################

df = preprocess(df)

def euc_distance(lat1, long1, lat2, long2):
    return(((lat1-lat2)**2 + (long1-long2)**2)**0.5)

df['distance'] = euc_distance(df['pickup_latitude'], df['pickup_longitude'], df['dropoff_latitude'], df['dropoff_longitude'])

df.plot.scatter('fare_amount', 'distance')
plt.show()

"""
