curDir = pwd;

addpath('ert_linux/');

cd('ert_linux/');
addpath(pwd);
cd('..');

cd('../../matlab');
build

cd(curDir);

slbuild('simulink_example');
