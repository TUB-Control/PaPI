function [ json_config ] = simulink_example_config_stateflow( state, compact)
%SIMULINK_EXAMPLE_CONFIG Summary of this function goes here
%   Detailed explanation goes here
    block_name_ortd = 'SourceGroup0';
    plugin_name_ortd = 'ORTDPlugin1';

    
    if state == 1

        signals = {'sine','state'};
        parameters = {'next_state','p2'};

        pf = PacketFramework('PaPIConfig');

        plot_uname = pf.PF_addpluginToTab('Plot', 'PlotData', '(300,300)', '(0,0)', 'Diego');
        lcd_uname = pf.PF_addpluginToTab('LCDDisplay', 'LCDState', '(150,75)', '(0,300)', 'Diego');
        button_uname = pf.PF_addpluginToTab('Button', 'NextState', '(100,50)', '(300,0)', 'Diego');

        pf.PF_changePluginConfig(plot_uname, { ...
               {'yRange', '[0.0 3.0]'}
           } ...
        )
    
        pf.PF_changePluginConfig(lcd_uname, { ...
               {'digit_count', '3'}
           } ...
        )
        
        
        pf.PF_changePluginConfig(button_uname, { ...
               {'state1', '0'}, ...
               {'state2', '2'}, ...
               {'state1_text', 'Next Menu'} ...
               {'state2_text', 'Next Menu'} ...
           } ...
        )

        

        % Create subscription
        
        pf.PF_addsubs(plot_uname, block_name_ortd, {signals(2)});
        
        pf.PF_addsubs(lcd_uname, block_name_ortd, {signals(2)});
        pf.PF_addcontrol(button_uname, 'Click_Event', parameters(1));
        
        json_config = savejson('', pf.config, 'Compact', compact);
    
    end
        
    if state == 2
                             
        signals = {'sine', 'state' };
        parameters = {'next_state','multiplier'};
                       
        pf = PacketFramework('PaPIConfig');

        plot_uname = pf.PF_addpluginToTab('Plot', 'PlotData', '(300,300)', '(0,0)', 'Diego');
        button_uname = pf.PF_addpluginToTab('Button', 'NextState', '(100,50)', '(300,0)', 'Diego');
        lcd_uname = pf.PF_addpluginToTab('LCDDisplay', 'LCDState', '(150,75)', '(0,300)', 'Diego');
        slider_uname = pf.PF_addpluginToTab('Slider', 'Multiplier', '(150,75)', '(300,75)', 'Diego');

        pf.PF_changePluginConfig(plot_uname, { ...
               {'yRange', '[0.0 3.0]'}
           } ...
        )        
    
        pf.PF_changePluginConfig(lcd_uname, { ...
               {'digit_count', '3'}
           } ...
        )
        
        pf.PF_changePluginConfig(slider_uname, { ...
               {'upper_bound', '100'}, ...
               {'lower_bound', '0'}, ...
               {'step_count', '101'} ...
           } ...
        )

        pf.PF_changePluginConfig(button_uname, { ...
               {'state1', '0'}, ...
               {'state2', '1'}, ...
               {'state1_text', 'Next Menu'} ...
               {'state2_text', 'Next Menu'} ...
           } ...
        )         
        
        

        % Create subscription
        
        pf.PF_addsubs(plot_uname, block_name_ortd, {signals(1)} );
        pf.PF_addsubs(lcd_uname, block_name_ortd, {signals(2)});
        
        pf.PF_addcontrol(slider_uname, 'SliderBlock', parameters(2));
        pf.PF_addcontrol(button_uname, 'Click_Event', parameters(1));
        
        json_config = savejson('', pf.config, 'Compact', compact);
    
    end
    

end

