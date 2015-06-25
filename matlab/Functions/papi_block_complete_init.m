function papi_block_complete_init( gcb, amount_parameters, amount_input, json_config)
%PAPI_BLOCK_COMPLETE_INIT Summary of this function goes here
%   Detailed explanation goes here

    disp('Start---------------')
    load_system(gcb);

    amountIn=amount_input;
    amountOut=size(amount_parameters,2);

    sizeParameters = sum(amount_parameters);

    name_papi_block = 'PaPI Block';

    if amountIn < 0
        amountIn = 0;
    end

    papi_block_handle = get_param([gcb '/PaPI Block'],'handle');

    papi_block = get_param(papi_block_handle, 'PortHandles'); 

    port_handler = papi_block.Outport(2);
    papi_parameter_port = get(port_handler);

    % ------------------------------------------------
    % Adjust input mux settings
    % ------------------------------------------------

    mux_input = find_system(gcb,...
          'LookUnderMasks','on',...
          'FollowLinks','on','Name','InputMux');



    if isempty(mux_input)
       disp(['Input mux not found !! '])
       return
    end

    inmux_handle = get_param([gcb '/InputMux'],'handle');

    inmux = get_param(inmux_handle, 'PortHandles');    


    % ----------------------
    % Remove current lines
    % at input mux
    % ----------------------
    papi_remove_block(inmux_handle, 1)
    papi_connect_two_blocks(gcb, inmux_handle, 1, papi_block_handle, 1)

    % -----------------
    % Adjust needed
    % amount of ports
    % -----------------

    set_param(inmux_handle,'Inputs',num2str(amountIn));

    % ------------------------------------------------
    % Create missing inputs
    % ------------------------------------------------
    lastInput = amountIn;

    for n=1:amountIn
       input = ['In' num2str(n)];
        block = find_system(gcb,...
          'LookUnderMasks','on',...
          'FollowLinks','on','Name',input);

        if isempty(block)
            add_block('built-in/Inport',[gcb, ['/' input]]);
        end
        
        src_handler = get_param([gcb '/' input],'handle');
        dest_handler = inmux_handle;
        
        papi_connect_two_blocks(gcb, src_handler, 1, dest_handler, n)

        lastInput=n;
    end
    
    %disp('Delete non needed inports')

    % ------------------------------------------------
    % Delete non needed inputs
    % ------------------------------------------------

    for n=lastInput+1:20
       input = ['In' num2str(n)];

       block = find_system(gcb,...
              'LookUnderMasks','on',...
              'FollowLinks','on','Name',input);

       if ~isempty(block)
           block_handler = get_param([gcb '/' input],'handle');
           papi_remove_block(block_handler,0)
       end      

    end

    % ------------------------------------------------
    % Create missing outputs
    % ------------------------------------------------

    lastOutput = amountOut;

    for n=1:amountOut
        output = ['Out' num2str(n)];
        selector = ['Selector' num2str(n)];

        block = find_system(gcb,...
              'LookUnderMasks','on',...
              'FollowLinks','on','Name',output);

        if isempty(block)
           %disp(['Add ' output])
           add_block('built-in/Outport',[gcb, ['/' output]]);
        end

        % ---
        % Create selector per outport
        % ---

        block = find_system(gcb,...
          'LookUnderMasks','on',...
          'FollowLinks','on','Name',selector);

        if isempty(block)
            add_block('built-in/Selector',[gcb, ['/' selector]]);
        end
        
        select_handler = get_param([gcb '/' selector],'handle');
        outport_handler = get_param([gcb '/' output],'handle');
        disp(amount_parameters)
        start_i = sum(amount_parameters(1:n-1)) + 1;
        end_i   = start_i + amount_parameters(n) - 1;
        
        range = ['[' num2str(start_i) ':' num2str(end_i) ']'];
        
        %disp(range)
        
        set_param(select_handler, 'IndexParamArray', {range},'InputPortWidth', num2str(sizeParameters));
        
        %get(select_handler)
        
        
        
        

           
        % ---
        % Create connection selector <-> output
        % ---    
        src_handler = select_handler;
        dest_handler = outport_handler;
        papi_connect_two_blocks(gcb, src_handler, 1, dest_handler, 1)

        % ---
        % Create connection papi <-> selector
        % ---        
        src_handler = papi_block_handle;
        dest_handler = select_handler;
        papi_connect_two_blocks(gcb, src_handler, 2, dest_handler, 1)
        
        lastOutput=n;
    end

    % ------------------------------------------------
    % Delete non needed outputs
    % ------------------------------------------------

    for n=lastOutput+1:20
       output = ['Out' num2str(n)];
       selector = ['Selector' num2str(n)];

       block = find_system(gcb,...
              'LookUnderMasks','on',...
              'FollowLinks','on','Name',output);

       if ~isempty(block)

           selector_handler = get_param([gcb '/' selector],'handle');
           papi_remove_block(selector_handler)
           %papi_remove_block(block)
           
           delete_block(block);
           
       end      
   

    end

    
    % ------------------------------------------------
    % Get block names
    % ------------------------------------------------

    papi_block_set_signal_parameter_names(gcb, json_config, papi_block_handle)
end

