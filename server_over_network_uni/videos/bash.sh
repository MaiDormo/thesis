# create a bash script to convert every mp4 file in the current folder
# and subfolder to a multi-bitrate video in MP4-DASH format

# in the beginning, we find the current directory name and save it in a variable
MYDIR=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
SAVEDIR=$(pwd)

# then we check wether the needed programs, ffmpeg and MP4Box, are installed.
# if not, a message appears in the terminal informing the user.
if [ -z "$(which x264)" ]; then
    echo "Error: x264 is not installed"
    exit 1
fi

if [ -z "$(which MP4Box)" ]; then
    echo "Error: MP4Box is not installed"
    exit 1
fi

# next we change directory
cd $MYDIR

# Then, there is the main part of the script. We find all the .mp4 files in the
# current folder and subfolders. We save the name of each file without its extension
# (.mp4 or .mov) and we start converting each file to a multi-bitrate video in MPEG-DASH format.
TARGET_FILES=$(find ./ -maxdepth 1 -type f \( -name "*.mp4" -o -name "*.mov" \))

echo "Converting files in $(pwd)"

for f in $TARGET_FILES
do
    fe=$(basename "$f") # full name of the file
    f="${fe%.*}" # name without extension

    if [ ! -d "${f}" ]; then # if the folder does not exist, convert 
        echo "Converting \"$f\" to multi-bitrate video in MPEG-DASH"
        
        # ffmpeg -y -i "${fe}" -vn -c:a copy "${f}_audio.m4a"
        # ffmpeg -y -i "${fe}" -preset slow -tune film -vsync passthrough -an -c:v libx264 -x264opts 'keyint=25:min-keyint=25:no-scenecut' -crf 22 -maxrate 5000k -bufsize 12000k -pix_fmt yuv420p -f mp4 "${f}_5000.mp4"
        # ffmpeg -y -i "${fe}" -preset slow -tune film -vsync passthrough -an -c:v libx264 -x264opts 'keyint=25:min-keyint=25:no-scenecut' -crf 23 -maxrate 3000k -bufsize 6000k -pix_fmt yuv420p -f mp4  "${f}_3000.mp4"
        # ffmpeg -y -i "${fe}" -preset slow -tune film -vsync passthrough -an -c:v libx264 -x264opts 'keyint=25:min-keyint=25:no-scenecut' -crf 23 -maxrate 1500k -bufsize 3000k -pix_fmt yuv420p -f mp4   "${f}_1500.mp4"
        # ffmpeg -y -i "${fe}" -preset slow -tune film -vsync passthrough -an -c:v libx264 -x264opts 'keyint=25:min-keyint=25:no-scenecut' -crf 23 -maxrate 800k -bufsize 2000k -pix_fmt yuv420p -vf "scale=-2:720" -f mp4  "${f}_800.mp4"
        # ffmpeg -y -i "${fe}" -preset slow -tune film -vsync passthrough -an -c:v libx264 -x264opts 'keyint=25:min-keyint=25:no-scenecut' -crf 23 -maxrate 400k -bufsize 1000k -pix_fmt yuv420p -vf "scale=-2:540" -f mp4  "${f}_400.mp4"
        
        
        #VARIANTE TROVATA NELLA TESI
        # ffmpeg -i "${fe}" -vn -c:a copy "${f}_audio.mp4"    
        # ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 5300k -maxrate 5300k -bufsize 10600k -vf 'scale=-1:1080' "${f}_1080.mp4"
        # ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 2400k -maxrate 2400k -bufsize 4800k -vf 'scale=-1:720' "${f}_720.mp4"
        # ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 1060k -maxrate 1060k -bufsize 2120k -vf 'scale=-1:478' "${f}_480.mp4"
        # ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 600k -maxrate 600k -bufsize 1200k -vf 'scale=-1:360' "${f}_360.mp4"
        # ffmpeg -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 260k -maxrate 260k -bufsize 520k -vf 'scale=-1:242' "${f}_242.mp4"

        # ffmpeg -y -i "${fe}" -vn -c:a aac -b:a 128k "${f}_audio.m4a"
        # ffmpeg -y -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 1500k -maxrate 1500k -bufsize 3000k -vf "scale=-1:720" "${f}_720.mp4"
        # ffmpeg -y -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 800k -maxrate 800k -bufsize 1600k -vf "scale=-1:540" "${f}_540.mp4"
        # ffmpeg -y -i "${fe}" -an -c:v libx264 -x264opts 'keyint=24:min-keyint=24:no-scenecut' -b:v 400k -maxrate 400k -bufsize 800k -vf "scale=-1:360" "${f}_360.mp4"
        
        
    #    # Convert to 1080p video
    #    ffmpeg -i "${fe}" -c:v h264_nvenc -preset p7 -rc vbr -b:v 6800k -maxrate:v 13600k -bufsize:v 27200k -vf "scale=1920:1080" -g 120 -keyint_min 120 -profile:v main -level 4.1 -pix_fmt yuv420p "${f}_1080.mp4"

    #    # Convert to 720p video
    #    ffmpeg -i "${fe}" -c:v h264_nvenc -preset p7 -rc vbr -b:v 5000k -maxrate:v 10000k -bufsize:v 20000k -vf "scale=1280:720" -g 120 -keyint_min 120 -profile:v main -level 4.1 -pix_fmt yuv420p "${f}_720.mp4"

    #    # Convert to 576p video
    #    ffmpeg -i "${fe}" -c:v h264_nvenc -preset p7 -rc vbr -b:v 3500k -maxrate:v 7000k -bufsize:v 14000k -vf "scale=1024:576" -g 120 -keyint_min 120 -profile:v main -level 4.1 -pix_fmt yuv420p "${f}_576.mp4"

    #    # Convert to 540p video
    #    ffmpeg -i "${fe}" -c:v h264_nvenc -preset p7 -rc vbr -b:v 3000k -maxrate:v 6000k -bufsize:v 12000k -vf "scale=960:540" -g 120 -keyint_min 120 -profile:v main -level 4.1 -pix_fmt yuv420p "${f}_540.mp4"

    #    # Convert to 432p video
    #    ffmpeg -i "${fe}" -c:v h264_nvenc -preset p7 -rc vbr -b:v 2000k -maxrate:v 4000k -bufsize:v 8000k -vf "scale=768:432" -g 120 -keyint_min 120 -profile:v main -level 4.1 -pix_fmt yuv420p "${f}_432.mp4"

    #    # Convert to 360p video
    #    ffmpeg -i "${fe}" -c:v h264_nvenc -preset p7 -rc vbr -b:v 1500k -maxrate:v 3000k -bufsize:v 6000k -vf "scale=640:360" -g 120 -keyint_min 120 -profile:v main -level 4.1 -pix_fmt yuv420p "${f}_360.mp4"

    #    # Convert to 270p video
    #    ffmpeg -i "${fe}" -c:v h264_nvenc -preset p7 -rc vbr -b:v 800k -maxrate:v 1600k -bufsize:v 3200k -vf "scale=480:270" -g 120 -keyint_min 120 -profile:v main -level 4.1 -pix_fmt yuv420p "${f}_270.mp4"

    #    # Convert to 180p video
    #    ffmpeg -i "${fe}" -c:v h264_nvenc -preset p7 -rc vbr -b:v 500k -maxrate:v 1000k -bufsize:v 2000k -vf "scale=320:180" -g 120 -keyint_min 120 -profile:v main -level 4.1 -pix_fmt yuv420p "${f}_180.mp4"


        	
        # x264 --output "${f}_720.264" --fps 24 --preset slow --bitrate 2400 --vbv-maxrate 4800 --vbv-bufsize 9600 --min-keyint 48 --keyint 48 --scenecut 0 --no-scenecut --pass 1 --video-filter "resize:width=1280,height=720" "${fe}"
        # create a 2160p video
        x264 --output "${f}_2160.264" --fps 30 --preset slow --bitrate 12000 --vbv-maxrate 24000 --vbv-bufsize 48000 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=3840,height=2160" "${fe}"

        #create a 1440p video
        x264 --output "${f}_1440.264" --fps 30 --preset slow --bitrate 8000 --vbv-maxrate 16000 --vbv-bufsize 32000 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=2560,height=1440" "${fe}"

        # Create a 1080p video
        x264 --output "${f}_1080.264" --fps 30 --preset slow --bitrate 6800 --vbv-maxrate 13600 --vbv-bufsize 27200 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=1920,height=1080" "${fe}"

        # Create a 720p video
        x264 --output "${f}_720.264" --fps 30 --preset slow --bitrate 5000 --vbv-maxrate 10000 --vbv-bufsize 20000 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=1280,height=720" "${fe}"

        # Create a 576p video
        x264 --output "${f}_576.264" --fps 30 --preset slow --bitrate 3500 --vbv-maxrate 7000 --vbv-bufsize 14000 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=1024,height=576" "${fe}"

        # Create a 540p video
        x264 --output "${f}_540.264" --fps 30 --preset slow --bitrate 3000 --vbv-maxrate 6000 --vbv-bufsize 12000 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=960,height=540" "${fe}"

        # Create a 432p video
        x264 --output "${f}_432.264" --fps 30 --preset slow --bitrate 2000 --vbv-maxrate 4000 --vbv-bufsize 8000 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=768,height=432" "${fe}"

        # Create a 360p video
        x264 --output "${f}_360.264" --fps 30 --preset slow --bitrate 1500 --vbv-maxrate 3000 --vbv-bufsize 6000 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=640,height=360" "${fe}"

        # Create a 270p video
        x264 --output "${f}_270.264" --fps 30 --preset slow --bitrate 800 --vbv-maxrate 1600 --vbv-bufsize 3200 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=480,height=270" "${fe}"

        # Create a 180p video
        x264 --output "${f}_180.264" --fps 30 --preset slow --bitrate 500 --vbv-maxrate 1000 --vbv-bufsize 2000 --keyint 120 --min-keyint 120 --no-scenecut --pass 1 --video-filter "resize:width=320,height=180" "${fe}"

        Add the videos to MP4Box
        for res in 2160 1440 1080 720 576 540 432 360 270 180; do
            MP4Box -add "${f}_${res}.264" -fps 30 "${f}_${res}.mp4"
        done

        # MP4Box -dash 4000 -frag 4000 -rap -profile "dashavc264:live" -segment-duration 4000 -out "${f}.mpd" "${f}_1080.mp4" "${f}_720.mp4" "${f}_576.mp4" "${f}_540.mp4" "${f}_432.mp4" "${f}_360.mp4" "${f}_270.mp4" "${f}_180.mp4"
        # echo "Finished converting \"$f\""
        # rm -f ffmpeg*log*

        # Then, the Media Presentation Description (MPD) file is generated.
        # The MPD file stores all the data for the current project in a database format.
        # if [ -e "${f}_audio.mp4" ]; then
        # if [-e "${f}_audio.m4a"]; then
        #     echo "generating mpd"
            
            #VARIANTE TROVATA NELLA TESI
            # MP4Box -dash 1000 -rap -frag-rap -profile onDemand "${f}_1080.mp4" "${f}_720.mp4" "${f}_480.mp4" "${f}_360.mp4" "${f}_242.mp4" "${f}_audio.mp4" -out "${f}.mpd"

            # MP4Box -dash 2000 -rap -frag-rap -bs-switching no -profile "dashavc264:live" -out "${f}.mpd" "${f}_720.mp4" "${f}_540.mp4" "${f}_360.mp4" "${f}_audio.m4a"

            # MP4Box -dash 1000 -rap -frag-rap -bs-switching no -profile "dashavc264:onDemand" -out "${f}.mpd" "${f}_720.mp4" "${f}_540.mp4" "${f}_360.mp4" "${f}_audio.m4a"
            
            # MP4Box -dash 4000 -frag 4000 -rap -segment-name segment_ -out bigbuck.mpd bigbuck_out_720.mp4 bigbuck_out_540.mp4 bigbuck_out_360.mp4 
            # MP4Box -dash 4000 -frag 4000 -rap -profile "dashavc264:live" -out bigbuck.mpd bigbuck_720.mp4 bigbuck_540.mp4 bigbuck_360.mp4
            MP4Box -dash 4000 -frag 4000 -rap -profile "dashavc264:live" -out "${f}.mpd" "${f}_2160.mp4" "${f}_1440.mp4" "${f}_1080.mp4" "${f}_720.mp4" "${f}_576.mp4" "${f}_540.mp4" "${f}_432.mp4" "${f}_360.mp4" "${f}_270.mp4" "${f}_180.mp4"

            # MP4Box -dash-strict 2000 -rap -frag-rap -bs-switching no -profile "dashavc264:live" -out "bigbuck.mpd" "bigbuck_720.mp4" "bigbuck_540.mp4" "bigbuck_360.mp4" "bigbuck_audio.m4a"
            
            # MP4Box -dash 2000 -rap -frag-rap  -bs-switching no -profile "dashavc264:live" "${f}_5000.mp4" "${f}_3000.mp4" "${f}_1500.mp4" "${f}_800.mp4" "${f}_400.mp4" "${f}_audio.m4a" -out "${f}.mpd" 
            # rm "${f}_5000.mp4" "${f}_3000.mp4" "${f}_1500.mp4" "${f}_800.mp4" "${f}_400.mp4" "${f}_audio.m4a"

            echo "finished generating mpd"
        # else
        #     echo "no audio found"
            
        #     MP4Box -dash 1000 -rap -frag-rap -profile onDemand "${f}_1080.mp4" "${f}_720.mp4" "${f}_480.mp4" "${f}_360.mp4" "${f}_242.mp4" -out "${f}.mpd"
        # fi
    fi
done

