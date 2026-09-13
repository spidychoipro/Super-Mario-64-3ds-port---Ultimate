import ndspy.rom, ndspy.narc

rom = ndspy.rom.NintendoDSRom.fromFile('C:/Users/swpar/Downloads/Super Mario 64 DS (Korea).nds')
n = ndspy.narc.NARC(bytes(rom.files[106]))
b = n.files[14]


def rows(plane, off):
    t = b[off + plane * 0x20: off + plane * 0x20 + 0x20]
    r = []
    for y in range(8):
        s = ''
        for x in range(8):
            v = (t[y * 4 + x // 2] >> (4 * (1 - (x % 2)))) & 0xF
            s += '*' if v else ' '
        r.append(s)
    return r


def glyph(c):
    idx = ((c & 0x1f) + ((c & 0xe0) << 1))
    base = idx * 0x20
    return rows(0, base) + rows(1, base)


for c in range(0x40):
    out = glyph(c)
    print('C %02X' % c)
    hdr = '    '
    for r in out:
        print(hdr + r)