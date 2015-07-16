#!/usr/bin/env node



var ipc=require('node-ipc');

/***************************************\
 * 
 * You should start both hello and world
 * then you will see them communicating.
 * 
 * *************************************/

ipc.config.id   = 'hello';
ipc.config.retry = 1000;
ipc.config.silent = true;

ipc.connectTo(
    'world',
    function(){
        ipc.of.world.on(
            'connect',
            function(){
                ipc.log('## connected to world ##'.rainbow, ipc.config.delay);
                ipc.of.world.emit(
                    'app.message',
                    {
                        id      : ipc.config.id,
                        message : 'StartScilab'
                    }
                )
            }
        );
        ipc.of.world.on(
            'disconnect',
            function(){
                ipc.log('disconnected from world'.notice);
            }
        );
        ipc.of.world.on(
            'app.message',
            function(data){
                ipc.log('got a message from remote Scilab : \n'.debug, data.message);
                process.stdout.write(data.message);
            }
        );
    }
);





process.stdin.resume();
process.stdin.setEncoding('utf8');


process.stdin.on('data', function(chunk) {

  //console.log("Got someting");
  //console.log(chunk);

                ipc.of.world.emit(
                    'app.message',
                    {
                        id      : ipc.config.id,
                        message : 'ScilabCommand',
                        command : chunk
                    }
                )



});

process.stdin.on('end', function() {
  console.log('HUP');

                  ipc.of.world.emit(
                    'app.message',
                    {
                        id      : ipc.config.id,
                        message : 'StopScilab'
                    }
                )
});



process.on('beforeExit', function(code) {
  console.log('About to exit with code:', code);

                  ipc.of.world.emit(
                    'app.message',
                    {
                        id      : ipc.config.id,
                        message : 'StopScilab'
                    }
                );

});






