function [ line_name, signal_name ] = papi_block_get_line_name( line_handle, prefix, postfix )
%PAPI_BLOCK_GET_LINE_NAME Summary of this function goes here
%   Detailed explanation goes here
    line_name = '';
    signal_name = '';
    
    if ishandle(line_handle)
        line = get(line_handle);
        src_block =get(line.SrcBlockHandle);

        if ~isempty(line.Name)
            signal_name = {[line.Name, postfix]};
            line_name = line.Name;
        else
            signal_name = {[prefix, postfix]};
            line_name = prefix;
        end

    else
            signal_name = {[prefix, postfix]};
            line_name = prefix;
    end

end

