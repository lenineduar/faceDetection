const onvif = require('node-onvif');

console.log('Start the discovery process.');
// Find the ONVIF network cameras.
// It will take about 3 seconds.
var cant = 0;
var uri = [];
onvif.startProbe().then((device_info_list) => {
  console.log(device_info_list.length + ' devices were found.');
  // Show the device name and the URL of the end point.
  cant = device_info_list.length;
  var i = 0
  device_info_list.forEach((info) => {
    console.log('- ' + info.urn);
    console.log('  - ' + info.name);
    console.log('  - ' + info.xaddrs[0]);

    let device = new onvif.OnvifDevice({
      xaddr: info.xaddrs[0],
      user : 'admin',
      pass : 'admin'
    });
    
    device.init().then(() => {
      // Get the UDP stream URL
      let url = device.getUdpStreamUrl();
      console.log("  -Streaming url: "+device.getUdpStreamUrl());
      uri[i] = url.slice(0,7)+"admin:admin@"+url.slice(7);
      console.log("URI: "+uri[i])
      i++;
    }).catch((error) => {
      console.error(error);
    });
  
  });
}).catch((error) => {
  console.error(error);
});