// 
// 
//   Example for a communication interface from ORTD using UDP datagrams to e.g.
//   nodejs. 
//   The file webinterface/webappUDP.js is the counterpart that provides a 
//   web-interface to control a oscillator-system in this example.
//   
//   For more details, please consider the readme-file.
// 
//   Rev 1
// 

// The name of the program
ProgramName = 'UDPio'; // must be the filename without .sce















// 
// 
//   A packet based communication interface from ORTD using UDP datagrams to e.g.
//   nodejs. 
//   webappUDP.js is the counterpart that provides a web-interface 
// 
// Current Rev: 8
// 
// Revisions:
// 
// 27.3.14 - possibility to reservate sources
// 3.4.14  - small re-arrangements
// 4.4.14  - Bugfixes
// 7.4.14  - Bugfix
// 12.6.14 - Bugfix
// 2.11.14 - Added group finalising packet
// 


function [PacketFramework,SourceID] = ld_PF_addsource(PacketFramework, NValues_send, datatype, SourceName)
  SourceID = PacketFramework.SourceID_counter;

  Source.SourceName = SourceName;
  Source.SourceID = SourceID;
  Source.NValues_send = NValues_send;
  Source.datatype =  datatype;
  
  // Add new source to the list
  PacketFramework.Sources($+1) = Source;
  
  // inc counter
  PacketFramework.SourceID_counter = PacketFramework.SourceID_counter + 1;
endfunction

function [PacketFramework,ParameterID,MemoryOfs] = ld_PF_addparameter(PacketFramework, NValues, datatype, ParameterName)
  ParameterID = PacketFramework.Parameterid_counter;

  Parameter.ParameterName = ParameterName;
  Parameter.ParameterID = ParameterID;
  Parameter.NValues = NValues;
  Parameter.datatype =  datatype;
  Parameter.MemoryOfs = PacketFramework.ParameterMemOfs_counter;
  
  // Add new source to the list
  PacketFramework.Parameters($+1) = Parameter;
  
  // inc counters
  PacketFramework.Parameterid_counter = PacketFramework.Parameterid_counter + 1;
  PacketFramework.ParameterMemOfs_counter = PacketFramework.ParameterMemOfs_counter + NValues;

  // return values
  ParameterID = Parameter.ParameterID; 
  MemoryOfs = Parameter.MemoryOfs;
endfunction

function [sim, PacketFramework, Parameter] = ld_PF_Parameter(sim, PacketFramework, NValues, datatype, ParameterName) // PARSEDOCU_BLOCK
// 
// Define a parameter
// 
// NValues - amount of data sets
// datatype - only ORTD.DATATYPE_FLOAT for now
// ParameterName - a unique string decribing the parameter
// 
// 
// 

    [PacketFramework,ParameterID,MemoryOfs] = ld_PF_addparameter(PacketFramework, NValues, datatype, ParameterName);
   
    // read data from global memory
    [sim, readI] = ld_const(sim, 0, MemoryOfs); // start at index 1
    [sim, Parameter] = ld_read_global_memory(sim, 0, index=readI, ident_str=PacketFramework.InstanceName+"Memory", ...
						datatype, NValues);
endfunction




// Send a signal via UDP, a simple protocoll is defined, internal function
function [sim] = ld_PF_ISendUDP(sim, PacketFramework, Signal, NValues_send, datatype, SourceID)
  InstanceName = PacketFramework.InstanceName;
  [sim,one] = ld_const(sim, 0, 1);

  // Packet counter, so the order of the network packages can be determined
  [sim, Counter] = ld_modcounter(sim, 0, in=one, initial_count=0, mod=100000);
  [sim, Counter_int32] = ld_ceilInt32(sim, 0, Counter);

  // Source ID
  [sim, SourceID] = ld_const(sim, 0, SourceID);
  [sim, SourceID_int32] = ld_ceilInt32(sim, 0, SourceID);

  // Sender ID
  [sim, SenderID] = ld_const(sim, 0, PacketFramework.SenderID); // random number
  [sim, SenderID_int32] = ld_ceilInt32(sim, 0, SenderID);

  // make a binary structure
  [sim, Data, NBytes] = ld_ConcateData(sim, 0, ...
			inlist=list(SenderID_int32, Counter_int32, SourceID_int32, Signal ), insizes=[1,1,1,NValues_send], ...
			intypes=[ ORTD.DATATYPE_INT32, ORTD.DATATYPE_INT32, ORTD.DATATYPE_INT32, datatype ] );

  printf("The size of the UDP-packets will be %d bytes.\n", NBytes);

  // send to the network 
  [sim, NBytes__] = ld_constvecInt32(sim, 0, vec=NBytes); // the number of bytes that are actually send is dynamic, but must be smaller or equal to 
  [sim] = ld_UDPSocket_SendTo(sim, 0, SendSize=NBytes__, ObjectIdentifyer=InstanceName+"aSocket", ...
			      hostname=PacketFramework.Configuration.DestHost, ...
                              UDPPort=PacketFramework.Configuration.DestPort, in=Data, ...
			      insize=NBytes);

endfunction




function [sim, PacketFramework] = ld_SendPacket(sim, PacketFramework, Signal, NValues_send, datatype, SourceName) // PARSEDOCU_BLOCK // PARSEDOCU_BLOCK
// 
// Stream data - block
// 
// Signal - the signal to stream
// NValues_send - the vector length of Signal
// datatype - only ORTD.DATATYPE_FLOAT by now
// SourceName - a unique string identifier descring the stream
// 
// 
// 

  [PacketFramework,SourceID] = ld_PF_addsource(PacketFramework, NValues_send, datatype, SourceName);
  [sim]=ld_PF_ISendUDP(sim, PacketFramework, Signal, NValues_send, datatype, SourceID);
endfunction




function [sim, PacketFramework] = ld_PF_InitInstance2(sim, InstanceName, Configuration) // PARSEDOCU_BLOCK
// 
// Initialise an instance of the Packet Framework
//   
// InstanceName - a unique string identifier for the instance
// Configuration must include the following properties:
// 
//   Configuration.UnderlyingProtocoll = "UDP"
//   Configuration.DestHost
//   Configuration.DestPort
//   Configuration.LocalSocketHost
//   Configuration.LocalSocketPort
// 
// 
// Example:
// 
// 
//   Configuration.UnderlyingProtocoll = "UDP";
//   Configuration.DestHost = "127.0.0.1";
//   Configuration.DestPort = 20000;
//   Configuration.LocalSocketHost = "127.0.0.1";
//   Configuration.LocalSocketPort = 20001;
//   [sim, PacketFramework] = ld_PF_InitInstance(sim, InstanceName="UDPCommunication", Configuration);
// 
// 
// 
// Also consider the file webappUDP.js as the counterpart that communicates to ORTD-simulations
// 
// 

  // initialise structure for sources
  PacketFramework.InstanceName = InstanceName;
  PacketFramework.Configuration = Configuration;

  PacketFramework.Configuration.debugmode = %F;

//   disp(Configuration.UnderlyingProtocoll)

  if Configuration.UnderlyingProtocoll == 'UDP'
    null;
  else
    error("PacketFramework: Only UDP supported up to now");
  end

  // possible packet sizes for UDP
  PacketFramework.TotalElemetsPerPacket = floor((1400-3*4)/8); // number of doubles values that fit into one UDP-packet with maximal size of 1400 bytes
  PacketFramework.PacketSize = PacketFramework.TotalElemetsPerPacket*8 + 3*4;

  // sources
  PacketFramework.SourceID_counter = 0;
  PacketFramework.Sources = list();
  
  // parameters
  PacketFramework.Parameterid_counter = 0;
  PacketFramework.ParameterMemOfs_counter = 1; // start at the first index in the memory
  PacketFramework.Parameters = list();
  
  PacketFramework.SenderID = 1295793;
  
  // Groups
  DefaultGroup.ID = 0;
  
  PacketFramework.GroupIdCounter = 1;
  PacketFramework.GroupList = list();
  PacketFramework.ActiveGroup = DefaultGroup;
  
endfunction


// added 23.12.14
function [sim, PacketFramework, Group] = ld_PF_NewGroup(sim, PacketFramework, GroupName, opt)
    
  Group.ID = PacketFramework.GroupIdCounter;
  Group.Name = GroupName;

  PacketFramework.GroupIdCounter = PacketFramework.GroupIdCounter + 1;
  PacketFramework.GroupList( PacketFramework.GroupIdCounter ) = Group;
endfunction

// added 23.12.14
function [sim, PacketFramework] = ld_PF_FinishGroup(sim, PacketFramework, Group)
  [sim] = ld_PF_SendGroupFinshUDP(sim, PacketFramework, Group.ID);
endfunction

// added 23.12.14
function [sim, PacketFramework] = ld_PF_SetActiveGroup(sim, PacketFramework, Group)
  PacketFramework.ActiveGroup = Group;
endfunction


// Send a signal via UDP, a simple protocoll is defined, internal function
function [sim] = ld_PF_SendGroupFinshUDP(sim, PacketFramework, GroupID)
  InstanceName = PacketFramework.InstanceName;
  [sim,one] = ld_const(sim, 0, 1);

  // Packet counter, so the order of the network packages can be determined
  [sim, Counter] = ld_modcounter(sim, 0, in=one, initial_count=0, mod=100000);
  [sim, Counter_int32] = ld_ceilInt32(sim, 0, Counter);

  // Source ID
  [sim, SourceID] = ld_const(sim, 0, -1);                   // -1 means finish a group of sources
  [sim, SourceID_int32] = ld_ceilInt32(sim, 0, SourceID);

  // Group ID
  [sim, GroupID_] = ld_const(sim, 0, GroupID);                   // -1 means finish a group of sources
  [sim, GroupID_int32] = ld_ceilInt32(sim, 0, GroupID_);

  // Sender ID
  [sim, SenderID] = ld_const(sim, 0, PacketFramework.SenderID); // random number
  [sim, SenderID_int32] = ld_ceilInt32(sim, 0, SenderID);

  // make a binary structure
  [sim, Data, NBytes] = ld_ConcateData(sim, 0, ...
			inlist=list(SenderID_int32, Counter_int32, SourceID_int32, GroupID_int32 ), insizes=[1,1,1,1], ...
			intypes=[ ORTD.DATATYPE_INT32, ORTD.DATATYPE_INT32, ORTD.DATATYPE_INT32, ORTD.DATATYPE_INT32 ] );

//  printf("The size of the UDP-packets will be %d bytes.\n", NBytes);

  // send to the network 
  [sim, NBytes__] = ld_constvecInt32(sim, 0, vec=NBytes); // the number of bytes that are actually send is dynamic, but must be smaller or equal to 
  [sim] = ld_UDPSocket_SendTo(sim, 0, SendSize=NBytes__, ObjectIdentifyer=InstanceName+"aSocket", ...
			      hostname=PacketFramework.Configuration.DestHost, ...
                              UDPPort=PacketFramework.Configuration.DestPort, in=Data, ...
			      insize=NBytes);


  // [sim] = ld_printf(sim, ev, GroupID_, "Sent finish packet ", 1);
endfunction

function [sim,PacketFramework] = ld_PF_Finalise(sim,PacketFramework) // PARSEDOCU_BLOCK
// 
// Finalise the instance.
// 
// 

      // The main real-time thread
      function [sim] = ld_PF_InitUDP(sim, InstanceName, ParameterMemory)

	  function [sim, outlist, userdata] = UDPReceiverThread(sim, inlist, userdata)
	    // This will run in a thread. Each time a UDP-packet is received 
	    // one simulation step is performed. Herein, the packet is parsed
	    // and the contained parameters are stored into a memory.

	    // Sync the simulation to incomming UDP-packets
	    [sim, Data, SrcAddr] = ld_UDPSocket_Recv(sim, 0, ObjectIdentifyer=InstanceName+"aSocket", outsize=PacketSize );

	    // disassemble packet's structure
	    [sim, DisAsm] = ld_DisassembleData(sim, 0, in=Data, ...
				  outsizes=[1,1,1,TotalElemetsPerPacket], ...
				  outtypes=[ ORTD.DATATYPE_INT32, ORTD.DATATYPE_INT32, ORTD.DATATYPE_INT32, ORTD.DATATYPE_FLOAT ] );



            DisAsm_ = list();
            DisAsm_(4) = DisAsm(4);
	    [sim, DisAsm_(1)] = ld_Int32ToFloat(sim, 0, DisAsm(1) );
	    [sim, DisAsm_(2)] = ld_Int32ToFloat(sim, 0, DisAsm(2) );
	    [sim, DisAsm_(3)] = ld_Int32ToFloat(sim, 0, DisAsm(3) );


            [sim, memofs] = ld_ArrayInt32(sim, 0, array=ParameterMemory.MemoryOfs, in=DisAsm(3) );
            [sim, Nelements] = ld_ArrayInt32(sim, 0, array=ParameterMemory.Sizes, in=DisAsm(3) );

 	    [sim, memofs_] = ld_Int32ToFloat(sim, 0, memofs );
 	    [sim, Nelements_] = ld_Int32ToFloat(sim, 0, Nelements );

            if PacketFramework.Configuration.debugmode then 
	      // print the contents of the packet
	      [sim] = ld_printf(sim, 0, DisAsm_(1), "DisAsm(1) (SenderID)       = ", 1);
	      [sim] = ld_printf(sim, 0, DisAsm_(2), "DisAsm(2) (Packet Counter) = ", 1);
	      [sim] = ld_printf(sim, 0, DisAsm_(3), "DisAsm(3) (SourceID)       = ", 1);
	      [sim] = ld_printf(sim, 0, DisAsm_(4), "DisAsm(4) (Signal)         = ", TotalElemetsPerPacket);

	      [sim] = ld_printf(sim, 0, memofs_ ,  "memofs                    = ", 1);
	      [sim] = ld_printf(sim, 0, memofs_ ,  "Nelements                 = ", 1);
            end

	    // Store the input data into a shared memory
	    [sim] = ld_WriteMemory2(sim, 0, data=DisAsm(4), index=memofs, ElementsToWrite=Nelements, ...
					  ident_str=InstanceName+"Memory", datatype=ORTD.DATATYPE_FLOAT, MaxElements=TotalElemetsPerPacket );



	    // output of schematic
	    outlist = list();
	  endfunction

	
	
	// start the node.js service from the subfolder webinterface
	//[sim, out] = ld_startproc2(sim, 0, exepath="./webappUDP.sh", chpwd="webinterface", prio=0, whentorun=0);
	
        TotalMemorySize = sum(PacketFramework.ParameterMemory.Sizes);
        TotalElemetsPerPacket = PacketFramework.TotalElemetsPerPacket; // number of doubles values that fit into one UDP-packet with maximal size of 1400 bytes
        PacketSize = PacketFramework.PacketSize;

	// Open an UDP-Port in server mode
	[sim] = ld_UDPSocket_shObj(sim, 0, ObjectIdentifyer=InstanceName+"aSocket", Visibility=0, ...
                                  hostname=PacketFramework.Configuration.LocalSocketHost, ...
                                  UDPPort=PacketFramework.Configuration.LocalSocketPort);

	// initialise a global memory for storing the input data for the computation
	[sim] = ld_global_memory(sim, 0, ident_str=InstanceName+"Memory", ... 
				datatype=ORTD.DATATYPE_FLOAT, len=TotalMemorySize, ...
				initial_data=[zeros(TotalMemorySize,1)], ... 
				visibility='global', useMutex=1);

	// Create thread for the receiver
	ThreadPrioStruct.prio1=ORTD.ORTD_RT_NORMALTASK, ThreadPrioStruct.prio2=0, ThreadPrioStruct.cpu = -1;
	[sim, startcalc] = ld_const(sim, 0, 1); // triggers your computation during each time step
	[sim, outlist, computation_finished] = ld_async_simulation(sim, 0, ...
			      inlist=list(), ...
			      insizes=[], outsizes=[], ...
			      intypes=[], outtypes=[], ...
			      nested_fn = UDPReceiverThread, ...
			      TriggerSignal=startcalc, name=InstanceName+"Thread1", ...
			      ThreadPrioStruct, userdata=list() );


      endfunction





  // calc memory
  MemoryOfs = [];
  Sizes = [];
  // go through all parameters and create memories for all
  for i=1:length(PacketFramework.Parameters)
     P = PacketFramework.Parameters(i);

     Sizes = [Sizes; P.NValues];
     MemoryOfs = [MemoryOfs; P.MemoryOfs];
  end
  
  PacketFramework.ParameterMemory.MemoryOfs = MemoryOfs;
  PacketFramework.ParameterMemory.Sizes = Sizes;

  // udp
  [sim] = ld_PF_InitUDP(sim, PacketFramework.InstanceName, PacketFramework.ParameterMemory);
  
  // Send to group update notifications for each group (currently only one possible)
  [sim] = ld_PF_SendGroupFinshUDP(sim, PacketFramework, GroupID=0);
  
endfunction

function ld_PF_Export_js(PacketFramework, fname) // PARSEDOCU_BLOCK
// 
// Export configuration of the defined protocoll (Sources, Parameters) 
// into JSON-format. This is to be used by software that shall communicate 
// to the real-time system.
// 
// fname - The file name
// 
// 


   fd = mopen(fname,'wt');
  
   mfprintf(fd,' {""SourcesConfig"" : {\n');

  for i=1:length(PacketFramework.Sources)
    
    
    SourceID = PacketFramework.Sources(i).SourceID;
    SourceName =  PacketFramework.Sources(i).SourceName;
    disp(SourceID );
    disp( SourceName );
      
      
     line=sprintf(" ""%s"" : { ""SourceName"" : ""%s"" , ""NValues_send"" : ""%s"", ""datatype"" : ""%s""  } \n", ...
               string(PacketFramework.Sources(i).SourceID), ...
               string(PacketFramework.Sources(i).SourceName), ...
               string(PacketFramework.Sources(i).NValues_send), ...
               string(PacketFramework.Sources(i).datatype) );
      
     
     if i==length(PacketFramework.Sources)
       // finalise the last entry without ","
       printf('%s \n' , line);
       mfprintf(fd,'%s', line);
     else
       printf('%s, \n' , line);
       mfprintf(fd,'%s,', line);
     end
    

  end
  
  

  
   mfprintf(fd,'} , \n ""ParametersConfig"" : {\n');
   
  // go through all parameters and create memories for all
  for i=1:length(PacketFramework.Parameters)
        
    printf("export of parameter %s \n",PacketFramework.Parameters(i).ParameterName );

     line=sprintf(" ""%s"" : { ""ParameterName"" : ""%s"" , ""NValues"" : ""%s"", ""datatype"" : ""%s""  } \n", ...
               string(PacketFramework.Parameters(i).ParameterID), ...
               string(PacketFramework.Parameters(i).ParameterName), ...
               string(PacketFramework.Parameters(i).NValues), ...
               string(PacketFramework.Parameters(i).datatype) );
      
     
     if i==length(PacketFramework.Parameters) 
       // finalise the last entry without ","
       printf('%s \n' , line);
       mfprintf(fd,'%s', line);
     else
       printf('%s, \n' , line);
       mfprintf(fd,'%s,', line);
     end
    
    
  end  
  
  mfprintf(fd,'}\n}');
  
  mclose(fd);
endfunction

// 
// Added 27.3.14
// 

function [sim, PacketFramework, SourceID]=ld_SendPacketReserve(sim, PacketFramework, NValues_send, datatype, SourceName)
  [PacketFramework,SourceID] = ld_PF_addsource(PacketFramework, NValues_send, datatype, SourceName);
endfunction

function [sim, PacketFramework]=ld_SendPacket2(sim, PacketFramework, Signal, SourceName)
  // find Sourcename
  index  = -1;
  for i=1:length(PacketFramework.Sources)
    S = PacketFramework.Sources(i);
    if S.SourceName == SourceName
      index = i;
      printf(" %s found at index %d Nvalues %d\n", SourceName, index, S.NValues_send);
      break;
    end
  end

  if index == -1
    printf("SourceName = %s\n", SourceName);
    error("SourceName not found! This source must be reservated using ld_SendPacketReserve");
  end

  [sim]=ld_PF_ISendUDP(sim, PacketFramework, Signal, S.NValues_send, S.datatype, S.SourceID);
endfunction



function [sim, PacketFramework, ParameterID]=ld_PF_ParameterReserve(sim, PacketFramework, NValues, datatype, ParameterName)
    [PacketFramework,ParameterID,MemoryOfs] = ld_PF_addparameter(PacketFramework, NValues, datatype, ParameterName);   
endfunction


function [sim, PacketFramework, Parameter]=ld_PF_Parameter2(sim, PacketFramework, ParameterName)
  // find Sourcename
  index  = -1;
  for i=1:length(PacketFramework.Parameters)
    P = PacketFramework.Parameters(i);
    if P.ParameterName == ParameterName
      index = i;
      printf(" %s found at index %d Nvalues %d\n", ParameterName, index, P.NValues);
      break;
    end
  end

  if index == -1
    printf("ParameterName = %s\n", ParameterName);
    error("ParameterName not found! This source must be reservated using ld_PF_ParameterReserve");
  end
   
  // read data from global memory
  [sim, readI] = ld_const(sim, 0, P.MemoryOfs); // start at index 1
  [sim, Parameter] = ld_read_global_memory(sim, 0, index=readI, ident_str=PacketFramework.InstanceName+"Memory", ...
                                           P.datatype, P.NValues);
endfunction












// And example-system that is controlled via UDP and one step further with the Web-gui
// Superblock: A more complex oscillator with damping
function [sim, x,v] = damped_oscillator(sim, u)
    // create feedback signals
    [sim,x_feedback] = libdyn_new_feedback(sim);

        [sim,v_feedback] = libdyn_new_feedback(sim);

            // use this as a normal signal
            [sim,a] = ld_add(sim, ev, list(u, x_feedback), [1, -1]);
            [sim,a] = ld_add(sim, ev, list(a, v_feedback), [1, -1]);
    
            [sim,v] = ld_ztf(sim, ev, a, 1/(z-1) * T_a ); // Integrator approximation
    
            // feedback gain
            [sim,v_gain] = ld_gain(sim, ev, v, 0.1);
    
            // close loop v_gain = v_feedback
        [sim] = libdyn_close_loop(sim, v_gain, v_feedback);
    
    
        [sim,x] = ld_ztf(sim, ev, v, 1/(z-1) * T_a ); // Integrator approximation  
    
        // feedback gain
        [sim,x_gain] = ld_gain(sim, ev, x, 0.6);
    
    // close loop x_gain = x_feedback
    [sim] = libdyn_close_loop(sim, x_gain, x_feedback);
endfunction






function [sim, outlist, active_state, x_global_kp1, userdata] = state_mainfn(sim, inlist, x_global, state, statename, userdata)
  // This function is called multiple times -- once to define each state.
  // At runtime, all states will become different nested simulations of 
  // which only one is active a a time. Switching
  // between them represents state changing, thus each simulation 
  // represents a certain state.
  
  PacketFramework = userdata(1);
  
  printf("Defining state %s (#%d) ...\n", statename, state);
  
  // define names for the first event in the simulation
  events = 0;
  

  // demultiplex x_global that is a state variable shared among the different states
  [sim, x_global] = ld_demux(sim, events, vecsize=4, invec=x_global);


  // The signals "active_state" is used to indicate state switching: A value > 0 means the 
  // the state enumed by "active_state" shall be activated in the next time step.
  // A value less or equal to zero causes the statemachine to stay in its currently active
  // state

  select state
    case 1 // state 1

  [sim, PacketFramework, Group2] = ld_PF_NewGroup(sim, PacketFramework, GroupName="G1", opt=list() );
  [sim, PacketFramework]=ld_PF_SetActiveGroup(sim, PacketFramework, Group2);

    [sim, PacketFramework]=ld_SendPacket(sim, PacketFramework, Signal=x_global(1), NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="Counter");
  
  [sim, PacketFramework]=ld_PF_FinishGroup(sim, PacketFramework, Group2);

   [sim] = ld_printf(sim, ev, x_global(1), "--- ", 1);

      // wait 10 simulation steps and then switch to state 2
      [sim, active_state] = ld_steps(sim, events, activation_simsteps=[10], values=[-1,2]); // -1 means stay within this state. 2 means go to state # 2
      [sim, x_global(1)] = ld_add_ofs(sim, events, x_global(1), 1); // increase counter 1 by 1
    case 2 // state 2
      // wait 10 simulation steps and then switch to state 3
      [sim, active_state] = ld_steps(sim, events, activation_simsteps=[10], values=[-1,3]);
      [sim, x_global(2)] = ld_add_ofs(sim, events, x_global(2), 1); // increase counter 2 by 1
    case 3 // state 3
      // wait 10 simulation steps and then switch to state 1
      [sim, active_state] = ld_steps(sim, events, activation_simsteps=[10], values=[-1,1]);
      [sim, x_global(3)] = ld_add_ofs(sim, events, x_global(3), 1); // increase counter 3 by 1
  end

  // multiplex the new global states
  [sim, x_global_kp1] = ld_mux(sim, events, vecsize=4, inlist=x_global);
  
  userdata(1) = PacketFramework;
  
  // the user defined output signals of this nested simulation
  outlist = list();
endfunction


// The main real-time thread
function [sim, outlist, userdata] = Thread_MainRT(sim, inlist, userdata)
  // This will run in a thread
  [sim, Tpause] = ld_const(sim, ev, 1/27);  // The sampling time that is constant at 20 Hz in this example
  [sim, out] = ld_ClockSync(sim, ev, in=Tpause); // synchronise this simulation

  //
  // Add you own control system here
  //


   Configuration.UnderlyingProtocoll = "UDP";
   Configuration.DestHost = "127.0.0.1";
   Configuration.DestPort = 20000;
   Configuration.LocalSocketHost = "127.0.0.1";
   Configuration.LocalSocketPort = 20001;
   PacketFramework.Configuration.debugmode = %t;
   [sim, PacketFramework] = ld_PF_InitInstance2(sim, InstanceName="RemoteControl", Configuration);

   // Add a parameter for controlling the oscillator
   [sim, PacketFramework, Input]=ld_PF_Parameter(sim, PacketFramework, NValues=1, datatype=ORTD.DATATYPE_FLOAT, ParameterName="Oscillator input");

   // some some more parameters
   [sim, PacketFramework, AParVector]=ld_PF_Parameter(sim, PacketFramework, NValues=10, datatype=ORTD.DATATYPE_FLOAT, ParameterName="A vectorial parameter");
   [sim, PacketFramework, par2]=ld_PF_Parameter(sim, PacketFramework, NValues=2, datatype=ORTD.DATATYPE_FLOAT, ParameterName="Test");

   // printf these parameters
   [sim] = ld_printf(sim, ev, Input, "Oscillator input ", 1);
   [sim] = ld_printf(sim, ev, par2, "Test ", 2);
   [sim] = ld_printf(sim, ev, AParVector, "A vectorial parameter", 10);





  // The system to control
  T_a = 0.1; [sim, x,v] = damped_oscillator(sim, Input);


  // Stream the data of the oscillator
  [sim, PacketFramework, Group1] = ld_PF_NewGroup(sim, PacketFramework, GroupName="G1", opt=list() );
  [sim, PacketFramework]=ld_PF_SetActiveGroup(sim, PacketFramework, Group1);
  
    [sim, PacketFramework]=ld_SendPacket(sim, PacketFramework, Signal=x, NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="X")
    [sim, PacketFramework]=ld_SendPacket(sim, PacketFramework, Signal=v, NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="V")
  
  [sim, PacketFramework]=ld_PF_FinishGroup(sim, PacketFramework, Group1);




  // set-up three states represented by three nested simulations
  [sim, outlist, x_global, active_state,userdata] = ld_statemachine(sim, 0, ...
      inlist=list( x, v ), ..
      insizes=[1,1], outsizes=[], ... 
      intypes=[ORTD.DATATYPE_FLOAT,ORTD.DATATYPE_FLOAT  ], outtypes=[], ...
      nested_fn=state_mainfn, Nstates=3, state_names_list=list("state1", "state2", "state3"), ...
      inittial_state=3, x0_global=[1,0,2,0], userdata=list( PacketFramework )  );

   PacketFramework = userdata(1);


  // finalise the communication interface
  [sim,PacketFramework] = ld_PF_Finalise(sim,PacketFramework);
  ld_PF_Export_js(PacketFramework, fname="ProtocollConfig.json");


  outlist = list();
endfunction




// This is the main top level schematic
function [sim, outlist] = schematic_fn(sim, inlist)  

// 
// Create a thread that runs the control system
// 
   
        ThreadPrioStruct.prio1=ORTD.ORTD_RT_NORMALTASK; // or  ORTD.ORTD_RT_NORMALTASK
        ThreadPrioStruct.prio2=0; // for ORTD.ORTD_RT_REALTIMETASK: 1-99 as described in   man sched_setscheduler
                                  // for ORTD.ORTD_RT_NORMALTASK this is the nice-value (higher value means less priority)
        ThreadPrioStruct.cpu = -1; // The CPU on which the thread will run; -1 dynamically assigns to a CPU, 
                                   // counting of the CPUs starts at 0

        [sim, StartThread] = ld_initimpuls(sim, ev); // triggers your computation only once
        [sim, outlist, computation_finished] = ld_async_simulation(sim, ev, ...
                              inlist=list(), ...
                              insizes=[], outsizes=[], ...
                              intypes=[], outtypes=[], ...
                              nested_fn = Thread_MainRT, ...
                              TriggerSignal=StartThread, name="MainRealtimeThread", ...
                              ThreadPrioStruct, userdata=list() );
       
   // output of schematic (empty)
   outlist = list();
endfunction

  



//
// Set-up (no detailed understanding necessary)
//

thispath = get_absolute_file_path(ProgramName+'.sce');
cd(thispath);
z = poly(0,'z');


// The following code is integrated into ORTD since rev 494.
// Thus the following line is commented.

exec('webinterface/PacketFramework.sce');



// defile ev
ev = [0]; // main event

// set-up schematic by calling the user defined function "schematic_fn"
insizes = []; outsizes=[];
[sim_container_irpar, sim]=libdyn_setup_schematic(schematic_fn, insizes, outsizes);

// pack the simulation into a irpar container
parlist = new_irparam_set();
parlist = new_irparam_container(parlist, sim_container_irpar, 901); // pack simulations into irpar container with id = 901
par = combine_irparam(parlist); // complete irparam set
save_irparam(par, ProgramName+'.ipar', ProgramName+'.rpar'); // Save the schematic to disk

// clear
par.ipar = []; par.rpar = [];


