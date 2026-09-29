#!/bin/bash
# rhwp SVG 페이지들을 크롬 헤드리스로 PNG 렌더링: svg2png.sh <svg폴더> <png폴더> [scale]
set -e
SRC=$1; DST=$2; SCALE=${3:-1}
CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome
mkdir -p "$DST"
for f in "$SRC"/*.svg; do
  b=$(basename "$f" .svg)
  w=$(grep -o 'width="[0-9.]*' "$f" | head -1 | cut -d'"' -f2)
  h=$(grep -o 'height="[0-9.]*' "$f" | head -1 | cut -d'"' -f2)
  "$CHROME" --headless=new --no-sandbox --disable-gpu --hide-scrollbars --allow-file-access-from-files \
    --window-size=${w%.*},$(( ${h%.*} + 200 )) --force-device-scale-factor=$SCALE \
    --screenshot="$DST/$b.png" "file://$(realpath "$f")" >/dev/null 2>&1
  python3 -c "from PIL import Image; im=Image.open('$DST/$b.png'); im.crop((0,0,int($w*$SCALE),int($h*$SCALE))).save('$DST/$b.png')"
done
ls "$DST"
