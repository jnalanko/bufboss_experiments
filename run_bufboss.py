
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

build_program = "bufboss/bin/bufboss_build"
update_program = "bufboss/bin/bufboss_update"
query_program = "bufboss/bin/bufboss_query"

outdir = "bufboss_out"
run("mkdir -p " + outdir)

built = outdir + "/built"
added = outdir + "/added"
deleted = outdir + "/deleted"
run("mkdir -p " + built)
run("mkdir -p " + added)
run("mkdir -p " + deleted)

query_out = outdir + "/queries.txt"
resultfile = open("bufboss_results.txt",'w')

run_build, run_add, run_del, run_query_no_buffer, run_query_vs_buffer_fraction = False, False, False, True, False

if run_build:
    run_timed_rss("./bufboss/KMC/bin/kmc -v -k31 -m1 -ci1 -cs1 -fm temp/build.fasta temp/kmc_db temp", "KMC", resultfile)
    run_timed_rss("./bufboss/bin/bufboss_build --KMC temp/kmc_db -o " + built + " -t " + tempdir, "build_from_KMC", resultfile)

if run_add:
    #buf_fractions = [1.0, 0.5, 0.25, 0.1, 0.5, 0.025, 0.01]
    buf_fractions = [1.0]
    for b in buf_fractions:
        run_timed_rss(update_program + " -k " + str(nodemer_k) + " -r -b " + str(b) + " -i " + built + " -o " + added + " --add-files " + addlist, "bufboss-add-" + str(b), resultfile)

if run_del:
    for b in buf_fractions:
        run_timed_rss(update_program + " -k " + str(nodemer_k) + " -r -b " + str(b) + " -i " + added + " -o " + deleted + " --del-files " + dellist, "bufboss-del-" + str(b), resultfile)

if run_query_no_buffer:
    # Existing build sequence
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + query_existing_build_sequence, "bufboss-query-existing-build-sequence", resultfile)

    # Existing added sequence
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + query_existing_added_sequence, "bufboss-query-existing-added-sequence", resultfile)
    
    # Random sequence
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + query_random_sequence, "bufboss-query-random-sequence", resultfile)

    # Existing build edgemers
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + query_existing_build_edgemers, "bufboss-query-existing-build-edgemers", resultfile)

    # Existing added edgemers
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + query_existing_added_edgemers, "bufboss-query-existing-added-edgemers", resultfile)

    # Random edgemers
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + query_random_edgemers, "bufboss-query-random-edgemers", resultfile)

if run_query_vs_buffer_fraction:
    run("./bufboss/bin/query_performance_experiment -i " + built + " --add-files " + addlist + " --buf-fraction-increment 0.01 --max-buf-fraction 1.0 -q " + query_existing_build_sequence + " --tempdir " + tempdir + " --experiment-out buf-frac-query-existing-build-seq.txt")
    run("./bufboss/bin/query_performance_experiment -i " + built + " --add-files " + addlist + " --buf-fraction-increment 0.01 --max-buf-fraction 1.0 -q " + query_random_sequence + " --tempdir " + tempdir + " --experiment-out buf-frac-query-random-seq.txt")
    run("./bufboss/bin/query_performance_experiment -i " + built + " --add-files " + addlist + " --buf-fraction-increment 0.01 --max-buf-fraction 1.0 -q " + query_existing_build_edgemers + " --tempdir " + tempdir + " --experiment-out buf-frac-query-existing-build-edgemers.txt")
    run("./bufboss/bin/query_performance_experiment -i " + built + " --add-files " + addlist + " --buf-fraction-increment 0.01 --max-buf-fraction 1.0 -q " + query_random_edgemers + " --tempdir " + tempdir + " --experiment-out buf-frac-query-random-edgemers.txt")