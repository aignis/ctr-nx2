"""Rebuild a PAL (SCES-02105) CTR BIGFILE.BIG into the NTSC-U (SCUS-94426) layout.

The PAL bigfile has 723 entries; NTSC-U has 608. Indices 0..453 match; PAL then
inserts localized boss heads and cutscenes. ctr-native hardcodes NTSC-U indices,
so we emit a 608-entry bigfile with the PAL file data placed at USA indices.

usage: pal2usa_bigfile.py PAL_BIGFILE.BIG OUT_BIGFILE.BIG [--lang es]
"""
import struct
import sys

SECTOR = 2048
USA_COUNT = 608
PAL_COUNT = 723

# USA lang file indices (234=ja 235=en 236=uk 237=fr 238=de 239=it 240=es 241=ne)
LANG_INDEX = {"ja": 234, "en": 235, "uk": 236, "fr": 237, "de": 238, "it": 239, "es": 240, "nl": 241}


def usa_to_pal():
    m = {}
    for i in range(0, 454):
        m[i] = i
    # boss heads: roo(450,451) joe(452,453) pin(454,455) papu(456,457) oxide(458,459)
    for k, pal in enumerate([450, 452, 464, 476, 488]):
        m[450 + 2 * k] = pal
        m[451 + 2 * k] = pal + 1
    # boss head lose
    for k, pal in enumerate([500, 502, 514, 526, 538]):
        m[460 + 2 * k] = pal
        m[461 + 2 * k] = pal + 1
    for i in range(470, 480):
        m[i] = i + 80  # boss bodies
    for i in range(480, 542):
        m[i] = i + 80  # VlcTable, thumbs, titles, cutscenes up to last_oxide_intro
    m[542], m[543] = 637, 638  # oxide01
    m[544], m[545] = 649, 650  # oxide02
    for i in range(546, 606):
        m[i] = i + 115  # credits
    m[606], m[607] = 721, 722
    assert sorted(m) == list(range(USA_COUNT))
    return m


def main():
    src, dst = sys.argv[1], sys.argv[2]
    lang = None
    if "--lang" in sys.argv:
        lang = sys.argv[sys.argv.index("--lang") + 1]
    with open(src, "rb") as f:
        data = f.read()
    zero, count = struct.unpack_from("<II", data, 0)
    assert count == PAL_COUNT, f"expected PAL bigfile with {PAL_COUNT} entries, got {count}"
    entries = [struct.unpack_from("<II", data, 8 + 8 * i) for i in range(count)]
    mapping = usa_to_pal()
    if lang:
        # the USA exe always loads en.lng; serve the chosen language in its slot
        mapping[LANG_INDEX["en"]] = LANG_INDEX[lang]

    header_size = 8 + 8 * USA_COUNT
    sector = (header_size + SECTOR - 1) // SECTOR
    out_entries = []
    blobs = []
    for i in range(USA_COUNT):
        psec, psize = entries[mapping[i]]
        blob = data[psec * SECTOR: psec * SECTOR + psize]
        out_entries.append((sector, psize))
        pad = (-psize) % SECTOR
        blobs.append(blob + b"\0" * pad)
        sector += (psize + pad) // SECTOR
    with open(dst, "wb") as o:
        hdr = struct.pack("<II", zero, USA_COUNT) + b"".join(struct.pack("<II", *e) for e in out_entries)
        o.write(hdr + b"\0" * ((-len(hdr)) % SECTOR))
        for b in blobs:
            o.write(b)
    print(f"wrote {dst}: {USA_COUNT} entries, {sector} sectors")


if __name__ == "__main__":
    main()
