#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include<string>
#include <math.h>
#define BOOST_LOG_DYN_LINK 1
#include <boost/log/core.hpp>
#include <boost/log/trivial.hpp>
#include <boost/log/expressions.hpp>
#include <chrono>
#include "FDBG.cpp"
#include "TestUtil.cpp"
#include "formatutil.cpp"

int main(int argc, char* argv[]){
string graphName = argv[1];
FDBG Graph;
     ifstream ifile_ds( graphName, ios::in | ios::binary );
     Graph.load( ifile_ds );
        //       FDBG original_Graph = Graph;
     BOOST_LOG_TRIVIAL(info) << "Data structure loaded " ;
     BOOST_LOG_TRIVIAL(info)<<"k value or node size is: "<<Graph.k<<" graph has "<<Graph.n<<" nodes ";
     BOOST_LOG_TRIVIAL(info) << "Original Bits per element:" << Graph.bitSize() / static_cast<double>( Graph.n );
}
