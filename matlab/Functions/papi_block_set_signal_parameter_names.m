function papi_block_set_signal_parameter_names( gcb, json_config, papi_block_handle, init_command, input_offset, output_offset)
%PAPI_BLOCK_SET_SIGNAL_PARAMETER_NAMES Summary of this function goes here
%   Detailed explanation goes here


    config = loadjson(json_config);
    q = char(39);
    

    % ---------------------
    % Fill ParameterNames
    % and SignalNames if ncessary
    % ---------------------
    
    if isfield(config, 'BlockConfig')
        
        % used ParameterNames as described in BlockConfig
        
        if isfield(config.BlockConfig, 'ParameterNames')
            disp('has ParameterNames config');
        end
        
        % used SignalNames as described in BlockConfig

        if isfield(config.BlockConfig, 'SignalNames')
            disp('has ParameterNames config');
        end

    else
         % Try to derive ParameterNames and SignalNames itself
          papi_block_complete_handle = get_param( gcb,'handle');
          papi_block_complete = get_param(papi_block_complete_handle, 'PortHandles');
                    
          parameters = {};
          signals = {};
          
           for n=1+input_offset:length(papi_block_complete.Inport)
              port_handler = papi_block_complete.Inport(n);
              port = get(port_handler);
              line_handler = port.Line;
              if ishandle(line_handler)
                  line = get(line_handler);
                  %signals(n-input_offset) = {line.Name};

                  if length(line.Name)
                    signals(n-input_offset) = {line.Name};
                  else
                    signals(n-input_offset) = {['s', num2str(n-input_offset)]}; 
                  end
                  
              else
                  signals(n-input_offset) = {['s', num2str(n-input_offset)]};
              end
              
              set_param(gcb,'MaskDisplay',['port_label(''input'', ' num2str(n) ' ,''channel 1'')']);
              
           end 
           
           for n=1+output_offset:length(papi_block_complete.Outport)
               port_handler = papi_block_complete.Outport(n);
               port = get(port_handler);
               line_handler = port.Line;

               if ishandle(line_handler)
                   line = get(line_handler);
                   %parameters(n) = {line.Name};
                   
                   if length(line.Name)
                        parameters(n-output_offset) = {line.Name};
                   else
                        parameters(n-output_offset) = {['p', num2str(n-output_offset)]}; 
                  end
               else
                   parameters(n-output_offset) = {['p', num2str(n-output_offset)]};
                   
               end
               
           end
           
           config.BlockConfig.ParameterNames = parameters;
           config.BlockConfig.SignalNames = signals;
                  
    end

    % ---------------------
    % Set port labels for inport/outport
    % based on SignalNames and ParameterNames in config.BlockConfig
    % ---------------------
    papi_block_complete_handle = get_param( gcb,'handle');
    papi_block_complete = get_param(papi_block_complete_handle, 'PortHandles');
    
    command = init_command;
    
    for n=1+input_offset:length(papi_block_complete.Inport)
        ch_name = '';
        if (n-input_offset <= length(config.BlockConfig.SignalNames))
            ch_name = config.BlockConfig.SignalNames(n-input_offset);            
        else
            ch_name = ['s', num2str(n-input_offset)];
        end
        command = [command ['port_label(''input'', ' num2str(n) ' ,''' [ch_name] ''');']]; 
    end

    for n=1+output_offset:length(papi_block_complete.Outport)
        ch_name = '';
        if (n-output_offset <= length(config.BlockConfig.ParameterNames))
            ch_name = config.BlockConfig.ParameterNames(n-output_offset);            
        else
            ch_name = ['p', num2str(n-output_offset)];
        end 
        command = [command ['port_label(''output'', ' num2str(n) ' ,''' [ch_name] ''');']]; 
    end

    command = strjoin(command);
    
    
   
    set_param(gcb,'MaskDisplay',command);
    
    if isfield(config, 'PaPIConfig')
        %disp('has PaPIConfig config');
    end
    
    final_json_config = savejson('', config, 'Compact', 1);
    
    set_param(papi_block_handle,'json_string', strcat(q, final_json_config, q) );
end

