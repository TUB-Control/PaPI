curPath = pwd;

cd('S_Functions');
delete('legacy/*cpp');
delete('legacy/*mexa*');
delete('legacy/*tlc');
delete('legacy/*m');
cd(curPath);
