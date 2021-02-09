#include <iostream>
#include <vector>
#include <cassert>
#include "input_reading.hh"

typedef long long LL;
using namespace std;

// Todo: explain what this does
vector<string> segment_string(const string& S, LL edgemer_k){
    vector<bool> bad(S.size());
    LL k = edgemer_k; // Shorthand
    for(LL i = 0; i < (LL)S.size(); i++){
        if(S[i] != 'A' && S[i] != 'C' && S[i] != 'G' && S[i] != 'T'){
            for(LL j = max((LL)0, i-k+1); j <= min((LL)S.size()-1, i+k-1); j++)
                bad[j] = 1;
        }
    }

    vector<string> ans;
    string cur = "";
    for(LL i = 0; i < (LL)S.size(); i++){
        if(!bad[i]) cur += S[i];
        if(bad[i] || i == (LL)S.size() - 1){
            if((LL)cur.size() >= k) ans.push_back(cur);
            cur = "";
        }
    }
    return ans;
}

LL count_reads(string readfile){
    throwing_ifstream in(readfile);
    string line;
    LL count = 0;
    while(in.getline(line)){
        if(line.size() > 0 && line[0] == '>') count++;
    }
    return count;
}

int main(int argc, char** argv){

    if(argc == 1){
        // run("./input_cleaning/split_and_remove_non_ACGT " + str(edgemer_k) + " " + readfile + " " + build_percentage + " " + add_percentage + " " + del_percentage + " " + build_concat + " " + add_concat + " " + del_concat)
        cerr << "Usage: " << argv[0] << " edgemer_k readfile build% add% del% build_reads.fasta add_reads.fasta del_reads.fasta" << endl;
        cerr << "Percentage must be integers and sum to 100." << endl;
        return 1;
    }

    LL edgemer_k = stoll(argv[1]);
    string infile = argv[2];
    LL build_percent = stoll(argv[3]);
    LL add_percent = stoll(argv[4]);
    LL del_percent = stoll(argv[5]);
    string build_outfile = argv[6];
    string add_outfile = argv[7];
    string del_outfile = argv[8];

    assert(build_percent + add_percent + del_percent == 100);

    cerr << "counting reads" << endl;
    LL n_reads = count_reads(infile);
    cerr << n_reads << " reads found" << endl;

    throwing_ofstream build_out(build_outfile);
    throwing_ofstream add_out(add_outfile);
    throwing_ofstream del_out(del_outfile);
    LL read_id = 0;
    LL part_id = 0;
    Sequence_Reader sr(infile, FASTA_MODE);
    while(!sr.done()){
        string seq = sr.get_next_query_stream().get_all();
        for(string part : segment_string(seq, edgemer_k)){
            if(read_id < n_reads * build_percent / 100)
                build_out << ">" << part_id++ << "\n" << part << "\n";
            else if(read_id < n_reads * (build_percent + add_percent) / 100)
                add_out << ">" << part_id++ << "\n" << part << "\n";
            else
                del_out << ">" << part_id++ << "\n" << part << "\n";
        }
        read_id++;
    }
    cerr << "Done" << endl;

}