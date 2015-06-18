
curPath = pwd;

addpath(curPath);

cd('S_Functions');

addpath('S_Functions');

addpath('hpp');
addpath('cpp');
addpath('legacy');

libPaths = {'/usr/lib/','/usr/lib/x86_64-linux-gnu/'};

legacy_folder_cpp = 'legacy/';


% Create Struct

defs = [];

% ---------------------------#
% PaPIBlock
% ---------------------------#

def = legacy_code('initialize');
def.SFunctionName = 'papi_simulink_block';
def.OutputFcnSpec = 'outputPaPIBlock(double u1[], int32 u2[], int32 u3, double u4, int32 y1[p3], double y2[p4], int32 y3[1])';
def.StartFcnSpec = 'createPaPIBlock(int32 size(u1,1), int32 size(u2,1), int32 p3, int32 p1[], int32 size(p1,1), int8 p2[], int32 size(p2,1), int32 p4)';
def.TerminateFcnSpec = 'deletePaPIBlock()';
def.HeaderFiles = {'PaPIBlock.hpp'};
def.SourceFiles = {'PaPIBlock.cpp'};
def.IncPaths = {'../hpp'};
def.SrcPaths = {'../cpp'};
def.Options.useTlcWithAccel = false;
def.HostLibFiles = {'libjsoncpp.so.0'};
def.TargetLibFiles = {'libjsoncpp.so.0'};
def.Options.language = 'C++';
def.LibPaths = libPaths;

defs = [defs; def];


cd(legacy_folder_cpp);

legacy_code('generate_for_sim', defs);

legacy_code('sfcn_tlc_generate', defs);
legacy_code('rtwmakecfg_generate', defs);

addpath(pwd);

cd('..');

addpath(pwd);

cd('..');
