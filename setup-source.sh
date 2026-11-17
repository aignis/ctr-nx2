#!/bin/sh
# Fetch the publicly available CTRPad base and apply this port's source changes.
set -eu
HERE=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SRC=${SRC:-$HERE/.cache/ctrpad}
URL=${CTR_SOURCE_URL:-https://github.com/chrissotraidis/ctrpad.git}
REV=d578636d
if [ -e "$SRC" ]; then
    echo "Source path already exists: $SRC (preserved)" >&2
    exit 1
fi
mkdir -p "$(dirname "$SRC")"
git clone --no-checkout "$URL" "$SRC"
git -C "$SRC" checkout --detach "$REV"
for patch in "$HERE"/patches/*.patch; do
    git -C "$SRC" apply --check "$patch"
    git -C "$SRC" apply "$patch"
done
printf 'Prepared CTRPad source at %s\n' "$SRC"
