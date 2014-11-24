/*

  Sample communication interface to ORTD using UDP datagrams.
  A web-interface is provided, go to http://localhost:8090
  UDPio.sce is the counterpart whose simulation can be controlled
  via the web-interface.
  The web-interface is defined in html/main.html
  
*/

var app = require('http').createServer(handler);
var io = require('socket.io').listen(app);
var fs = require('fs');
var dgram = require('dgram');

// binary packets
var jParser = require('jParser');
var Concentrate = require('concentrate');

// http-interface
app.listen(8090);

// UDP config
var PORT = 10000;
var HOST = '127.0.0.1';
var ORTD_HOST = '127.0.0.1'; // the IP and port of the ORTD simulator running UDPio.sce
var ORTD_PORT = 10001;

// 
// http-server
// 
function handler (req, res) {
  fs.readFile('html/main.html',
  function (err, data) {
    if (err) {
      res.writeHead(500);
      return res.end('Error loading main.html');
    }
 
    res.writeHead(200);
    res.end(data);
  });
}
 
 
  
//  
// UDP interface
// 
var server = dgram.createSocket('udp4');
server.on('listening', function () {
    var address = server.address();
    console.log('UDP Server listening on ' + address.address + ":" + address.port);
});


server.on('message', function (message, remote) {
    // received new packet from ORTD via UDP
    //console.log(remote.address + ':' + remote.port);  

    var NValues = 6; // must be the same as NValues_send defined in UDPio.sce when calling UDPSend
  
    // check if the recved packet has the correct size
    if ( message.length == 12+8*NValues) {
      // prepare the disassembling of the binary message
      var parserS = new jParser(message, {
	packet: {
	  SenderID: 'int32',
	  PacketCounter: 'int32',
	  SourceID: 'int32',
	  Values: ['array', 'float64', NValues] 
	}
      });

      // Disasseble
      Disasm = parserS.parse('packet')
      
      // If the sender ID is correct, forward to the client
      if (Disasm.SenderID == 1295793) {
	// send to web browser
	io.sockets.emit('Values', Disasm.Values );
      }
    }
  
});
 
// bind UDP-port
server.bind(PORT, HOST);


// 
// websockets connection to the web browser(s) 
// 
io.sockets.on('connection', function (socket) {
  console.log('iosocket init ok');
  
  // wait for a parameter upload by the client
  socket.on('ChangeParam_Set', function (data) {
    //console.log(data);

    // Nvalues_recv == 2 in UDPio.sce, thus two double values must be send here
    
    // assemble the binary udp-packet
    var message = Concentrate().int32le(1).int32le(1234).int32le(6468235);
        message = message.doublele(data[0]).doublele(data[1]).doublele(data[2]).doublele(data[3]).doublele(data[4]).doublele(data[5]).result(); // two double values
    
    // send this packet to ORTD
    server.send(message, 0, message.length, ORTD_PORT, ORTD_HOST, function(err, bytes) {
      if (err) throw err;
      console.log('UDP message sent to ' + ORTD_HOST +':'+ ORTD_PORT);
    });
  });
  
  
});

  