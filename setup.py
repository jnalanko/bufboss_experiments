
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

def parse_our_printed_time(filename):
    for line in open(filename).readlines():
        if "Time for all queries:" in line:
            return float(line.split()[-2])
    print("Error parsing time from " + filename)
    assert(False)

def run_get_output(command):
    # Command can have pipes
    sys.stderr.write(command + "\n")
    proc = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    if proc.returncode != 0:
        print("Error: nonzero return code for command: " + command)
        sys.exit(1)
    return proc.stdout.decode("utf-8").strip()

def run(command):
    sys.stderr.write(command + "\n")
    if subprocess.run(command, shell=True).returncode != 0:
        print("Error: nonzero return code for command: " + command)
        sys.exit(1)

def run_to_files(command, out_prefix):
    sys.stderr.write(command + "\n")
    stdout_file = out_prefix + ".stdout.txt"
    stderr_file = out_prefix + ".stderr.txt"
    sys.stderr.write("stdout to " + stdout_file + "\n")
    sys.stderr.write("stderr to " + stderr_file + "\n")
    stdout_stream = open(stdout_file, 'w')
    stderr_stream = open(stderr_file, 'w')
    if subprocess.run(command, shell=True, stdout=stdout_stream, stderr=stderr_stream).returncode != 0:
        print("Error: nonzero return code for command: " + command)
        sys.exit(1)

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

# Returns pair (time seconds, RSS bytes)
def parse_usr_bin_time(stderr_file):
    rss, time = None, None
    for line in open(stderr_file):
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
        print("Error parsing /usr/time/time -v from " + stderr_file)
        assert(False)

    return time, rss

# Path can be a directory or a single file
# If directory, returns the total size of the directory
# If file, returns the file size
def get_disk_size_bytes(path):
    return int(run_get_output("du -d 0 -b "  + path).split()[0])

datadir = "data"
tempdir = "temp"

buildlist = "lists/coli_build.txt"
addlist = "lists/coli_add.txt"
dellist = "lists/coli_del.txt"

build_concat = datadir + "/build.fasta"
add_concat = datadir + "/add.fasta"
del_concat = datadir + "/del.fasta"

build_concat_with_rc = datadir + "/build_with_rc.fasta"
add_concat_with_rc = datadir + "/add_with_rc.fasta"
del_concat_with_rc = datadir + "/del_with_rc.fasta"

nodemer_k = 30
edgemer_k = nodemer_k + 1

query_inputs = {"query-random_edgemers": "data/random/edgemers.fasta",
                "query-random_sequence": "data/random/sequence.fasta",
                "query-existing_build_edgemers": "data/existing/build_edgemers.fasta",
                "query-existing_build_sequence": "data/existing/build_sequence.fasta",
                "query-existing_added_edgemers": "data/existing/added_edgemers.fasta",
                "query-existing_added_sequence" : "data/existing/added_sequence.fasta"}
query_metadatafile = "lists/query_metadata.txt"

def fasta_count_edgemers(fastafile):
    seq_len = 0
    total_edgemers = 0
    for line in open(fastafile):
        line = line.strip()
        if len(line) == 0: continue
        if line[0] == '>':
            total_edgemers += max(0, seq_len - edgemer_k + 1)
            seq_len = 0
        else:
            seq_len += len(line)
    total_edgemers += max(0, seq_len - edgemer_k + 1) # Last sequence
    return total_edgemers

def generate_input_files_from_readfile(readfile, build_percentage, add_percentage, del_percentage):
    # Split to build, add, del
    run("./input_cleaning/split_and_remove_non_ACGT " + str(edgemer_k) + " " + readfile + " " + build_percentage + " " + add_percentage + " " + del_percentage + " " + build_concat + " " + add_concat + " " + del_concat)

    # For tools that don't index reverse complements (looking at you dynboss), create input files with
    # concatenated reverse complements in the end
    run("./input_cleaning/get_rc " + build_concat + " temp/temp_rc.fasta")
    run("cat " + build_concat + " temp/temp_rc.fasta > " + build_concat_with_rc) 

    run("./input_cleaning/get_rc " + add_concat + " temp/temp_rc.fasta")
    run("cat " + add_concat + " temp/temp_rc.fasta > " + add_concat_with_rc)

    run("./input_cleaning/get_rc " + del_concat + " temp/temp_rc.fasta")
    run("cat " + del_concat + " temp/temp_rc.fasta > " + del_concat_with_rc)

    # Generate random queries
    run("mkdir -p data/random")
    run("python3 gen_random_kmers.py 31 1000000 > " + query_inputs["query-random_edgemers"]) # Million edgemers
    run("python3 gen_random_kmers.py 1000000 1 > " + query_inputs["query-random_sequence"]) # Million - k + 1 edgemers

    # Generate existing queries...
    run("mkdir -p data/existing")

    # ...for existing k-mers, build a bufboss and sample from there. First for build kmers...
    index_dir = tempdir + "/buffboss"
    run("mkdir -p " + index_dir)
    run("./bufboss/KMC/bin/kmc -k31 -m1 -ci1 -cs1 -fm " + build_concat + " " + tempdir + "/kmc_db temp")
    run("./bufboss/bin/bufboss_build --KMC " + tempdir + "/kmc_db -o " + index_dir + " -t " + tempdir)
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + index_dir + " -o " + query_inputs["query-existing_build_edgemers"] + " --count 1000000")

    # ...then for added kmers (reuse the same index dir)
    run("./bufboss/KMC/bin/kmc -k31 -m1 -ci1 -cs1 -fm " + add_concat + " " + tempdir + "/kmc_db temp")
    run("./bufboss/bin/bufboss_build --KMC " + tempdir + "/kmc_db -o " + index_dir + " -t " + tempdir)
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + index_dir + " -o " + query_inputs["query-existing_added_edgemers"] + " --count 1000000")

    # For existing sequences, take 1 million base pairs from buildlist and addlist
    run("./input_cleaning/take_prefix 1000000 " + build_concat + " " + query_inputs["query-existing_build_sequence"])
    run("./input_cleaning/take_prefix 1000000 " + add_concat + " " + query_inputs["query-existing_added_sequence"])

    print("Calculating metadata")
    metadata = open(query_metadatafile,'w')
    for name in query_inputs:
        metadata.write(name + " " + str(fasta_count_edgemers(query_inputs[name])) + "\n")

def generate_input_files_from_genomes():

    # Concatenate fasta files and remove non-ACGT
    run("./input_cleaning/collect_and_remove_non_ACGT " + buildlist + " " + build_concat + " " + str(edgemer_k))
    run("./input_cleaning/collect_and_remove_non_ACGT " + addlist + " " + add_concat + " " + str(edgemer_k))
    run("./input_cleaning/collect_and_remove_non_ACGT " + dellist + " " + del_concat + " " + str(edgemer_k))

    # For tools that don't index reverse complements (looking at you dynboss), create input files with
    # concatenated reverse complements in the end
    run("./input_cleaning/get_rc " + build_concat + " temp/temp_rc.fasta")
    run("cat " + build_concat + " temp/temp_rc.fasta > " + build_concat_with_rc) 

    run("./input_cleaning/get_rc " + add_concat + " temp/temp_rc.fasta")
    run("cat " + add_concat + " temp/temp_rc.fasta > " + add_concat_with_rc)

    run("./input_cleaning/get_rc " + del_concat + " temp/temp_rc.fasta")
    run("cat " + del_concat + " temp/temp_rc.fasta > " + del_concat_with_rc)

    # Generate random queries
    run("mkdir -p data/random")
    run("python3 gen_random_kmers.py 31 1000000 > " + query_inputs["query-random_edgemers"]) # Million edgemers
    run("python3 gen_random_kmers.py 1000000 1 > " + query_inputs["query-random_sequence"]) # Million - k + 1 edgemers

    # Generate existing queries...
    run("mkdir -p data/existing")

    # ...for existing k-mers, build a bufboss and sample from there. First for build kmers...
    index_dir = tempdir + "/buffboss"
    run("mkdir -p " + index_dir)
    run("./bufboss/KMC/bin/kmc -k31 -m1 -ci1 -cs1 -fm " + build_concat + " " + tempdir + "/kmc_db temp")
    run("./bufboss/bin/bufboss_build --KMC " + tempdir + "/kmc_db -o " + index_dir + " -t " + tempdir)
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + index_dir + " -o " + query_inputs["query-existing_build_edgemers"] + " --count 1000000")

    # ...then for added kmers (reuse the same index dir)
    run("./bufboss/KMC/bin/kmc -k31 -m1 -ci1 -cs1 -fm " + add_concat + " " + tempdir + "/kmc_db temp")
    run("./bufboss/bin/bufboss_build --KMC " + tempdir + "/kmc_db -o " + index_dir + " -t " + tempdir)
    run("./bufboss/bin/bufboss_sample_random_edgemers -i " + index_dir + " -o " + query_inputs["query-existing_added_edgemers"] + " --count 1000000")

    # For existing sequences, take the first file in buildlist and in addlist
    run("head -n 1 " + buildlist + " > " + tempdir + "/buildlist_first.txt")
    run("./input_cleaning/collect_and_remove_non_ACGT " + tempdir + "/buildlist_first.txt " + query_inputs["query-existing_build_sequence"] + " " + str(edgemer_k))

    run("head -n 1 " + addlist + " > " + tempdir + "/addlist_first.txt")
    run("./input_cleaning/collect_and_remove_non_ACGT " + tempdir + "/addlist_first.txt " + query_inputs["query-existing_added_sequence"] + " " + str(edgemer_k))

    print("Calculating metadata")
    metadata = open(query_metadatafile,'w')
    for name in query_inputs:
        metadata.write(name + " " + str(fasta_count_edgemers(query_inputs[name])) + "\n")

# Takes number of genomes to build, add and del respectively.
if __name__ == "__main__":
    if sys.argv[1] == "ecoli":
        n_build = int(sys.argv[2])
        n_add = int(sys.argv[3])
        n_del = int(sys.argv[4])
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
        
        generate_input_files_from_genomes()
    elif sys.argv[1] == "reads":
        readfile = sys.argv[2]
        build_percentage = int(sys.argv[3])
        add_percentage = int(sys.argv[4])
        del_percentage = int(sys.argv[5])
        assert(build_percentage + add_percentage + del_percentage == 100)
        generate_input_files_from_readfile(readfile, build_percentage, add_percentage, del_percentage)
    else:
        print("Invalid experiment name: " + sys.argv[1])
        quit(1)
