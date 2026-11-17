#!/usr/bin/env python3
"""Extract a locally owned PAL SCES-02105 MODE2/2352 disc.
Usage: python3 -I extract-pal.py game-pal.bin [output-directory]
Outputs the converted PAL BIGFILE and Spanish voices for the PAL profile."""
import os, struct, sys, subprocess

RAW = 2352

def main():
    if len(sys.argv) not in (2, 3):
        sys.exit(__doc__)
    src = sys.argv[1]
    dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '.cache', 'pal')
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
    if not any(k.startswith('/SCES_021.05') for k in files):
        sys.exit('Not the expected PAL disc (SCES_021.05 missing)')

    def save(rel, blob):
        p = os.path.join(dest, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, 'wb') as out:
            out.write(blob)
        print(f'  {rel} ({len(blob)} bytes)')

    required = ('/BIGFILE.BIG', '/XA/SPN.XNF', '/SCES_021.05')
    for path in required:
        if path not in files:
            sys.exit('Missing from PAL disc: ' + path)
    if not any(path.startswith('/XA/SPN/GAME/') for path in files) or not any(path.startswith('/XA/SPN/EXTRA/') for path in files):
        sys.exit('Spanish voice files are missing from the PAL disc')
    for path, (lba, size) in sorted(files.items()):
        sectors = (size + 2047) // 2048
        if path == '/BIGFILE.BIG':
            save('BIGFILE.PAL', data(lba, sectors)[:size])
        elif path in ('/XA/SPN.XNF', '/SCES_021.05'):
            save(path[1:], data(lba, sectors)[:size])
        elif path.startswith('/XA/SPN/'):
            save(path[1:], form2(lba, sectors))
    script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'tools', 'pal2usa_bigfile.py'))
    subprocess.run([sys.executable, '-I', script, os.path.join(dest, 'BIGFILE.PAL'), os.path.join(dest, 'BIGFILE.BIG'), '--lang', 'es'], check=True)
    # Keep original-game lookup tables local. Generate them from the user's
    # executable instead of distributing those bytes in this repository.
    exe_path = os.path.join(dest, 'SCES_021.05')
    with open(exe_path, 'rb') as exe_file:
        exe = exe_file.read()
    load_addr = struct.unpack_from('<I', exe, 0x18)[0]
    tables = [('s_nativeFontEurTilde', 0x80082948, 12),
              ('s_nativeFontEurInvertedMark', 0x80082968, 8),
              ('s_nativeFontEurOrdinal', 0x80082988, 8)]
    with open(os.path.join(dest, 'pal_font_tables.h'), 'w') as out:
        out.write('/* Generated locally from the user-provided PAL executable. */\n')
        for name, address, count in tables:
            values = struct.unpack_from('<' + 'h' * count, exe, address - load_addr + 0x800)
            out.write('static const s16 %s[%d] = {%s};\n' % (name, count, ', '.join(map(str, values))))
    os.remove(exe_path)


if __name__ == '__main__':
    main()
