curDir = pwd;

addpath([curDir '/ert_linux/']);


cd('../../matlab');

build

cd(curDir);

slbuild('simulink_example');
