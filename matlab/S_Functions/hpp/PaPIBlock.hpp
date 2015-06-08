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
    //Parameter
    int max_msg_length;
    //Used to remember the amount of elements of the input vector u1
    int amount_input;
    //Used to remember the amount of elements of the input vector y1
    int amount_output;
    int amount_parameter;
    

    Json::Value papiJsonConfig;
    Json::Value blockJsonConfig;

    std::string config;
    std::string str;
    bool sent;
    int sent_counter;
    int output_length;
    bool config_sent;
    std::string data_to_sent;
    void parseBlockJsonConfig(signed char json_string[]);
    void buildConfiguration();
public:
    PaPIBlock(int size_data_in, int size_stream_in, int size_stream_out, int size_para_out, signed char json_string[], int size_json_string);
    void setOutput(double u1[], int stream_in[], int msg_length, double time, int stream_out[], double para_out[], int flag_new_data[]);
    void setParaOut(int stream_in[], int msg_length, double para_out[]);

    void sendConfig(int stream_out[]);
    void sendInput(double u1[], double time, int stream_out[]);
    void clearOutput(int stream_out[]);
};

// External declaration for class instance global storage
extern PaPIBlock *papiBlockVar;

// Method wrappers
extern void createPaPIBlock(int size_data_in, int size_stream_in, int size_stream_out, int size_para_out, signed char json_string[], int size_json_string);
extern void deletePaPIBlock();
extern void outputPaPIBlock(double data_in[], int stream_in[], int msg_length, double time, int stream_out[], double para_out[], int flag_new_data[]);

#endif /* _PAPI_BLOCK_ */
