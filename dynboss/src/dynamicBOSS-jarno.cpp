#include <libgen.h>  // basename

#include <chrono>
#include <fstream>
#include <iostream>
#include <sdsl/bit_vectors.hpp>
#include <sdsl/wavelet_trees.hpp>

#include "algorithm.hpp"
#include "dynBoss.hpp"
#include "formatutil.cpp"
#include "input_reading.hh"
#include "io.hpp"
#include "kmer-counter.hpp"
#include "tclap/CmdLine.h"
#include "utility.hpp"
using namespace std;
using namespace sdsl;

long long cur_time_millis() {
    return (std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()))
        .count();
}

string extension;
struct parameters_t {
    std::string function = "";
    std::string pack_filename = "";
    std::string graph_filename = "";
    std::string output_filename = "";
    std::string kmer_filename = "";
    std::string query_result = "";
};

void parse_arguments(int argc, char **argv, parameters_t &params);
void parse_arguments(int argc, char **argv, parameters_t &params) {
    TCLAP::CmdLine cmd(
        "DynamicBOSS. Copyright (c) Bahar Alipanahi, Alan Kuhnle, Alex Bowe "
        "2019",
        ' ', VERSION);

    TCLAP::UnlabeledValueArg<std::string> function_arg(
        "functions", ".enter add, delete or query.", true, "", "functions",
        cmd);

    TCLAP::ValueArg<std::string> kmer_filename_arg(
        "s", "kmers", ".fasta file to count kmers to add and delete.", false,
        "", "kmer file", cmd);

    TCLAP::ValueArg<std::string> graph_filename_arg(
        "g", "input", ".dbg file (output from dynamicBOSS -f build).", false,
        "", "dbg file", cmd);

    TCLAP::ValueArg<std::string> pack_filename_arg(
        "p", "pack-input", ".packed file (output from cosmo-pack).", false, "",
        "pack file", cmd);

    TCLAP::ValueArg<std::string> output_filename_arg(
        "o", "output", "Output graph name", false, "", "output file", cmd);

    TCLAP::ValueArg<std::string> query_output_filename_arg(
        "q", "query-result", "File for writing the query results", false, "", "query output file", cmd);

    cmd.parse(argc, argv);
    params.function = function_arg.getValue();
    params.pack_filename = pack_filename_arg.getValue();
    params.graph_filename = graph_filename_arg.getValue();
    params.kmer_filename = kmer_filename_arg.getValue();
    params.output_filename = output_filename_arg.getValue();
    params.query_result = query_output_filename_arg.getValue();
}

int main(int argc, char *argv[]) {
    parameters_t p;
    string ext;

    parse_arguments(argc, argv, p);

    if (p.function != "build" && p.function != "add" &&
        p.function != "delete" && p.function != "query") {
        cout << "ERROR: Please insert one of the functions build, add, delete, "
                "or query\n";
        exit(0);
    }
    cout << "Function " << p.function << " is called" << endl;

    if (p.function == "add" || p.function == "delete" ||
        p.function == "query") {
        if (p.graph_filename == "") {
            cout << "ERROR: No graph file entered to update or query (empty -g "
                    "option)"
                 << endl;
            exit(0);
        }

        ext = p.graph_filename.substr(p.graph_filename.find_last_of(".") + 1);
        if (ext != "dbg" && ext != "updated") {
            cout << "ERROR: Graph file name must have extension .dbg or "
                    ".updated only"
                 << endl;
            exit(0);
        }

        if (p.kmer_filename == "") {
            cout << "ERROR: No kmer file entered--kmers to update/query will "
                    "be counted from this file (empty -s option)"
                 << endl;
            exit(0);
        }

        ext = p.kmer_filename.substr(p.kmer_filename.find_last_of(".") + 1);
        if (ext != "fasta" && ext != "fa") {
            cout << "ERROR: Kmer file format must be fasta (extension .fa or "
                    ".fasta only)"
                 << endl;
            exit(0);
        }
    }

    else {
        if (p.pack_filename == "") {
            cout << "ERROR: No .packed file entered for build (empty -p option)"
                 << endl;
            exit(0);
        }

        ext = p.pack_filename.substr(p.pack_filename.find_last_of(".") + 1);
        if (ext != "packed") {
            cout << "ERROR: .packed file must have extension .packed" << endl;
            exit(0);
        }
    }
    cout << "=================================================================="
            "==\n";

    dyn_boss dbg;
    size_t bs;
    bool warning = 0;
    double time_elapsed = 0;
    clock_t t_start;

    if (p.function == "build") {
        cout << "BUILDING GRAPH\n";

        ifstream input(p.pack_filename, ios::in | ios::binary | ios::ate);

        t_start = clock();
        dbg.load_from_packed_edges(input, "$ACGT");
        time_elapsed += double(clock() - t_start);

        input.close();
        cout << "DynamicBOSS graph is built in: "
             << time_elapsed / CLOCKS_PER_SEC << " (s)" << endl;
    }

    else {
        cout << "LOADING GRAPH\n";
        cout << "Loading DynamicBOSS from file: " << p.graph_filename << endl;
        ifstream input(p.graph_filename, ios::in | ios::binary | ios::ate);
        load_from_file(dbg, p.graph_filename);
        input.close();
        cout << "Original graph: " << endl;
        cout << "k             : " << dbg.k << endl;
        cout << "num_nodes()   : " << dbg.num_nodes() << endl;
        cout << "num_edges()   : " << dbg.num_edges() << endl;
        bs = dbg.bit_size();
        cout << "Total size    : " << bs / 8.0 / 1024.0 / 1024.0 << " MB"
             << endl;
        cout << "Bits per edge : " << bs / static_cast<double>(dbg.num_edges())
             << " Bits" << endl;
        cout << "=============================================================="
                "======\n";

        cout << "OPENING KMER FILE\n";
        cout << "Reading FASTA file " << p.kmer_filename << endl;
        size_t nKmers;
        set<string> kmers;
        if (p.function != "query"){  // Jarno fix: stream k-mers in query
            getKmers(nKmers, dbg.k, kmers, p.kmer_filename);
            cout << nKmers << " distinct kmers were counted " << endl;
            cout << "=============================================================="
                "======\n";
        }

        size_t counter = 0;
        size_t available_kmers = 0;
        size_t absent_kmers = 0;

        cout << "PROCESS STARTS\n";
        if (p.function == "add") {
            for (auto it = kmers.begin(); it != kmers.end(); ++it) {
                if (counter % 1000 == 0) {
                    cerr << "\r           \r";
                    cerr << (double)counter * 100 / kmers.size()
                         << "% of kmers were processed";
                }
                string kmer = *it;
                if (!dbg.index_edge_alan(kmer.begin())) {
                    t_start = clock();
                    dbg.add_edge(kmer);
                    time_elapsed += double(clock() - t_start);

                } else
                    available_kmers += 1;
                counter += 1;
            }
            cerr << "\n100% of kmers were processed\n";
            if (available_kmers > 0) {
                cout << available_kmers << " ("
                     << (double)available_kmers * 100 / kmers.size()
                     << "%) of the kmers were already in the graph\n";
                if (available_kmers == kmers.size()) {
                    warning = 1;
                    cout << "WARNING! all kmers were already in the graph!\n";
                }
            }
            cout << kmers.size() - available_kmers
                 << " kmers added to the graph in "
                 << time_elapsed / CLOCKS_PER_SEC << " (s)" << endl;
            cout << "Time per operaition: "
                 << (time_elapsed / CLOCKS_PER_SEC) / kmers.size() << " (s)"
                 << endl;
        }

        if (p.function == "delete") {
            for (auto it = kmers.begin(); it != kmers.end(); ++it) {
                if (counter % 1000 == 0) {
                    cerr << "\r           \r";
                    cerr << (double)counter * 100 / kmers.size()
                         << "% of kmers were processed";
                }
                string kmer = *it;
                if (dbg.index_edge_alan(kmer.begin())) {
                    clock_t t_start = clock();
                    dbg.delete_edge(kmer);
                    time_elapsed += double(clock() - t_start);

                } else
                    absent_kmers += 1;
                counter += 1;
            }
            cerr << "\n100% of kmers were processed\n";
            if (absent_kmers > 0) {
                cout << absent_kmers << " ("
                     << (double)absent_kmers * 100 / kmers.size()
                     << "%) of the kmers were not in the graph\n";
                if (absent_kmers == kmers.size()) {
                    warning = 1;
                    cout << "WARNING! none of the kmers were in the graph!\n";
                }
            }
            cout << kmers.size() - absent_kmers
                 << " kmers deleted from the graph in "
                 << time_elapsed / CLOCKS_PER_SEC << " (s)" << endl;
            cout << "Time per operaition: "
                 << (time_elapsed / CLOCKS_PER_SEC) / kmers.size() << " (s)"
                 << endl;
        }
        if (p.function == "query") {
            if(p.query_result == ""){
              std::cerr << "Error: query output file not given" << std::endl;
              return 1;
            }
            long long query_start_jarno = cur_time_millis();
            long long edgemer_k =
                dbg.k;  // This is edgemer k: see dynboss::edge_label(size_t i)
            ofstream ofs(p.query_result);
            if(!ofs.good()){
              cerr << "Error opening query outfile: " << p.query_result << endl;
              return 1;
            }
            Sequence_Reader sr(p.kmer_filename, FASTA_MODE);
            while (!sr.done()) {
                string seq = sr.get_next_query_stream().get_all();
                vector<bool> hits(std::max(0LL, (long long)seq.size() - edgemer_k + 1));
                for (long long i = 0; i < (long long)seq.size() - edgemer_k + 1; i++) {
                    bool present = dbg.index_edge_alan(seq.begin() + i);
                    hits[i] = present;
                }
                // Write out
                for(long long i = 0; i < (long long)hits.size(); i++)
                  ofs << hits[i];
                ofs << "\n";
            }
            long long elapsed_jarno = cur_time_millis() - query_start_jarno;
            std::cerr << "Time for all queries: " << (double)elapsed_jarno / 1e3
                      << " seconds" << std::endl;

            /*cerr<<"\n100% of kmers were processed\n";
            cout<<kmers.size()-absent_kmers<<"
            ("<<(double)(kmers.size()-absent_kmers)*100/kmers.size()<<"%) of the
            kmers were in the graph\n"; cout<<kmers.size()<< " kmers were
            queried in "<< time_elapsed/CLOCKS_PER_SEC<<" (s)"<<endl;
            cout<<"Time per operaition:
            "<<(time_elapsed/CLOCKS_PER_SEC)/kmers.size()<<" (s)"<<endl;
            ofs.close();*/
        }
    }
    cout << "=================================================================="
            "==\n";
    if (p.function != "build") cout << "PROCESS FINISHED\n";
    if (p.function == "build" || (p.function != "query" && !warning)) {
        (p.function == "build") ? cout << "Graph:\n"
                                : cout << "Updated graph:\n";
        cout << "k             : " << dbg.k << endl;
        cout << "num_nodes()   : " << dbg.num_nodes() << endl;
        cout << "num_edges()   : " << dbg.num_edges() << endl;
        bs = dbg.bit_size();
        cout << "Total size    : " << bs / 8.0 / 1024.0 / 1024.0 << " MB"
             << endl;
        cout << "Bits per edge : " << bs / static_cast<double>(dbg.num_edges())
             << " Bits" << endl;

        cout << "Writing the DynamicBOSS in file: " << p.output_filename
             << endl;

        ofstream ofs(p.output_filename, ios::out | ios::binary);
        dbg.serialize(ofs);
        ofs.close();
    }
    if (warning)
        cout << "There were no kmers to process (above WARNING), so graph is "
                "unchanged\n";

    if (p.function == "query")
        cout << "Query results in file: " << p.query_result << endl;

    cout << "DONE!" << endl;
}
