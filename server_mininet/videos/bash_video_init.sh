#!/bin/bash

# Define the URL of the zip file
url="https://download.blender.org/demo/movies/BBB/bbb_sunflower_2160p_30fps_normal.mp4.zip"

# Download the zip file
wget $url

# Extract the zip file
unzip bbb_sunflower_2160p_30fps_normal.mp4.zip

# Rename the video
mv bbb_sunflower_2160p_30fps_normal.mp4 bbb_sunflower_2160p_30fps_normal_original.mp4

# Run the ffmpeg command
ffmpeg -ss 00:00:00 -i bbb_sunflower_2160p_30fps_normal_original.mp4 -t 00:05:00 -c copy bbb_sunflower_2160p_30fps_normal.mp4

# Remove the original video and the zip file
rm bbb_sunflower_2160p_30fps_normal_original.mp4
rm file.zip