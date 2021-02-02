
import subprocess
import time
import sys
import os
import uuid
import random
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

#
# Setup start
#

datadir = "data"
outdir = "bufboss_out"
tempdir = "temp"
run("mkdir -p " + outdir)

build_program = "bufboss/bin/bufboss_build"
update_program = "bufboss/bin/bufboss_update"
query_program = "bufboss/bin/bufboss_query"
buildlist = datadir + "/coli12_build.txt"
addlist = datadir + "/coli12_add.txt"
dellist = datadir + "/coli12_del.txt"

# Concatenate fasta files
build_genomes = run_get_output("cat " + buildlist).split('\n')
add_genomes = run_get_output("cat " + addlist).split('\n')
del_genomes = run_get_output("cat " + dellist).split('\n')
build_concat = tempdir + "/build.fasta"
concatenate_to(build_genomes, build_concat)
add_concat = tempdir + "/add.fasta"
concatenate_to(add_genomes, add_concat)
del_concat = tempdir + "/del.fasta"
concatenate_to(del_genomes, del_concat)

nodemer_k = 30
edgemer_k = nodemer_k + 1

# These are directories
built = outdir + "/built"
added = outdir + "/added"
deleted = outdir + "/deleted"
run("mkdir -p " + built)
run("mkdir -p " + added)
run("mkdir -p " + deleted)
query_out = outdir + "/queries.txt"
#query_data = "data/reads/coli_reads_half1.fasta"

resultfile = open("bufboss_results.txt",'w')

run_build, run_add, run_del, run_query = False, False, False, True

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

if run_query:
    # Existing reads
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + add_concat, "bufboss-query-existing-sequences", resultfile)
    
    # Random reads
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + "data/random/sequence.fna", "bufboss-query-random-sequence", resultfile)

    # Existing k-mers
    
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + added + " -o " + outdir + "/sampled_edgemers.fna --count 1000000") # Sample
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + outdir + "/sampled_edgemers.fna", "bufboss-query-existing-kmers", resultfile) # Query

    # Random k-mers
    run_timed_rss(query_program + " -i " + added + " -o " + query_out + " -q " + "data/random/edgemers.fna", "bufboss-query-random-kmers", resultfile) # Query
