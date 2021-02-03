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

# Count k-mers. We use the reverse-complement concatenated data because dynboss does not index rc by itself.
run_to_files("/usr/bin/time -v dynboss/dsk-1.6906/dsk " + build_concat_with_rc + " " + str(edgemer_k), resultdir + "/dsk")
run_to_files("/usr/bin/time -v dynboss/bin/cosmo-pack " + drop_path_and_extension(build_concat_with_rc) + ".solid_kmers_binary", resultdir + "/pack")

# Build
run_to_files("/usr/bin/time -v " + program + " build -p " + drop_path_and_extension(build_concat_with_rc) + ".solid_kmers_binary.packed -o " + built, resultdir + "/build")

# Add
run_to_files("/usr/bin/time -v " + program + " add -g " + built + " -s " + add_concat_with_rc + " -o " + added, resultdir + "/add")

# Del
run_to_files("/usr/bin/time -v " + program + " delete -g " + added + " -s " + del_concat_with_rc + " -o " + deleted, resultdir + "/del")

# Query
for name in query_inputs:
    filename = query_inputs[name]
    run_to_files("/usr/bin/time -v " + program + " query -g " + built + " -s " + filename + " --query-result " + outdir + "/" + name + "-result.txt", resultdir + "/" + name)

# Parse summary
summary_out = open(resultdir + "/summary.txt", 'w')
dsk_time, dsk_rss = parse_usr_bin_time(resultdir + "/dsk.stderr.txt")
pack_time, pack_rss = parse_usr_bin_time(resultdir + "/pack.stderr.txt")
build_time, build_rss = parse_usr_bin_time(resultdir + "/build.stderr.txt")
summary_out.write("build " + str(dsk_time + pack_time + build_time) + " " + str(max(dsk_rss, pack_rss, build_rss)) + "\n")

add_time, add_rss = parse_usr_bin_time(resultdir + "/add.stderr.txt")
summary_out.write("add " + str(add_time) + " " + str(add_rss) + "\n")

del_time, del_rss = parse_usr_bin_time(resultdir + "/del.stderr.txt")
summary_out.write("del " + str(del_time) + " " + str(del_rss) + "\n")

for name in query_inputs:
    time = parse_our_printed_time(resultdir + "/" + name + ".stderr.txt")
    rss = -1 # Not available
    summary_out.write(name + " " + str(time) + " " + str(rss) + "\n")
