#!/usr/bin/env node

// http://localhost:8091/index.html

var ipc=require('node-ipc');
var cldprocess = require('child_process');




http = require('http');
url = require("url"),
path = require("path"),
fs = require("fs")

var fs = require('fs');


//
// Webinterface
//

// http-server config
var HTTPPORT = 8091;



// http-server

// got from stackoverflow: 
// http://stackoverflow.com/questions/6084360/node-js-as-a-simple-web-server
var httpserver = http.createServer(function(request, response) {

  var uri = url.parse(request.url).pathname
    , filename = path.join(process.cwd(), 'html', uri);

   fs.stat(filename, function(err, stat) {
      if(err != null) {
     //if(!exists) {
       response.writeHead(404, {"Content-Type": "text/plain"});
       response.write("404 Not Found\n");
       response.end();
       return;
     }

    if (fs.statSync(filename).isDirectory()) filename += '/index.html';

    fs.readFile(filename, "binary", function(err, file) {
      if(err) {        
        response.writeHead(500, {"Content-Type": "text/plain"});
        response.write(err + "\n");
        response.end();
        return;
      }

      console.log(filename);
      if (filename.split('.').pop() == 'js') {
  console.log('sending javascipt');
         response.writeHead(200, {"Content-Type": "text/javascript"});  
//         response.writeHead(200);
      } else {
        response.writeHead(200);
      }
      response.write(file, "binary");
      response.end();
    });
  });
}).listen(HTTPPORT);

// set-up socket.io
var io = require('socket.io').listen(httpserver);
io.set('log level', 1); // reduce logging


// try { io.sockets.emit('SCISTOUT', {  "Data" : line } ); } catch(err) { }






/***************************************\
 * 
 * You should start both hello and world
 * then you will see them communicating.
 * 
 * *************************************/

ipc.config.id   = 'world';
ipc.config.retry= 1500;
ipc.config.silent = true;

var ScilabProc;


ipc.serve(
    function(){
        ipc.server.on(
            'app.disconnected',
            function(data,socket){
              console.log('**************************');

            });



        ipc.server.on(
            'app.message',
            function(data,socket){

                ipc.log('got a message from'.debug, (data.id).variable, (data.message));

                if (data.message == 'ScilabCommand') {
                  ScilabProc.stdin.write( data.command );
                  process.stdout.write('TO  S> ' + data.command);
                }

                if (data.message == 'StopScilab') {
                  console.log('About to stop scilab');
                  //ScilabProc.disconnect();
                  ScilabProc.kill();
                }

                if (data.message == 'StartScilab') {
                    console.log('Starting Scilab');

                    try {
                      ScilabProc.kill();
                      console.log('A previously active Scilab Process has been killed');
                    } catch (err) {

                    }

                    //try {
                    // ScilabProc = cldprocess.spawn('/Applications/scilab-5.5.1.app/Contents/MacOS/bin/scilab', [ '-nwni' ], { cwd : '.' } );
                    //} catch(e) {



                      ScilabProc = cldprocess.spawn('scilab551', [ '-nwni' ], { cwd : '.' } );
                    //}


                    console.log( ScilabProc.pid );

                   // ScilabProc.stdin.write('a=111111111\n');
                   // ScilabProc.stdin.write('disp(a)\n');


                    ScilabProc.stdout.on('data', function (data) {
//                      console.log('stdout: ' + data);
                      process.stdout.write('FROM S> ' + data);

                      //try { 
                        io.sockets.emit('SCISTOUT', {  ConsoleId : 1 , Data : ''+data } ); 
                        //} catch(err) { }


                      ipc.server.emit(
                        socket,
                        'app.message',
                        {
                          id      : ipc.config.id,
                          message : '' + data
                        }
                      );

                    });

                    ScilabProc.stderr.on('data', function (data) {
                      console.log('stderr: ' + data);
                    });


                    ScilabProc.on('close', function (code) {
                      console.log('child process exited with code ' + code);
                      ipc.server.emit(
                        socket,
                        'app.message',
                        {
                          id      : ipc.config.id,
                          message : 'ScilabExited'
                        }
                      );

                    });
    

                }


                // ipc.server.emit(
                //     socket,
                //     'app.message',
                //     {
                //         id      : ipc.config.id,
                //         message : data.message+' world!'
                //     }
                // );
            }
        );
    }
);

ipc.server.define.listen['app.message']='This event type listens for message strings as value of data key.';

ipc.server.start();

//console.log(ipc.server.define.listen);



/* UDP PaPi Packets forwarding */



    
var dgram = require('dgram');

// var PORT_toORTD   = parseInt(process.argv[3],10);//20001;
// var PORT_fromORTD = parseInt(process.argv[2],10);//20000;

// var PORT_toRecv   = parseInt(process.argv[4],10);//21000;

var PORT_toORTD   = 20001;
var PORT_fromORTD = 20000;

var PORT_toRecv   = 21000;


var RecvAddress   = 0;
var RecvPort = 0;

var ORTDAddress   = 'localhost';

var clientORTD    = dgram.createSocket('udp4');
clientORTD.bind(PORT_fromORTD);

var clientRecv    = dgram.createSocket('udp4');
clientRecv.bind(PORT_toRecv);

var packetCount = 0;

clientORTD.on('message', function(message) {
  if (packetCount != 0) {
      clientORTD.send(message,0,message.length, PORT_toRecv, RecvAddress);
  }
});



clientRecv.on('message', function(message, rinfo) {
    if (packetCount == 0) {
      RecvAddress = rinfo.address;
      RecvPort = rinfo.port;
      packetCount =1;
      console.log('Relay to: ', RecvAddress+':'+RecvPort);
    }
    clientRecv.send(message,0,message.length, PORT_toORTD, ORTDAddress);
    
});




//
// Socket io
//
io.on('connection', function(socket){

  // forwards commands comming from Web/PaPi to Scilab
  socket.on('ConsoleCommand', function(msg){
    console.log(msg);
    ScilabProc.stdin.write( msg.Data + '\n' );
  });
});









  var prompt = require('prompt');
 
  // 
  // Start the prompt 
  // 
 
  // 
  // Get two properties from the user: username and email 
  // 

 prompt.start();


function initScilabPrompt() { 
  prompt.get(['Scilab'], function (err, result) {


//    try {
      ScilabProc.stdin.write( result.Scilab + '\n' );
//    } catch (err) {
//      process.stderr.write('Scilab not stated\n');
//    }

    initScilabPrompt();
  });
}

initScilabPrompt();


// // input from Stdin
// var readline  = require('readline');

// readline.createInterface({
//     input     : ls.stderr,
//     terminal  : false
//   }).on('line', function(line) {

//      console.log('LINE:' + line);    


    
//   }).on('close', function() {
    
//   });

