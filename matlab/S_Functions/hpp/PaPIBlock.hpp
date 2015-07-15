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

#include <jsoncpp/json/json.h>


class PaPIBlock {
private:

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

    int* offset_parameter;
    int* offset_input;
    Json::Value papiJsonConfig;
    Json::Value blockJsonConfig;

    std::string config;
    std::string str;
    bool sent;
    int sent_counter;

    bool config_sent;
    std::string data_to_sent;
    void parseBlockJsonConfig(signed char json_string[]);
    void buildConfiguration(double para_out[]);

    std::string getInitialValueForParameter(double para_out[], int p_id);



public:
    PaPIBlock(
        int size_u1, int size_u2, int size_p1, int size_p2, int size_p5, int size_p6,  // Sizes determined by size() in the build script
        int p1_dimension_parameters[], signed char p2_json_config[], int p3_size_data_out, // Parameters: p1 - p3
        int p4_amount_para_out, int p5_dimension_input_signals[], int p6_split_signals[]   // Parameters: p4 - p5
    );
    void setOutput(double u1[], int stream_in[], int msg_length, double time, int stream_out[], double para_out[]);
    void setParaOut(int stream_in[], int msg_length, double para_out[]);

    void sendConfig(int stream_out[]);
    void sendInput(double u1[], double time, int stream_out[]);
    void clearOutput(int stream_out[]);
    void reset(double para_out[]);
};

// External declaration for class instance global storage
extern PaPIBlock *papiBlockVar;
// amount_parameters, [unicode2native(json_string, 'ISO-8859-1') 0], output_size, sum(amount_parameters), define_inputs, sum(define_inputs)

// Method wrappers
extern void createPaPIBlock(
    void **work1, //Working vector
    int size_u1, int size_u2, int size_p1, int size_p2, int size_p5, int size_p6, // Sizes determined by size() in the build script
    int p1_dimension_parameters[], signed char p2_json_config[], int p3_size_data_out, // Parameters: p1 - p3
    int p4_amount_para_out, int p5_dimension_input_signals[], int p6_split_signals[]   // Parameters: p4 - p5
);

extern void deletePaPIBlock(void **work1);

extern void outputPaPIBlock(
    void **work1, double u1_data_in[], int u2_stream_in[],
    int u3_msg_length, double u4_time, int u5_reset_event, int y1_stream_out[],
    double y2_para_out[]
);

#endif /* _PAPI_BLOCK_ */
