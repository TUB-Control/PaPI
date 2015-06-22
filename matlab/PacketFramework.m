% pf = PacketFramework % just 'PaPIConfig' without Parameters and Sources
% pf = PacketFramework('SourcesConfig', 'ParametersConfig') % if you want
% to export a PaPI-ready config without evaluating 'BlockConfig'
% pf = PacketFramework('BlockConfig') % if you want to give the json-struct
% to another function which generates the Parameters and Sources by
% evaluating 'BlockConfig'
classdef PacketFramework < handle
    properties
        SourceID_counter = 0;
        Sources = {};
        Parameterid_counter = 0;
        ParameterMemOfs_counter = 1;
        Parameters = {};
        PluginID_counter = 0;
        config = struct;
    end
    
    methods
        % pf = PacketFramework
        % pf = PacketFramework('SourcesConfig', 'ParametersConfig')
        % pf = PacketFramework('BlockConfig')
        function obj = PacketFramework(varargin)
            if (nargin == 0)
                obj. config = struct('PaPIConfig', []);
            else
                for i=1:nargin
                    obj.config.(varargin{i}) = [];
                end
                obj.config.PaPIConfig = [];
            end
        end
        % PluginUname = pf.PF_addplugin('Plot', 'XY', '(1,1)', '(0,0)')
        function PluginUname = PF_addplugin(obj, PluginType, PluginName, PluginSize, PluginPos)
            % inc counter
            new_PluginID_counter = obj.PluginID_counter + 1;
            
            PluginUname = strcat('Plugin', num2str(new_PluginID_counter));
            
            % Add new plugin to the struct
            new_Plugin.identifier.value =  PluginType;
            
            new_Plugin.config.name.value = PluginName;
            new_Plugin.config.size.value = PluginSize;
            new_Plugin.config.position.value = PluginPos;
            
            obj.config.PaPIConfig.ToCreate.(PluginUname) = new_Plugin;
            obj.PluginID_counter = new_PluginID_counter;
        end
        
        % PluginUname = pf.PF_addpluginToTab('Plot', 'XY', '(1,1)', '(0,0)', 'PaPI-Tab')
        function PluginUname = PF_addpluginToTab(obj, PluginType, PluginName, PluginSize, PluginPos, TabName)
            PluginUname = obj.PF_addplugin(PluginType, PluginName, PluginSize, PluginPos);
            obj.config.PaPIConfig.ToCreate.(PluginUname).config.tab.value = TabName;
        end
        
        % pf.PF_changePluginSetting('Plugin1', 'name', 'test')
        function PF_changePluginSetting(obj, PluginUname, PluginSetting, PluginSettingValue)
            obj.config.PaPIConfig.ToCreate.(PluginUname).config.(PluginSetting).value = PluginSettingValue;
        end
        
        % pf.PF_changePluginConfig('Plugin1', {{'name', 'test'}, {'size', '(2,2)'}})
        function PF_changePluginConfig(obj, PluginUname, PluginSettingsList)
            for iSetting = PluginSettingsList
                obj.PF_changePluginSetting(PluginUname, iSetting{1}{1}, iSetting{1}{2});
            end
        end
        
        % PluginUname = pf.PF_addpluginAdvanced('Button', 'Measurement', '(250,100)', '(250,100)', 'PaPI-Tab', {{'state1_text','Go to'}, {'state2_text','Leaving to'}})
        function PluginUname = PF_addpluginAdvanced(obj, PluginType, PluginName, PluginSize, PluginPos, TabName, PluginSettingsList)
            PluginUname = obj.PF_addpluginToTab(PluginType, PluginName, PluginSize, PluginPos, TabName);
            obj.PF_changePluginConfig(PluginUname, PluginSettingsList);
        end
        
        % pf.PF_addpluginAdvancedInclControl('Button', 'Measurement', '(250,100)', '(250,100)', 'PaPI-Tab', {{'state1_text','Go to'}, {'state2_text','Leaving to'}}, 0, 'Click_Event')
        function PF_addpluginAdvancedInclControl(obj, PluginType, PluginName, PluginSize, PluginPos, TabName, PluginSettingsList, ControlParameterID, ControlBlock)
            PluginUname = obj.PF_addpluginAdvanced(PluginType, PluginName, PluginSize, PluginPos, TabName, PluginSettingsList);
            obj.PF_addcontrolbyID(PluginUname, ControlBlock, ControlParameterID);
        end
        
        % pf.PF_addpluginAdvancedInclSub('Plot', 'Plot X', '(500,500)', '(0,0)', 'PaPI-Tab', {{'yRange', '[-10.0 10.0]'}}, 0, 'SourceGroup0')
        % pf.PF_addpluginAdvancedInclSub('Plot', 'Plot XY', '(500,500)', '(0,0)', 'PaPI-Tab', {{'yRange', '[-10.0 10.0]'}}, [0,1], 'SourceGroup0')
        function PF_addpluginAdvancedInclSub(obj, PluginType, PluginName, PluginSize, PluginPos, TabName, PluginSettingsList, SubSourceIDs, SubBlock)
            PluginUname = obj.PF_addpluginAdvanced(PluginType, PluginName, PluginSize, PluginPos, TabName, PluginSettingsList);
            obj.PF_addsubsbyID(PluginUname, SubBlock, SubSourceIDs);
        end
        
        % pf.PF_addsubs('Plugin1', 'SourceGroup0', 'X')
        % pf.PF_addsubs('Plugin1', 'SourceGroup0', {'X', 'Y'})
        function PF_addsubs(obj, SubPluginUname, SubBlock, SubSignals)
            if (isfield(obj.config.PaPIConfig, 'ToSub'))
                if (isfield(obj.config.PaPIConfig.ToSub, SubPluginUname))
                    obj.config.PaPIConfig.ToSub.(SubPluginUname).signals = [obj.config.PaPIConfig.ToSub.(SubPluginUname).signals, SubSignals];
                else
                    obj.config.PaPIConfig.ToSub.(SubPluginUname).signals =  SubSignals;
                end
            else
                obj.config.PaPIConfig.ToSub.(SubPluginUname).signals =  SubSignals;
            end
            obj.config.PaPIConfig.ToSub.(SubPluginUname).block =  SubBlock;
        end
        
        % pf.PF_addsubsbyID('Plugin1', 'SourceGroup0', 0)
        % pf.PF_addsubsbyID('Plugin1', 'SourceGroup0', [0,1])
        function PF_addsubsbyID(obj, SubPluginUname, SubBlock, SubSignalIDs)
            SubSignals = cell(1, length(SubSignalIDs));
            j = 0;
            for i=SubSignalIDs
                j = j + 1;
                SubSignals{j} = obj.Sources{i+1}.SourceName;
            end
            obj.PF_addsubs(SubPluginUname, SubBlock, SubSignals);
        end
        
        % pf.PF_addcontrol('Plugin1', 'SliderBlock', 'sliderVal')
        function PF_addcontrol(obj, ControlPluginUname, ControlBlock, ControlParam)
            obj.config.PaPIConfig.ToControl.(ControlPluginUname).block =  ControlBlock;
            obj.config.PaPIConfig.ToControl.(ControlPluginUname).parameter =  ControlParam;
        end
        
        % pf.PF_addcontrolbyID('Plugin1', 'Click_Event', 0)
        function PF_addcontrolbyID(obj, ControlPluginUname, ControlBlock, ControlParamID)
            obj.PF_addcontrol(ControlPluginUname, ControlBlock, obj.Parameters{ControlParamID+1}.ParameterName);
        end
        
        % SourceID = pf.PF_addsource(1, 257, 'X') % 257 = FLOAT
        function SourceID = PF_addsource(obj, NValues_send, datatype, SourceName)
            SourceID = obj.SourceID_counter;
            
            Source.SourceName = SourceName;
            Source.SourceID = SourceID;
            % Source.NValues_send = NValues_send;
            % Source.datatype =  datatype;
            
            new_SourceConfig.SourceName = SourceName;
            new_SourceConfig.NValues_send = num2str(NValues_send);
            new_SourceConfig.datatype = num2str(datatype);
            ValidSourceIDField = regexprep(num2str(SourceID),'^([^A-Za-z])','x0x${sprintf(''%X'',unicode2native($1))}_','once');
            
            % Add new source to the lists
            obj.Sources{end+1} = Source;
            obj.config.SourcesConfig.(ValidSourceIDField) = new_SourceConfig;
            
            % inc counter
            obj.SourceID_counter = obj.SourceID_counter + 1;
        end
        
        % SourceID = pf.PF_addsourceInclSub(1, 257, 'X', 'Plugin1', 'SourceGroup0') % 257 = FLOAT
        function SourceID = PF_addsourceInclSub(obj, NValues_send, datatype, SourceName, SubPluginUname, SubBlock)
            SourceID = obj.PF_addsource(NValues_send, datatype, SourceName);
            obj.PF_addsubsbyID(SubPluginUname, SubBlock, SourceID);
        end
        
        % [ParameterID, MemoryOfs] = pf.PF_addparameter(1, 257, 'wrWR', 1.6) % with InitValue, 257 = FLOAT
        % [ParameterID, MemoryOfs] = pf.PF_addparameter(2, 257, 'wrWR', [1.6,1]) % Vector with InitValue, 257 = FLOAT
        % [ParameterID, MemoryOfs] = pf.PF_addparameter(1, 257, 'wrWR') % without InitValue, 257 = FLOAT
        function [ParameterID, MemoryOfs] = PF_addparameter(obj, NValues, datatype, ParameterName, optionalInitValue)
            if nargin < 5
                optionalInitValue = zeros(1,NValues);
            end
            if (length(optionalInitValue) ~= NValues)
                error(['length(optionalInitValue) = ', num2str(length(optionalInitValue)), ' ~= NValues = ', num2str(NValues)]);
            end
            ParameterID = obj.Parameterid_counter;
            
            Parameter.ParameterName = ParameterName;
            Parameter.ParameterID = ParameterID;
            % Parameter.NValues = NValues;
            % Parameter.datatype =  datatype;
            % Parameter.InitialValue = optionalInitValue;
            Parameter.MemoryOfs = obj.ParameterMemOfs_counter;
            
            new_ParameterConfig.ParameterName = ParameterName;
            new_ParameterConfig.NValues = num2str(NValues);
            new_ParameterConfig.datatype = num2str(datatype);
            new_ParameterConfig.initial_value = optionalInitValue;
            ValidParameterIDField = regexprep(num2str(ParameterID),'^([^A-Za-z])','x0x${sprintf(''%X'',unicode2native($1))}_','once');
            
            % Add new parameter to the lists
            obj.Parameters{end+1} = Parameter;
            obj.config.ParametersConfig.(ValidParameterIDField) = new_ParameterConfig;
            
            % inc counters
            obj.Parameterid_counter = obj.Parameterid_counter + 1;
            obj.ParameterMemOfs_counter = obj.ParameterMemOfs_counter + NValues;
            
            % return values
            MemoryOfs = Parameter.MemoryOfs;
        end
        
        % [ParameterID, MemoryOfs] = pf.PF_addparameterInclControl(1, 257, 'wrWR', 'Plugin1', 'SliderBlock', 1.6) % with InitValue, 257 = FLOAT
        % [ParameterID, MemoryOfs] = pf.PF_addparameterInclControl(1, 257, 'wrWR', 'Plugin1', 'SliderBlock') % without InitValue, 257 = FLOAT
        function [ParameterID, MemoryOfs] = PF_addparameterInclControl(obj, NValues, datatype, ParameterName, ControlPluginUname, ControlBlock, optionalInitValue)
            if nargin < 7
                optionalInitValue = zeros(1,NValues);
            end
            [ParameterID, MemoryOfs] = obj.PF_addparameter(NValues, datatype, ParameterName, optionalInitValue);
            obj.PF_addcontrolbyID(ControlPluginUname, ControlBlock, ParameterID);
        end
        
        % pf.PF_addparametersForBlockConfig('wrWR')
        % pf.PF_addparametersForBlockConfig({'wrWR', 'erWR'})
        function PF_addparametersForBlockConfig(obj, ParameterNames)
            if (isfield(obj.config.BlockConfig, 'ParameterNames'))
                obj.config.BlockConfig.ParameterNames = [obj.config.BlockConfig.ParameterNames, ParameterNames];
            else
                obj.config.BlockConfig.ParameterNames =  ParameterNames;
            end
        end
        
        % pf.PF_addsignalsForBlockConfig('X')
        % pf.PF_addsignalsForBlockConfig({'X', 'Y'})
        function PF_addsignalsForBlockConfig(obj, SignalNames)
            if (isfield(obj.config.BlockConfig, 'SignalNames'))
                obj.config.BlockConfig.SignalNames = [obj.config.BlockConfig.SignalNames, SignalNames];
            else
                obj.config.BlockConfig.SignalNames =  SignalNames;
            end
        end
    end
end