function [ json_config ] = simulink_example_config( state, compact)
%SIMULINK_EXAMPLE_CONFIG Summary of this function goes here
%   Detailed explanation goes here
    block_name_ortd = 'SourceGroup0';
    plugin_name_ortd = 'ORTDPlugin1';

        
    if state == 1
                             
        signals = {'sine_1','sine_multiplier', 'sine_3', 'noise', 'pulse','sine','new_sine'};
        parameters = {'multiplier'};
                       
        pf = PacketFramework('PaPIConfig');

        plot_uname = pf.PF_addplugin('Plot', 'PlotData', '(300,300)', '(0,0)');
        slider_uname = pf.PF_addplugin('Slider', 'Multiplier', '(150,75)', '(300,0)');
 
        pf.PF_changePluginConfig(slider_uname, { ...
                {'upper_bound', '100'}, ...
                {'lower_bound', '0'}, ...
                {'step_count', '101'} ...
            } ...
        )
        
        %pf.PF_addparametersForBlockConfig({'Multiplier'});
        %pf.PF_addparametersForBlockConfig({'Parameter(105)'});

        
        
        % pf.PF_addsignalsForBlockConfig(signals(1:3));

        % Create subscription
        
        pf.PF_addsubs(plot_uname, block_name_ortd, signals(1:3) );
        
        pf.PF_addcontrol(slider_uname, 'SliderBlock', {parameters(1)});
        
        json_config = savejson('', pf.config, 'Compact', compact);
    
    end
    
    if state == 2

        pf = PacketFramework('PaPIConfig');

        plot_uname = pf.PF_addplugin('Plot', 'PlotData', '(300,300)', '(0,0)');
        slider_uname = pf.PF_addplugin('Slider', 'Multiplier', '(150,75)', '(300,0)');
 
        pf.PF_changePluginConfig(slider_uname, { ...
                {'upper_bound', '100'}, ...
                {'lower_bound', '0'}, ...
                {'step_count', '101'} ...
            } ...
        )
        

        signals = {'sine_1','sine_multiplier', 'sine_3', 'noise', 'pulse','sine','new_sine'};
        parameters = {'multiplier'};

        % Create subscription
        
        pf.PF_addsubs(plot_uname, block_name_ortd, signals);
        
        pf.PF_addcontrol(slider_uname, 'SliderBlock', 'Multiplier');
        
        json_config = savejson('', pf.config, 'Compact', compact);
    
    end
end
