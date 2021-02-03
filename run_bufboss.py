
import subprocess
import time
import sys
import os
import uuid
import random
from setup import * # My setup file
from multiprocessing import Pool

if sys.version_info < (3, 0):
    sys.stdout.write("Error: Python3 required\n")
    sys.exit(1)

def parse_time(filename):
    for line in open(filename).readline():
        if "Time for all queries:" in line:
            return float(line.split()[-2])
    print("Error parsing time from " + filename)
    assert(False)

build_program = "bufboss/bin/bufboss_build"
update_program = "bufboss/bin/bufboss_update"
query_program = "bufboss/bin/bufboss_query"

outdir = "bufboss_out"
run("mkdir -p " + outdir)

resultdir = "bufboss_results"
run("mkdir -p " + resultdir)

built = outdir + "/built"
added = outdir + "/added"
deleted = outdir + "/deleted"
run("mkdir -p " + built)
run("mkdir -p " + added)
run("mkdir -p " + deleted)

query_out = outdir + "/queries.txt"

run_build = True
run_add = True
run_del = True
run_query = True
#run_query_vs_buffer_fraction = True

if run_build:
    run_to_files("/usr/bin/time -v ./bufboss/KMC/bin/kmc -v -k31 -m1 -ci1 -cs1 -fm " + build_concat + " temp/kmc_db temp", 
                 resultdir + "/build_run_KMC")
    run_to_files("/usr/bin/time -v ./bufboss/bin/bufboss_build --KMC temp/kmc_db -o " + built + " -t " + tempdir, 
                 resultdir + "/build_BOSS_from_KMC")

if run_add:
    #buf_fractions = [1.0, 0.5, 0.25, 0.1, 0.5, 0.025, 0.01]
    buf_fractions = [1.0]
    for b in buf_fractions:
        run_to_files("/usr/bin/time -v " + update_program + " -k " + str(nodemer_k) + " --end-flush -r -b " + str(b) + " -i " + built + " -o " + added + " --add-files " + addlist, resultdir + "/add-" + str(b))

if run_del:
    for b in buf_fractions:
        run_to_files("/usr/bin/time -v " + update_program + " -k " + str(nodemer_k) + " --end-flush -r -b " + str(b) + " -i " + added + " -o " + deleted + " --del-files " + dellist, "del-" + str(b))

if run_query:
    for name in query_inputs:
        filename = query_inputs[name]
        run_to_files("/usr/bin/time -v " + query_program + " -i " + added + " -o " + query_out + " -q " + filename, 
                     resultdir + "/query-" + name)

#if run_query_vs_buffer_fraction:
#    for name in query_inputs:
#        filename = query_inputs[name]
#        run_to_files("./bufboss/bin/query_performance_experiment -i " + built + " --add-files " + addlist + " --buf-fraction-increment 0.01 --max-buf-fraction 1.0 -q " + filename + " --tempdir " + tempdir + " --experiment-out " + resultdir + "/buf_frac_query" + name + ".txt")
