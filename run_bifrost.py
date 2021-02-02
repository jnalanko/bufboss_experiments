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

def run_get_output(command):
    # Command can have pipes
    sys.stderr.write(command + "\n")
    return subprocess.run(command, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8").strip()

def run(command):
    sys.stderr.write(command + "\n")
    return subprocess.run(command, shell=True)

def drop_path_and_extension(S):
    return os.path.splitext(os.path.split(S)[1])[0]

def drop_extension(S):
    return os.path.splitext(S)[0]

def concatenate_to(filelist, destination):
    for i, file in enumerate(filelist):
        if i == 0:
            run("cat " + file + " > " + destination)
        else:
            run("cat " + file + " >> " + destination)

# Runs the command and writes to outfile (an opened file object) a line:
# name: time rss
# where time is in seconds and rss is in bytes
def run_timed_rss(command, name, outfile):
    sys.stderr.write(command + "\n")

    # /usr/bin/time -v prints to stderr
    stderr_data = subprocess.run("/usr/bin/time -v " + command, shell=True, stderr=subprocess.PIPE).stderr.decode("utf-8").strip()
    print(stderr_data)
    rss, time = None, None
    for line in stderr_data.split('\n'):
        if "Maximum resident set size (kbytes)" in line:
            rss = int(line.split()[-1]) * 2**10 # bytes
        if "Elapsed (wall clock) time (h:mm:ss or m:ss)" in line:
            token = line.split()[-1]
            hours, minutes, seconds = 0,0,0
            if token.count(":") == 1:
                minutes = float(token.split(":")[0])
                seconds = float(token.split(":")[1])
            elif token.count(":") == 2:
                hours = float(token.split(":")[0])
                minutes = float(token.split(":")[1])
                seconds = float(token.split(":")[2])
            else:
                print("Error parsing /usr/time/time -v")
                assert(False)
            time = hours * 60*60 + minutes*60 + seconds
    if rss == None or time == None:
        print("Error parsing /usr/time/time -v")
        assert(False)
    outfile.write(name + " " + str(time) + " " + str(rss) + "\n")
    outfile.flush()

datadir = "data"
outdir = "bifrost_out"
run("mkdir -p " + outdir)

program = "bifrost/build/src/Bifrost"
buildlist = datadir + "/coli12_build.txt"
addlist = datadir + "/coli12_add.txt"
#queryfile = "data/reads/coli_reads_half1.fasta"

# Bifrost appends .gfa to these
built = outdir + "/built.dbg"
added = outdir + "/added.dbg"
deleted = outdir + "/deleted.dbg"
query_out = outdir + "/queries.txt"

resultfile = open("bifrost_results.txt",'w')

# Bifrost is node-centric and nodes are k-mers.
#run_timed_rss(program + " build -r " + buildlist + " -k 30 -y -o " + built, "bifrost-build", resultfile)
#run_timed_rss(program + " update -g " + built+".gfa" + " -r " + addlist + " -k 30 -o " + added, "bifrost-update", resultfile)
run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_random_edgemers + " -o " + query_out + " --ratio-kmers 0", "bifrost-query-random_edgemer", resultfile)
run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_random_sequence + " -o " + query_out + " --ratio-kmers 0", "bifrost-query-random-sequence", resultfile)
run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_existing_edgemers + " -o " + query_out + " --ratio-kmers 1", "bifrost-query-existing-edgemer", resultfile)
run_timed_rss(program + " query -g " + added+".gfa" + " -q " + query_existing_sequence + " -o " + query_out + " --ratio-kmers 1", "bifrost-query-existing-sequence", resultfile)
