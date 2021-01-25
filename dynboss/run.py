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

tempdir = "temp"
run("mkdir -p " + tempdir)

datadir = "../data"
buildlist = datadir + "/coli12_build.txt"
addlist = datadir + "/coli12_add.txt"
dellist = datadir + "/coli12_del.txt"
nodemer_k = 30
edgemer_k = nodemer_k + 1

build_genomes = run_get_output("cat " + buildlist).split('\n')
add_genomes = run_get_output("cat " + addlist).split('\n')
del_genomes = run_get_output("cat " + dellist).split('\n')
resultfile = open("results.txt",'w')

# Concatenate fasta files
build_concat = tempdir + "/build.fasta"
concatenate_to(build_genomes, build_concat)

# Count k-mers
run_timed_rss("dsk-1.6906/dsk " + build_concat + " " + str(edgemer_k), "dsk", resultfile)

# Build
run_timed_rss("bin/cosmo-pack " + drop_path_and_extension(build_concat) + ".solid_kmers_binary", "pack", resultfile)
run_timed_rss("bin/dynamicBOSS build -p " + drop_path_and_extension(build_concat) + ".solid_kmers_binary.packed", "build", resultfile)

# Add
add_concat = tempdir + "/add.fasta"
concatenate_to(add_genomes, add_concat)
run_timed_rss("bin/dynamicBOSS add -g " + drop_path_and_extension(build_concat) + ".solid_kmers_binary.packed.dbg -s " + add_concat, "add", resultfile)

# Delete
del_concat = tempdir + "/del.fasta"
concatenate_to(del_genomes, del_concat)
run_timed_rss("bin/dynamicBOSS delete -g " + drop_path_and_extension(build_concat) + ".solid_kmers_binary.packed.dbg -s " + del_concat, "del", resultfile)

