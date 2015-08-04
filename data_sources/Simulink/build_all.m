curDir = pwd;

cd('../../matlab');

build

cd(curDir);

slbuild('simulink_example');
