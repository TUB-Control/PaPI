startDir = pwd;

[pathstr,name,ext] = fileparts(mfilename('fullpath'));

scriptDir = pathstr;

oldDir = pathstr;

cd(scriptDir);

curPath = pwd;

addpath(curPath);

addpath([curPath '/Functions']);
addpath([curPath '/jsonlab']);
addpath([curPath '/S_Functions']);

cd('S_Functions');

addpath([pwd '/hpp']);
addpath([pwd '/cpp']);
addpath([pwd '/legacy']);

libPaths = {'/usr/lib/','/usr/lib/x86_64-linux-gnu/'};

legacy_folder_cpp = 'legacy/';


% Create Struct

defs = [];

% ---------------------------#
% PaPIBlock
% ---------------------------#

def = legacy_code('initialize');
def.SFunctionName = 'papi_simulink_block';
def.OutputFcnSpec = 'outputPaPIBlock(void **work1, double u1[], int32 u2[], int32 u3, double u4, int32 u5, int32 y1[p3], double y2[p4])';

def.StartFcnSpec = 'createPaPIBlock(void **work1, int32 size(u1,1), int32 size(u2,1), int32 size(p1,1), int32 size(p2,1),  int32 p1[], int8 p2[], int32 p3 , int32 p4, int32 p5[], int32 p6[])';

def.TerminateFcnSpec = 'deletePaPIBlock(void **work1)';
def.HeaderFiles = {'PaPIBlock.hpp'};
def.SourceFiles = {'PaPIBlock.cpp'};
def.IncPaths = {'../hpp'};
def.SrcPaths = {'../cpp'};
def.Options.useTlcWithAccel = false;
def.HostLibFiles = {'libjsoncpp.so'};
def.TargetLibFiles = {'libjsoncpp.so'};
def.Options.language = 'C++';
def.LibPaths = libPaths;

defs = [defs; def];


cd(legacy_folder_cpp);
try
    legacy_code('generate_for_sim', defs);
    legacy_code('sfcn_tlc_generate', defs);
    legacy_code('rtwmakecfg_generate', defs);
    addpath(pwd);
catch exception
    msgString = getReport(exception);
    disp(msgString);
    warning('ERROR WHILE COMPLIATION');
    cd(startDir);
    return;
end

addpath(pwd);

cd('..');

cd(startDir);
