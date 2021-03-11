import matplotlib.pyplot as plt
import sys
import numpy as np
from setup import *
from collections import defaultdict

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--dir', type=str, help='base directory')

enable_bifrost = True
enable_bufboss = True
enable_dynboss = True
enable_fdbg = True
enable_fdbg_recsplit = True

args = parser.parse_args()

dir = args.dir

datasets = ["20K", "200K", "2M", "14M", "28M"]

# Returns formatted strings time, mem, disk
def parse_build_line(filename):
    for line in open(filename):
        tokens = line.split()
        if tokens[0] == "build":
            time, mem, disk = float(tokens[1]), int(tokens[2]), int(tokens[3])
            return "%.2f" % (time / 60), "%.2f" % (mem / 2**20), "%.2f" %  (disk / 2**20)
    print("Error parsing " + filename)


def parse_add_line(filename):
    for line in open(filename):
        tokens = line.split()
        if tokens[0] == "add" or tokens[0] == "add-0.025":
            time, mem, disk = float(tokens[1]), int(tokens[2]), int(tokens[3])
            return "%.2f" % (time / 60), "%.2f" % (mem / 2**20), "%.2f" %  (disk / 2**20)
    print("Error parsing " + filename)

def parse_del_line(filename):
    for line in open(filename):
        tokens = line.split()
        if tokens[0] == "del" or tokens[0] == "del-0.025":
            time, mem, disk = float(tokens[1]), int(tokens[2]), int(tokens[3])
            return "%.2f" % (time / 60), "%.2f" % (mem / 2**20), "%.2f" %  (disk / 2**20)
    print("Error parsing " + filename)

def parse_summaries(tablename):

    parse_func = None
    if tablename == "build": parse_func = parse_build_line
    if tablename == "add": parse_func = parse_add_line
    if tablename == "del": parse_func = parse_del_line
    assert(parse_func != None)

    for dataset in datasets:

        print("\\hline " + dataset + " & ")

        time, mem, disk = parse_func(dir + "/" + dataset + "/bufboss_results/summary.txt")
        print(disk + " & " + mem + " & " + time + " & ")

        time, mem, disk = parse_func(dir + "/" + dataset + "/dynboss_results/summary.txt")
        print(disk + " & " + mem + " & " + time + " & ")
        
        time, mem, disk = parse_func(dir + "/" + dataset + "/fdbg_recsplit_results/summary.txt")
        print(disk + " & " + mem + " & " + time + " & ")

        time, mem, disk = parse_func(dir + "/" + dataset + "/fdbg_results/summary.txt")
        print(disk + " & " + mem + " & " + time + " & ")

        if tablename == "del":
            print(" & & \\\\") # Bifrost does not do delete
        else:
            time, mem, disk = parse_func(dir + "/" + dataset + "/bifrost_results/summary.txt")
            print(disk + " & " + mem + " & " + time + " \\\\ ")





# Returns dict for numebr of k-mers in each query input
def parse_query_metadata():
    D = dict()
    for line in open(dir + "/lists/query_metadata.txt"):
        D[line.split()[0]] = int(line.split()[-1])
    return D


table_prefix = """\\begin{table*}[h]

 	\\centering
	\\fontsize{7}{12}\\selectfont
	\\resizebox{\\textwidth}{!}{
 	\\begin{tabular}{|p{0.75cm}|p{0.55cm}|p{1.2cm}|p{1cm}|p{0.55cm}|p{1.5cm}|p{1.3cm}|p{0.55cm}|p{1.2cm}|p{1cm}|p{0.55cm}|p{1.2cm}|p{1cm}|p{0.55cm}|p{1.2cm}|p{1cm}|}

 \hline

 \multicolumn{1}{|c|}{}  
 & \multicolumn{3}{|c|}{\\textbf{\\textsc{BuffBOSS}}} 
 & \multicolumn{3}{|c|} {DynamicBOSS} 
 & \multicolumn{3}{|c|}{FDBG-RecSplit}  
 & \multicolumn{3}{|c|}{FDBG} 
 & \multicolumn{3}{|c|}{Bifrost}\\\\
 \hline

 \hline
 	&Disk  &Memory  & Time       &Disk  &Memory    & Time       &Disk   &Memory    & Time       &Disk &Memory &Time &Disk &Memory  &Time\\\\"""

table_suffix = """\\hline
  	\\end{tabular}}
 	\\caption{}
 	\\label{}
 \\end{table*}
 """

print(table_prefix)
parse_summaries("build")
print(table_suffix)

print(table_prefix)
parse_summaries("add")
print(table_suffix)

print(table_prefix)
parse_summaries("del")
print(table_suffix)