const onvif = require('node-onvif');

console.log('Start the discovery process.');
// Find the ONVIF network cameras.
// It will take about 3 seconds.
onvif.startProbe().then((device_info_list) => {
  console.log(device_info_list.length + ' devices were found.');
  // Show the device name and the URL of the end point.
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
    }).catch((error) => {
      console.error(error);
    });
  
  });
}).catch((error) => {
  console.error(error);
});