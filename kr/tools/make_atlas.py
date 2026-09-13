import ndspy.rom, ndspy.narc, struct
from PIL import Image, ImageDraw

ROMD = 'C:/Users/swpar/Downloads/Super Mario 64 DS (Korea).nds'
OUT = r'C:\Users\swpar\AppData\Local\Temp\opencode\sm64kor'
rom = ndspy.rom.NintendoDSRom.fromFile(ROMD)
n = ndspy.narc.NARC(bytes(rom.files[106]))
font = n.files[14]
pal_raw = bytes(rom.files[137])
pal = []
for i in range(256):
    v = struct.unpack_from('<H', pal_raw, i * 2)[0]
    r, g, b = (v & 0x1F), ((v >> 5) & 0x1F), ((v >> 10) & 0x1F)
    pal.append((int(r * 255 / 31), int(g * 255 / 31), int(b * 255 / 31), 255))


def glyph_px(c):
    idx = ((c & 0x1f) + ((c & 0xe0) << 1))
    base = idx * 0x20
    px = [[0] * 8 for _ in range(16)]
    for plane in (0, 1):
        t = font[base + plane * 0x20: base + plane * 0x20 + 0x20]
        for y in range(8):
            for x in range(8):
                v = (t[y * 4 + x // 2] >> (4 * (1 - (x % 2)))) & 0xF
                px[y + plane * 8][x] = v
    return px


def blit(img, px, ox, oy, pal, scale=2):
    for y in range(16):
        for x in range(8):
            v = px[y][x]
            if v:
                img.putpixel((ox + x * scale, oy + y), pal[v & 0xFF])


# atlas
im = Image.new('RGB', (16 * 20 + 2, 16 * 20 + 2), (24, 24, 24))
for c in range(256):
    px = glyph_px(c)
    blit(im, px, (c % 16) * 20 + 2, (c // 16) * 20 + 2, pal)
im.save(OUT + r'\kr_font_atlas_256.png')

# BMG
bmg = open(r'C:\Users\swpar\AppData\Local\Temp\opencode\sm64kor\dsfiles\f0646.bin', 'rb').read()
cnt, sh = struct.unpack('<HH', bmg[0x28:0x2C])
dat = bmg[0x20 + 0x10 + cnt * 8 + 8:]


def msg_codes(i):
    v0 = struct.unpack('<H', bmg[0x20 + 0x10 + i * 8: 0x20 + 0x10 + i * 8 + 2])[0]
    raw = dat[v0:]
    end = raw.find(b'\xFF')
    if end < 0:
        end = len(raw)
    return raw[:end]


used = set()
for i in range(cnt):
    used.update(msg_codes(i))
print('entries', cnt, 'distinct used codes', len(used))

CW, CH = 18, 18
LW = 60  # chars per line
PAGE_H = 46
PAGE_W = LW * CW
pages = []
cur = Image.new('RGB', (PAGE_W, 2000), (16, 16, 16))
cur_y = 0


def newpage():
    global cur, cur_y
    pages.append(cur.crop((0, 0, PAGE_W, min(cur_y + 1, 2000))))
    cur = Image.new('RGB', (PAGE_W, 2000), (16, 16, 16))
    cur_y = 0


ds = ImageDraw.Draw(cur)
meta = []
for i in range(cnt):
    codes = msg_codes(i)
    meta.append((i, len(codes), codes[:8].hex(' '), codes[-3:].hex(' ')))
    if cur_y + 2 * CH > 2000:
        newpage()
        ds = ImageDraw.Draw(cur)
    ds.text((0, cur_y), '[%04d]' % i, fill=(140, 220, 140))
    cur_y += CH
    col = 0
    for c in codes:
        if c == 0xFC:
            col += 1
            continue
        if c == 0xFD:
            col = LW
            cur_y += CH
        if col >= LW:
            col = 0
            cur_y += CH
            if cur_y + 2 * CH > 2000:
                newpage()
                ds = ImageDraw.Draw(cur)
        blit(cur, glyph_px(c), col * CW, cur_y, pal)
        col += 1
    cur_y += CH
    cur_y += 2

newpage()

import os
os.makedirs(OUT + r'\sheets', exist_ok=True)
for pi, pg in enumerate(pages):
    pg.save(OUT + r'\sheets\kr_sheet_p%02d.png' % pi)
print('pages:', len(pages))
with open(OUT + r'\kr_messages_meta.tsv', 'w', encoding='utf-8') as f:
    for m in meta:
        f.write('%d\t%d\t%s\t%s\n' % m)
uc = sorted(used)
print('used codes: %s' % ' '.join('%02X' % c for c in uc))