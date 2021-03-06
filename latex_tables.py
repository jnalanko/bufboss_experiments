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

def parse_summaries():

    for dataset in datasets:

        print("\\hline " + dataset + " & ")

        if dataset == "200K" or dataset == "2M": 
            print(" & & & ") # summary.txt does not exist for some reason
        else:
            time, mem, disk = parse_build_line(dir + "/" + dataset + "/bufboss_results/summary.txt")
            print(disk + " & " + mem + " & " + time + " & ")

        time, mem, disk = parse_build_line(dir + "/" + dataset + "/dynboss_results/summary.txt")
        print(disk + " & " + mem + " & " + time + " & ")
        
        time, mem, disk = parse_build_line(dir + "/" + dataset + "/fdbg_recsplit_results/summary.txt")
        print(disk + " & " + mem + " & " + time + " & ")

        if dataset == "28M":
            print(" & & & ") # Vanilla FBDG still running
        else:
            time, mem, disk = parse_build_line(dir + "/" + dataset + "/fdbg_results/summary.txt")
            print(disk + " & " + mem + " & " + time + " & ")

        time, mem, disk = parse_build_line(dir + "/" + dataset + "/bifrost_results/summary.txt")
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
 	\\caption{E coli reads construction. Time in minutes, memory and disk in mebibytes (2^{20} bytes).}
 	\\label{construction}
 \\end{table*}
 """

print(table_prefix)
parse_summaries()
print(table_suffix)