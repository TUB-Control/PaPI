// Commandline Args:

// 1: Port FROM ORTD
// 2: Port TO ORTD
// 3: Port TO Recv
// 4: Port FROM Recv



var dgram = require('dgram');

var PORT_toORTD   = parseInt(process.argv[3],10);//20001;
var PORT_fromORTD = parseInt(process.argv[2],10);//20000;

var PORT_toRecv   = parseInt(process.argv[4],10);//21000;
var PORT_fromRecv = parseInt(process.argv[5],10);//21001;

var RecvAddress   = 0;
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
		packetCount =1;
		console.log('Relay to address: ', RecvAddress);
    }
    clientRecv.send(message,0,message.length, PORT_toORTD, ORTDAddress);
    
});


