#!/bin/bash

# Find the current directory name and save it in a variable
MYDIR=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
SAVEDIR=$(pwd)

# Check whether the needed programs, ffmpeg, are installed.
if [ -z "$(which ffmpeg)" ]; then
   echo "Error: ffmpeg is not installed"
   exit 1
fi

# Change directory
cd $MYDIR

# Find all the .mp4 files in the current folder and subfolders.
TARGET_FILES=$(find ./ -maxdepth 1 -type f \( -name "*.mp4" -o -name "*.mov" \))

echo "Converting files in $(pwd)"

for f in $TARGET_FILES
do
   fe=$(basename "$f") # full name of the file
   f="${fe%.*}" # name without extension

   if [ ! -d "${f}" ]; then # if the folder does not exist, convert
       echo "Converting \"$f\" to multi-bitrate video in MPEG-DASH"

       # FFmpeg command to create DASH manifest and segments for multiple resolutions
       ffmpeg -i "${fe}" \
       -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a \
       -s:v:0 1920x1080 -c:v:0 h264_nvenc -b:v:0 5000k \
       -s:v:1 1280x720 -c:v:1 h264_nvenc -b:v:1 2800k \
       -s:v:2 854x480 -c:v:2 h264_nvenc -b:v:2 1400k \
       -s:v:3 640x360 -c:v:3 h264_nvenc -b:v:3 800k \
       -s:v:4 320x180 -c:v:4 h264_nvenc -b:v:4 400k \
       -c:a:0 aac -b:a:0 128k -c:a:1 aac -b:a:1 128k -c:a:2 aac -b:a:2 128k -c:a:3 aac -b:a:3 128k -c:a:4 aac -b:a:4 128k \
       -var_stream_map "v:0,a:0 v:1,a:1 v:2,a:2 v:3,a:3 v:4,a:4" \
       -use_timeline 1 -use_template 1 \
       -adaptation_sets "id=0,streams=v id=1,streams=a" \
       -f dash "${f}_manifest.mpd"

      

       echo "Finished converting \"$f\""
   fi
done

# Change back to the original directory
cd $SAVEDIR