function [ json_config ] = rehastim_config( compact)
%SIMULINK_EXAMPLE_CONFIG Summary of this function goes here
%   Detailed explanation goes here
    block_name_ortd = 'SourceGroup0';
    plugin_name_ortd = 'ORTDPlugin1';

    signals = {'CurrentState'};

    parameters = {'Configuration','Hearbeat','Control','MaximaSlider','Start','NextState','Slider'};

    pf = PacketFramework('PaPIConfig');

%    plot_uname    = pf.PF_addplugin('Plot', 'PlotData', '(300,300)', '(0,0)');
    rehagui_uname = pf.PF_addplugin('RehaStimGUI', 'RehaStimGUI', '(150,75)', '(300,0)');

    pf.PF_changePluginConfig(rehagui_uname, { ...
            {'maximized', '1'}, ...
            {'config', 'papi/plugin/visual/RehaStimGUI/_static/example_config.xml'} ...
            {'signal_next_state', 'CurrentState'} ...
        } ...
    )

    %pf.PF_addparametersForBlockConfig({'Multiplier'});
    %pf.PF_addparametersForBlockConfig({'Parameter(105)'});



    % pf.PF_addsignalsForBlockConfig(signals(1:3));

    % Create subscription

    pf.PF_addsubs(rehagui_uname, block_name_ortd, {signals(1)} );

    pf.PF_addcontrol(rehagui_uname, 'StimulatorConfiguration', {parameters(1)});
    pf.PF_addcontrol(rehagui_uname, 'Heartbeat', {parameters(2)});
    pf.PF_addcontrol(rehagui_uname, 'ControlStim', {parameters(3)});
    pf.PF_addcontrol(rehagui_uname, 'MaximaSlider', {parameters(4)});
    pf.PF_addcontrol(rehagui_uname, 'Start', {parameters(5)});
    pf.PF_addcontrol(rehagui_uname, 'NextState', {parameters(6)});
    
    json_config = savejson('', pf.config, 'Compact', compact);


end

