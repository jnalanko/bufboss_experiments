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

config = ExperimentConfig()
config.load(sys.argv[1])
experiment_dir = config.experiment_dir

outdir = experiment_dir + "/fdbg_out"
run("mkdir -p " + outdir)

built = outdir + "/built.dbg"
added = outdir + "/added.dbg"
deleted = outdir + "/deleted.dbg"

resultdir = experiment_dir + "/fdbg_results"
run("mkdir -p " + resultdir)

# Todo: does it do rc? seems no... build from forward + rc

# Build
run_to_files("/usr/bin/time -v ./bahar-fdbg/cpp-src/fdbg-build-jarno " + config.buildfile_rc + " " + str(nodemer_k) + " " + built, resultdir + "/build")

# Add
run_to_files("/usr/bin/time -v ./bahar-fdbg/cpp-src/fdbg-add-jarno " + config.addfile_rc + " " + str(nodemer_k) + " " + built + " " + added, resultdir + "/add")

# Del
run_to_files("/usr/bin/time -v ./bahar-fdbg/cpp-src/fdbg-del-jarno " + config.delfile_rc + " " + str(nodemer_k) + " " + added + " " + deleted, resultdir + "/del")

# Query TODO: query program does not exist
#for name in config.query_inputs:
#    filename = config.query_inputs[name]
#    run_to_files("/usr/bin/time -v ./bahar-fdbg/cpp-src/fdbg-query-jarno " + added + " " + filename + " " + outdir + "/" + name + "-result.txt", resultdir + "/" + name)
    #run_to_files("/usr/bin/time -v ./FDBG-RecSplit/cpp-src/fdbg-recsplit-query " + built + " " + filename + " " + outdir + "/" + name + "-result.txt", resultdir + "/" + name)

# ./bahar-fdbg/cpp-src/fdbg-query-jarno fdbg_out/added.dbg data/existing/build_sequence.fasta temp/out.txt

# Parse summary
summary_out = open(resultdir + "/summary.txt", 'w')
build_time, build_rss = parse_usr_bin_time(resultdir + "/build.stderr.txt")
build_disk = get_disk_size_bytes(built)
summary_out.write("build " + str(build_time) + " " + str(build_rss) + " " + str(build_disk) + "\n")

add_time, add_rss = parse_usr_bin_time(resultdir + "/add.stderr.txt")
add_disk = get_disk_size_bytes(added)
summary_out.write("add " + str(add_time) + " " + str(add_rss) + " " + str(add_disk) + "\n")

#del_time, del_rss = parse_usr_bin_time(resultdir + "/del.stderr.txt")
#summary_out.write("del " + str(del_time) + " " + str(del_rss) + "\n")

#for name in config.query_inputs:
#    time = parse_our_printed_time(resultdir + "/" + name + ".stderr.txt")
#    rss = -1 # Not available
#    summary_out.write(name + " " + str(time) + " " + str(rss) + "\n")
