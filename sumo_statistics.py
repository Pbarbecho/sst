# @file    sumo_statistics.py
# @author  Pablo Barbecho
# @author  Guillem
# @date    2020-10-10

import argparse
import os
import sys
import pandas as pd


if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")


def get_options(arglist=None):
    ## Command line options ##
    parser = argparse.ArgumentParser(prog='SUMO Statistics', usage='%(prog)s [options]')
    parser.add_argument('-i', '--input', type=file_dir, dest='input', help='XML SUMO file', default='trips.xml')
    parser.add_argument('-o', '--output', dest='output', help='Result file name', default='statistics.csv')
    return parser.parse_args()


def file_dir(dir_name):
    ## Validate input file ##
    dir, name = os.path.split(dir_name)
    dir_path(dir)
    dir_files = os.listdir(dir)
    if name in dir_files:
        return dir_name
    else:
        raise argparse.ArgumentTypeError("{}{} file not found".format(dir, name))


def dir_path(path):
    ## validate directory ##
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError("{} is not a valid".format(path))


def xml2df(input, output):
    # Herramienta de sumo para convertir xml en csv
    output_convert = os.path.join(tools, 'xml', 'xml2csv.py')
    # Ejecutamos sumo tool con sumo output file como input
    os.system('python {} {} -s , -o {}'.format(output_convert, input, output))
    # Read csv into a dataframe
    data = pd.read_csv(output)
    return data


def plot(data):
    print('plot')


def main(args=None):
    # get command line options
    options = get_options(args)
    # xml to df
    df_output = xml2df(options.input, options.output)
    # Plot statistics
    plot(df_output)


if __name__ == "__main__":
    main()