function papi_remove_block( block_handler, only_disconnect )
%PAPI_REMOVE_BLOCK Summary of this function goes here
%   Detailed explanation goes here

    object = get_param(block_handler, 'PortHandles');   
    
    if nargin < 2
        only_disconnect = 0;
    end
    
    
    for n=1:length(object.Outport)
        port_handler = object.Outport(n);
        port = get(port_handler);
        line_handler = port.Line;
        if ishandle(line_handler)
            delete_line(line_handler );
        end
    end

    for n=1:length(object.Inport)
        port_handler = object.Inport(n);
        port = get(port_handler);
        line_handler = port.Line;
        if ishandle(line_handler)
            delete_line(line_handler );
        end
    end    

    
    if ~only_disconnect
        delete_block(block_handler)
    end
end

