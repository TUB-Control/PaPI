function papi_connect_two_blocks( sys, src_handler, src_port, dest_handler, dest_port )
%PAPI_CONNECT_TWO_BLOCKS Summary of this function goes here
%   Detailed explanation goes here
    
    src_name = get_param(src_handler,'Name');
    dest_name = get_param(dest_handler,'Name');
    
    source = strcat(src_name, ['/' num2str(src_port)]);
    dest   = strcat(dest_name, ['/' num2str(dest_port)]);
    
    %Has dest already a line?
    object = get_param(dest_handler, 'PortHandles');
    
    port_handler = object.Inport(dest_port);
    port = get(port_handler);
    line_handler = port.Line;

    if ~ishandle(line_handler)
        add_line(gcb, source , dest );
    end    
end

