function blkStruct = slblocks

    blkStruct.Name = ['PaPI' sprintf('\n') 'Library'];

    Browser(1).Name = 'PaPI';
    Browser(1).Library = 'PaPI';
    Browser(1).IsFlat  = 0;

    blkStruct.Browser = Browser;
    
%     if (~verLessThan('matlab', '8.4'))  % R2014b
%       % Add repository information if not yet done
%       sys = 'PaPI';
%       try
%         load_system(sys);
%         if (strcmp(get_param(sys, 'EnableLBRepository'), 'off'))
%           set_param(sys', 'Lock', 'off');
%           set_param(sys, 'EnableLBRepository', 'on');
%           set_param(sys, 'Lock', 'on');
%           save_system(sys);
%         end;
%         close_system(sys);
%       catch ex
%       end
%     end;
