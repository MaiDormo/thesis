const URL = 'http://localhost:1337/bbb_sunflower_2160p_30fps_normal.mpd';
const RESOLUTIONS = ['320x180', '480x270', '640x360', '768x432', '940x540', '1024x576', '1280x720', '1920x1080', '2560x1440', '3840x2160'];
const BITS_IN_MEGABIT = 1000000;

let downloadRates = [];
let actualResolutions = [];
let bufferLengths = [];
let bitrates = [];
let droppedFrames = [];
let effectiveBitrates = [];

//download rate sliding window
let lastThreePackets = [];

let csvData = {
    'data.csv': '',
    'resolutionData.csv': '',
    'droppedFrames.csv': ''
};
//calculate download rate
let totalBytesReceived = 0;
let startTime = Date.now();
let totalRequests = 0;
let totalFrames = 0;

const player = createPlayer();

document.addEventListener('DOMContentLoaded', initializePlayer);
document.getElementById('downloadButton').addEventListener('click', downloadAllCSVs);


function createPlayer() {
    const player = dashjs.MediaPlayer().create();
    // player.on(dashjs.MediaPlayer.events.FRAGMENT_LOADING_COMPLETED, logDownloadRate);
    player.on(dashjs.MediaPlayer.events.FRAGMENT_LOADING_COMPLETED, logDownloadRateSlidingWindow);  
    player.on(dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED, logMoreData);
    player.on(dashjs.MediaPlayer.events["PLAYBACK_PAUSED"], function () {
        clearInterval(eventPoller);
        clearInterval(bitrateCalculator);
    });
    return player;
}


function initializePlayer() {
    const video = document.querySelector('#videoPlayer');
    player.initialize(video, URL);
    // Create CSV files and write headers
    csvData['data.csv'] = 'Time,Download Rate,Buffer Length,Bitrate,Effective Bitrate\n';
    csvData['resolutionData.csv'] = 'Time,Resolution\n';
    csvData['droppedFrames.csv'] = 'Time,Dropped Frames\n';

}

const config = {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'Actual Resolution',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                fill: false
            }
        ]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    maxTicksLimit: 8,
                    callback: (context) => {
                        return RESOLUTIONS[context];
                    }
                }
            }
        }
    }
};

const ctx = document.getElementById('myChart').getContext('2d');
const chart = createChart(ctx);
const resolutionCtx = document.getElementById('resolutionChart').getContext('2d');
const resolutionChart = createResolutionChart(resolutionCtx);
const droppedFramesCtx = document.getElementById('droppedFramesChart').getContext('2d');
const droppedFramesChart = createDroppedFramesChart(droppedFramesCtx);

const video = document.querySelector('#videoPlayer');

if (video.webkitVideoDecodedByteCount !== undefined) {
    var lastDecodedByteCount = 0;
    const bitrateInterval = 1;
    var bitrateCalculator = setInterval(function () {
        var calculatedBitrate = (((video.webkitVideoDecodedByteCount - lastDecodedByteCount) / 1000**2) * 8) / bitrateInterval;
        effectiveBitrates.push(calculatedBitrate);
        lastDecodedByteCount = video.webkitVideoDecodedByteCount;
    }, bitrateInterval * 1000);
}

function logDownloadRate(e) {
    if (e.request.type === 'MediaSegment') {
        totalBytesReceived += e.request.bytesTotal;
        totalRequests++;
        const elapsedTime = (Date.now() - startTime) / 1000; // in seconds
        const downloadRate = (totalBytesReceived * 8) / (elapsedTime * BITS_IN_MEGABIT); // Convert to Mbps
        downloadRates.push(downloadRate);
    } 
}

function logDownloadRateSlidingWindow(e) {
    if (e.request.type === 'MediaSegment') {
        const elapsedTime = (Date.now() - startTime) / 1000; // in seconds
        const downloadRate = (e.request.bytesTotal * 8) / (elapsedTime * BITS_IN_MEGABIT); // Convert to Mbps


        // Add the new packet to the array
        lastThreePackets.push({time: Date.now(), rate: downloadRate});

        // Remove the oldest packet if there are more than three packets
        if (lastThreePackets.length > 1) {
            lastThreePackets.shift();
        }

        // Calculate the average download rate of the last three packets
        const totalRate = lastThreePackets.reduce((sum, packet) => sum + packet.rate, 0);
        const avgRate = totalRate / lastThreePackets.length;

        // Add the average download rate to the array
        downloadRates.push(avgRate);

        // Update the start time to the current time
        startTime = Date.now();
    }
}


var eventPoller = setInterval(function () { 
    var streamInfo = player.getActiveStream().getStreamInfo();
    var dashMetrics = player.getDashMetrics();
    var dashAdapter = player.getDashAdapter();

    if (dashMetrics && streamInfo) {
        const periodIdx = streamInfo.index;
        var repSwitch = dashMetrics.getCurrentRepresentationSwitch('video', true);
        var bufferLevel = dashMetrics.getCurrentBufferLevel('video', true);
        var adaptation = dashAdapter.getAdaptationForType(periodIdx, 'video', streamInfo);
        var currentRep = adaptation.Representation_asArray.find(function (rep) {
            return rep.id === repSwitch.to
        })
        bufferLengths.push(bufferLevel); // Add buffer length
        updateChart();
    }
}, 1000);

function logMoreData(e) {
    
    const actualResolution = player.getQualityFor(e.mediaType);
    if (actualResolution === null) {
        console.error('Could not get actual resolution');
        return;
    }

    actualResolutions.push(actualResolution);

    const bitrateInfoList = player.getBitrateInfoListFor('video');
    if (bitrateInfoList) {
        const match = bitrateInfoList.find(b => b.qualityIndex === actualResolution);
        const currentBitrate = match ? match.bitrate : undefined;

        if (currentBitrate !== null) {
            bitrates.push(currentBitrate / BITS_IN_MEGABIT); // Add bitrate
        } else {
            console.error('Could not get bitrate for quality index ' + actualResolution);
            return;
        }
    }

    const video = document.querySelector('#videoPlayer');
    const droppedFrameCount = player.getDashMetrics().getCurrentDroppedFrames(video);
    if (droppedFrameCount !== null) {
        droppedFrames.push(droppedFrameCount.droppedFrames); // Add dropped frames
    }

    // const downloadLatency = player.getCurrentLiveLatency();
    // downloadLatencies.push(downloadLatency); // Add download latency
    //updateChart();
}





function createChart(ctx) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Download Rate',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    fill: false
                },
                {
                    label: 'Buffer Length',
                    data: [],
                    borderColor: 'rgb(0, 0, 255)',
                    fill: false
                },
                {
                    label: 'Bitrate',
                    data: [],
                    borderColor: 'rgb(0, 255, 0)',
                    fill: false
                },

                {
                    label: 'Effective Bitrate',
                    data: [],
                    borderColor: 'rgb(128, 0, 0)',
                    fill: false
                },
            ]
        },
    });
}

function createDroppedFramesChart(ctx) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Dropped Frames',
                    data: [],
                    borderColor: 'rgb(236, 124, 32)',
                    fill: false
                }
            ]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function createResolutionChart(resolutionCtx) {
    return new Chart(resolutionCtx, config);
}


function updateChart() {
    const arrays = [downloadRates, bufferLengths, bitrates, effectiveBitrates];
    if (arrays.every(array => array.length > 0)) {
        const currentTime = player.convertToTimeCode(player.time());
        pushDataToChart(chart, currentTime, arrays);
        pushDataToResolutionChart(resolutionChart, currentTime, actualResolutions);
        pushDataToDroppedFramesChart(droppedFramesChart, currentTime, droppedFrames);
        writeDataToCSV(currentTime, arrays);
        writeResolutionDataToCSV(currentTime, actualResolutions);
        writeDroppedFramesToCSV(currentTime, droppedFrames);
    }
}

function pushDataToChart(chart, currentTime, dataArrays) {
    chart.data.labels.push(currentTime);
    dataArrays.forEach((dataArray, index) => {
        chart.data.datasets[index].data.push(getLastElement(dataArray));
    });
    chart.update();
}

function pushDataToResolutionChart(chart, currentTime, actualResolutions) {
    chart.data.labels.push(currentTime);
    chart.data.datasets[0].data.push(getLastElement(actualResolutions));
    chart.update();
}

function pushDataToDroppedFramesChart(chart, currentTime, droppedFrames) {
    chart.data.labels.push(currentTime);
    chart.data.datasets[0].data.push(getLastElement(droppedFrames));
    chart.update();
}

function getLastElement(array) {
    return array[array.length - 1];
}

function writeDataToCSV(currentTime, arrays) {
    csvData['data.csv'] += `${currentTime},${arrays[0][arrays[0].length - 1]},${arrays[1][arrays[1].length - 1]},${arrays[2][arrays[2].length - 1]},${arrays[3][arrays[3].length - 1]}\n`;
}

function writeResolutionDataToCSV(currentTime, actualResolutions) {
    csvData['resolutionData.csv'] += `${currentTime},${RESOLUTIONS[actualResolutions[actualResolutions.length - 1]]}\n`;
}

function writeDroppedFramesToCSV(currentTime, droppedFrames) {
    csvData['droppedFrames.csv'] += `${currentTime},${droppedFrames[droppedFrames.length - 1]}\n`;
}

function downloadCSV(filename) {
    var element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(csvData[filename]));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Call this function when you have collected all the data
function downloadAllCSVs() {
    downloadCSV('data.csv');
    downloadCSV('resolutionData.csv');
    downloadCSV('droppedFrames.csv');
}