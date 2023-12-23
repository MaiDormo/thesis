// client.js
const url = 'http://127.0.0.1:1337/bbb_sunflower_1080p_30fps_normal.mpd';
const player = dashjs.MediaPlayer().create();
const resolutions = ['320x180', '480x270', '640x360', '768x432', '940x540', '1024x576', '1280x720', '1920x1080']; 

let downloadRates = [];
let actualResolutions = [];
let bufferLengths = [];
let bitrates = [];
let downloadLatencies = [];
let droppedFrames = [];

document.addEventListener('DOMContentLoaded', () => {
    const video = document.querySelector('#videoPlayer');
    player.initialize(video, url);
    player.updateSettings({
        'debug': {
            'logLevel': dashjs.Debug.LOG_LEVEL_NONE
        },
    });
});

player.on(dashjs.MediaPlayer.events.FRAGMENT_LOADING_COMPLETED, logDownloadRate);
player.on(dashjs.MediaPlayer.events.QUALITY_CHANGE_RENDERED, logActualResolution);

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
                        return resolutions[context];
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


function logDownloadRate(e) {
    if (e.request.type === 'MediaSegment') {
        const downloadRate = (e.request.bytesTotal * 8) / (e.request.duration * 1000000); // Convert to Mbps
        downloadRates.push(downloadRate);
        downloadLatencies.push(e.request.duration); // Add download latency
        updateChart();
    }
}

function getBitrateForQuality(mediaType, qualityIndex) {
    const bitrateList = player.getBitrateInfoListFor(mediaType);
    if (!bitrateList || bitrateList.length <= qualityIndex) {
        console.error('Invalid quality index or bitrate list');
        return null;
    }
    return bitrateList[qualityIndex].bandwidth;
}

function logActualResolution(e) {
    const actualResolution = player.getQualityFor(e.mediaType);
    if (actualResolution === null) {
        console.error('Could not get actual resolution');
        return;
    }

    actualResolutions.push(actualResolution);
    bufferLengths.push(player.getBufferLength()); // Add buffer length

    const currentBitrate = getBitrateForQuality(e.mediaType, actualResolution);
    if (currentBitrate !== null) {
        bitrates.push(currentBitrate); // Add bitrate
    }

    const video = document.querySelector('#videoPlayer');
    const droppedFrameCount = video.webkitDroppedFrameCount;
    if (droppedFrameCount !== null) {
        droppedFrames.push(droppedFrameCount); // Add dropped frames
    }

    console.log('Resolution:', actualResolution);
    console.log('Actual Resolution:', resolutions[actualResolution]); // Print the resolution to the console
    console.log('Bitrate:', currentBitrate);
    console.log('Dropped Frames:', droppedFrameCount);
    updateChart();
}

// ... rest of the code remains the same ...




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
                    label: 'Download Latency',
                    data: [],
                    borderColor: 'rgb(255, 0, 0)',
                    fill: false
                },
                {
                    label: 'Dropped Frames',
                    data: [],
                    borderColor: 'rgb(255, 255, 0)',
                    fill: false
                }
            ]
        },
        scales: {
            xAxes: [{
                ticks: {
                    callback: (value) => {
                        const minutes = Math.floor(value / 60);
                        const seconds = value % 60;
                        return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
                    }
                }
            }],
        }
    });
}

function createResolutionChart(resolutionCtx) {
    return new Chart(resolutionCtx, config);
}


function updateChart() {
    if (downloadRates.length > 0 && bufferLengths.length > 0 && bitrates.length > 0 && downloadLatencies.length > 0 && droppedFrames.length > 0) {
        chart.data.labels.push(player.time());
        chart.data.datasets[0].data.push(downloadRates[downloadRates.length - 1]);
        chart.data.datasets[1].data.push(bufferLengths[bufferLengths.length - 1]);
        chart.data.datasets[2].data.push(bitrates[bitrates.length - 1]);
        chart.data.datasets[3].data.push(downloadLatencies[downloadLatencies.length - 1]);
        chart.data.datasets[4].data.push(droppedFrames[droppedFrames.length - 1]);
        chart.update();
    }

    if (actualResolutions.length > 0) {
        resolutionChart.data.labels.push(player.time());
        resolutionChart.data.datasets[0].data.push(actualResolutions[actualResolutions.length - 1]);
        resolutionChart.update();
    }
}