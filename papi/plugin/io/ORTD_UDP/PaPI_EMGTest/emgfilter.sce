



// // 
// // Sample to for using the lambda filter using physiosense 4k-sampling
// // 

//   //
//   // EMG - Filter
//   //
// 
//   // Model for the stimulation artifact. the length of this must be even!
//   //par.CorrModel = [0.0,0.5,1,0.5]; // Use this if unipolar stimulation pulses are observed
//   par.CorrModel = [-1,-1,1,1];  // Use this if bipolar stimulation pulses are observed (normal case!)
// 
//                              // the window to perform the final abs(sum(       )) of.
//   par.wndstart_ofs = 10;     //        
//                              // The window starts from the position of the stimulation artifact plus par.wndstart_ofs
//   par.WindowLen = 40;        // window length
//                              
//   
//   par.CalcMeanNsamples = 10; // amount of samples to calculate a mean at the beginning of the emg-vetor:  mean( emgvector(1:par.CalcMeanNsamples) )
//   par.StimMuteOfs = -5;      // start muting at the found stim index minus par.StimMuteOfs
//   par.StimMuteLength = 15;   // mute length of the muting of the stim artifact
// 
//   par.DebugActive = %T;      // show some information on the filter state in real-time
//   par.WriteFiles = %F;       // write some internal signals of the filter into files denoted by measurement_path
// 
//   a_lp = 0.0;  a_hp = 0.4;       H =(1 - (1-a_hp)/(z-a_hp) )  * z*(1-a_lp)/(z-a_lp) ;  
// 
//   [sim, lambda] = eemg_filter4A(sim, ev, emgvector=rawEMG, EMGNumdata, measurement_path="dest/", H, EMGveclen, par); // V4A
// 
// 




//   //  
//   // EMG - Filter configured for 2k measurements e.g. the TMSI device
//   //

// 
//   // Model for the stimulation artifact. the length of this must be even!
//   //par.CorrModel = [0.0,0.5,1,0.5]; // Use this if unipolar stimulation pulses are observed
//   par.CorrModel = [-1,-1,1,1];  // Use this if bipolar stimulation pulses are observed (normal case!)
// 
// 
//                              // the window to perform the final abs(sum(       )) of.
//   par.wndstart_ofs = 8;     //        
//                              // The window starts from the position of the stimulation artifact plus par.wndstart_ofs
//   par.WindowLen = 40;        // window length
//                              
//   
//   par.CalcMeanNsamples = 4;  // amount of samples to calculate a mean at the beginning of the emg-vetor:  mean( emgvector(1:par.CalcMeanNsamples) )
//   par.StimMuteOfs = -4;      // start muting at the found stim index minus par.StimMuteOfs
//   par.StimMuteLength = 12;   // mute length of the muting of the stim artifact
// 
//   par.DebugActive = %T;      // show some information on the filter state in real-time
//   par.WriteFiles = %F;       // write some internal signals of the filter into files denoted by measurement_path
// 
//   a_lp = 0.0;  a_hp = 0.4;       H =(1 - (1-a_hp)/(z-a_hp) )  * z*(1-a_lp)/(z-a_lp) ;  
// 
//   [sim, lambda] = eemg_filter4A(sim, ev, emgvector=rawEMG, EMGNumdata, measurement_path="dest/", H, EMGveclen, par); // V4A
// 


function [par] = ParSet_eemg_filter4A(configStr)
// Generate some default configuration for the eemg filter

  select configStr
    case 'PhysioSenseBipolar'

      par.vecsize = EMGveclen;
      par.CorrModel = [-1,-1,1,1];  // Use this if bipolar stimulation pulses are observed (normal case!)

				// the window to perform the final abs(sum(       )) of.
      par.wndstart_ofs = 10;     //        
				// The window starts from the position of the stimulation artifact plus par.wndstart_ofs
      par.WindowLen = 40;        // window length
				      
      par.CalcMeanNsamples = 10; // amount of samples to calculate a mean at the beginning of the emg-vetor:  mean( emgvector(1:par.CalcMeanNsamples) )
      par.StimMuteOfs = -5;      // start muting at the found stim index minus par.StimMuteOfs
      par.StimMuteLength = 15;   // mute length of the muting of the stim artifact

      par.DebugActive = %T;      // show some information on the filter state in real-time
      par.WriteFiles = %F;       // write some internal signals of the filter into files denoted by measurement_path

      a_lp = 0.0;  a_hp = 0.4;       par.H =(1 - (1-a_hp)/(z-a_hp) )  * z*(1-a_lp)/(z-a_lp) ;  


    case 'TMSIUnipolar'

      // Model for the stimulation artifact. the length of this must be even!
      par.CorrModel = [0.0,0.5,1,0.5]; // Use this if unipolar stimulation pulses are observed
				// the window to perform the final abs(sum(       )) of.
      par.wndstart_ofs = 8;     //        
				// The window starts from the position of the stimulation artifact plus par.wndstart_ofs
      par.WindowLen = 40;        // window length
				
      
      par.CalcMeanNsamples = 4;  // amount of samples to calculate a mean at the beginning of the emg-vetor:  mean( emgvector(1:par.CalcMeanNsamples) )
      par.StimMuteOfs = -4;      // start muting at the found stim index minus par.StimMuteOfs
      par.StimMuteLength = 12;   // mute length of the muting of the stim artifact

      par.DebugActive = %T;      // show some information on the filter state in real-time
      par.WriteFiles = %F;       // write some internal signals of the filter into files denoted by measurement_path

      a_lp = 0.0;  a_hp = 0.4;       par.H =(1 - (1-a_hp)/(z-a_hp) )  * z*(1-a_lp)/(z-a_lp) ;  


  end

  
endfunction


function [sim, eemg, InnerSignals] = eemg_filter4A(sim, ev, emgvector, EMGsamples, measurement_path, par) // neues Filter
// Version date: 26.3.14.
// 
// 22.1.14: Adaption to TMSI and clean-up
// 23.1.14: Possibilies to activate debug and write to files- mode
// 26.3.14: more detailed outputs; all parameters concerning the filter-alg are now in par
// 

  H = par.H;
  EMGveclen = par.vecsize;


  function P = build_P(len, Gz) // Für ILC
    imp_resp = dsimul(tf2ss(Gz), [ 1, zeros(1, len-1) ] );

    P = zeros(len,len);
    for i = 1:len 
        tmp = [ zeros(1, i-1), imp_resp(1:($-i+1)) ];
        length(tmp);
        P(:,i) = tmp';
        //	P = [ P , tmp' ];
    end;
  endfunction
  
  function Qm = build_Q(len, Q) // Für ILC
    tmp = build_P(len,Q);
    Qm = tmp'*tmp;          // Vorwärts und Rückwärts in der Zeit Filtern; tmp' filtert rückwärts
  endfunction

  [sim, one] = ld_const(sim, ev, 1);

// defined outside this function
//  EMGveclen = 200;

  StimAttifactWlan = ceil(0.5 * EMGveclen); // the stimulation artifact must be in the first half of the emgvector
  

  SHAPE1 = par.CorrModel;
  SHAPEveclen = length(SHAPE1);  // needs to be even!

//   SHAPE1 = [-1,-1,1,1];
//   SHAPEveclen = 4;  // needs to be even!


  // at very first, remove the ofset of the emgvector
  // calc the mean of the raw signal for the first 10 = par.CalcMeanNsamples  samples
  [sim, beginning] = ld_vector_extract(sim, ev, in=emgvector, from=one, window_len=par.CalcMeanNsamples, vecsize=EMGveclen);
  [sim, tmp] = ld_vector_sum(sim, ev, in=beginning, vecsize=par.CalcMeanNsamples);
  [sim, MinusOfset] = ld_gain(sim, ev, tmp, -1/par.CalcMeanNsamples); 
  [sim, emgvector] = ld_vector_addscalar(sim, 0, emgvector, MinusOfset, vecsize=EMGveclen)  // emgvector = emgvector - Ofset
    

//  [sim] = ld_printf(sim, ev, beginning, "beginning = ", 10);
//  [sim] = ld_printf(sim, ev, beginofs, "beginofs = ", 1);



   // Differrenzwert = 0.4, index_ofs = 10, windows_lange = 40 
  //Differenzverktor bilden
  [sim, diffvec] = ld_vector_diff(sim, ev, in=emgvector, vecsize=EMGveclen )

   // vector find thr test
  [sim, threshold] = ld_const(sim, ev, 1.5);
//  [sim,stim_index] = ld_vector_findthr(sim, ev, in=diffvec, thr=threshold, greater=1, vecsize=EMGveclen-1);
    


  // extract the beginning  of the raw EMG vector that shall contain the stimulation artifact in any
  // case, if an artifact is available.
  [sim, emgvectorBegin] = ld_vector_extract(sim, ev, in=emgvector, from=one, window_len=StimAttifactWlan, vecsize=EMGveclen);
  printf("eemg_filter4A: The stimulation-artifact must stay within the first %d samples of the raw EMG-vector\n", StimAttifactWlan);

//   emgvectorBegin = emgvector // disable above


  // find stim index by using cross correlation - FIXME seems to be not working correctly
  [sim, corr_vector] = ld_simplecovar(sim, ev, in=emgvectorBegin, shape=SHAPE1, vecsize=StimAttifactWlan);
  
  // calc absolute correlation vectors
  [sim, abs_corr_vector] = ld_vector_abs(sim, ev, in=corr_vector, vecsize=StimAttifactWlan-SHAPEveclen+1);

  // get the index where the correlation has it's maximum --> stim_index
  [sim, corr_index, corr_value] = ld_vector_minmax(sim, ev, in=abs_corr_vector, findmax=1, vecsize=StimAttifactWlan-SHAPEveclen+1);
  //[sim]=ld_savefile(sim, ev, fname=measurement_path+"corr_value.dat", source=corr_value, vlen=1);
  
  // compensate for the SHAPEveclen
  [sim, stim_index] = ld_add_ofs(sim, ev, corr_index, ofs=(SHAPEveclen/2));
  
  // do not consider M-waves that do not correlate to the SHAPE that much
  [sim, HighCorrelation] = ld_compare(sim, ev, in=corr_value,  thr=10);
  [sim, LowCorrelation] = ld_gain(sim, ev, HighCorrelation, -1);
  [sim, stim_index_clean] = ld_cond_overwrite(sim, ev, in=stim_index, condition=LowCorrelation, setto=1); // if a low correlation is observed

  // Check if the max of the correlation was at the end of the vector (e.g. due to problems with real-time operation)
  [sim, StimIndex_TooBig] = ld_compare(sim, ev, in=stim_index,  thr=StimAttifactWlan); // TODO: adjust this number
//   [sim, stim_index_clean_low] = ld_cond_overwrite(sim, ev, in=stim_index_clean, condition=stim_index_invalid, setto=0);
  StimIndex = stim_index_clean;

//   [sim] = ld_savefile(sim, ev, fname=measurement_path+"stimindex_clean.dat", source=stim_index_clean, vlen=1);
//   [sim] = ld_savefile(sim, ev, fname=measurement_path+"stimindex_clean_low.dat", source=StimIndex, vlen=1);

if par.DebugActive
  [sim] = ld_printf(sim, ev, stim_index, "stim imp found at :" , 1);
end

if par.WriteFiles
  [sim]=ld_savefile(sim, ev, fname=measurement_path+"stimindex.dat", source=stim_index, vlen=1);
end

  // calc the mean of the raw signal for the first 10 = par.CalcMeanNsamples  samples
  [sim, beginning] = ld_vector_extract(sim, ev, in=emgvector, from=one, window_len=par.CalcMeanNsamples, vecsize=EMGveclen);
  [sim, tmp] = ld_vector_sum(sim, ev, in=beginning, vecsize=par.CalcMeanNsamples);
  [sim, beginofs] = ld_gain(sim, ev, tmp, 1/par.CalcMeanNsamples); 
  
//  [sim] = ld_printf(sim, ev, beginning, "beginning = ", 10);
//  [sim] = ld_printf(sim, ev, beginofs, "beginofs = ", 1);

  // mute (set the values to beginofs) the stimulation artifact (15 = par.StimMuteLength samples in length)
  [sim, mutelen] = ld_const(sim, ev, par.StimMuteLength);
  [sim, beginmute] = ld_add_ofs(sim, ev, StimIndex, par.StimMuteOfs); // -5
  [sim, muted_emgvec] = ld_vector_mute(sim, ev, in=emgvector, from=beginmute, len=mutelen, setto=beginofs, vecsize=EMGveclen);

 // [sim] = ld_printf(sim, ev, beginmute, "beginmute = ", 1);

if par.WriteFiles
  [sim]=ld_savefile(sim, ev, fname=measurement_path+"muted_emgvec.dat", source=muted_emgvec, vlen=EMGveclen);
end

  // filter the emg vector
  Hmat = build_Q(EMGveclen, H); //Hmat = 2*eye(Hmat);
  [sim,H_constmat] = ld_constmat(sim, ev, Hmat ); //  Matrix
  [sim,filtered_EMG] = ld_matmul(sim, ev, H_constmat, size(Hmat), muted_emgvec, [EMGveclen,1] );

if par.WriteFiles
  [sim]=ld_savefile(sim, ev, fname=measurement_path+"filtered_EMG.dat", source=filtered_EMG, vlen=EMGveclen);
end

  // cut out a window (StimIndex+10 : StimIndex+10 + 40) to process the M-wave
  [sim,wndstart] = ld_add_ofs(sim, ev, StimIndex, ofs=par.wndstart_ofs);
  [sim,Mwave] = ld_vector_extract(sim, ev, in=filtered_EMG, from=wndstart, window_len=par.WindowLen, vecsize=EMGveclen);
  
if par.WriteFiles
  [sim]=ld_savefile(sim, ev, fname=measurement_path+"Mwave.dat", source=Mwave, vlen=par.WindowLen);
end

  // apply abs and sum
  [sim, eemg_tmp] = ld_vector_abssum(sim, ev, in=Mwave, vecsize=par.WindowLen);



  

  // If the stimulation artifact could not be found, set lambda to zero
  // as it is assumed that there is no stimulatuion and hence no M-wave and thus
  // lambda = 0  
   [sim, eemg] = ld_cond_overwrite(sim, ev, in=eemg_tmp, condition=LowCorrelation, setto=0);

  // if stim_index_invalid use the last lambda
  [sim, StimIndex_Good] = ld_not(sim, ev, StimIndex_TooBig); // StimIndex_TooBig
  
  // check if there is enough data available for cutting out a window
  [sim,wndend] = ld_add_ofs(sim, ev, wndstart, ofs=par.WindowLen);
  [sim,Nsamples_AtEnd] = ld_add(sim, ev, list(wndend, EMGsamples), [ -1, 1 ] );
  [sim, window_ok] = ld_compare(sim, ev, in=Nsamples_AtEnd,  thr=0); // check if Nsamples_AtEnd is not negative

if par.WriteFiles
  [sim]=ld_savefile(sim, ev, fname=measurement_path+"window_ok.dat", source=window_ok, vlen=1);
end

  // use last lambda=eemg if something is not correct
  [sim, everything_ok] = ld_and(sim, ev, list( window_ok, StimIndex_Good ) );
  [sim, eemg] = ld_memory(sim, ev, in=eemg, rememberin=everything_ok, initial_state=0);
    



  // return inner signals
  InnerSignals.MinusOfset = MinusOfset; // mean of the ofsets of the first rawEMG elements
  InnerSignals.emgvector = emgvector; // ofset free emgvector
  InnerSignals.StimIndex = StimIndex;
  InnerSignals.stim_index_clean = stim_index_clean;
  InnerSignals.muted_emgvec = muted_emgvec;
endfunction








// 
// Find stimulation artifact
// 
  function [sim, stim_index_clean] = get_stim_index(sim, ev, emgvector) // 0 means: no stimindex found
      
    EMGveclen = 200;
    SHAPE1 = [-1,-1,1,1];
    SHAPEveclen = 4;  // needs to be even!

    // find stim index by using stupid covariance
    [sim, emgvector_start] = ld_const(sim, ev, 1);
    [sim, emgvector_part] = ld_vector_extract(sim, ev, in=emgvector, from=emgvector_start, window_len=100, vecsize=EMGveclen);
    [sim, cov_vector] = ld_simplecovar(sim, ev, in=emgvector_part, shape=SHAPE1, vecsize=100);

    // calc absolute correlation vectors
    [sim, abs_cov_vector] = ld_vector_abs(sim, ev, in=cov_vector, vecsize=100-SHAPEveclen+1);

    // get the index where the covariance has it's maximum --> stim_index
    [sim, cov_index, cov_value] = ld_vector_minmax(sim, ev, in=abs_cov_vector, findmax=1, vecsize=100-SHAPEveclen+1);

    // compensate for the SHAPEveclen
    [sim, stim_index] = ld_add_ofs(sim, ev, cov_index, ofs=(SHAPEveclen/2));

    // do not consider M-waves that do not correlate to the SHAPE that much
    [sim, cov_value_eval] = ld_compare(sim, ev, in=cov_value,  thr=1);
    [sim, flipped_covvaleval] = ld_gain(sim, ev, cov_value_eval, -1);
    [sim, stim_index_clean] = ld_cond_overwrite(sim, ev, in=stim_index, condition=flipped_covvaleval, setto=0);
      
  endfunction



// 
// One version of a lambda filter
// 

function [sim, eemg] = eemg_filter4(sim, ev, emgvector, EMGsamples, measurement_path) // neues Filter

  function P = build_P(len, Gz) // Für ILC
    imp_resp = dsimul(tf2ss(Gz), [ 1, zeros(1, len-1) ] );

    P = zeros(len,len);
    for i = 1:len 
        tmp = [ zeros(1, i-1), imp_resp(1:($-i+1)) ];
        length(tmp);
        P(:,i) = tmp';
        //	P = [ P , tmp' ];
    end;
  endfunction
  
  function Qm = build_Q(len, Q) // Für ILC
    tmp = build_P(len,Q);
    Qm = tmp'*tmp;          // Vorwärts und Rückwärts in der Zeit Filtern; tmp' filtert rückwärts
  endfunction

  par.wndstart_ofs = 15;  // 15 for two channel stimulation
  par.WindowLen = 40;

  EMGveclen = 200;
  
  SHAPE1 = [-1,-1,1,1];
  SHAPEveclen = 4;  // needs to be even!

   // Differrenzwert = 0.4, index_ofs = 10, windows_lange = 40 
  //Differenzverktor bilden
  [sim, diffvec] = ld_vector_diff(sim, ev, in=emgvector, vecsize=EMGveclen )

   // vector find thr test
  [sim, threshold] = ld_const(sim, ev, 1.5);
//  [sim,stim_index] = ld_vector_findthr(sim, ev, in=diffvec, thr=threshold, greater=1, vecsize=EMGveclen-1);
    
  // find stim index by using cross correlation - FIXME seems to be not working correctly
  [sim, corr_vector] = ld_simplecovar(sim, ev, in=emgvector, shape=SHAPE1, vecsize=EMGveclen);
  
  // calc absolute correlation vectors
  [sim, abs_corr_vector] = ld_vector_abs(sim, ev, in=corr_vector, vecsize=EMGveclen-SHAPEveclen+1);

  // get the index where the correlation has it's maximum --> stim_index
  [sim, corr_index, corr_value] = ld_vector_minmax(sim, ev, in=abs_corr_vector, findmax=1, vecsize=EMGveclen-SHAPEveclen+1);
  //[sim]=ld_savefile(sim, ev, fname=measurement_path+"corr_value.dat", source=corr_value, vlen=1);
  
  // compensate for the SHAPEveclen
  [sim, stim_index] = ld_add_ofs(sim, ev, corr_index, ofs=(SHAPEveclen/2));
  
  // do not consider M-waves that do not correlate to the SHAPE that much
  [sim, corr_value_eval] = ld_compare(sim, ev, in=corr_value,  thr=10);
  [sim, flipped_corrvaleval] = ld_gain(sim, ev, corr_value_eval, -1);
  [sim, stim_index_clean] = ld_cond_overwrite(sim, ev, in=stim_index, condition=flipped_corrvaleval, setto=0);
  
  // only consider M-waves that correlate to the SHAPE at the beginning of the vector
  [sim, stim_index_invalid] = ld_compare(sim, ev, in=stim_index,  thr=100);
  [sim, stim_index_clean_low] = ld_cond_overwrite(sim, ev, in=stim_index_clean, condition=stim_index_invalid, setto=0);
  
  [sim] = ld_savefile(sim, ev, fname=measurement_path+"stimindex_clean.dat", source=stim_index_clean, vlen=1);
  [sim] = ld_savefile(sim, ev, fname=measurement_path+"stimindex_clean_low.dat", source=stim_index_clean_low, vlen=1);

//  [sim] = ld_printf(sim, ev, stim_index, "stim imp found at :" , 1);
  [sim]=ld_savefile(sim, ev, fname=measurement_path+"stimindex.dat", source=stim_index, vlen=1);
    
  // calc ofs in the beginning
  [sim, wndstart] = ld_const(sim, ev, 1);
  [sim, beginning] = ld_vector_extract(sim, ev, in=emgvector, from=wndstart, window_len=10, vecsize=EMGveclen);
  [sim, tmp] = ld_vector_sum(sim, ev, in=beginning, vecsize=10);
  [sim, beginofs] = ld_gain(sim, ev, tmp, 1/10); 

  
//  [sim] = ld_printf(sim, ev, beginning, "beginning = ", 10);
//  [sim] = ld_printf(sim, ev, beginofs, "beginofs = ", 1);

  // mute the stimulation artifact
  [sim, mutelen] = ld_const(sim, ev, 15);
  [sim, beginmute] = ld_add_ofs(sim, ev, stim_index_clean_low, -5);
  [sim, muted_emgvec] = ld_vector_mute(sim, ev, in=emgvector, from=beginmute, len=mutelen, setto=beginofs, vecsize=EMGveclen);

 // [sim] = ld_printf(sim, ev, beginmute, "beginmute = ", 1);


  [sim]=ld_savefile(sim, ev, fname=measurement_path+"muted_emgvec.dat", source=muted_emgvec, vlen=EMGveclen);
//  [sim]=ld_savefile(sim, ev, fname=measurement_path+"muted_emgvec.dat", source=diffvec, vlen=EMGveclen-1);


  // filter the emg vector
  a_lp = 0.0;  a_hp = 0.4;
  z=poly(0,'z');   H =(1 - (1-a_hp)/(z-a_hp) )  * z*(1-a_lp)/(z-a_lp) ;  
//  H =  z*(1-a_lp)/(z-a_lp) ;  

  Hmat = build_Q(EMGveclen, H); //Hmat = 2*eye(Hmat);
  [sim,H_constmat] = ld_constmat(sim, ev, Hmat ); //  Matrix
  [sim,filtered_EMG] = ld_matmul(sim, ev, H_constmat, size(Hmat), muted_emgvec, [EMGveclen,1] );


  [sim]=ld_savefile(sim, ev, fname=measurement_path+"filtered_EMG.dat", source=filtered_EMG, vlen=EMGveclen);


  // cut out a window (stim_index_clean+10 : stim_index_clean+10 + 40) to process the M-wave
  [sim,wndstart] = ld_add_ofs(sim, ev, stim_index_clean_low, ofs=par.wndstart_ofs);
  [sim,Mwave] = ld_vector_extract(sim, ev, in=filtered_EMG, from=wndstart, window_len=par.WindowLen, vecsize=EMGveclen);
  
  [sim]=ld_savefile(sim, ev, fname=measurement_path+"Mwave.dat", source=Mwave, vlen=par.WindowLen);

  // apply abs and sum
  [sim, eemg_tmp] = ld_vector_abssum(sim, ev, in=Mwave, vecsize=par.WindowLen);



  

  //again, do not consider M-waves that do not correlate to the SHAPE that much
   [sim, eemg] = ld_cond_overwrite(sim, ev, in=eemg_tmp, condition=flipped_corrvaleval, setto=0);
//   eemg = eemg_tmp;

  // if stim_index_invalid use the last lambda
  [sim, stim_index_valid] = ld_not(sim, ev, stim_index_invalid);
  
  // check if there is enough data available for cutting out a window
  [sim,wndend] = ld_add_ofs(sim, ev, wndstart, ofs=par.WindowLen);
  [sim,SpaceAtTheEnd] = ld_add(sim, ev, list(wndend, EMGsamples), [ -1, 1 ] );
  [sim, window_ok] = ld_compare(sim, ev, in=SpaceAtTheEnd,  thr=0);

  [sim]=ld_savefile(sim, ev, fname=measurement_path+"window_ok.dat", source=window_ok, vlen=1);

  // use last lambda if something is not correct
  [sim, everything_ok] = ld_and(sim, ev, list( window_ok, stim_index_valid ) );
  [sim, eemg] = ld_memory(sim, ev, in=eemg, rememberin=everything_ok, initial_state=0);

  //disp(emgvector);


//  [sim, eemg] = ld_const(sim, ev, 1);

    
endfunction



function [sim, lambda_] = emg_filter5(sim, ev, emgvector, Nelements)
  printf("Defining: EMG_Filter Version 5\n");

  function P = build_P(len, Gz) // Für ILC
      imp_resp = dsimul(tf2ss(Gz), [ 1, zeros(1, len-1) ] );

      P = zeros(len,len);
      for i = 1:len 
	  tmp = [ zeros(1, i-1), imp_resp(1:($-i+1)) ];
	  length(tmp);
	  P(:,i) = tmp';
	  //	P = [ P , tmp' ];
      end;
  endfunction
    
  function Qm = build_Q(len, Q) // Für ILC
      tmp = build_P(len,Q);
      Qm = tmp'*tmp;          // Vorwärts und Rückwärts in der Zeit Filtern; tmp' filtert rückwärts
  endfunction


  function [sim, lambda_ret] = filter_ls_w40_o10_pp(sim, ev, emgvector) // lambda out of least squares estimated M-wave
    
    EMGveclen = 200;
    stim_art_dist = 10;
    wndlen=40;
    
    [sim, stim_index] = get_stim_index(sim, ev, emgvector);
    [sim, window_start] = ld_add_ofs(sim, ev, stim_index, stim_art_dist);
    [sim, y] = ld_vector_extract(sim, ev, in=emgvector, from=window_start, window_len=wndlen, vecsize=EMGveclen);
    
    [sim, Phi_zm1] = ld_vector_delay(sim, ev, in=y, vecsize=wndlen);
    [sim, Phi_zm2] = ld_vector_delay(sim, ev, in=Phi_zm1, vecsize=wndlen);
    [sim, Phi_zm3] = ld_vector_delay(sim, ev, in=Phi_zm2, vecsize=wndlen);
    [sim, Phi_zm4] = ld_vector_delay(sim, ev, in=Phi_zm3, vecsize=wndlen);
    [sim, Phi_zm5] = ld_vector_delay(sim, ev, in=Phi_zm4, vecsize=wndlen);
    [sim, Phi_zm6] = ld_vector_delay(sim, ev, in=Phi_zm5, vecsize=wndlen);
    
    [sim, yhat, param] = ld_leastsquares(sim, ev, list(Phi_zm6, Phi_zm5, Phi_zm4, Phi_zm3, Phi_zm2, Phi_zm1, y), veclen=wndlen, n_param=6);
    
    [sim, yhat_sum] = ld_vector_sum(sim, ev, in=yhat, vecsize=wndlen);
    [sim, minus_yhat_mean] = ld_gain(sim, ev, yhat_sum, -1/wndlen);
    [sim, yhat_wo_offset] = ld_vector_addscalar(sim, ev, in=yhat, add=minus_yhat_mean, vecsize=wndlen);
    // find max peak
    [sim, max_index, max_value] = ld_vector_minmax(sim, ev, in=yhat_wo_offset, findmax=1, vecsize=wndlen);
    // find min peak
    [sim, min_index, min_value] = ld_vector_minmax(sim, ev, in=yhat_wo_offset, findmax=0, vecsize=wndlen);
    // calc peak-to-peak lambda
    [sim, lambda_] = ld_add(sim, ev, list(max_value, min_value), [ 1, -1 ] );
    
    // use last lambda if something is not correct
    [sim, one] = ld_const(sim, ev, 1);
    [sim, everything_ok] = ld_and(sim, ev, list( one, stim_index ));
    [sim, lambda_ret] = ld_memory(sim, ev, in=lambda_, rememberin=everything_ok, initial_state=0);
    
  endfunction



  // 
  // Main
  // 

  //[sim, gamma_raw] = eemg_gamma_raw(sim, ev, emgvector, samplenum=Nelements);
  [sim, lambda_ret] = filter_ls_w40_o10_pp(sim, ev, emgvector);

//   gamma_ = gamma_raw;
  lambda_ = lambda_ret;
endfunction



// Voluntary
function [sim, gamma_raw] = eemg_gamma_raw(sim, ev, emgvector, samplenum) // gamma representing the volitional muscular activity @4kHz sample rate
      
    EMGveclen = 200;
    stim_art_dist = 100;
    wndlen=30;
    wndlen2=20;
    min_num_samples=stim_art_dist + wndlen + 5;

    sample_rate = 4000;
    hp_freq = 200;
    hp_order = 2;
    hz = iir(hp_order,'hp','butt',[hp_freq/sample_rate 0],[0 0]);

    HPF = build_Q(wndlen, hz);
    
    [sim, emgvec_zm1] = ld_vector_delay(sim, ev, in=emgvector, vecsize=EMGveclen);
    [sim, valid_number_zm1] = ld_delay(sim, ev, u=samplenum, N=1);
    [sim, stim_index1] = get_stim_index(sim, ev, emgvec_zm1);
    [sim, stim_index2] = get_stim_index(sim, ev, emgvector);
    [sim, one] = ld_const(sim, ev, 1);
    [sim, gluedvec, gluednum] = ld_vector_glue(sim, ev, in1=emgvec_zm1, fromindex1=stim_index1, toindex1=valid_number_zm1...
						  , in2=emgvector, fromindex2=one, toindex2=stim_index2, vecsize=EMGveclen);
    
    //[sim] = ld_savefile(sim, ev, fname="glued_vec.dat", source=gluedvec, vlen=2*EMGveclen);

    [sim, eval_start] = ld_const(sim, ev, stim_art_dist);
    [sim, evalvec] = ld_vector_extract(sim, ev, in=gluedvec, from=eval_start, window_len=wndlen, vecsize=2*EMGveclen);
    [sim, evalvecsum] = ld_vector_sum(sim, ev, in=evalvec, vecsize=wndlen);
    [sim, minusevalvecmean] = ld_gain(sim, ev, evalvecsum, -1/wndlen);
    [sim, evalvec_wo_off] = ld_vector_addscalar(sim, ev, in=evalvec, add=minusevalvecmean, vecsize=wndlen);
    
    //[sim] = ld_savefile(sim, ev, fname="evalvec_wo_off3.dat", source=evalvec_wo_off, vlen=wndlen);
    
    [sim, H_constmat] = ld_constmat(sim, ev, HPF); //  Matrix
    [sim, filtered_evalvec] = ld_matmul(sim, ev, H_constmat, size(HPF), evalvec_wo_off, [wndlen,1] ); // Filtering
    
    //[sim] = ld_savefile(sim, ev, fname="filtered_evalvec3.dat", source=filtered_evalvec, vlen=wndlen);
    
    [sim, wnd2start] = ld_const(sim, ev, 5);
    [sim, filtered_evalvec_part] = ld_vector_extract(sim, ev, in=filtered_evalvec, from=wnd2start, window_len=wndlen2, vecsize=wndlen);
    
    //[sim] = ld_savefile(sim, ev, fname="filtered_evalvec_part3.dat", source=filtered_evalvec_part, vlen=wndlen2);
    
    [sim, gamma1] = ld_vector_abssum(sim, ev, in=filtered_evalvec_part, vecsize=wndlen2);
    
    // hold old gamma value if there the number of valid samples is not sufficient
    [sim, everything_ok] = ld_add_ofs(sim, ev, gluednum, -min_num_samples);
    [sim, gamma2] = ld_memory(sim, ev, in=gamma1, rememberin=everything_ok, initial_state=0);
    
    // set gamma to zero if one of the stimulation impulses is missing
    [sim, zero] = ld_const(sim, ev, 0);
    [sim, everything_ok] = ld_and(sim, ev, list( stim_index1, stim_index2 ));
    [sim, gamma_raw] = ld_switch2to1(sim, ev, cntrl=everything_ok, in1=gamma2, in2=zero);

  endfunction



