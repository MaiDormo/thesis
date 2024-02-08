#!/bin/bash

# Define the URL of the zip file
local url="https://download.blender.org/demo/movies/BBB/bbb_sunflower_2160p_30fps_normal.mp4.zip"
local base_name="bbb_sunflower_2160p_30fps_normal"

# Download and extract the zip file
wget "$url" -O "${base_name}.zip" && unzip "${base_name}.zip" && rm "${base_name}.zip"

# Rename the video
mv "${base_name}.mp4" "${base_name}_original.mp4"

# Trim the video to  5 minutes
ffmpeg -ss "00:00:00" -i "${base_name}_original.mp4" -t "00:05:00" -c copy "${base_name}.mp4"

# Remove the original video
rm "${base_name}_original.mp4"