// 
// 
// This a template for writing real-time applications using OpenRTDynamics
// (openrtdynamics.sf.net)
// 
//
// 


// The name of the program
ProgramName = 'template'; // must be the filename without .sce

//
// 


// The main real-time thread
function [sim, outlist, userdata] = Thread_MainRT(sim, inlist, userdata)
  // This will run in a thread
  [sim, Tpause] = ld_const(sim, ev, 1/27);  // The sampling time that is constant at 27 Hz in this example
  [sim, out] = ld_ClockSync(sim, ev, in=Tpause); // synchronise this simulation

  // print the time interval
  [sim] = ld_printf(sim, ev, Tpause, "Time interval [s]", 1);

//
  // remote control interface
  Configuration.UnderlyingProtocoll = "UDP";
  Configuration.DestHost = "127.0.0.1";
  Configuration.DestPort = 20000;
  Configuration.LocalSocketHost = "127.0.0.1";
  Configuration.LocalSocketPort = 20001;
  PacketFramework.Configuration.debugmode = %t;
  [sim, PacketFramework] = ld_PF_InitInstance(sim, InstanceName="RemoteControl1", Configuration)


  [sim, PacketFramework, WindowShift]=ld_PF_Parameter(sim, PacketFramework, NValues=1, datatype=ORTD.DATATYPE_FLOAT, ParameterName="WindowShift");
  [sim] = ld_printf(sim, ev, WindowShift, "WindowShift", 1);



  // constants
  [sim, zero] = ld_const(sim, 0, 0.0);

//     // Read the input files
//     EMGveclen = 100; // change
//     [sim, EMGNumdata] = ld_ReadAsciiFile(sim, 0, fname="source/cable_virtual.txt", veclen=1);
//     [sim, rawEMG] = ld_ReadAsciiFile(sim, 0, fname="source/rawEMG.dat", veclen=EMGveclen);


    EMGveclen = 200; // change
    [sim, EMGNumdata] = ld_ReadAsciiFile(sim, 0, fname="source/SampleEMGData/emg_numdata.dat", veclen=1);
    [sim, rawEMG] = ld_ReadAsciiFile(sim, 0, fname="source/SampleEMGData/saved_vector_1.dat", veclen=EMGveclen);

  //  
  // EMG - Filter configured for 4k measurements
  //

 

  [par] = ParSet_eemg_filter4A('PhysioSenseBipolar'); // Create default parameter set

  [sim, lambda, InnerSignals] = eemg_filter4A(sim, ev, emgvector=rawEMG, EMGNumdata, measurement_path="dest/", par); // V4A
      


  // cut out a window (StimIndex-5 : StimIndex+10 + 40) to show the M-wave
//   [sim,wndstart] = ld_add_ofs(sim, ev, InnerSignals.StimIndex, ofs=WindowShift);
  VisualisationWndLen = 100;
  [sim,wndstart] = ld_add(sim, 0, list(InnerSignals.StimIndex, WindowShift), [1,-1]);
  [sim,MwaveAndStim] = ld_vector_extract(sim, ev, in=InnerSignals.emgvector, from=wndstart, window_len=VisualisationWndLen, vecsize=EMGveclen);


  [sim] = ld_printf(sim, ev, lambda, "lambda", 1);




  // Send dataa to the GUI
  [sim, PacketFramework]=ld_SendPacket(sim, PacketFramework, Signal=lambda, NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="lambda")
  [sim, PacketFramework]=ld_SendPacket(sim, PacketFramework, Signal=InnerSignals.stim_index_clean, NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="stim_index_clean")
  [sim, PacketFramework]=ld_SendPacket(sim, PacketFramework, Signal=rawEMG, NValues_send=EMGveclen, datatype=ORTD.DATATYPE_FLOAT, SourceName="rawEMG")
  [sim, PacketFramework]=ld_SendPacket(sim, PacketFramework, Signal=MwaveAndStim, NValues_send=VisualisationWndLen, datatype=ORTD.DATATYPE_FLOAT, SourceName="MwaveAndStim")


  
   [sim,PacketFramework] = ld_PF_Finalise(sim,PacketFramework);
   ld_PF_Export_js(PacketFramework, fname="ProtocollConfig.json");



//   // save the absolute time into a file
//   [sim, time] = ld_clock(sim, ev);
//   [sim] = ld_savefile(sim, ev, fname="AbsoluteTime.dat", source=time, vlen=1);


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
       

//    NOTE: for rt_preempt real-time you can use e.g. the following parameters:
// 
//         // Create a RT thread on CPU 0:
//         ThreadPrioStruct.prio1=ORTD.ORTD_RT_REALTIMETASK; // rt_preempt FIFO scheduler
//         ThreadPrioStruct.prio2=50; // Highest priority
//         ThreadPrioStruct.cpu = 0; // CPU 0


   // output of schematic (empty)
   outlist = list();
endfunction

  








//
// Set-up (no detailed understanding necessary)
//

thispath = get_absolute_file_path(ProgramName+'.sce');
cd(thispath);
z = poly(0,'z');


exec('emgfilter.sce');
//exec('webinterface/PacketFramework.sce');



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


