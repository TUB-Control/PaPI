
// load data 
A=fscanfMat('saved_vector_1.dat');
ValidEMGSamplesPerVector = fscanfMat('emg_numdata.dat');


size(A)
 ans  =
 
    5982.    200.


// extract emgVector and the number of valid samples for k=1001
emgVector = A(1001,:)
ValidSamples = ValidEMGSamplesPerVector(1001);

// Valid data is 
ValidEMGData = emgVector(1:ValidSamples);



scf(); plot(A(1001,:))
