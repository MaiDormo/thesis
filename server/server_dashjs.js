const express = require('express');
const app = express();
const http = require('http');
const fs = require('fs');
const path = require('path');
const dashjs = require('dashjs');

const server = http.createServer(app);
const PORT = 1337;
const HOST = '10.0.0.1';

app.get('/videos/:videoName/:mpdName', (req, res) => {
  const videoName = req.params.videoName;
  const mpdName = req.params.mpdName;

  const videoPath = path.join(__dirname, 'server', 'videos', videoName, mpdName);

  fs.readFile(videoPath, (err, data) => {
    if (err) {
      console.error(err);
      res.status(500).send('Internal Server Error');
      return;
    }

    res.type('application/dash+xml');
    res.send(data);
  });
});

// Serve dash.js library
app.use('/dash.js', express.static(path.join(__dirname, 'node_modules/dashjs/dist')));

// Start the server
server.listen(PORT, HOST, () => {
  console.log(`Server running at http://${HOST}:${PORT}`);
});

// Gracefully handle shutdown
process.on('SIGINT', () => {
  console.log('Server shutting down...');
  server.close(() => {
    console.log('Server shut down successfully.');
    process.exit(0);
  });
});
