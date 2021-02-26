
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

config = ExperimentConfig()
config.load(sys.argv[1])
experiment_dir = config.experiment_dir

build_program = "bufboss/bin/bufboss_build"
update_program = "bufboss/bin/bufboss_update"
query_program = "bufboss/bin/bufboss_query"

outdir = experiment_dir + "/bufboss_out"
run("mkdir -p " + outdir)

resultdir = experiment_dir + "/bufboss_results"
run("mkdir -p " + resultdir)

built = outdir + "/built"
added = outdir + "/added"
deleted = outdir + "/deleted"
added_and_deleted = outdir + "/added_and_deleted"
run("mkdir -p " + built)
run("mkdir -p " + added)
run("mkdir -p " + deleted)
run("mkdir -p " + added_and_deleted)

query_out = outdir + "/queries.txt"

run_build = True
run_add = True
run_del = True
run_query = True
#run_query_vs_buffer_fraction = True

#buf_fractions = [1.0]
buf_fractions = [1.0, 0.5, 0.25, 0.1, 0.5, 0.025, 0.01]

if run_build:
    run_to_files("/usr/bin/time -v ./bufboss/KMC/bin/kmc -v -k31 -m1 -ci1 -cs1 -fm " + config.buildfile + " " + config.temp_dir + "/kmc_db " + config.temp_dir, 
                 resultdir + "/build_run_KMC")
    run_to_files("/usr/bin/time -v ./bufboss/bin/bufboss_build --KMC " + config.temp_dir + "/kmc_db -o " + built + " -t " + config.temp_dir, 
                 resultdir + "/build_BOSS_from_KMC")

if run_add:
    for b in buf_fractions:
        run_to_files("/usr/bin/time -v " + update_program + " -k " + str(nodemer_k) + " -r -b " + str(b) + " -i " + built + " -o " + added + " --add " + config.addfile, resultdir + "/add-" + str(b))

if run_del:
    for b in buf_fractions:
        run_to_files("/usr/bin/time -v " + update_program + " -k " + str(nodemer_k) + " -r -b " + str(b) + " -i " + added + " -o " + deleted + " --del " + config.delfile, resultdir + "/del-" + str(b))

if run_add and run_del:
    for b in buf_fractions:
        run_to_files("/usr/bin/time -v " + update_program + " --add-before-del -k " + str(nodemer_k) + " -r -b " + str(b) + " -i " + built + " -o " + added_and_deleted + " --del " + config.delfile + " --add " + config.addfile, resultdir + "/adddel-" + str(b))


if run_query:
    for name in config.query_inputs:
        filename = config.query_inputs[name]
        run_to_files("/usr/bin/time -v " + query_program + " -i " + added + " -o " + outdir + "/query_result" + name + ".txt" + " -q " + filename, 
                     resultdir + "/" + name)

#if run_query_vs_buffer_fraction:
#    for name in query_inputs:
#        filename = query_inputs[name]
#        run_to_files("./bufboss/bin/query_performance_experiment -i " + built + " --add-files " + addlist + " --buf-fraction-increment 0.01 --max-buf-fraction 1.0 -q " + filename + " --tempdir " + tempdir + " --experiment-out " + resultdir + "/buf_frac_query" + name + ".txt")

# Parse summary
summary_out = open(resultdir + "/summary.txt", 'w')
KMC_time, KMC_rss = parse_usr_bin_time(resultdir + "/build_run_KMC.stderr.txt")
build_time, build_rss = parse_usr_bin_time(resultdir + "/build_BOSS_from_KMC.stderr.txt")
build_disk = get_disk_size_bytes(built)
summary_out.write("build " + str(KMC_time + build_time) + " " + str(max(build_rss, KMC_rss)) + " " + str(build_disk) + "\n")

# Add
for b in buf_fractions:
    add_time, add_rss = parse_usr_bin_time(resultdir + "/add-" + str(b) + ".stderr.txt")
    add_disk = 0 # Todo
    summary_out.write("add-" + str(b) + " " + str(add_time) + " " + str(add_rss) + " " + str(add_disk) + "\n")

# Delete
for b in buf_fractions:
    del_time, del_rss = parse_usr_bin_time(resultdir + "/del-" + str(b) + ".stderr.txt")
    del_disk = 0 # todo
    summary_out.write("del-" + str(b) + " " + str(del_time) + " " + str(del_rss) + " " + str(del_disk) + "\n")

# Add and delete
for b in buf_fractions:
    adddel_time, adddel_rss = parse_usr_bin_time(resultdir + "/adddel-" + str(b) + ".stderr.txt")
    adddel_disk = 0 # todo
    summary_out.write("adddel-" + str(b) + " " + str(adddel_time) + " " + str(adddel_rss) + " " + str(adddel_disk) + "\n")

for name in config.query_inputs:
    time = parse_our_printed_time(resultdir + "/" + name + ".stderr.txt")
    rss = -1 # Not available
    summary_out.write(name + " " + str(time) + " " + str(rss) + "\n")
