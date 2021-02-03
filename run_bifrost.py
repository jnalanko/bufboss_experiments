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

# Bifrost is node-centric and nodes are k-mers.
run_to_files("/usr/bin/time -v " + program + " build -r " + buildlist + " -k 30 -y -o " + built, resultdir + "/build")
run_to_files("/usr/bin/time -v " + program + " update -g " + built+".gfa" + " -r " + addlist + " -k 30 -o " + added, resultdir + "/add")

for name in query_inputs:
    filename = query_inputs[name]
    run_to_files("/usr/bin/time -v " + program + " query -g " + added+".gfa" + " -q " + filename + " -o " + query_out + " --ratio-kmers 1", resultdir + "/query-" + name)
