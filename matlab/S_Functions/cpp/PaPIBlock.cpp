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

#include "PaPIBlock.hpp"
#include "UDPHandle.hpp"

#include <limits>

#define START_MESSAGE_COUNTER 1

using namespace std;

/***************************************/
/**** Class instance global storage ****/
/***************************************/

union udouble {
  double d;
  uint64_t u;
};

typedef struct __attribute__((packed)) para {
    int32_t constant;
    int32_t counter;
    int32_t pid;
    double value;
};

/**********************************/
/**** Class method definitions ****/
/**********************************/

PaPIBlock::PaPIBlock(
    int size_u1, int size_p1, int size_p2, int size_p5, int size_p6,  // Sizes determined by size() in the build script
    int p1_dimension_parameters[], signed char p2_json_config[], int p3_size_data_out,    // Parameters: p1 - p3
    int p4_amount_para_out, int p5_dimension_input_signals[], int p6_split_signals[],     // Parameters: p4 - p6
    int p7_local_port, int p8_remote_port, signed char p9_remote_ip[], int p10_start_udp  // Parameters: p7 - p10
    )
    {

    #ifdef WITH_HW
        printf("Create: PaPIBlock (Embedded Coder)\n");
    #endif

    #ifndef WITH_HW
        printf("Create: PaPIBlock (Simulation)\n");
    #endif


    this->size_config = 0;
    this->stream_in_length = 0;
    this->output_was_init_with_zero = false;
    this->para_out_was_set = false;

    /* ******************************************
    *    Store information about UDP
    ******************************************* */
    this->local_port = p7_local_port;
    this->remote_port = p8_remote_port;

    /* ******************************************
    *    Store information about the parameters
    ****************************************** */
    this->amount_parameter = size_p1; // size_para_out;
    this->dimension_parameters = p1_dimension_parameters;
    this->size_output_parameters = p4_amount_para_out;

    this->offset_parameter = (int*) malloc(sizeof(int) * this->amount_parameter);

    int offset = 0;
    for (int i=0; i <this->amount_parameter; i++) {
        this->offset_parameter[i] = offset;
        offset += this->dimension_parameters[i];
    }

    /* ******************************************
    *    Store information about the data input stream
    ****************************************** */
    this->size_u1_vector = size_u1;
    this->dimension_inputs = p5_dimension_input_signals;

    this->amount_inputs = size_p5;
    this->split_signals = (int*) malloc(sizeof(int) * this->amount_inputs);

    for (int i=0; i<this->amount_inputs; i++)
    {
        if ( i < size_p6 ) {
            this->split_signals[i] = p6_split_signals[i];
        } else {
            this->split_signals[i] = 1;
        }
    }

    this->offset_input = (int*) malloc(sizeof(int) * this->amount_inputs);
    offset = 0;

    for (int i=0; i <this->amount_inputs; i++)
    {
        this->offset_input[i] = offset;
        offset += this->dimension_inputs[i];
    }

    /* ******************************************
    *   Store information about the data output stream
    ****************************************** */
    this->stream_out_size = 650;
    this->stream_out = new int[this->stream_out_size];
    this->amount_output = this->stream_out_size;

    this->sent_counter = START_MESSAGE_COUNTER;
    this->config_sent = false;
    this->parseBlockJsonConfig(p2_json_config);

    /* ******************************************
    *    Start thread: UDP
    ****************************************** */

    std::stringstream ss;

    for(int i=0;;i++) {
        ss << p9_remote_ip[i];
        if (p9_remote_ip[i] == '\0') {
            break;
        }
    }

    this->remote_ip = ss.str();
    this->local_ip  = "0.0.0.0";

    #ifdef WITH_HW
        this->createUDPServer();
        if (p10_start_udp) {
            this->startUDPServer();
        }
    #endif

}

PaPIBlock::~PaPIBlock() {
    #ifdef WITH_HW
        this->udphandle->stop();
    #endif
}

void PaPIBlock::createUDPServer() {
    this->udphandle = new UDPHandle(this->local_port, this->remote_port, this->local_ip, this->remote_ip);
    this->udphandle->otherHandleRecieve = boost::bind(&PaPIBlock::handleStream, this, _1, _2);
}

void PaPIBlock::startUDPServer() {

    this->udphandle->run();

}

void PaPIBlock::stopUDPServer() {
    this->udphandle->stop();
}


void PaPIBlock::parseBlockJsonConfig(signed char json_string[]) {
    Json::Value root;
    Json::Reader reader;
    std::string json_str;
    std::stringstream ss;

    for(int i=0;;i++) {
        ss << json_string[i];
        if (json_string[i] == '\0') {
            break;
        }

    }

    json_str = ss.str();
    //printf("String Parsed: %s \n", json_str.c_str());

    bool success = reader.parse(json_str, root, false);
    if (success) {
        cout << reader.getFormatedErrorMessages() << endl;
    } else {
        printf("Failed to parse json string \n");
    }

    this->blockJsonConfig = root;

}

void PaPIBlock::buildConfiguration(double para_out[]) {

    Json::Value blockConfig = this->blockJsonConfig["BlockConfig"];

    Json::Value parameterNames = blockConfig["ParameterNames"];
    Json::Value signalNames    =    blockConfig["SignalNames"];

    Json::Value papiConfig    =    this->blockJsonConfig["PaPIConfig"];

    Json::Value sourcesConfig;
    Json::Value parametersConfig;

    Json::StyledWriter styledWriter;
    std::stringstream ssConfig;

    std::string u_name;

    // ---------------------------------
    // Create signals
    // ---------------------------------
    int signal_count  = 0;
    for (int i=0; i<this->amount_inputs+1; i++) {

        Json::Value ui;

        std::stringstream ss;
        std::stringstream ssd;
        std::stringstream ssc;

        ss << i;

        std::string i_string =  ss.str();
        std::string d_string;
        std::string c_string;

        if (i < this->amount_inputs ) {

            if ( this->split_signals[i] ) {

                // -----------------------------------------------
                // Split current signal into d signals:
                // -----------------------------------------------
                int offset = i;

                // Create a single signal for each dimension
                for( int d=0; d<this->dimension_inputs[i]; d++ ) {
                    //Convert current string into a string
                    ssd << d;
                    d_string = ssd.str();

                    //Check if a name exists for this signal
                    if ( signal_count < signalNames.size() ) {
                        u_name = signalNames[signal_count].asString();
                    } else if (!signalNames.empty()) {
                        u_name = signalNames.asString();
                    }  else {
                        u_name = "s" + i_string + "(" +d_string + ")";
                    }

                    //Add signal to configuration
                    ui["SourceName"] = u_name;
                    ui["NValues_send"] = "1";
                    ui["datatype"]     = "257";

                    ssd.str("");
                    ssd.clear();

                    //Take signal_count as unique identifier
                    ssc << signal_count;
                    c_string = ssc.str();

                    sourcesConfig[c_string] = ui;
                    ssc.str("");
                    ssc.clear();
                    signal_count++;
                }
            } else {
                // -----------------------------------------------
                // Add current signal as multi dimensional vector:
                // -----------------------------------------------


                //This signal shoud be send as vector of size d
                int vector_size = this->dimension_inputs[i];
                ssd << vector_size;
                d_string = ssd.str();

                if ( signal_count < signalNames.size() ) {
                    u_name = signalNames[signal_count].asString();
                } else if (!signalNames.empty()) {
                    u_name = signalNames.asString();
                } else {
                    u_name = "s" + i_string + "(" +d_string + ")";
                }

                ui["SourceName"] = u_name;
                ui["NValues_send"] = d_string;
                ui["datatype"]     = "257";

                ssc << signal_count;
                c_string = ssc.str();

                sourcesConfig[c_string] = ui;
                ssc.str("");
                ssc.clear();

                signal_count++;

            }

        } else {
            //Add signal for time
            ssc << signal_count;
            c_string = ssc.str();

            ui["SourceName"] = "time";
            ui["NValues_send"] = "1";
            ui["datatype"]     = "257";

            sourcesConfig[c_string] = ui;
            ssc.str("");
            ssc.clear();
        }
    }

    // ---------------------------------
    // Create parameters
    // ---------------------------------
    for (int i=0; i<this->amount_parameter; i++) {

        Json::Value pi;

        std::stringstream ss;
        ss << i;
        std::string i_string = ss.str();
        if (i < parameterNames.size()) {
            u_name = parameterNames[i].asString();
        } else if (!parameterNames.empty()) {
            u_name = parameterNames.asString();
        }   else {
            u_name = "p" + ss.str();
        }
        pi["ParameterName"]   = u_name;
        pi["NValues"] = this->dimension_parameters[i];
        pi["datatype"]     = "257";

        pi["initial_value"]     = getInitialValueForParameter(para_out, i);
        parametersConfig[i_string] = pi;
    }

    // ---------------------------------
    // Create PaPI Config
    // ---------------------------------

    this->papiJsonConfig["SourcesConfig"] = sourcesConfig;
    this->papiJsonConfig["ParametersConfig"] = parametersConfig;

    if (papiConfig.empty()) {
        this->papiJsonConfig["PaPIConfig"] = "{}";
    } else {
        this->papiJsonConfig["PaPIConfig"] = papiConfig;
    }

    ssConfig << styledWriter.write(this->papiJsonConfig);
    std::string config  = ssConfig.str();
    config.erase(std::remove(config.begin(), config.end(), '\n'), config.end());
    //printf("%s", config.c_str());

    //printf("Config size=%zu\n", config.size() );
    this->config = config;
}

std::string PaPIBlock::getInitialValueForParameter(double para_out[], int pid) {

    if (pid < 0 or pid > this->amount_parameter) {
        return "0";
    }

    std::stringstream ss;
    double someValue = 0.0;

    if (this->dimension_parameters[pid] > 1) {
        ss << "[";
    }

    for (int i=0; i<this->dimension_parameters[pid];i++) {

        someValue = para_out[this->offset_parameter[pid] + i];
        if (someValue <  std::numeric_limits<double>::epsilon() &&
            someValue > -std::numeric_limits<double>::epsilon()) {
          someValue = 0.0;
        }

        ss << someValue;

        if (i < this->dimension_parameters[pid]-1) {
            ss << ",";
        }
    }

    if (this->dimension_parameters[pid] > 1) {
        ss << "]";
    }

    std::string init_value_string = ss.str().c_str();

    return init_value_string;

}

void PaPIBlock::setOutput(double u1[], double time, double y1_para_out[]) {

    this->para_out = y1_para_out;
    this->para_out_was_set = true;

    if (!this->output_was_init_with_zero) {
        this->initOutputWithZero(y1_para_out, this->size_output_parameters);
        this->output_was_init_with_zero = true;
    }

    this->mutex_stream_in.lock();
    if (this->stream_in_length > 0 ) {
        if (this->stream_in_length >= 1) {
            // Request for current configuration
            if (this->stream_in[2] == -3) {
                if (this->config_sent) {
                    this->buildConfiguration(this->para_out);
                }
                this->config_sent = false;
                this->data_to_sent = this->config.substr(0);
            }
            // if (this->stream_in[0] == 12) {
            //     this->setParaOut(y1_para_out);
            // }
        }
        this->stream_in_length = 0;
    }
    this->mutex_stream_in.unlock();


    //If still needed or requested, send current configuration
    if (!this->config_sent) {
        this->sendConfig(this->stream_out);
        this->udphandle->sendData(this->stream_out, (std::size_t) this->size_config);

    } else {

    //send current input data
        this->clearOutput(this->stream_out);
        this->sendInput(u1, time, this->stream_out);
        this->udphandle->sendData(this->stream_out, (std::size_t) this->amount_output);
    }



}

void PaPIBlock::setParaOut(double para_out[]) {

    struct para* p1 = (struct para*) this->stream_in.begin();

    double * dp = &p1->value;

    // printf("Constant: %d \n", p1->constant);
    // printf("Counter: %d \n", p1->counter);
    // printf("PID: %d \n", p1->pid);
    // printf("Value: %f \n", p1->value);


    /*
        Check if p1->pid is an valid value
    */

    if (p1->pid <0 or p1->pid > this->amount_parameter) {
        return;
    }

    for (int i=0; i<this->dimension_parameters[p1->pid];i++) {

        para_out[this->offset_parameter[p1->pid] + i] = dp[i];
    }
}

void PaPIBlock::reset(double para_out[]) {

    this->initOutputWithZero(para_out, this->size_output_parameters);
    this->buildConfiguration(para_out);

    this->config_sent = false;
    this->data_to_sent = this->config.substr(0);
}

void PaPIBlock::control(int control, double para_out[]){
    if (control == 1) {

        #ifdef _PAPI_BLOCK_DEBUG_
            printf("PaPIBlock::control::startUDPServer\n");
        #endif
        this->startUDPServer();
        this->reset(para_out);
    }

    if (control == 2) {
        #ifdef _PAPI_BLOCK_DEBUG_
            printf("PaPIBlock::control::stopUDPServer\n");
        #endif
        this->stopUDPServer();
    }

}


void PaPIBlock::clearOutput(int stream_out[]) {
    for (int i=0; i<this->amount_output;i++) {
        stream_out[i] = 0;
    }
}

void PaPIBlock::sendInput(double u1[], double sim_time, int stream_out[]) {

    int ui_offset = 0;
    int stream_offset = 4;
    int signal_count = 0;

    udouble data;

    //Mark as PaPI Data package
    stream_out[0] = 0;
    stream_out[1] = 0;
    stream_out[2] = -100;
    stream_out[3] = 0;


    // -----------------------------------------
    // Send current input vector
    // -----------------------------------------
    for (int i=0; i<this->amount_inputs;i++) {
        ui_offset = this->offset_input[i];

        // Send all splitted signals as a single signal
        if (1 == this->split_signals[i]) {
            for (int d=0; d<this->dimension_inputs[i];d++) {

                data.d = u1[ui_offset+d];

                stream_out[  stream_offset] = signal_count;
                stream_out[++stream_offset] = data.u;
                stream_out[++stream_offset] = data.u >> 32;

                stream_offset += 1;
                signal_count++;
            }
        } else {

            ui_offset = this->offset_input[i];

            stream_out[stream_offset+0] = signal_count;

            for (int d=0; d<this->dimension_inputs[i];d++) {


                data.d = u1[ui_offset+d];
                stream_out[++stream_offset] = data.u;
                stream_out[++stream_offset] = data.u >> 32;

            }
            stream_offset += 1;

            signal_count++;
        }
    }


    // -----------------------------------------
    // Send current timestamp
    // as an extra signal
    // -----------------------------------------
    data.d = sim_time;

    stream_out[stream_offset+0] = signal_count;
    stream_out[stream_offset+1] = data.u;
    stream_out[stream_offset+2] = data.u >> 32;

}

void PaPIBlock::handleStream(std::size_t bytes_transferred /*in bytes_transferred*/, boost::array<char, 8192> buffer) {

    this->mutex_stream_in.lock();

    //TODO: Aufrunden


    this->stream_in_length = (int) bytes_transferred / 4;

    std::memcpy(this->stream_in.begin(), buffer.begin(), bytes_transferred);

    if (this->stream_in_length >= 1) {
        // Request for current configuration
        if (12 == this->stream_in[0]) {
            if (this->para_out_was_set) {
                this->setParaOut(this->para_out);
    //                this->stream_in_length = 0;
            }
        }
    }

    this->mutex_stream_in.unlock();

}

void PaPIBlock::sendConfig(int stream_out[]) {

    this->size_config = 4;

    for (int i=0; i<this->amount_output;i++) {
        stream_out[i] = 0;
    }

    if (!this->config_sent) {

        stream_out[0] = 0;
        stream_out[1] = this->sent_counter;
        stream_out[2] = -4;
        stream_out[3] = 0;


        int output_count = 4;
        int shift = 0;
        char c;
        for (int i=0;;i++) {
            //printf("%c", c);
            if ( i % 4 == 0 and i > 1) {
                output_count ++;
                shift = 0;
            }

            if ( output_count > this->amount_output-1) {
                break;
            }

            if(this->data_to_sent.empty()) {
                c = ' ';

            } else {
                c = this->data_to_sent[0];
                std::string sub_data = this->data_to_sent.substr(1);
                this->data_to_sent = sub_data;
            }

            stream_out[output_count] = stream_out[output_count] | c << 8*shift;
            shift++;
        }

        if (this->data_to_sent.empty()) {
                this->config_sent = true;
                this->sent_counter = START_MESSAGE_COUNTER;
        } else {
            this->sent_counter ++;
            //printf("Still missing: %s \n", this->data_to_sent.c_str());
        }

        this->size_config = output_count;
    }
}

void PaPIBlock::initOutputWithZero(double para_out[], int amount_output) {
    for (int i=0; i<amount_output; i++) {
        para_out[i] = 0;
    }

}

//*************************************************
//**** Helper functions
//*************************************************

std::string intToString(int i) {
    std::stringstream ss;
    ss << i;
    std::string i_string = ss.str();

    return i_string;
}


//*************************************************
//**** Wrappers for methods called in Simulink ****
//*************************************************

void createPaPIBlock(
    void **work1, //Working vector
    int size_u1, int size_p1, int size_p2, int size_p5, int size_p6, // Sizes determined by size() in the build script
    int p1_dimension_parameters[], signed char p2_json_config[], int p3_size_data_out,    // Parameters: p1 - p3
    int p4_amount_para_out, int p5_dimension_input_signals[], int p6_split_signals[],     // Parameters: p4 - p6
    int p7_local_port, int p8_remote_port, signed char p9_remote_ip[], int p10_start_udp  // Parameters: p7 - p10
    )
    {

    *work1 = (void *) new PaPIBlock(
        size_u1, size_p1, size_p2, size_p5, size_p6,
        p1_dimension_parameters, p2_json_config, p3_size_data_out,
        p4_amount_para_out, p5_dimension_input_signals, p6_split_signals,
        p7_local_port, p8_remote_port, p9_remote_ip, p10_start_udp
        );
    PaPIBlock *madClass = (class PaPIBlock *) *work1;
}

void deletePaPIBlock(void **work1)
{
    PaPIBlock *madClass = (class PaPIBlock *) *work1;
    delete madClass;
}

void outputPaPIBlock(
    void **work1, double u1_data_in[], double u2_time, int u3_control,
    double y1_para_out[]
    )
    {

    PaPIBlock *madClass = (class PaPIBlock *) *work1;

    if (0 < u3_control) {
        madClass->control(u3_control, y1_para_out);
    }

    madClass->setOutput(u1_data_in, u2_time, y1_para_out);
}
