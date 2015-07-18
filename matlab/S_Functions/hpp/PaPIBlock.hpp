/*
Copyright (C) 2014 Technische Universität Berlin,
Fakultät IV - Elektrotechnik und Informatik,
Fachgebiet Regelungssysteme,
Einsteinufer 17, D-10587 Berlin, Germany

This file is part of PaPI.

PaPI is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PaPI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with PaPI.  If not, see <http://www.gnu.org/licenses/>.

Contributors:
Sven Knuth
*/


#ifndef _PAPI_BLOCK_
#define _PAPI_BLOCK_

//#include <cstdint>

#include <string>
#include <iostream>
#include <sstream>
#include <cstdio>
#include <algorithm>
#include <signal.h>
#include <stdlib.h>

#include <boost/array.hpp>

#include <jsoncpp/json/json.h>

#include "UDPHandle.hpp"

class PaPIBlock {
private:
    //--------------------------
    // Important pointer
    double* y2_para_out;

    // -------------------------
    // Important variables
    // -------------------------
    //Used to remember the amount of elements of the input vector u1
    int size_u1_vector;
    //Used to remember the amount of elements of the input vector y1
    int amount_output;
    //Amount of different parameters [1,5,4,3] => 4
    int amount_parameter;
    //Size of the single for the parameter [1,5,4,3] => size(p1)=1, size(p2)=5, size(p3)=4, size(p4)=3
    int* dimension_parameters;
    int* dimension_inputs;
    int* split_signals;
    int amount_inputs;
    //Size of output vector for the parameter [1,5,4,3] => sum([1,5,4,3]) = 13
    int size_output_parameters;

    int* stream_in;
    std::size_t stream_in_length;
    int* stream_out;
    int stream_out_size;

    boost::mutex mutex_stream_in;

    int* offset_parameter;
    int* offset_input;
    Json::Value papiJsonConfig;
    Json::Value blockJsonConfig;

    int size_config;
    std::string config;
    std::string str;
    bool sent;
    int sent_counter;
    bool config_sent;
    std::string data_to_sent;

    void parseBlockJsonConfig(signed char json_string[]);
    void buildConfiguration(double para_out[]);

    std::string getInitialValueForParameter(double para_out[], int p_id);

    UDPHandle* udphandle;
    void handleStream(std::size_t msg_length, boost::array<char, 8192> buffer);
    int local_port;
    int remote_port;


public:
    PaPIBlock(
        int size_u1, int size_p1, int size_p2, int size_p5, int size_p6,  // Sizes determined by size() in the build script
        int p1_dimension_parameters[], signed char p2_json_config[], int p3_size_data_out, // Parameters: p1 - p3
        int p4_amount_para_out, int p5_dimension_input_signals[], int p6_split_signals[],  // Parameters: p4 - p6
        int p7_local_port, int p8_remote_port, signed char p9_remote_ip[]                  // Parameters: p7 - p9
    );

    ~PaPIBlock();

    void setOutput(double u1[], double time, double para_out[]);
    void setParaOut(int stream_in[], std::size_t msg_length, double para_out[]);

    void sendConfig(int stream_out[]);
    void sendInput(double u1[], double time, int stream_out[]);
    void clearOutput(int stream_out[]);
    void reset(double para_out[]);

};

// Method wrappers
extern void createPaPIBlock(
    void **work1, //Working vector
    int size_u1, int size_p1, int size_p2, int size_p5, int size_p6, // Sizes determined by size() in the build script
    int p1_dimension_parameters[], signed char p2_json_config[], int p3_size_data_out, // Parameters: p1 - p3
    int p4_amount_para_out, int p5_dimension_input_signals[], int p6_split_signals[],  // Parameters: p4 - p6
    int p7_local_port, int p8_remote_port, signed char p9_remote_ip[]                  // Parameters: p7 - p9
);

extern void deletePaPIBlock(void **work1);

extern void outputPaPIBlock(
    void **work1, double u1_data_in[], double u2_time, int u3_reset_event,
    double y1_para_out[]
);

#endif /* _PAPI_BLOCK_ */
