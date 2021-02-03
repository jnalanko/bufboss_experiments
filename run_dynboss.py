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

outdir = "dynboss_out"
run("mkdir -p " + outdir)

program = "dynboss/bin/dynamicBOSS-jarno"

built = outdir + "/built.dbg"
added = outdir + "/added.dbg"
deleted = outdir + "/deleted.dbg"

resultdir = "dynboss_results"
run("mkdir -p " + resultdir)

# Count k-mers
run_to_files("dynboss/dsk-1.6906/dsk " + build_concat + " " + str(edgemer_k), resultdir + "/dsk")
run_to_files("dynboss/bin/cosmo-pack " + drop_path_and_extension(build_concat) + ".solid_kmers_binary", resultdir + "/pack")

# Build
run_to_files(program + " build -p " + drop_path_and_extension(build_concat) + ".solid_kmers_binary.packed -o " + built, resultdir + "/build")

# Add
#run_to_files(program + " add -g " + built + " -s " + add_concat + " -o " + added, resultdir + "/add")

# Del
#run_to_files(program + " delete -g " + added + " -s " + del_concat + " -o " + deleted, resultdir + "/del")

# Query
for name in query_inputs:
    filename = query_inputs[name]
    run_to_files(program + " query -g " + built + " -s " + filename, resultdir + "/" + name)
