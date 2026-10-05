#!/usr/bin/env bash
# Cinemagraph: freeze the whole frame, keep one local motion, ping-pong for a
# seamless loop.  Usage: cinemagraph.sh <clip> <out-prefix> [start-seconds] [width]
set -euo pipefail
clip="$1"; out="$2"; ss="${3:-3}"; W="${4:-3840}"
H=$(( W * 9 / 16 ))
d="$(dirname "$out")"; b="$d/.cine-$(basename "$out")"; mkdir -p "$b"
scale="scale=${W}:${H}:flags=lanczos,setsar=1"

ffmpeg -loglevel error -y -ss "$ss" -t 6 -i "$clip" -an -vf "$scale" \
  -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p "$b/vid.mp4"
ffmpeg -loglevel error -y -ss 1 -i "$b/vid.mp4" -frames:v 1 "$b/base.png"
ffmpeg -loglevel error -y -i "$b/vid.mp4" -vf \
  "tblend=all_mode=difference,format=gray,lutyuv=y='if(gt(val,14),255,0)',tmix=frames=50,lutyuv=y='if(gt(val,8),255,0)',gblur=sigma=4" \
  -frames:v 1 "$b/mask.png"
# alphamerge + overlay keeps RGB; maskedmerge would silently grey the frame.
ffmpeg -loglevel error -y -loop 1 -t 5 -i "$b/base.png" -t 5 -i "$b/vid.mp4" -loop 1 -t 5 -i "$b/mask.png" \
  -filter_complex "[2:v]format=gray[mk];[1:v]format=yuva420p,${scale}[fg];[fg][mk]alphamerge[fa];[0:v]${scale}[bg];[bg][fa]overlay=format=auto:shortest=1,format=yuv420p[out]" \
  -map "[out]" -an -r 24 -c:v libx264 -crf 22 -preset medium -pix_fmt yuv420p "$b/fwd.mp4"
ffmpeg -loglevel error -y -i "$b/fwd.mp4" -t 4.5 -c:v libx264 -crf 24 -preset medium -pix_fmt yuv420p "$b/fwd2.mp4"
ffmpeg -loglevel error -y -i "$b/fwd2.mp4" -vf reverse -an -c:v libx264 -crf 24 -preset medium -pix_fmt yuv420p "$b/rev2.mp4"
printf "file '%s'\nfile '%s'\n" "$b/fwd2.mp4" "$b/rev2.mp4" > "$b/list.txt"
ffmpeg -loglevel error -y -f concat -safe 0 -i "$b/list.txt" -c copy -movflags +faststart "$out.mp4"
kb=$(du -k "$out.mp4" | cut -f1)
if [ "$kb" -gt 14000 ]; then   # module hard limit is 15 MB
  ffmpeg -loglevel error -y -i "$out.mp4" -t 4 -vf "scale=3072:-2" -c:v libx264 -crf 27 -preset medium -pix_fmt yuv420p "$out.small.mp4"
  mv "$out.small.mp4" "$out.mp4"; kb=$(du -k "$out.mp4" | cut -f1)
fi
ffmpeg -loglevel error -y -ss 0.3 -i "$out.mp4" -frames:v 1 -vf "scale=1920:-2" -q:v 4 "$out-poster.jpg"
echo "$out.mp4  ${kb}KB  poster=$out-poster.jpg"
