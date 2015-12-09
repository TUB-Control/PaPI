function papi_block_set_signal_parameter_names( gcb, json_config, papi_block_handle, init_command, input_offset, output_offset, define_inputs, split_signals)
%PAPI_BLOCK_SET_SIGNAL_PARAMETER_NAMES Summary of this function goes here
%   Detailed explanation goes here


    config = loadjson(json_config);
    q = char(39);

    size_diff = size(define_inputs,2) - size(split_signals, 2);

    if ( size_diff > 0 )
        split_signals = [split_signals ones(1, size_diff)];
    end

    % -------------
    % Mask command
    % -------------
    command = init_command;


    % ------------
    % Get importand handles
    % ----------------------

    papi_block_complete_handle = get_param( gcb,'handle');
    papi_block_complete = get_param(papi_block_complete_handle, 'PortHandles');

    % ---------------------
    % Fill ParameterNames
    % and SignalNames if ncessary
    % ---------------------

    if isfield(config, 'BlockConfig')

        % used ParameterNames as described in BlockConfig
        if isfield(config.BlockConfig, 'ParameterNames')
            %disp('has ParameterNames config');
        else
            error('You are using a BlockConfig: Define the parameters');
        end

        % used SignalNames as described in BlockConfig
        if isfield(config.BlockConfig, 'SignalNames')
            %disp('has SignalNames config');
        else
            error('You are using a BlockConfig: Define the signals');
        end


        % ---------------------
        % Set port labels for inport/outport
        % based on SignalNames and ParameterNames in config.BlockConfig
        % ---------------------

        offset = 0;
        for n=1+input_offset:length(papi_block_complete.Inport)
            port_number = n-input_offset;

            ch_name = '';
            if (n-input_offset+offset <= length(config.BlockConfig.SignalNames))
                ch_name = config.BlockConfig.SignalNames(port_number + offset);
            else
                ch_name = ['s', num2str(port_number)];
            end

            if split_signals(port_number)
                offset = offset + define_inputs(port_number)-1;
            end

            command = [command ['port_label(''input'', ' num2str(n) ' ,''' [ch_name] ''');']];
        end


    else
          % Try to derive ParameterNames and SignalNames itself

          parameters = {};
          signals = {};

          % ----------------------
          % Set signal names
          % ----------------------

          %disp(get(papi_block_complete_handle))

           signal_count = 1;

           for n=1+input_offset:length(papi_block_complete.Inport)
              port_handler = papi_block_complete.Inport(n);
              port = get(port_handler);
              line_handler = port.Line;

              input_dimension = define_inputs(n-input_offset);

              line_name = '';

              if split_signals(n-input_offset) && input_dimension ~= 1

                  for d=1:input_dimension

                      [line_name, signal_name] = papi_block_get_line_name(line_handler, ['s' num2str(n-input_offset) ''], ['(' num2str(d) ')']);

                      signals(signal_count) = {strjoin(signal_name)};

                      signal_count = signal_count + 1;
                  end
              else
                 [line_name, signal_name] = papi_block_get_line_name(line_handler, ['s' num2str(n-input_offset) ''], '');
                 signals(signal_count) = {strjoin(signal_name)};

                 signal_count = signal_count + 1;
              end

              set_param(gcb,'MaskDisplay',['port_label(''input'', ' num2str(n) ' ,''channel 1'')']);

              command = [command ['port_label(''input'', ' num2str(n) ' ,''' [line_name] ''');']];

           end

          % ----------------------
          % Set parameter names
          % ----------------------

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

           assignin('base', 'papi_signals', signals);
           assignin('base', 'papi_parameters', parameters);

           config.BlockConfig.ParameterNames = parameters;
           config.BlockConfig.SignalNames = signals;

    end

    % ---------------------
    % Set port labels for inport/outport
    % based on ParameterNames in config.BlockConfig
    % ---------------------

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
