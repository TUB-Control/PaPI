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

PaPIBlock::PaPIBlock(int size_data_in,int size_stream_in, int size_stream_out, int size_para_out[], int amount_para_out, signed char json_string[], int size_json_string, int size_output_parameters) {
    printf("Create: PaPIBlock \n");

    /* ******************************************
    *    Store information about the parameters
    ****************************************** */
    this->amount_parameter = amount_para_out; // size_para_out;
    this->size_parameter = size_para_out;
    this->size_output_parameters = size_output_parameters;

    this->offset_parameter = (int*) malloc(sizeof(int) * this->amount_parameter);

    int offset = 0;
    for (int i=0; i <this->amount_parameter; i++) {

        //printf("Offset parameter[%d] %d \n", i, offset);

        this->offset_parameter[i] = offset;
        offset += this->size_parameter[i];

    }

    /* ******************************************
    *    Store information about the data input stream
    ****************************************** */
    this->amount_input = size_data_in;

    /* ******************************************
    *   Store information about the data output stream
    ****************************************** */
    this->amount_output = size_stream_out;

    
    this->sent_counter = START_MESSAGE_COUNTER;
    this->config_sent = false;

    /*
    printf("Amount parameter %d \n", amount_para_out);

    printf("Size out parameters %d \n", this->size_output_parameters);

    for (int i=0; i<this->amount_parameter; i++){
        printf("Size(%d) = %d \n",i, this->size_parameter[i]);
    }
    */

    this->parseBlockJsonConfig(json_string);

    //this->buildConfiguration();
}

void PaPIBlock::parseBlockJsonConfig(signed char json_string[]) {
    Json::Value root;
    Json::Reader reader;

    
    //printf("JSon: String %s \n", json_string);

   // const char *c = json_string;

    std::string json_str;
    std::stringstream ss;
   // signed char c;
    //const char c1 = '{';
    //json_str.append(json_string[0]);

    for(int i=0;;i++) {
        
        //const char c = (const char) json_string[i];
       
        ss << json_string[i];
   //     printf("Stream %s " , ss.str().c_str());
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

}

void PaPIBlock::buildConfiguration(double para_out[]) {
    Json::Value blockConfig = this->blockJsonConfig["BlockConfig"];

    Json::Value parameterNames = blockConfig["ParameterNames"];
    Json::Value signalNames    =    blockConfig["SignalNames"];

    Json::Value papiConfig    =    this->blockJsonConfig["PaPIConfig"];

    /* Create Inputs */
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

    for (int i=0; i<this->amount_input+1; i++) {
        
        Json::Value ui;

        std::stringstream ss;
        ss << i;
        std::string i_string =  ss.str();

        if (i < this->amount_input) {

            if (i < signalNames.size()) {
                u_name = signalNames[i].asString();
                
            } else {
                u_name = "u" + i_string;
            }
            ui["SourceName"]   = u_name;
        } else {
            ui["SourceName"]   = "time";
        }
        ui["NValues_send"] = "1";
        ui["datatype"]     = "257";
    
        sourcesConfig[i_string] = ui;
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
        pi["NValues"] = this->size_parameter[i];
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
    printf("%s", config.c_str());
    this->config = config;
}

std::string PaPIBlock::getInitialValueForParameter(double para_out[], int pid) {

    if (pid <0 or pid > this->amount_parameter) {
        return "0";
    }

    std::stringstream ss;
    double someValue = 0.0;

    if (this->size_parameter[pid] > 1) {
        ss << "[";
    }

    for (int i=0; i<this->size_parameter[pid];i++) {

        someValue = para_out[this->offset_parameter[pid] + i];

        if (someValue <  std::numeric_limits<double>::epsilon() && 
            someValue > -std::numeric_limits<double>::epsilon()) {
          someValue = 0.0;
        }

        ss << someValue;

        if (i < this->size_parameter[pid]-1) {
            ss << ",";
        }




        printf("Double [%d] value: %f \n", i, para_out[i]);


    }

    if (this->size_parameter[pid] > 1) {
        ss << "]";
    }


    std::string init_value_string = ss.str().c_str();

    return init_value_string;


    if (pid >= 1)
        return "[1,2]";

    return "1";


}

void PaPIBlock::setOutput(double u1[], int stream_in[], int msg_length, double time, int stream_out[], double para_out[]) {
    
    
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


    printf("Msg Length %d \n", msg_length);
    /*

    printf("Constant: %d \n", p1->constant);
    */


    printf("Size parameters: %d \n", this->size_parameter[p1->pid]);

    printf("Double pointer: %f \n", dp[0]);
    
    printf("PID: %d \n", p1->pid);
    printf("Counter: %d \n", p1->counter);
    printf("Value: %f \n", p1->value);


    /*
        Check if p1->pid is an valid value
    */

    if (p1->pid <0 or p1->pid > this->amount_parameter) {
        return;
    }

    for (int i=0; i<this->size_parameter[p1->pid];i++) {

        printf("Double [%d] value: %f \n", i, dp[i]);

        para_out[this->offset_parameter[p1->pid] + i] = dp[i];
    }
        

//    para_out[p1->pid] = p1->value;
   
}

void PaPIBlock::clearOutput(int stream_out[]) {
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

    int offset = 0;

    udouble data;

    for (int i=0; i<this->amount_input+1;i++) {

        offset = 3*i+3+1;

        if (offset+3 >= this->amount_output) {
            printf("Can't sent next input due to limitation of the output length. \n");
        }

        //printf("Input[%d]=%f \n", i, u1[i]);

        if (i<this->amount_input) {        
            data.d = u1[i];
        }   else {
            data.d = sim_time;
        }
       
        stream_out[offset+0] = i;
        stream_out[offset+1] = data.u;
        stream_out[offset+2] = data.u >> 32;
    
        //printf("i=%d, %f offset=%d \n", i, data.d, offset);
        
    }

    //At last, set time

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
//**** Wrappers for methods called in Simulink ****
//*************************************************

void createPaPIBlock(void **work1, int size_data_in, int size_stream_in, int size_stream_out, int size_para_out[], int amount_para_out, signed char json_string[], int size_json_string, int size_output_parameters) {
    
    *work1 = (void *) new PaPIBlock(size_data_in, size_stream_in, size_stream_out, size_para_out, amount_para_out, json_string, size_json_string, size_output_parameters);

    PaPIBlock *madClass = (class PaPIBlock *) *work1;

	//papiBlockVar = new PaPIBlock(size_data_in, size_stream_in, size_stream_out, size_para_out, amount_para_out, json_string, size_json_string, size_output_parameters);
}

void deletePaPIBlock(void **work1) {

    PaPIBlock *madClass = (class PaPIBlock *) *work1;
    delete madClass;
}

void outputPaPIBlock(void **work1, double u1[], int stream_in[], int msg_length, double time, int stream_out[], double para_out[]) {

    PaPIBlock *madClass = (class PaPIBlock *) *work1;
    madClass->setOutput(u1,stream_in,msg_length,time,stream_out, para_out);

}
