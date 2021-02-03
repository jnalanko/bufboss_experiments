#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#include <iostream>
#include <string>
#define BOOST_LOG_DYN_LINK 1
#include <boost/log/core.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/trivial.hpp>
#include <chrono>

#include "FDBG.cpp"
#include "TestUtil.cpp"
#include "formatutil.cpp"

void getKmers(size_t& nKmers, size_t k, vector<string>& kmers, ifstream& in) {
    // ifstream in(p.kmer_filename );
    string sline;
    vector<string> vline;
    while (getline(in, sline)) {
        vline.push_back(sline);
    }

    size_t pos = 0;
    vector<string> reads;
    string read;
    do {
        if (vline[pos][0] == '>') {
            // finish current read and start a new one
            if (!read.empty()) {
                reads.push_back(read);
                read.clear();
            }
        } else {
            read += vline[pos];
        }

        ++pos;
    } while (pos != vline.size());

    if (!read.empty())  // handle the last read
        reads.push_back(read);

    for (size_t i = 0; i < reads.size(); ++i) {
        string sline = reads[i];
        size_t read_length = sline.size();

        size_t nMers = read_length - k + 1;
        for (size_t start = 0; start < nMers; ++start) {
            string kmer = sline.substr(start, k);
            kmers.push_back(kmer);
        }
    }
}

int main(int argc, char* argv[]) {
    size_t nKmers;
    vector<string> kmer_2;
    ifstream input;

    input.open(argv[1]);
    
    unsigned int nodeLength = stoi(argv[2]);
    unsigned int edgemer_k = nodeLength + 1;
    string graphName = argv[3];
    string outfile = argv[4];

    BOOST_LOG_TRIVIAL(info) << "reading kmers from new fasta file";
    getKmers(nKmers, edgemer_k, kmer_2, input);
    BOOST_LOG_TRIVIAL(info)
        << "number of kmers for operations: " << kmer_2.size();

    unsigned int num = 0;
    FDBG Graph;
    ifstream ifile_ds(graphName, ios::in | ios::binary);
    Graph.load(ifile_ds);
    //	 FDBG original_Graph = Graph;
    BOOST_LOG_TRIVIAL(info) << "Data structure loaded ";
    BOOST_LOG_TRIVIAL(info) << "k value or node size is: " << Graph.k
                            << " graph has " << Graph.n << " nodes ";
    BOOST_LOG_TRIVIAL(info) << "Original Bits per element:"
                            << Graph.bitSize() / static_cast<double>(Graph.n);

    // indexing edges
    clock_t t_start = clock();
    for (size_t i = 0; i < nodes.size(); i++) {
        if (!Graph.IsEdgeInGraph(nodes[i].first, nodes[i].second))

 
}
