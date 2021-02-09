import subprocess
import time
import sys
import os
import uuid
import random
from setup import *
from multiprocessing import Pool

if sys.version_info < (3, 0):
    sys.stdout.write("Error: Python3 required\n")
    sys.exit(1)

datadir = "data"
outdir = "bifrost_out"
run("mkdir -p " + outdir)

program = "bifrost/build/src/Bifrost"

# Bifrost appends .gfa to these
built = outdir + "/built.dbg"
added = outdir + "/added.dbg"
deleted = outdir + "/deleted.dbg"
query_out = outdir + "/queries.txt"

resultdir = "bifrost_results"
run("mkdir -p " + resultdir)

run_build = True
run_add = True
run_query = True

# Bifrost is node-centric and nodes are k-mers.
if run_build:
    run_to_files("/usr/bin/time -v " + program + " build -r " + build_concat + " -k 30 -y -o " + built, resultdir + "/build")
if run_add:    
    run_to_files("/usr/bin/time -v " + program + " update -g " + built+".gfa" + " -r " + add_concat + " -k 30 -o " + added, resultdir + "/add")
if run_query:
    for name in query_inputs:
        filename = query_inputs[name]
        run_to_files("/usr/bin/time -v " + program + " query -g " + added+".gfa" + " -q " + filename + " -o " + query_out + " --ratio-kmers 1", resultdir + "/" + name)

# Parse summary
summary_out = open(resultdir + "/summary.txt", 'w')
build_time, build_rss = parse_usr_bin_time(resultdir + "/build.stderr.txt")
build_disk = get_disk_size_bytes(built + ".gfa")
summary_out.write("build " + str(build_time) + " " + str(build_rss) + " " + str(build_disk) + "\n")

add_time, add_rss = parse_usr_bin_time(resultdir + "/add.stderr.txt")
add_disk = get_disk_size_bytes(added + ".gfa")
summary_out.write("add " + str(add_time) + " " + str(add_rss) + " " + str(add_disk) + "\n")

for name in query_inputs:
    time = parse_our_printed_time(resultdir + "/" + name + ".stderr.txt")
    rss = -1 # Not available
    summary_out.write(name + " " + str(time) + " " + str(rss) + "\n")