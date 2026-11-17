#!/bin/sh
# Build a Switch 2 NRO in the reproducible ounce-devkit Docker image.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC=${SRC:-$HERE/.cache/ctrpad}
MODE=${MODE:-pal}
case "$MODE" in
  pal) PROFILE=ON; DEFAULT_VOLUME=ctr-switch2-build; DEFAULT_OUT="$HERE/out" ;;
  ntsc) PROFILE=OFF; DEFAULT_VOLUME=ctr-switch2-ntsc-build; DEFAULT_OUT="$HERE/out/ntsc" ;;
  *) echo "MODE must be pal or ntsc" >&2; exit 1 ;;
esac
VOLUME=${VOLUME:-$DEFAULT_VOLUME}
OUT=${OUT:-$DEFAULT_OUT}
IMAGE=${IMAGE:-ctr-kaihen-devkit:20261117}
BUILD_TYPE=${BUILD_TYPE:-Release}
if [ "${1:-}" = clean ]; then docker volume rm "$VOLUME" >/dev/null 2>&1 || true; exit 0; fi
[ -f "$SRC/CMakeLists.txt" ] || { echo "Run ./setup-source.sh first" >&2; exit 1; }
if [ "$MODE" = pal ]; then
    [ -f "$HERE/.cache/pal/pal_font_tables.h" ] || { echo "Run extract-pal.py with your PAL disc first" >&2; exit 1; }
    cp "$HERE/.cache/pal/pal_font_tables.h" "$SRC/include/pal_font_tables.h"
fi
mkdir -p "$OUT"
COMMIT=$(git -C "$SRC" rev-parse HEAD 2>/dev/null || echo 000000000000)
EXCLUDES="--exclude ./.git --exclude ./docs"
for d in "$SRC"/externals/SDL/*; do
    name=${d##*/}
    if [ "$name" != include ] && [ "$name" != LICENSE.txt ]; then EXCLUDES="$EXCLUDES --exclude ./externals/SDL/$name"; fi
done
# shellcheck disable=SC2086
(cd "$SRC" && COPYFILE_DISABLE=1 tar -cf - $EXCLUDES .) |
docker run --rm -i --platform linux/amd64 --network none \
    --mount "type=volume,src=$VOLUME,dst=/work" --mount "type=bind,src=$OUT,dst=/out" \
    -e BUILD_TYPE="$BUILD_TYPE" -e COMMIT="$COMMIT" -e PROFILE="$PROFILE" "$IMAGE" sh -lc '
        set -e
        mkdir -p /work/src /work/build
        tar -xf - -C /work/src
        . /opt/devkitpro/switch2vars.sh >/dev/null 2>&1
        aarch64-none-elf-cmake -S /work/src -B /work/build -G Ninja \
            -DCMAKE_BUILD_TYPE="$BUILD_TYPE" -DBUILD_TESTING=OFF -DCTR_SWITCH2_CTR_WEB_ASSETS="$PROFILE" \
            -DCTR_NATIVE_SOURCE_COMMIT="$COMMIT"
        cmake --build /work/build -j"$(nproc)"
        cp /work/build/ctr-native.nro /work/build/ctr-native.elf /out/
        ls -lh /out/ctr-native.nro
    '
