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


#define MAX_MESSAGE_LENGTH 50
#define START_MESSAGE_COUNTER 1
#define MAX_INPUT_LENGTH 8

#define QUOTE( x ) #x

using namespace std;

/***************************************/
/**** Class instance global storage ****/
/***************************************/

PaPIBlock *papiBlockVar;
//sudo apt-get install gedit-classbrowser3g-plugin
union udouble {
  double d;
  unsigned long u;
};

struct para {
    int constant;
    int counter;
    int pid;
    double value;
};


/**********************************/
/**** Class method definitions ****/
/**********************************/

PaPIBlock::PaPIBlock(
    int size_u1, int size_u2, int size_p1, int size_p2, int size_p5, int size_p6,  // Sizes determined by size() in the build script
    int p1_dimension_parameters[], signed char p2_json_config[], int p3_size_data_out, // Parameters: p1 - p3
    int p4_amount_para_out, int p5_dimension_input_signals[], int p6_split_signals[]   // Parameters: p4 - p5
    )
    {
    printf("Create: PaPIBlock \n");

    /* ******************************************
    *    Store information about the parameters
    ****************************************** */
    this->amount_parameter = p4_amount_para_out; // size_para_out;
    this->dimension_parameters = p1_dimension_parameters;
    this->size_output_parameters = size_p1;

    this->offset_parameter = (int*) malloc(sizeof(int) * this->amount_parameter);

    printf("Create: PaPIBlock 1 \n");

    int offset = 0;
    for (int i=0; i <this->amount_parameter; i++) {
        this->offset_parameter[i] = offset;
        offset += this->dimension_parameters[i];
    }

    printf("Create: PaPIBlock 2 \n");

    /* ******************************************
    *    Store information about the data input stream
    ****************************************** */


    this->size_u1_vector = size_u1;
    this->dimension_inputs = p5_dimension_input_signals;


    this->split_signals = (int*) malloc(sizeof(int) * this->amount_inputs);

    this->amount_inputs = size_p5;

    for (int i=0; i <this->amount_inputs; i++)
    {
        if ( i < size_p6 ) {
            this->split_signals[i] = p6_split_signals[i];
        } else {
            this->split_signals[i] = 1;
        }
    }

    printf("Create: PaPIBlock 3 \n");


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
    this->amount_output = p3_size_data_out;

    this->sent_counter = START_MESSAGE_COUNTER;
    this->config_sent = false;

    /*
    printf("Amount parameter %d \n", amount_para_out);

    printf("Size out parameters %d \n", this->size_output_parameters);

    for (int i=0; i<this->amount_parameter; i++){
        printf("Size(%d) = %d \n",i, this->dimension_parameters[i]);
    }
    */

    this->parseBlockJsonConfig(p2_json_config);


    /* ******************************************
    *    Start thread: UDP
    ****************************************** */

    this->udphandle = new UDPHandle();

    this->udphandle->otherHandler = boost::bind(&PaPIBlock::handleStream, this, _1, _2);

/*    this->udphandle->otherHandler = std::bind1st(
                                        std::mem_fun(&PaPIBlock::handleStream),
                                        this);
*/    this->udphandle->run();

    //this->buildConfiguration();
}

void PaPIBlock::parseBlockJsonConfig(signed char json_string[]) {
    Json::Value root;
    Json::Reader reader;


    //printf("JSon: String %s \n", json_string);


    std::string json_str;
    std::stringstream ss;

    for(int i=0;;i++) {

        ss << json_string[i];
        if (json_string[i] == '\0') {
            break;
        }

    }

    json_str = ss.str();

//    printf("String Parsed: %s \n", json_str.c_str());


    bool success = reader.parse(json_str, root, false);

    if (success) {
        cout << reader.getFormatedErrorMessages() << endl;
        printf("Parsed json string \n");
    } else {
        printf("Failed to parse json string \n");
    }

    this->blockJsonConfig = root;

    printf("Created: PaPIBlock END \n");

}

void PaPIBlock::buildConfiguration(double para_out[]) {
    printf("Build configuration\n");
    Json::Value blockConfig = this->blockJsonConfig["BlockConfig"];

    Json::Value parameterNames = blockConfig["ParameterNames"];
    Json::Value signalNames    =    blockConfig["SignalNames"];

    Json::Value papiConfig    =    this->blockJsonConfig["PaPIConfig"];

    Json::Value sourcesConfig;
    Json::Value parametersConfig;

    Json::StyledWriter styledWriter;
    std::stringstream ssConfig;

    std::string u_name;

    /*
    ssConfig << styledWriter.write(papiConfig);
    std::string str_papi = ssConfig.str();
    printf("PaPIConfig: %s \n", str_papi.c_str());
    ssConfig.clear();
    */

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
                    } else {
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

                printf("Send as vector : \n" );
                //This signal shoud be send as vector of size d
                int vector_size = this->dimension_inputs[i];
                ssd << vector_size;
                d_string = ssd.str();

                if ( signal_count < signalNames.size() ) {
                    u_name = signalNames[signal_count].asString();
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

                printf(" -----> %s\n", u_name.c_str() );
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
        //this->define_inputs[i]

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
        } else {
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

/*
    Json::Value papiConfig;
    Json::Value toCreate;
    Json::Value toSub;
    Json::Value toControl;


    papiConfig["ToCreate"] = toCreate;

    papiConfig["ToSub"]    = toSub;
    papiConfig["ToControl"] = toControl;
   */
    // ----------------


    this->papiJsonConfig["SourcesConfig"] = sourcesConfig;
    this->papiJsonConfig["ParametersConfig"] = parametersConfig;

    if (papiConfig.empty()) {
        this->papiJsonConfig["PaPIConfig"] = "{}";

/*        papiConfig = Json::Value();

        Json::Value toCreate;
        Json::Value toSub;
        Json::Value toControl;

        papiConfig["ToCreate"] = "{}";

        papiConfig["ToSub"]    = "{}";
        papiConfig["ToControl"] = toControl;
*/
    } else {
        this->papiJsonConfig["PaPIConfig"] = papiConfig;

    }


    // ----------------

    //Json::StyledWriter styledWriter;
    //std::stringstream ssConfig;
    ssConfig << styledWriter.write(this->papiJsonConfig);

    std::string config  = ssConfig.str();

    config.erase(std::remove(config.begin(), config.end(), '\n'), config.end());
    //printf("%s", config.c_str());
    this->config = config;
}

std::string PaPIBlock::getInitialValueForParameter(double para_out[], int pid) {

    if (pid <0 or pid > this->amount_parameter) {
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

        //printf("Double [%d] value: %f \n", i, para_out[i]);
    }

    if (this->dimension_parameters[pid] > 1) {
        ss << "]";
    }


    std::string init_value_string = ss.str().c_str();

    return init_value_string;

}

void PaPIBlock::setOutput(double u1[], int stream_in[], int msg_length, double time, int stream_out[], double para_out[]) {

    //TODO: Temporary solution
    this->y2_para_out = para_out;

    if (msg_length > 0 ) {

        if (msg_length >= 1) {
            // Request for current configuration
            if (stream_in[2] == -3) {

                if (this->config_sent) {
                    this->buildConfiguration(para_out);
                }

                this->config_sent = false;
                this->data_to_sent = this->config.substr(0);
            }

            if (stream_in[0] == 12) {
                this->setParaOut(stream_in, msg_length, para_out);
            }
        }

    }

    //If still needed or requested, send current configuration
    if (!this->config_sent) {
        this->sendConfig(stream_out);
    } else {


    //send current input data
        this->clearOutput(stream_out);
        this->sendInput(u1, time, stream_out);
    }

}

void PaPIBlock::setParaOut(int stream_in[], int msg_length, double para_out[]) {

    struct para* p1 = (struct para*) stream_in;

    double * dp = &p1->value;

    /*
    printf("Msg Length %d \n", msg_length);


    printf("Constant: %d \n", p1->constant);
    */
    /*
    printf("PID: %d \n", p1->pid);

    printf("Size parameters: %d \n", this->dimension_parameters[p1->pid]);

    printf("Double pointer: %f \n", dp[0]);
    */
    /*

    printf("Counter: %d \n", p1->counter);
    printf("Value: %f \n", p1->value);
    */

    /*
        Check if p1->pid is an valid value
    */

    if (p1->pid <0 or p1->pid > this->amount_parameter) {
        return;
    }

    for (int i=0; i<this->dimension_parameters[p1->pid];i++) {

        //printf("Double [%d] value: %f at offset=%d \n", i, dp[i],this->offset_parameter[p1->pid] + i);

        para_out[this->offset_parameter[p1->pid] + i] = dp[i];
    }


//    para_out[p1->pid] = p1->value;

}

void PaPIBlock::reset(double para_out[]) {

    for (int i=0; i<this->size_output_parameters; i++) {
        para_out[i] = 0;
    }


    this->buildConfiguration(para_out);


    this->config_sent = false;
    this->data_to_sent = this->config.substr(0);
}

void PaPIBlock::clearOutput(int stream_out[]) {
    //printf("Clear output '\n");

    for (int i=0; i<this->amount_output;i++) {
        stream_out[i] = 0;
    }

}

void PaPIBlock::sendInput(double u1[], double sim_time, int stream_out[]) {


    //Mark as PaPI Data package
    stream_out[0] = 0;
    stream_out[1] = 0;
    stream_out[2] = -100;
    stream_out[3] = 0;

    int ui_offset = 0;
    int stream_offset = 4;

    int signal_count = 0;

    udouble data;

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

//                printf("-> stream_out[%d]\n", stream_offset);

                stream_out[++stream_offset] = data.u;
                stream_out[++stream_offset] = data.u >> 32;

//                stream_offset += 2;

            }
            stream_offset += 1;

            signal_count++;
        }
    }


    // -----------------------------------------
    // Send current timestamp
    // -----------------------------------------
    data.d = sim_time;

    stream_out[stream_offset+0] = signal_count;
    stream_out[stream_offset+1] = data.u;
    stream_out[stream_offset+2] = data.u >> 32;

    // for (int i=0; i<26;++i) {
    //     printf("stream_out[%d]=%d\n", i, stream_out[i] );
    // }
    //
    //
    // printf("size(stream_out)=%d, stream_offset=%d\n", this->amount_output, stream_offset );

    return;

    for (int i=0; i<this->size_u1_vector+1;i++) {

        stream_offset = 3*i+3+1;

        if (stream_offset+3 >= this->amount_output) {
            printf("Can't sent next input due to limitation of the output length. \n");
        }

        //printf("Input[%d]=%f \n", i, u1[i]);

        if (i<this->size_u1_vector) {
            data.d = u1[i];
        }   else {
            data.d = sim_time;
        }

        stream_out[stream_offset+0] = i;
        stream_out[stream_offset+1] = data.u;
        stream_out[stream_offset+2] = data.u >> 32;

        //printf("i=%d, %f offset=%d \n", i, data.d, offset);

    }

    //At last, set time

}

void PaPIBlock::handleStream(std::size_t msg_length, boost::array<int, 8192> buffer) {
    printf("PaPIBlock::handleStream[msg_length=%zu]\n", msg_length);

    int* stream_in = buffer.data();

    if (msg_length > 0 ) {

        if (msg_length >= 1) {
            // Request for current configuration
            if (stream_in[2] == -3) {

                if (this->config_sent) {
                    this->buildConfiguration(this->y2_para_out);
                }

                this->config_sent = false;
                this->data_to_sent = this->config.substr(0);
            }

            if (buffer[0] == 12) {
                this->setParaOut(stream_in, msg_length, this->y2_para_out);
            }
        }

    }
}

void PaPIBlock::sendConfig(int stream_out[]) {


    //Set current output to zero

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
                printf("Sent current configuration \n");
                this->config_sent = true;
                this->sent_counter = START_MESSAGE_COUNTER;

        } else {
            this->sent_counter ++;

            //printf("Still missing: %s \n", this->data_to_sent.c_str());
        }
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
    int size_u1, int size_u2, int size_p1, int size_p2, int size_p5, int size_p6,  // Sizes determined by size() in the build script
    int p1_dimension_parameters[], signed char p2_json_config[], int p3_size_data_out, // Parameters: p1 - p3
    int p4_amount_para_out, int p5_dimension_input_signals[], int p6_split_signals[]   // Parameters: p4 - p5
)
    {

    *work1 = (void *) new PaPIBlock(
        size_u1, size_u2, size_p1, size_p2, size_p5, size_p6,
        p1_dimension_parameters, p2_json_config, p3_size_data_out,
        p4_amount_para_out, p5_dimension_input_signals, p6_split_signals
        );
    PaPIBlock *madClass = (class PaPIBlock *) *work1;

	//papiBlockVar = new PaPIBlock(size_data_in, size_stream_in, size_stream_out, size_para_out, amount_para_out, json_string, size_json_string, size_output_parameters);
}

void deletePaPIBlock(void **work1)
{
    PaPIBlock *madClass = (class PaPIBlock *) *work1;
    delete madClass;
}

void outputPaPIBlock(
    void **work1, double u1_data_in[], int u2_stream_in[],
    int u3_msg_length, double u4_time, int u5_reset_event, int y1_stream_out[],
    double y2_para_out[])
    {

    PaPIBlock *madClass = (class PaPIBlock *) *work1;

    if (u5_reset_event) {
        printf("Resent configuration and set output to zero");
        madClass->reset(y2_para_out);
    }
    madClass->setOutput(u1_data_in,u2_stream_in,u3_msg_length,u4_time, y1_stream_out, y2_para_out);
}
