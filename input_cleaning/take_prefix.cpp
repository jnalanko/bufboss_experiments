#include <iostream>
#include <vector>
#include <cassert>
#include "input_reading.hh"

typedef long long LL;
using namespace std;

int main(int argc, char** argv){

    if(argc == 1){
        //run("./input_cleaning/take_prefix 1000000 " + build_concat + " " + query_inputs["query-existing_build_sequence"])
        cerr << "Usage: " << argv[0] << " n_basepairs infile.fasta outfile.fasta" << endl;
        return 1;
    }

    LL n_basepairs = stoll(argv[1]);
    string infile = argv[2];
    string outfile = argv[3];

    throwing_ofstream out(outfile);
    LL read_id = 0;
    Sequence_Reader sr(infile, FASTA_MODE);
    LL n_taken = 0;
    while(!sr.done()){
        string seq = sr.get_next_query_stream().get_all();
        if(n_taken + (LL)seq.size() > n_basepairs){
            // Want n_taken + |seq| = n_basepairs
            // -> |seq| = n_basepairs - n_taken
            seq = seq.substr(0, n_basepairs - n_taken);
        }
        out << ">" << read_id++ << "\n" << seq << "\n";
        n_taken += seq.size();
        if(n_taken >= n_basepairs) break;
    }
    cerr << n_taken << " base pairs taken" << endl;

}