MYDIR=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
SAVEDIR=$(pwd)

# Function to check if a program is installed
check_installed() {
    if [ -z "$(which $1)" ]; then
        echo "Error: $1 is not installed"
        exit 1
    fi
}

# Function to create a video with a specific resolution and bitrate
create_video() {
    local resolution=$1
    local bitrate=$2
    local maxrate=$(($bitrate * 2))
    local bufsize=$(($maxrate * 2))
    local width=$3
    local height=$4

    x264 --output "${f}_${resolution}.264" --fps 30 --preset slow --bitrate $bitrate --vbv-maxrate $maxrate --vbv-bufsize $bufsize --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=$width,height=$height" "${fe}"
    MP4Box -add "${f}_${resolution}.264" -fps 30 "${f}_${resolution}.mp4"
}

# Function to convert a video to multiple bitrates
convert_video() {
    local resolutions=(2160 1440 1080 720 576 540 432 360 270 180)
    local bitrates=(12000 8000 6800 5000 3500 3000 2000 1500 800 500)
    local widths=(3840 2560 1920 1280 1024 960 768 640 480 320)
    local heights=(2160 1440 1080 720 576 540 432 360 270 180)

    for i in ${!resolutions[*]}
    do
        create_video ${resolutions[$i]} ${bitrates[$i]} ${widths[$i]} ${heights[$i]}
    done
}

check_installed x264
check_installed MP4Box

cd $MYDIR

TARGET_FILES=$(find ./ -maxdepth 1 -type f \( -name "*.mp4" -o -name "*.mov" \))

echo "Converting files in $(pwd)"

for f in $TARGET_FILES
do
    fe=$(basename "$f") # full name of the file
    f="${fe%.*}" # name without extension

    if [ ! -d "${f}" ]; then # if the folder does not exist, convert 
        echo "Converting \"$f\" to multi-bitrate video in MPEG-DASH"
    
        convert_video

        echo "Finished converting \"$f\""
        MP4Box -dash 4000 -frag 4000 -rap -profile "dashavc264:live" -out "${f}.mpd" "${f}_2160.mp4" "${f}_1440.mp4" "${f}_1080.mp4" "${f}_720.mp4" "${f}_576.mp4" "${f}_540.mp4" "${f}_432.mp4" "${f}_360.mp4" "${f}_270.mp4" "${f}_180.mp4"

        echo "finished generating mpd"
    fi
done