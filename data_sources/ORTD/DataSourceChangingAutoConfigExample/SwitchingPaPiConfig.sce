//
//    Copyright (C) 2011, 2012, 2013, 2014, 2015  Christian Klauer
//
//    This file is part of OpenRTDynamics, the Real-Time Dynamics Framework
//
//    OpenRTDynamics is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Lesser General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    OpenRTDynamics is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Lesser General Public License for more details.
//
//    You should have received a copy of the GNU Lesser General Public License
//    along with OpenRTDynamics.  If not, see <http://www.gnu.org/licenses/>.
//



// 
// 
//   Example for a changing PaPI-configuration, which is given by the ORTD-program.
//   The ORTD-program has several states, one to choose between two experiments,
//   one which evaluates the selection and two states with the different experiments.
//   In the first experiment an oscillator-system is given with a button to disturb it.
//   The second experiment shows a slider and the adjusted value is sent to the ORTD and
//   from there sent back to a LCD and a progress bar in PaPI. There is an additional
//   finish-state, which is normally not possible to be used.
// 
//   Rev 1
// 


funcprot(0);
// The name of the program
ProgramName = 'SwitchingPaPiConfig'; // must be the filename without .sce


function [sim, outlist] = AutoConfigExample(sim, Signal)

  function [sim, finished, outlist, userdata] = ExperimentCntrl(sim, ev, inlist, userdata, CalledOnline)

    // Define parameters. They must be defined once again at this place, because this will also be called at
    // runtime.
    NSamples=300;

    if CalledOnline == %t then
      // The contents of this part will be compiled on-line, while the control
      // system is running. The aim is to generate a new compiled schematic for
      // the experiment.
      // Please note: Since this code is only executed on-line, most potential errors 
      // occuring in this part become only visible during runtime.

      printf("Compiling a new control system\n");
      
      funcprot(0);
      z = poly(0,'z');
      // And example-system that is controlled via UDP and one step further with the Web-gui
      // Superblock: A more complex oscillator with damping
      function [sim, x,v] = damped_oscillator(sim, u, T_a)
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
      
      if userdata.isInitialised == %f then
        //
        // State variables can be initialise at this place
        //
        userdata.Acounter = 0;
        userdata.State = "chooseExp";
    
        userdata.isInitialised = %t; // prevent from initialising the variables once again
      end

      // 
      // Example for a state update: increase the counter
      // 
      userdata.Acounter = userdata.Acounter + 1;

      // Build an info-string
      SchematicInfo = "On-line compiled in iteration #" + string(userdata.Acounter);

      // 
      // Define a new experiment controller schematic depending on the currently active state
      // 
      
      // initalise the PaPi UDP Socket
      Configuration.UnderlyingProtocoll = "UDP";
      Configuration.DestHost = "127.0.0.1";
      Configuration.DestPort = 20000;
      Configuration.LocalSocketHost = "127.0.0.1";
      Configuration.LocalSocketPort = 20001;
      PacketFramework.Configuration.debugmode = %t;
      [sim, PacketFramework] = ld_PF_InitInstance(sim, InstanceName="SwitchingAutoConfig", Configuration);
  
      [sim, zero] = ld_const(sim, ev, 0);
      [sim, one] = ld_const(sim, 0, 1);

      // default output (dummy)
      outlist=list(zero);
      
      //
      // Here a state-machine is implemented that may be used to implement some automation
      // logic that is executed during runtime using the embedded Scilab interpreter.
      // In this example, a calibration run succeeded by the design/compilation/execution 
      // of a control-system is implemented. The schematics defined in each state are loaded
      // at runtime.
      // 
      select userdata.State
        case "chooseExp"
          // Add some parameters to choose the next state
          [PacketFramework, OscillatorButton] = ld_PF_addpluginAdvanced(PacketFramework, "Button", "Oscillator", "(250,100)", "(250,100)", "PaPI-Tab", list(["state1_text","Go to"], ["state2_text","Leaving to"]));
          [sim, PacketFramework, GoToOscillator]=ld_PF_ParameterInclControl(sim, PacketFramework, NValues=1, datatype=ORTD.DATATYPE_FLOAT, ParameterName="Osci", OscillatorButton, 'Click_Event');
          
          [PacketFramework, SliderLCDprogressbarButton] = ld_PF_addpluginAdvanced(PacketFramework, "Button", "Slider LCD ProgressBar", "(250,100)", "(250,250)", "PaPI-Tab", list(["state1_text","Go to"], ["state2_text","Leaving to"]));
          [sim, PacketFramework, GoToSliderLCDProgress]=ld_PF_ParameterInclControl(sim, PacketFramework, NValues=1, datatype=ORTD.DATATYPE_FLOAT, ParameterName="SliderLCDProgress", SliderLCDprogressbarButton, 'Click_Event');
          
          // finalise the communication interface
          [sim,PacketFramework] = ld_PF_Finalise(sim,PacketFramework);
          
          // finish if next state is chosen
          [sim, expState] = ld_add(sim, ev, list(GoToOscillator, GoToSliderLCDProgress), [1,2]);
          // write the next state on the first position of the global memory
          [sim] = ld_write_global_memory(sim, ev, data=expState, index=one, ...
                                         ident_str="NextStateData", datatype=ORTD.DATATYPE_FLOAT, ...
                                         ElementsToWrite=1);
          
          [sim, finished] = ld_and(sim, ev, list(expState, one));
          
          outlist=list(expState);
          [sim] = ld_printf(sim, ev, expState, "Case choose experiment active. Next Experiment is (0 means no change):", 1);
          // chose the next state to enter when the demo experiment has finished
          userdata.State = "choosedExp";
          
        case "choosedExp"
          printf("Got the following chosen experiment for iteration %d:\n", userdata.Acounter);  disp(userdata.InputData(1));
          [sim, nextExp] = ld_const(sim, ev, userdata.InputData(1));
          
          // finalise the communication interface
          [sim,PacketFramework] = ld_PF_Finalise(sim,PacketFramework);
          
          finished = one; // finish directly
          
          // chose the next state to enter when the demo experiment has finished
          select userdata.InputData(1)
          case 1
              userdata.State = "oscillator";
          case 2
              userdata.State = "sliderLCDprogressbar";
          else
              userdata.State = "finished";
          end
          
          outlist=list(nextExp);
          [sim] = ld_printf(sim, ev, nextExp, "Case choosed experiment active. Next Experiment is "+ userdata.State, 1);
          
        case "oscillator"  // define an experiment to perform an oscillator experiment
          in1 = inlist(1);
          [sim] = ld_printf(sim, 0, in1, "Case oscillator active: ", 1);

          // Add a parameter for controlling the oscillator
          [PacketFramework, DisturbanceButton] = ld_PF_addpluginAdvanced(PacketFramework, "Button", "Disturbancegrgrgrrgrgrgrgrggegerggeregeg", "(150,50)", "(600,100)", "PaPI-Tab", list(["state1_text","Disturb"], ["state2_text","Disturbing"]));
          [sim, PacketFramework, Input]=ld_PF_ParameterInclControl(sim, PacketFramework, NValues=1, datatype=ORTD.DATATYPE_FLOAT, ParameterName="Oscillator input", DisturbanceButton, 'Click_Event');
          
          // Add a button parameter to go to the experiment selection dialog
          [PacketFramework, OkButton] = ld_PF_addpluginAdvanced(PacketFramework, "Button", "Leaveergergergergerggegrggregegrgeegg", "(150,50)", "(600,325)", "PaPI-Tab", list(["state1_text","Ok"], ["state2_text","Leaving"]));
          [sim, PacketFramework, GoToChoose]=ld_PF_ParameterInclControl(sim, PacketFramework, NValues=1, datatype=ORTD.DATATYPE_FLOAT, ParameterName="ok", OkButton, 'Click_Event');

          // printf the parameter
          [sim] = ld_printf(sim, ev, Input, "Oscillator input ", 1);

          // The system to control
          [sim, Input] = ld_add_ofs(sim, 0, Input, 0.2);
          T_a = 0.1; [sim, x,v] = damped_oscillator(sim, Input, T_a);

          // Stream the data of the oscillator
          [PacketFramework, PlotXY] = ld_PF_addpluginAdvanced(PacketFramework, "Plot", "Plot XV", "(500,500)", "(0,0)", "PaPI-Tab", list(["yRange","[-10.0 10.0]"]));
          [sim, PacketFramework]=ld_SendPacketInclSub(sim, PacketFramework, Signal=x, NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="X", PlotXY, 'SourceGroup0');
          [sim, PacketFramework]=ld_SendPacketInclSub(sim, PacketFramework, Signal=v, NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="V", PlotXY, 'SourceGroup0');

          // finalise the communication interface
          [sim,PacketFramework] = ld_PF_Finalise(sim,PacketFramework);

          outlist=list(x);

          finished = GoToChoose;
          
          // chose the next state to enter when the demo experiment has finished
          userdata.State = "chooseExp";

        case "sliderLCDprogressbar" // design a constant signal to send to PaPi
          in1 = inlist(1);
          [sim] = ld_printf(sim, 0, in1, "Case sliderLCDprogressbar active: ", 1);
          
          // Add a button parameter to go to the experiment selection dialog
          [PacketFramework, OkButton] = ld_PF_addpluginAdvanced(PacketFramework, "Button", "Leave", "(150,50)", "(600,225)", "PaPI-Tab", list(["state1_text","Ok"], ["state2_text","Leaving"]));
          [sim, PacketFramework, GoToChoose]=ld_PF_ParameterInclControl(sim, PacketFramework, NValues=1, datatype=ORTD.DATATYPE_FLOAT, ParameterName="ok", OkButton, 'Click_Event');
          
          // Add a slider
          [PacketFramework, Slider] = ld_PF_addpluginAdvanced(PacketFramework, "Slider", "Slider Example", "(500,75)", "(50,50)", "PaPI-Tab", list(["step_count","101"], ["lower_bound","0.0"], ["upper_bound","1.0"]));
          [sim, PacketFramework, sliderValue]=ld_PF_ParameterInclControl(sim, PacketFramework, NValues=1, datatype=ORTD.DATATYPE_FLOAT, ParameterName="sliderVal", Slider, 'SliderBlock');
          
          // show the slider value on a progress bar
          [sim, percSliderValue] = ld_gain(sim, ev, sliderValue, 100);
          [PacketFramework, Pbar] = ld_PF_addpluginAdvanced(PacketFramework, "ProgressBar", "ProgressBar Example", "(500,75)", "(50,250)", "PaPI-Tab", list());
          [sim, PacketFramework]=ld_SendPacketInclSub(sim, PacketFramework, Signal=percSliderValue, NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="percent", Pbar, 'SourceGroup0');
          
          // show the slider value on a lcd display
          [PacketFramework, LCD] = ld_PF_addpluginAdvanced(PacketFramework, "LCDDisplay", "LCD Example", "(210,120)", "(195,450)", "PaPI-Tab", list(["updateFrequency","50"]));
          [sim, PacketFramework]=ld_SendPacketInclSub(sim, PacketFramework, Signal=sliderValue, NValues_send=1, datatype=ORTD.DATATYPE_FLOAT, SourceName="LCDVal", LCD, 'SourceGroup0');
          
          // finalise the communication interface
          [sim,PacketFramework] = ld_PF_Finalise(sim, PacketFramework);
          
          outlist=list(sliderValue);
          
          finished = GoToChoose;
          
          // chose the next state to enter when the demo experiment has finished
          userdata.State = "chooseExp";
          
        case "finished" // experiment finished - nothing to do
          in1 = inlist(1);
          [sim] = ld_printf(sim, ev, in1, "Case finished active" , 1);
          [sim, finished] = ld_const(sim, ev, 0); // never finish
          [sim, out] = ld_const(sim, 0, 5);
          outlist=list(out);
          
      end
    end // CalledOnline == %t

    // When RTmain.sce is executed, this part will be run. It may be used to define an initial experiment in advance to
    // the execution of the whole control system.
    if CalledOnline == %f then
      SchematicInfo = "Off-line compiled";

      // default output (dummy)
      [sim, out] = ld_const(sim, 0, 0);
      outlist=list(out);
      [sim, finished] = ld_steps2(sim, 0, activation_simsteps=10, values=[0,1] );
    end
    
  endfunction




  function [sim, outlist, HoldState, userdata] = whileComputing_example(sim, ev, inlist, CalibrationReturnVal, computation_finished, par);

	[sim, HoldState] = ld_const(sim, 0, 0);

	[sim] = ld_printf(sim, 0, HoldState, "calculating ... " , 1);

	// While the computation is running this is called regularly
	[sim, out] = ld_const(sim, ev, 0);
	outlist=list(out);
  endfunction


  function [sim, ToScilab, userdata] = PreScilabRun(sim, ev, par)
	userdata = par.userdata;

	// get the stored sensor data
	[sim, readI] = ld_const(sim, 0, 1); // start at index 1
	[sim, ToScilab] = ld_read_global_memory(sim, 0, index=readI, ident_str="NextStateData", ...
                                            datatype=ORTD.DATATYPE_FLOAT, ...
                                            ElementsToRead=1);
	//[sim, ToScilab] = ld_const(sim, ev, 0);
  endfunction


  // initialise a global memory for storing the next state
  [sim] = ld_global_memory(sim, ev, ident_str="NextStateData", ... 
                           datatype=ORTD.DATATYPE_FLOAT, len=1, ...
                           initial_data=[zeros(1,1)], ... 
                           visibility='global', useMutex=1);

  // Start the experiment
  ThreadPrioStruct.prio1=ORTD.ORTD_RT_NORMALTASK;
  ThreadPrioStruct.prio2=0, ThreadPrioStruct.cpu = -1;

  insizes=[1]; outsizes=[1];
  intypes=[ORTD.DATATYPE_FLOAT]; outtypes=[ORTD.DATATYPE_FLOAT];


  CallbackFns.experiment = ExperimentCntrl;
  CallbackFns.whileComputing = whileComputing_example;
  CallbackFns.PreScilabRun = PreScilabRun;

  // Please note ident_str must be unique.
  userdata = [];
  param.scilab_path = "BUILDIN_PATH";  
  [sim, finished, outlist, userdata] = ld_AutoOnlineExch_dev2(sim, 0, inlist=list(Signal), ...
                                                             insizes, outsizes, intypes, outtypes, ... 
                                                             ThreadPrioStruct, CallbackFns, ident_str="AutoConfigDemo", userdata, param);

  PacketFramework = userdata(1);
//   [sim] = ld_printf(sim, 0, finished, "State ", 1);
  
endfunction


// The main real-time thread
function [sim, outlist, userdata] = Thread_MainRT(sim, inlist, userdata)
  // This will run in a thread
  [sim, Tpause] = ld_const(sim, ev, 1/20);  // The sampling time that is constant at 20 Hz in this example
  [sim, out] = ld_ClockSync(sim, ev, in=Tpause); // synchronise this simulation

  //
  // Add you own control system here
  //

   // some dummy input to the state machine
  [sim,Signal] = ld_const(sim, 0, 0.4321);   

  [sim, outlist] = AutoConfigExample(sim, Signal);

  [sim] = ld_printf(sim, 0,  outlist(1)  , "output ", 1);


  outlist = list();
endfunction

// This is the main top level schematic
function [sim, outlist] = schematic_fn(sim, inlist)  

// 
// Create a thread that runs the control system
// 
   
        ThreadPrioStruct.prio1=ORTD.ORTD_RT_NORMALTASK; // or  ORTD.ORTD_RT_REALTIMETASK
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

