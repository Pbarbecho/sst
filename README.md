# SUMO output files processing SFP #

SFP  allows to process SUMO output files.  

# Usage #

```bash
# sumo_statistics --help
usage: SUMO Statistics -t <type of file>  -i <sumo output file> -s <sumo sim files directory>

optional arguments:
  -h, --help            show this help message and exit
  -t TYPE, --type TYPE  (tripinfo/summary/emmisions) type of output file
  -i INPUT, --input INPUT
                        SUMO output file (tripinfo/summary/emmisions)
  -s SUMOFILES, --dir SUMOFILES
                        Path of SUMO simulation files (.rou, TAZ)
```

SUMO output file names must follows:

* tripinfo -> tripinfo.xml
* summary  -> summary.xml



## Clone the repository ##
The osm package is developed using a pipenv. TO install osm on a virtual environment:
```bash
pip3 install pipenv
```

To clone the osm repository, on the command line, enter:
```bash
git clone https://github.com/Pbarbecho/sst.git
```
On the new venv, install osm project in an editable mode:

```bash
pipenv install -e sst/
```

Then, for use the new virtual environment instantiate a sub-shell as follows:

```bash
pipenv shell
```

At this time, you can interact with the SPF modules, customize you analysis and use sst utilities. 

 
In case you want to uninstall sst package: 

```bash
pip3 uninstall sumo_statistics
```



## Authors ##

Pablo Barbecho 


Guillem

