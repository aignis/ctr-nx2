#!/bin/sh
# Build the upstream Switch 2 toolchain image at a known revision.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
DEVKIT="$HERE/.cache/ounce-devkit"
REV=5e957599bd498643d82e5470aec80da67a12685d
if [ -e "$DEVKIT" ]; then
    echo "Toolchain checkout already exists: $DEVKIT (preserved)" >&2
    exit 1
fi
mkdir -p "$HERE/.cache"
git clone https://github.com/ouncebrew/ounce-devkit.git "$DEVKIT"
git -C "$DEVKIT" checkout --detach "$REV"
docker build --platform linux/amd64 -t ctr-kaihen-devkit:20261117 "$DEVKIT"
