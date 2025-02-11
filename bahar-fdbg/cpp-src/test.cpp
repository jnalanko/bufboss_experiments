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
    unsigned int k = stoi(argv[2]);
    string graphName = argv[3];

    unsigned int nodeLength = k - 1;

    BOOST_LOG_TRIVIAL(info) << "reading kmers from new fasta file";
    getKmers(nKmers, k, kmer_2, input);
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

    vector<pair<kmer_t, kmer_t>> nodes;
    set<kmer_t> added_deleted_nodes;
    set<pair<kmer_t, kmer_t>> added_deleted_edges;
    for (size_t i = 0; i < kmer_2.size(); i++) {
        string strU = kmer_2[i].substr(0, k - 1);
        string strV = kmer_2[i].substr(1, k);

        kmer_t u = mer_string_to_binary(strU, num, nodeLength);
        kmer_t v = mer_string_to_binary(strV, num, nodeLength);
        nodes.push_back(make_pair(u, v));
    }

    // indexing edges
    clock_t t_start = clock();
    for (size_t i = 0; i < nodes.size(); i++) {
        if (!Graph.IsEdgeInGraph(nodes[i].first, nodes[i].second))
            added_deleted_edges.insert(
                make_pair(nodes[i].first, nodes[i].second));
    }
    double t_elapsed = (clock() - t_start) / CLOCKS_PER_SEC;
    BOOST_LOG_TRIVIAL(info)
        << "DONE with indexing all " << kmer_2.size() << " edges";
    BOOST_LOG_TRIVIAL(info)
        << "Time per indexing: " << t_elapsed / kmer_2.size();
    BOOST_LOG_TRIVIAL(info) << kmer_2.size() - added_deleted_edges.size()
                            << " of the edges were already in the graph";

    /*for (size_t i = 0; i < added_deleted_edges.size() ;i++) {
            if (!Graph.detect_membership(added_deleted_edges[i].first)) {
                    added_deleted_nodes.push_back(added_deleted_edges[i].first);}
                    if (!Graph.detect_membership(added_deleted_edges[i].second))
       { added_deleted_nodes.push_back(added_deleted_edges[i].second);}
            }*/
    for (set<pair<kmer_t, kmer_t>>::iterator it = added_deleted_edges.begin();
         it != added_deleted_edges.end(); ++it) {
        if (!Graph.detect_membership(it->first)) {
            added_deleted_nodes.insert(it->first);
        }
        if (!Graph.detect_membership(it->second)) {
            added_deleted_nodes.insert(it->second);
        }
    }

    t_start = clock();
    for (set<kmer_t>::iterator it = added_deleted_nodes.begin();
         it != added_deleted_nodes.end(); ++it) {
        Graph.addNode(*it);
    }
    for (set<pair<kmer_t, kmer_t>>::iterator it = added_deleted_edges.begin();
         it != added_deleted_edges.end(); ++it) {
        Graph.newDynamicAddEdge(it->first, it->second);
    }

    t_elapsed = (clock() - t_start) / CLOCKS_PER_SEC;
    BOOST_LOG_TRIVIAL(info) << "DONE with addition of all "
                            << added_deleted_edges.size() << " edges";
    BOOST_LOG_TRIVIAL(info)
        << "Time per addition: " << t_elapsed / added_deleted_edges.size();
    BOOST_LOG_TRIVIAL(info)
        << "After addition graph has " << Graph.n << " nodes ";
    BOOST_LOG_TRIVIAL(info) << "Bits per element after addition: "
                            << Graph.bitSize() / static_cast<double>(Graph.n);

    for (set<pair<kmer_t, kmer_t>>::iterator it = added_deleted_edges.begin();
         it != added_deleted_edges.end(); ++it) {
        if (!Graph.IsEdgeInGraph(it->first, it->second)) {
            BOOST_LOG_TRIVIAL(info) << "Addition is not complete";
            exit(0);
        }
    }
    for (set<kmer_t>::iterator it = added_deleted_nodes.begin();
         it != added_deleted_nodes.end(); ++it) {
        if (!Graph.detect_membership(*it)) {
            BOOST_LOG_TRIVIAL(info) << "Addition is not complete";
            exit(0);
        }
    }

    BOOST_LOG_TRIVIAL(info) << "Addition is complete";
    t_start = clock();
    for (set<pair<kmer_t, kmer_t>>::iterator it = added_deleted_edges.begin();
         it != added_deleted_edges.end(); ++it) {
        Graph.dynamicRemoveEdge(it->first, it->second);
    }
    for (set<kmer_t>::iterator it = added_deleted_nodes.begin();
         it != added_deleted_nodes.end(); ++it) {
        Graph.removeNode(*it);
    }

    t_elapsed = (clock() - t_start) / CLOCKS_PER_SEC;
    BOOST_LOG_TRIVIAL(info) << "DONE with deletion of all "
                            << added_deleted_edges.size() << " edges";
    BOOST_LOG_TRIVIAL(info)
        << "Time per deletion: " << t_elapsed / added_deleted_edges.size();
    BOOST_LOG_TRIVIAL(info)
        << "After deletion graph has " << Graph.n << " nodes ";
    BOOST_LOG_TRIVIAL(info) << "Bits per element after deletion: "
                            << Graph.bitSize() / static_cast<double>(Graph.n);

    for (set<pair<kmer_t, kmer_t>>::iterator it = added_deleted_edges.begin();
         it != added_deleted_edges.end(); ++it) {
        if (Graph.IsEdgeInGraph(it->first, it->second)) {
            BOOST_LOG_TRIVIAL(info) << "Verification did not pass";
            exit(0);
        }
    }
    for (set<kmer_t>::iterator it = added_deleted_nodes.begin();
         it != added_deleted_nodes.end(); ++it) {
        if (Graph.detect_membership(*it)) {
            BOOST_LOG_TRIVIAL(info) << "Verification did not pass";
            exit(0);
        }
    }

    BOOST_LOG_TRIVIAL(info) << "Verification passed";
}
