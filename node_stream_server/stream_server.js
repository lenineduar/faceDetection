const app = require('express')(),
  server = require('http').Server(app),
  io = require('socket.io')(server),
  rtsp = require('rtsp-ffmpeg');
server.listen(5000);

// Descubrimiento de cámara
const onvif = require('node-onvif');

var cant = 0;
global.uri = [];
var error = false;
console.log('Start the discovery process.');
onvif.startProbe().then((device_info_list) => {
  //console.log(device_info_list.length + ' devices were found.');
  // Show the device name and the URL of the end point.
  cant = device_info_list.length;
  var i = 0;
  var uri = [];
  device_info_list.forEach((info) => {
    let device = new onvif.OnvifDevice({
      xaddr: info.xaddrs[0],
      user : 'admin',
      pass : 'admin'
    });
    device.init().then(() => {
      // Get the UDP stream URL
      let url = device.getUdpStreamUrl();
      uri[i] = url.slice(0,7)+"admin:admin@"+url.slice(7);
      i++;
    }).catch((error) => {
      console.error(error);
      error = true;
    });
  });
  // Esperar 5 seg. para crear el websocket
  setTimeout(function(){
    ServerStream(uri);
  },5000);
}).catch((error) => {
  console.error(error);
  error = true;
});
// Fin del Descubrimiento

function ServerStream(uri){
  var cams = [];
  for (i = 0; i < uri.length; i++ ){
    cams[i] = uri[i];
  }

  var camaras = cams.map(function(uri, i) {
    var stream = new rtsp.FFMpeg({input: uri});
    stream.on('start', function() {
      console.log('stream ' + i + ' started');
    });
    stream.on('stop', function() {
      console.log('stream ' + i + ' stopped');
    });
    return stream;
  });

  camaras.forEach(function(camStream, i) {
    i = i+1;
    var ns = io.of('/cam' + i);
    ns.on('connection', function(wsocket) {
      console.log('connected to /cam' + i);
      var pipeStream = function(data) {
        var bytes = new Uint8Array(data);
        wsocket.emit('data', data.toString("base64"));
      };
      camStream.on('data', pipeStream);

      wsocket.on('disconnect', function() {
      console.log('disconnected from /cam' + i);
        camStream.removeListener('data', pipeStream);
      });
    });
  });

  io.on('connection', function(socket) {
    socket.emit('start', cams.length);
  });

  app.get('/cameras', function (req, res) {
    let url_stream = {
        'uri': uri,
    };
    res.send(url_stream);
  });
  console.log('Start stream server.');
  console.log('Now you can start the web server.');
}