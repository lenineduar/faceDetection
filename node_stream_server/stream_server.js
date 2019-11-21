// Configure Canvas
const { Image } = require('canvas');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const { document } = (new JSDOM(`...`)).window;

const app = require('express')(),
  server = require('http').Server(app),
  io = require('socket.io')(server),
  rtsp = require('rtsp-ffmpeg');
server.listen(5000);

var request = require('request');
request('http://localhost:8000/get/cameras/actives', function (error, response, body) {
  console.log('error:', error); // Print the error if one occurred
  console.log('statusCode:', response && response.statusCode); // Print the response status code if a response was received
  console.log('body:', body); // Print the HTML for the Google homepage.
  var content = JSON.parse(body)
  
  var cams = [];
  for (i = 0; i < content.length; i++ ){
    cams[i] = content[i].src
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
        //image = changeResolution(data, 320, 240);
        //console.log(image);
        //wsocket.emit('data', image);
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
})

function changeResolution(base64, maxWidth, maxHeight){
 // Max size for thumbnail
  if(typeof(maxWidth) === 'undefined')  maxWidth = 500;
  if(typeof(maxHeight) === 'undefined')  maxHeight = 500;

  // Create and initialize two canvas
  var canvas = document.createElement("canvas");
  var ctx = canvas.getContext("2d");
  var canvasCopy = document.createElement("canvas");
  var copyContext = canvasCopy.getContext("2d");

  // Create original image
  var img = new Image();
  img.src = base64;

  // Determine new ratio based on max size
  var ratio = 1;
  if(img.width > maxWidth)
    ratio = maxWidth / img.width;
  else if(img.height > maxHeight)
    ratio = maxHeight / img.height;

  // Draw original image in second canvas
  canvasCopy.width = img.width;
  canvasCopy.height = img.height;
  copyContext.drawImage(img, 0, 0);

  // Copy and resize second canvas to first canvas
  canvas.width = img.width * ratio;
  canvas.height = img.height * ratio;
  ctx.drawImage(canvasCopy, 0, 0, canvasCopy.width, canvasCopy.height, 0, 0, canvas.width, canvas.height);

  return canvas.toDataURL();

}