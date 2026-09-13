import struct, collections, json

ROMD = r'C:\Users\swpar\AppData\Local\Temp\opencode\sm64kor\dsfiles'
fid = 646

d = open('%s\\f%04d.bin' % (ROMD, fid), 'rb').read()
cnt, sh = struct.unpack('<HH', d[0x20 + 8:0x20 + 12])
inf = 0x20 + 0x10 + cnt * 8
assert d[inf:inf+4] == b'1TAD'
dat = d[inf + 8:]

strings = []
for i in range(cnt):
    e = 0x20 + 0x10 + i * 8
    v0 = struct.unpack('<H', d[e:e+2])[0]
    # v1 has flags; offset used = v0 (matches our probe)
    raw = dat[v0:]
    end = raw.find(b'\xFF')
    if end < 0:
        end = len(raw)
    s = raw[:end]
    strings.append(s)

print('entry count:', cnt)
lens = [len(s) for s in strings]
print('len min/avg/max:', min(lens), sum(lens)//len(lens), max(lens))
print('nonempty:', sum(1 for l in lens if l > 0))

# byte frequency excluding terminator
freq = collections.Counter()
for s in strings:
    freq.update(s)
print('distinct dat1 bytes (excl FF):', len([b for b in freq if b != 0xFF]))

# structural split of bytes
ctl = [b for b in freq if b in (0xFC, 0xFD, 0xFE, 0x00, 0x01, 0x02)]
print('control-ish bytes present:', [hex(b) for b in sorted(ctl)])

# write per-entry hex to a local tsv (structural; tooling artifact)
with open(r'C:\Users\swpar\AppData\Local\Temp\opencode\sm64kor\kr_strings_hex.tsv', 'w', encoding='utf-8') as f:
    for i, s in enumerate(strings):
        f.write('%d\t%d\t%s\n' % (i, len(s), s.hex(' ')))
print('written kr_strings_hex.tsv')

# glyph usage: which byte codes actually appear (the alphabet set for KR)
used = sorted(b for b in freq if b != 0xFF)
print('used codes:', len(used))
print('ranges:', ' '.join('%02X-%02X' % (used[i], used[j]) for i, j in ranges(used) if False))

# report contiguous blocks
blocks = []
start = used[0]; prev = used[0]
for b in used[1:]:
    if b != prev + 1:
        blocks.append((start, prev))
        start = b
    prev = b
blocks.append((start, prev))
print('contiguous byte blocks:', ['%02X-%02X' % b for b in blocks])