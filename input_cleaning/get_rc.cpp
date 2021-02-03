#include <iostream>
#include <vector>
#include "input_reading.hh"

typedef long long LL;
using namespace std;

char get_rc(char c){
    switch(c){
        case 'A': return 'T';
        case 'T': return 'A';
        case 'C': return 'G';
        case 'G': return 'C';
        default: cerr << "Error getting reverse complement from " << c << endl; exit(1);
    }   
}

void reverse_complement(string& S){
    std::reverse(S.begin(), S.end());
    for(char& c : S) c = get_rc(c);
}  

int main(int argc, char** argv){

    if(argc == 1){
        cerr << "Usage: in.fasta out.fasta" << endl;
        return 1;
    }

    string infile = argv[1];
    string outfile = argv[2];

    throwing_ofstream out(outfile);

    Sequence_Reader sr(infile, FASTA_MODE);
    LL seq_id = 0;
    while(!sr.done()){
        string seq = sr.get_next_query_stream().get_all();
        reverse_complement(seq);
        out << ">" << seq_id++ << "rc" << "\n" << seq << "\n";
    }
    cerr << "Done" << endl;

}