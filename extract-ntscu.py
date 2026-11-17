#!/usr/bin/env python3
"""Extract locally owned NTSC-U SCUS-94426 MODE2/2352 game data.
Usage: python3 -I extract-ntscu.py game-ntsc.bin [output-directory]
Outputs BIGFILE, KART.HWL, English XA, XA music, and TEST.STR."""
import os, struct, sys

RAW = 2352

def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    src = sys.argv[1]
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache', 'ntscu')
    f = open(src, 'rb')

    def data(lba, count):
        out = bytearray()
        for i in range(count):
            f.seek((lba + i) * RAW + 24)
            out += f.read(2048)
        return bytes(out)

    def form2(lba, count):
        out = bytearray()
        for i in range(count):
            f.seek((lba + i) * RAW + 16)
            out += f.read(2336)
        return bytes(out)

    pvd = data(16, 1)
    if pvd[1:6] != b'CD001':
        sys.exit('Not an ISO9660 MODE2/2352 image')
    files = {}

    def walk(lba, size, path):
        d = data(lba, (size + 2047) // 2048)
        i = 0
        while i < len(d):
            n = d[i]
            if n == 0:
                i = (i // 2048 + 1) * 2048
                continue
            e = d[i:i + n]
            name = e[33:33 + e[32]]
            i += n
            if name in (b'\0', b'\1'):
                continue
            name = path + '/' + name.decode().split(';')[0]
            elba, esize = struct.unpack_from('<I', e, 2)[0], struct.unpack_from('<I', e, 10)[0]
            if e[25] & 2:
                walk(elba, esize, name)
            else:
                files[name] = (elba, esize)

    walk(struct.unpack_from('<I', pvd, 158)[0], struct.unpack_from('<I', pvd, 166)[0], '')
    if not any(k.startswith('/SCUS_944.26') for k in files):
        sys.exit('Not the expected NTSC-U disc (SCUS_944.26 missing)')

    def save(rel, blob):
        p = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as out:
            out.write(blob)
        print(f'  {rel} ({len(blob)} bytes)')

    for path, (lba, size) in sorted(files.items()):
        sectors = (size + 2047) // 2048
        if path in ('/BIGFILE.BIG', '/SOUNDS/KART.HWL', '/XA/ENG.XNF'):
            save(path[1:], data(lba, sectors)[:size])
        elif path == '/TEST.STR':
            save(path[1:], form2(lba, sectors))
        elif path.startswith('/XA/ENG/') or path.startswith('/XA/MUSIC/'):
            save(path[1:], form2(lba, sectors))

if __name__ == '__main__':
    main()
