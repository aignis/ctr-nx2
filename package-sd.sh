#!/bin/sh
# Assemble one profile's SD-card directory from locally extracted assets.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
MODE=${MODE:-pal}
case "$MODE" in
  pal) DEFAULT_OUT="$HERE/out"; BIGFILE="$HERE/.cache/pal/BIGFILE.BIG"; PAL_XA="$HERE/.cache/pal/XA" ;;
  ntsc) DEFAULT_OUT="$HERE/out/ntsc"; BIGFILE="$HERE/.cache/ntscu/BIGFILE.BIG" ;;
  *) echo "MODE must be pal or ntsc" >&2; exit 1 ;;
esac
OUT=${OUT:-$DEFAULT_OUT}
DEST="$OUT/sd/switch/ctr-native"
NTSC="$HERE/.cache/ntscu"
for f in "$OUT/ctr-native.nro" "$BIGFILE" "$NTSC/SOUNDS/KART.HWL" "$NTSC/XA/ENG.XNF" "$NTSC/XA/MUSIC/S00.XA" "$NTSC/XA/MUSIC/S01.XA" "$NTSC/TEST.STR"; do
    [ -f "$f" ] || { echo "Missing $f; extract the required discs and build this profile first" >&2; exit 1; }
done
[ -d "$NTSC/XA/ENG/EXTRA" ] && [ -d "$NTSC/XA/ENG/GAME" ] || { echo "English XA voice files are missing" >&2; exit 1; }
if [ "$MODE" = pal ]; then
    [ -f "$PAL_XA/SPN.XNF" ] && [ -d "$PAL_XA/SPN/GAME" ] && [ -d "$PAL_XA/SPN/EXTRA" ] || { echo "Spanish XA voice files are missing" >&2; exit 1; }
fi
python3 -c 'import struct,sys; h=struct.unpack_from("<10i",open(sys.argv[1],"rb").read(40)); sys.exit(0 if h[0]==0x4c574f48 and h[5]==258 else "KART.HWL is not the expected NTSC-U bank")' "$NTSC/SOUNDS/KART.HWL"
mkdir -p "$DEST/assets/SOUNDS" "$DEST/assets/XA/MUSIC" "$DEST/assets/XA/ENG"
cp "$OUT/ctr-native.nro" "$DEST/ctr-native.nro"
cp "$BIGFILE" "$DEST/assets/BIGFILE.BIG"
cp "$NTSC/SOUNDS/KART.HWL" "$DEST/assets/SOUNDS/KART.HWL"
cp "$NTSC/TEST.STR" "$DEST/assets/TEST.STR"
cp "$NTSC/XA/ENG.XNF" "$DEST/assets/XA/ENG.XNF"
cp -R "$NTSC/XA/ENG/EXTRA" "$NTSC/XA/ENG/GAME" "$DEST/assets/XA/ENG/"
cp "$NTSC/XA/MUSIC/S00.XA" "$NTSC/XA/MUSIC/S01.XA" "$DEST/assets/XA/MUSIC/"
if [ "$MODE" = pal ]; then cp -R "$PAL_XA/." "$DEST/assets/XA/"; fi
printf 'Copy the contents of %s/sd/ to the root of the microSD card.\n' "$OUT"
du -sh "$DEST"
