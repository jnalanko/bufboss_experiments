#include <iostream>
#include <vector>
#include "input_reading.hh"

typedef long long LL;
using namespace std;

vector<string> readlines(string file){
    throwing_ifstream in(file);
    vector<string> lines;
    string line;
    while(in.getline(line)){
        lines.push_back(line);
    }
    return lines;
}

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

int main(int argc, char** argv){

    if(argc == 1){
        cerr << "Usage: infile_list.txt outfile.fasta edgemer_k" << endl;
        return 1;
    }

    string infile_list = argv[1];
    string outfile = argv[2];
    LL edgemer_k = stoll(argv[3]);

    throwing_ofstream out(outfile);

    LL part_id = 0;
    for(string file : readlines(infile_list)){
        cerr << "Processing " << file << endl;
        Sequence_Reader sr(file, FASTA_MODE);
        while(!sr.done()){
            string seq = sr.get_next_query_stream().get_all();
            for(string part : segment_string(seq, edgemer_k)){
                out << ">" << part_id++ << "\n" << part << "\n";
            }
        }
    }
    cerr << "Done" << endl;

}