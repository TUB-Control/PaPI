stacksize max;


c1 = fscanfMat("source/cable1.dat");
c2 = fscanfMat("source/cable2.dat");
charge = fscanfMat("source/charge.dat");

scf(1); clf; plot(charge);

cdiff = c1-c2;

scf(2); clf; st=300; end=400; plot( cdiff( st:end, : )' );


// Load resutls after running the filter
lambda1 = fscanfMat("dest/lambda1.dat");
stimindex = fscanfMat("dest/stimindex.dat");
scf(3); clf; subplot(311); plot(lambda1);
             subplot(312); plot(charge);
             subplot(313); plot(stimindex);


//
scf(4); clf; indices=[5160, 5167, 5175, 5181]; plot( cdiff( indices, : )' );
disp( stimindex(indices) );


scf(4); clf; indices=[ 2960 ]; plot( cdiff( indices, : )' );
disp( stimindex(indices) );



// more channels
// Load resutls after running the filter
lambda2 = fscanfMat("dest/lambda2.dat");
lambda3 = fscanfMat("dest/lambda3.dat");
lambda3 = fscanfMat("dest/lambda3.dat");
lambda_bip = fscanfMat("dest/lambda_bip.dat");


stimindex = fscanfMat("dest/stimindex.dat");
scf(3); clf; subplot(311); plot(lambda1, 'b'); plot(lambda2, 'r'); plot(lambda3, 'g'); plot(lambda_bip, 'k'); legend('l1', 'l2', 'l3', 'lbip');
             subplot(312); plot(charge);
             subplot(313); plot(stimindex);




