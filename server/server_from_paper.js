var http = require('http');
var fs = require('fs');
var path = require('path');
// var fs2 = require('fs');

// Create directoty for statistics of our server
// var dir = './statistics';

// if (!fs2.existsSync(dir)){
//     fs2.mkdirSync(dir);
// }

// Start write to new File
    // let writeStream = fs2.createWriteStream('statistics/results_'+ myCurrentDate() +'.csv');
    // writeStream.write('FilePath,DateTime\n');



// The following part of the code is executed when the client makes a request. In case a
// segment file is requested, the data is inserted in the file described above.
var filePath = '';
var server = http.createServer(function (request, response) {
    filePath = './server/videos' + request.url;
    var datetimeRequestStart = myCurrentDate();
    console.log('filepath: ' + filePath + '\n');
    if(filePath.includes(".mpd") === true){
        console.log('(manifest) : request starting... : ' + filePath + '\n');
    }
    else if ( filePath.includes("lake_audio") === true){
        console.log('(audio) : request starting... : ' + filePath + '\n');
    }
    else if ( filePath.includes("lake") === true){
        console.log('(segment) : request starting... : ' + filePath + '\n');
        // write to a new line in file named secret.txt
        // writeStream.write(filePath + ','+ myCurrentTime() + '\n');
    }

    // The following code is executed in order to identify the content type of the requested
    // object. The general type of its object is specified as text/html.
    var extname = path.extname(filePath);
    var contentType = 'text/html';
    switch (extname) {
        case '.m4s':
            contentType = 'dash/m4s';
            break;
        case '_dashinit.mp4':
            contentType = 'dashinit/mp4';
            break;
        case '.mpd':
            contentType = 'manifest/mpd';
            break;
        case '.mp4':
            contentType = 'video/mp4';
            break;
        case '.m4a':
            contentType = 'audio/m4a';
            break;
    }

    // The data is sent to the client accompanied with an appropriate message. 
    // In case of an ENOEΝT error, the server responds ‘404 Not Found’. 
    // ENOEΝT errors occur when the server does not possess the requested data.
    fs.readFile(filePath, function(error, content) {
        if (error) {
            if(error.code == 'ENOENT'){
                fs.readFile('./404.html', function(error, content) {
                    response.writeHead(404, {"Content-Type": "text/html"});
                    response.write("404 Not Found\n");
                    response.end(content, 'utf-8');
                });
            }
            // The server responds ‘Sorry, check with the site admin for error: '+error.code+' ..’ where
            // error.code stands for 500.
            else {
                response.writeHead(500);
                response.end('Sorry, check with the site admin for error: '+error.code+' ..\n');
                response.end();
            }
        }
        // The server responds to a successfully made request with the status code 200. It also
        // sends the requested object as well as some relevant information about it in the format of
        // a Cookie. This information contains the name of the object and the resolution when its
        // type is relevant.
        else {
            //response.setHeader('Cookie', ['filePath=' + filePath, 'resolution=' + myResolution(filePath)]);
            response.setHeader('Cookie', [ filePath, myResolution(filePath)]);
            response.writeHead(200, { 'Content-Type': contentType });
            response.end(content, 'utf-8');
            }
        });
    }).listen(1337, '10.0.0.1');
    console.log("Running node.js %s on %s-%s", process.version, process.platform, process.arch);
    console.log('Server running at http://10.0.0.1:1337/');
    
    //}).listen(1337, '10.0.2.15');
    //console.log("Running node.js %s on %s-%s", process.version, process.platform, process.arch);
    //console.log('Server running at http://10.0.2.15:1337/');

    // The server terminates and also ends the procedure of the creation of the file which was
    // described previously. In addition, an appropriate message appears, informing the user
    // that the server is no longer online.
    server.on('close', function() {
        // the finish event is emitted when all data has been flushed from the stream
        // writeStream.on('finish', () => {
        //     console.log('Create a new file with statistics of the expiriment.\n');
        // });
        
        // close the stream
        // writeStream.end();

        console.log('Server stopped.\n');
    });

    // In case of an abrupt termination (kill), which means that the user has typed Ctrl + C or
    // Ctrl + Χ, the process ends smoothly as shown below:

    process.on('SIGINT', function() {
        console.log('User typed: Ctrl + C or Ctrl + Χ.\n');
        server.close();
    });


    // ------------------ Functions ------------------ //

    // The following auxiliary functions were created so as to make our server more understandable.
    // The function myCurrentDate() returns the current date in this form YYYYMMDD_hh:mm:ss.

    function myCurrentDate() {
        let date_ob = new Date();
        //current date
        // adjust 0 before single digit date
        let date = ("0" + date_ob.getDate()).slice(-2);
        // current month
        let month = ("0" + (date_ob.getMonth() + 1)).slice(-2);
        // current year
        let year = date_ob.getFullYear();
        // current hours
        let hours = date_ob.getHours();
        // current minutes
        let minutes = date_ob.getMinutes();
        // current seconds
        let seconds = date_ob.getSeconds();
        // current date of server in YYYYMMDD_HH:MM:SS format
        let myDate = year + month + date + '_' + hours + ':' + minutes + ':' + seconds;

        return myDate;
    }

    // The function myCurrentTime() returns the current time in this form hh:mm:ss.sss.

    function myCurrentTime() {
        let date_ob = new Date();
        // current hours
        let hours = date_ob.getHours();
        // current minutes
        let minutes = date_ob.getMinutes();
        // current seconds
        let seconds = date_ob.getSeconds();
        // current milliseconds
        let milliseconds = date_ob.getMilliseconds();
        // current time of server in HH:MM:SS.sss format
        let myTime = hours + ':' + minutes + ':' + seconds + '.' + milliseconds;

        return myTime;
    }

    // According to the name of the file (filePath) the function myResolution(filePath) finds and
    // returns the resolution of the video. The possible resolutions are '430 x 242', '640 x 360',
    // '849 x 480', '1280 x 720' and '1920 x 1080'.

    function myResolution(filePath) {
        //Find data from: https://stackoverflow.com/questions/10003683/extract-get-a-numberfrom-a-string

        if(filePath.includes(".mpd") === true) {
            return ''
        }
        else if ( filePath.includes("lake_audio") === true){
            return ''
        }
        else if ( filePath.includes("lake") === true){
            var myNum = filePath.replace(/^\D+|\D.*$/g, "");
            var myResolution = '1920 x 1080';
            console.log('num: ' + myNum + '\n');
            if( myNum === '242')
                myResolution = '430 x 242';
            else if( myNum === '360')
                myResolution = '640 x 360';
            else if( myNum === '480')
                myResolution = '849 x 480';
            else if( myNum === '720')
                myResolution = '1280 x 720';
            else if( myNum === '1080')
                myResolution = '1920 x 1080';
            return myResolution
        }
    }

    // The function simplifiedUnits(input), converts the number input to Bits.
    var units = ['B', 'kB', 'MB', 'TB'];
    function simplifiedUnits(input) {
        var unit = units[0];
        var i = 0;
        while (input > 1024 && ++i) {
            unit = units[i];
            input /= 1024;
        }
        return Math.round(input) + " " + unit;
    }
