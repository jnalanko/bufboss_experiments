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

outdir = "fdbg_out"
run("mkdir -p " + outdir)

built = outdir + "/built.dbg"
added = outdir + "/added.dbg"
deleted = outdir + "/deleted.dbg"

resultdir = "dynboss_results"
run("mkdir -p " + resultdir)

# Todo: does it do rc? seems no... build from forward + rc

# Build
run_to_files("./bahar-fdbg/cpp-src/fdbg-build-jarno " + build_concat_with_rc + " " + str(nodemer_k) + " " + built, resultdir + "/build")

# Add
run_to_files("./bahar-fdbg/cpp-src/fdbg-add-jarno " + add_concat_with_rc + " " + str(nodemer_k) + " " + built + " " + added, resultdir + "/add")

# Del
#run_to_files("./bahar-fdbg/cpp-src/fdbg-del-jarno " + del_concat_with_rc + " " + str(nodemer_k) + " " + added + " " + deleted, resultdir + "/del")

# Query
for name in query_inputs:
    filename = query_inputs[name]
    run_to_files("/usr/bin/time -v ./bahar-fdbg/cpp-src/fdbg-query-jarno " + added + " " + filename + " " + outdir + "/" + name + "-result.txt", resultdir + "/" + name)

# ./bahar-fdbg/cpp-src/fdbg-query-jarno fdbg_out/added.dbg data/existing/build_sequence.fasta temp/out.txt
