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

       # FFmpeg command to create DASH manifest and segments for multiple resolutions with a single audio track
       ffmpeg -re -i "${fe}" \
       -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a -map 0:v -map 0:a \
       -c:v libx264 -preset slow \
       -b:v:0 5000k -s:v:0 1920x1080 \
       -b:v:1 2800k -s:v:1 1280x720 \
       -b:v:2 1400k -s:v:2 854x480 \
       -b:v:3 800k -s:v:3 640x360 \
       -b:v:4 400k -s:v:4 320x180 \
       -c:a copy -b:a 128k \
       -keyint_min 120 -g 120 -sc_threshold 0 -b_strategy 0 \
       -use_timeline 1 -use_template 1 \
       -window_size 5 -adaptation_sets "id=0,streams=v id=1,streams=a" \
       -f dash "${f}_manifest.mpd"

       echo "Finished converting \"$f\""
   fi
done

# Change back to the original directory
cd $SAVEDIR