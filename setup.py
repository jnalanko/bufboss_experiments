
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

def run_to_files(command, stdout_file, stderr_file):
    sys.stderr.write(command + "\n")
    sys.stderr.write("stdout to " + stdout_file + "\n")
    sys.stderr.write("stderr to " + stderr_file + "\n")
    stdout_stream = open(stdout_file, 'w')
    stderr_stream = open(stderr_file, 'w')
    return subprocess.run(command, shell=True, stdout=stdout_stream, stderr=stderr_stream)

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
tempdir = "temp"

buildlist = "lists/coli_build.txt"
addlist = "lists/coli_add.txt"
dellist = "lists/coli_del.txt"

build_concat = datadir + "/build.fasta"
add_concat = datadir + "/add.fasta"
del_concat = datadir + "/del.fasta"

nodemer_k = 30
edgemer_k = nodemer_k + 1

query_inputs = {"random_edgemers": "data/random/edgemers.fna",
                "random_sequence": "data/random/sequence.fna",
                "existing_build_edgemers": "data/existing/build_edgemers.fna",
                "existing_build_sequence": "data/existing/build_sequence.fna",
                "existing_added_edgemers": "data/existing/added_edgemers.fna",
                "existing_added_sequence" : "data/existing/added_sequence.fna"}

def generate_input_files():

    # Concatenate fasta files
    build_genomes = run_get_output("cat " + buildlist).split('\n')
    add_genomes = run_get_output("cat " + addlist).split('\n')
    del_genomes = run_get_output("cat " + dellist).split('\n')

    concatenate_to(build_genomes, build_concat)
    concatenate_to(add_genomes, add_concat)
    concatenate_to(del_genomes, del_concat)

    # Generate random queries
    run("mkdir -p data/random")
    run("python3 gen_random_kmers.py 31 1000000 > " + query_inputs["random_edgemers"])
    run("python3 gen_random_kmers.py 31000000 1 > " + query_inputs["random_sequence"])

    # Generate existing queries...
    run("mkdir -p data/existing")

    # ...for existing k-mers, build a bufboss and sampled from there. First for build kmers...
    index_dir = tempdir + "/buffboss"
    run("mkdir -p " + index_dir)
    run("./bufboss/KMC/bin/kmc -k31 -m1 -ci1 -cs1 -fm " + build_concat + " " + tempdir + "/kmc_db temp")
    run("./bufboss/bin/bufboss_build --KMC " + tempdir + "/kmc_db -o " + index_dir + " -t " + tempdir)
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + index_dir + " -o " + query_inputs["existing_build_edgemers"] + " --count 1000000")

    # ...then for added kmers (resuse the same index dir
    run("./bufboss/KMC/bin/kmc -k31 -m1 -ci1 -cs1 -fm " + add_concat + " " + tempdir + "/kmc_db temp")
    run("./bufboss/bin/bufboss_build --KMC " + tempdir + "/kmc_db -o " + index_dir + " -t " + tempdir)
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + index_dir + " -o " + query_inputs["existing_added_edgemers"] + " --count 1000000")

    # For existing sequences, take the first file in buildlist and in addlist
    filename = open(buildlist).readlines()[0].strip()
    run("cp " + filename + " " + query_inputs["existing_build_sequence"])
    filename = open(addlist).readlines()[0].strip()
    run("cp " + filename + " " + query_inputs["existing_added_sequence"])

# Takes number of genomes to build, add and del respectively.
if __name__ == "__main__":
    n_build = int(sys.argv[1])
    n_add = int(sys.argv[2])
    n_del = int(sys.argv[3])
    assert(n_build + n_add + n_del <= 3682)
    run("mkdir -p lists")
    files = run_get_output("ls $PWD/data/coli3682/*.fna | shuf").splitlines()

    build_out = open("lists/coli_build.txt",'w')
    for i in range(n_build):
        build_out.write(files[i] + "\n")
    build_out.close()

    add_out = open("lists/coli_add.txt",'w')
    for i in range(n_build, n_build + n_add):
        add_out.write(files[i] + "\n")
    add_out.close()

    del_out = open("lists/coli_del.txt",'w')
    for i in range(n_build + n_add, n_build + n_add + n_del):
        del_out.write(files[i] + "\n")
    del_out.close()
    
    generate_input_files()
