#!/bin/bash
# 빌드 + rhwp 렌더 + PNG: preview.sh <작업폴더> <이름>
set -e
W=$1; N=${2:-lever}
cd "$W"
EQSIZE_BIN=/home/user/edwardkim/rhwp/target/release/examples/eqsize python3 /home/user/science/textbook/tools/build_lever.py fig out/$N.hwpx
rm -rf svg_$N png_$N
/home/user/edwardkim/rhwp/target/release/rhwp export-svg out/$N.hwpx -o svg_$N 2>&1 | grep -E "OVERFLOW:|OVERLAP|오류|error" | head -20 || true
bash /home/user/science/textbook/tools/svg2png.sh svg_$N png_$N 1.3 >/dev/null
ls png_$N | wc -l
