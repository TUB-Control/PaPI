 
//     Uses OpenRTDynamics to run
// http://openrtdynamics.sourceforge.net/bigace/

SchematicName = 'RunFilter'; // must be the filename without .sce
thispath = get_absolute_file_path(SchematicName+'.sce');
cd(thispath);

z = poly(0,'z');


EMGveclen = 100; // change


Nsamples = length( fscanfMat( "source/buf_size.dat" ) );
// Nsamples = 110;

//
// Set up simulation schematic
//
exec('emgfilter.sce');




// This is the main top level schematic
function [sim, outlist] = schematic_fn(sim, inlist)
  // this is the default event
  ev = 0;

 // if (1==1)   
    // BIPOLAR
    // Read the input files
    [sim, EMGNumdata] = ld_ReadAsciiFile(sim, 0, fname="source/cable_virtual.txt", veclen=1);
    [sim, rawEMG] = ld_ReadAsciiFile(sim, 0, fname="source/rawEMG.dat", veclen=EMGveclen);
  //lse
  
  
  //////////////////////////////////////////////////////////////////////////////////////////////////
    // UNIPOLAR
    // Read the input files
    [sim, EMGNumdata] = ld_ReadAsciiFile(sim, 0, fname="source/buf_size.dat", veclen=1);
    [sim, rawEMG_1] = ld_ReadAsciiFile(sim, 0, fname="source/cable1.dat", veclen=EMGveclen);
    [sim, rawEMG_2] = ld_ReadAsciiFile(sim, 0, fname="source/cable2.dat", veclen=EMGveclen);

    // implement  rawEMG = rawEMG_1 - rawEMG_2
    [sim, tmp] = ld_vector_gain(sim, 0, rawEMG_2, gain=-1, vecsize=EMGveclen);
    [sim, rawEMG] = ld_vector_add(sim, 0, rawEMG_1, tmp, vecsize=EMGveclen);
  //end
  
//     rawEMG = rawEMG_1;
    
    
    
    [sim, rawEMG] = ld_ReadAsciiFile(sim, 0, fname="source/cable_virtual.txt", veclen=EMGveclen);

  // print out the readings
  [sim] = ld_printf(sim, 0, EMGNumdata, "EMGNumdata = ", 1);
//   [sim] = ld_printf(sim, 0, rawEMG, "rawEMG = ", EMGveclen);
  
  
  // constants
  [sim, zero] = ld_const(sim, 0, 0.0);



  //  
  // EMG - Filter configured for 2k measurements
  //

  // Model for the stimulation artifact. the length of this must be even!
  par.CorrModel = [0.0,0.5,1,0.5]; // Use this if unipolar stimulation pulses are observed
//   par.CorrModel = [-1,-1,1,1];  // Use this if bipolar stimulation pulses are observed (normal case!)


                             // the window to perform the final abs(sum(       )) of.
  par.wndstart_ofs = 8;     //        
                             // The window starts from the position of the stimulation artifact plus par.wndstart_ofs
  par.WindowLen = 40;        // window length
                             
  
  par.CalcMeanNsamples = 4;  // amount of samples to calculate a mean at the beginning of the emg-vetor:  mean( emgvector(1:par.CalcMeanNsamples) )
  par.StimMuteOfs = -4;      // start muting at the found stim index minus par.StimMuteOfs
  par.StimMuteLength = 12;   // mute length of the muting of the stim artifact

  par.DebugActive = %T;      // show some information on the filter state in real-time
  par.WriteFiles = %F;       // write some internal signals of the filter into files denoted by measurement_path

  a_lp = 0.0;  a_hp = 0.4;       H =(1 - (1-a_hp)/(z-a_hp) )  * z*(1-a_lp)/(z-a_lp) ;  

  [sim, lambda] = eemg_filter4A(sim, ev, emgvector=rawEMG, EMGNumdata, measurement_path="dest/", H, EMGveclen, par); // V4A
      
  // print the results  
  [sim] = ld_printf(sim, 0, lambda, "lambda1 = ", 1);

  // save the signal
  [sim] = ld_savefile(sim, ev, fname="dest/lambda1.dat", source=lambda, vlen=1);

  //  
  // END of EMG - Filter
  //


  outlist = list(); // Simulation output (empty)
endfunction


  
//
// Set-up
//

// defile events
defaultevents = [0]; // main event

// set-up schematic by calling the user defined function "schematic_fn"
insizes = []; outsizes=[];
[sim_container_irpar, sim]=libdyn_setup_schematic(schematic_fn, insizes, outsizes);



//
// Save the schematic to disk (possibly with other ones or other irpar elements)
//

parlist = new_irparam_set();

// pack simulations into irpar container with id = 901
parlist = new_irparam_container(parlist, sim_container_irpar, 901);

// irparam set is complete convert
par = combine_irparam(parlist);

// save vectors to a file
save_irparam(par, SchematicName+'.ipar', SchematicName+'.rpar');

// clear
par.ipar = [];
par.rpar = [];



// 
// // optionally execute
// messages=unix_g(ORTD.ortd_executable+ ' -s '+SchematicName+' -i 901 -l 100');
printf("Run the following command from the directory %s\n", pwd() );
// printf('ortd -s '+SchematicName+' -i 901 -l ' + string( Nsamples ) + '\n');
// printf(ORTD.ortd_executable+ ' -s '+SchematicName+' -i 901 -l ' + string( Nsamples ) + '\n');

//
//// load results
//A = fscanfMat('result.dat');
//
//scf(1);clf;
//plot(A(:,1), 'k');

