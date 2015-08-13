function ert_linux_make_rtw_hook(hookMethod,modelName,rtwroot,templateMakefile,buildOpts,buildArgs)
% Hook file for the Workshop Host Target 
 
  switch hookMethod
   case 'error'
    disp('error');
   case 'entry'
    disp('Starting build');
    disp('Good hook spot to run Model Advisor checks');
   case 'before_tlc'
    % do nothing  
   case 'after_tlc'
    % do nothing
   case 'before_make'
    % do nothing
   case 'after_make'
    % do nothing
	if (~isempty(strfind(buildArgs, 'arm-linux-gnueabihf-gcc')))
%         unix(strcat('sshpass -p "constantin"',  ' scp ../', modelName, ' constantin@192.168.7.2:'), '-echo');
        unix(strcat('scp ../', modelName, ' root@192.168.7.2:'), '-echo');
    end
   case 'exit'
    disp('Done building');    
  end
