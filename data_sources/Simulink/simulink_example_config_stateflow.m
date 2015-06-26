function [ json_config ] = simulink_example_config_stateflow( state, compact)
%SIMULINK_EXAMPLE_CONFIG Summary of this function goes here
%   Detailed explanation goes here
    block_name_ortd = 'SourceGroup0';
    plugin_name_ortd = 'ORTDPlugin1';

    
    if state == 1

        pf = PacketFramework('PaPIConfig');

        plot_uname = pf.PF_addplugin('Plot', 'PlotData', '(300,300)', '(0,0)');
 
        signals = {'sine','state'};
        

        % Create subscription
        
        % pf.PF_addsubs(plot_uname, block_name_ortd, {signals(2) });
        
        
        json_config = savejson('', pf.config, 'Compact', compact);
    
    end
        
    if state == 2
                             
        signals = {'sine', 'state' };
        parameters = {'next_state','multiplier'};
                       
        pf = PacketFramework('PaPIConfig');

        plot_uname = pf.PF_addplugin('Plot', 'PlotData', '(300,300)', '(0,0)');
        slider_uname = pf.PF_addplugin('Slider', 'Multiplier', '(150,75)', '(300,0)');
 
        pf.PF_changePluginConfig(slider_uname, { ...
               {'upper_bound', '100'}, ...
               {'lower_bound', '0'}, ...
               {'step_count', '101'} ...
           } ...
        )
        
        
        

        % Create subscription
        
       % pf.PF_addsubs(plot_uname, block_name_ortd, signals());
        
       % pf.PF_addcontrol(slider_uname, 'SliderBlock', {parameters(2)});
        
        json_config = savejson('', pf.config, 'Compact', compact);
    
    end
    

end

