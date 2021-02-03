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
#buildlist = datadir + "/coli12_build.txt"
#addlist = datadir + "/coli12_add.txt"
#queryfile = "data/reads/coli_reads_half1.fasta"

# Bifrost appends .gfa to these
built = outdir + "/built.dbg"
added = outdir + "/added.dbg"
deleted = outdir + "/deleted.dbg"
query_out = outdir + "/queries.txt"

resultfile = open("bifrost_results.txt",'w')

# Bifrost is node-centric and nodes are k-mers.
run_timed_rss(program + " build -r " + buildlist + " -k 30 -y -o " + built, "bifrost-build", resultfile)
run_timed_rss(program + " update -g " + built+".gfa" + " -r " + addlist + " -k 30 -o " + added, "bifrost-update", resultfile)

run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_existing_build_edgemers + " -o " + query_out + " --ratio-kmers 1", "bifrost-query-existing_build_edgemers", resultfile)
run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_existing_build_sequence + " -o " + query_out + " --ratio-kmers 1", "bifrost-query-existing_build_seq", resultfile)
run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_existing_added_edgemers + " -o " + query_out + " --ratio-kmers 1", "bifrost-query-existing_added_edgemers", resultfile)
run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_existing_added_sequence + " -o " + query_out + " --ratio-kmers 1", "bifrost-query-existing-added-seq", resultfile)

run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_random_edgemers + " -o " + query_out + " --ratio-kmers 1", "bifrost-query-random_edgemers", resultfile)
run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_random_sequence + " -o " + query_out + " --ratio-kmers 1", "bifrost-query-random_seq", resultfile)