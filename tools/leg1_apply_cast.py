#!/usr/bin/env python3
"""Apply the Leg 1 cast (cast.json from leg1_cast.py) to a pokefirered decomp tree.

usage: leg1_apply_cast.py DECOMP_DIR ART_DIR [cast.json]
  ART_DIR has one folder per FE8 name (back.png = 64x64 indexed crop, normal.pal), e.g. Seth/back.png. FE8 art is not in this repo.
Does:
  1. Unique FireRed characters (leaders, Elite Four, Giovanni, rival, Red, Oak): their trainer picture is replaced by the FE8 portrait.
  2. Every other character gets a NEW trainer picture (TRAINER_PIC_FE8_*) and takes over one trainer: new name, new picture.
  3. Names in dialogue (BROCK, OAK, BILL ...) are replaced inside string literals.
"""
import re, sys, os, json, shutil
from PIL import Image
D, ART = sys.argv[1], sys.argv[2]
cast = json.load(open(sys.argv[3] if len(sys.argv) > 3 else 'cast.json'))['cast']

def rd(p): return open(os.path.join(D, p)).read()
def wr(p, s): open(os.path.join(D, p), 'w').write(s)
def folder(n):
    return {'Frelian': 'Frelia_Knight', 'Vigarde': 'Vigarde_healthy'}.get(n, re.sub(r'[^A-Za-z0-9]', '_', n))
def art(n, variant=None):
    f = os.path.join(ART, variant or folder(n))
    return os.path.join(f, 'back.png'), os.path.join(f, 'normal.pal')

# --- map existing pic constants to their files
tables = rd('src/data/trainer_graphics/front_pic_tables.h'); gfx = rd('src/data/graphics/trainers.h')
spr = dict(re.findall(r'TRAINER_SPRITE\((\w+), (\w+),', tables)); pal = dict(re.findall(r'TRAINER_PAL\((\w+), (\w+)\)', tables))
paths = dict(re.findall(r'const u32 (\w+)\[\] = INCBIN_U32\("([^"]+)"\)', gfx))
def files(const):
    k = const.replace('TRAINER_PIC_', '')
    png = os.path.join(D, paths[spr[k]].replace('.4bpp.lz', '.png')); p = os.path.join(D, paths[pal[k]].replace('.gbapal.lz', '.pal'))
    return png, p
def install(const, name, variant=None):
    a, ap = art(name, variant); png, p = files(const)
    shutil.copy(a, png); shutil.copy(ap, p)

variants = {}  # Lyon's normal portrait is used for every rival picture
for n, c in cast.items():
    for pc in c['pics']:
        install(pc, n, variants.get(pc))

# --- new pictures for trainer-slot characters
consts = rd('include/constants/trainers.h')
last = max(int(x) for x in re.findall(r'#define TRAINER_PIC_\w+\s+(\d+)', consts))
newc, k = {}, last
add_const, add_gfx, add_ext, add_spr, add_pal, add_coord, add_anim = [], [], [], [], [], [], []
for n, c in sorted(cast.items()):
    if not c['trainer']: continue
    k += 1; key = re.sub(r'[^A-Z0-9]', '', n.upper()); const = 'TRAINER_PIC_FE8_' + key; newc[n] = const
    low = key.lower(); camel = 'FE8' + n.replace("'", '').replace(' ', '')
    a, ap = art(n)
    shutil.copy(a, os.path.join(D, f'graphics/trainers/front_pics/fe8_{low}_front_pic.png')); shutil.copy(ap, os.path.join(D, f'graphics/trainers/palettes/fe8_{low}.pal'))
    add_const.append('#define %-32s %d' % (const, k))
    add_gfx.append(f'const u32 gTrainerFrontPic_{camel}[] = INCBIN_U32("graphics/trainers/front_pics/fe8_{low}_front_pic.4bpp.lz");\nconst u32 gTrainerPalette_{camel}[] = INCBIN_U32("graphics/trainers/palettes/fe8_{low}.gbapal.lz");')
    add_ext.append(f'extern const u32 gTrainerFrontPic_{camel}[];\nextern const u32 gTrainerPalette_{camel}[];')
    add_spr.append(f'    TRAINER_SPRITE(FE8_{key}, gTrainerFrontPic_{camel}, 0x800),'); add_pal.append(f'    TRAINER_PAL(FE8_{key}, gTrainerPalette_{camel}),')
    add_coord.append('    {.size = 8, .y_offset = 1},'); add_anim.append(f'    [{const}] = sAnims_Painter,')
def ins_before_end(s, marker, lines, last_in_array=True):
    i = s.rindex(marker); return s[:i] + '\n'.join(lines) + '\n' + s[i:]
wr('include/constants/trainers.h', consts.replace('#define TRAINER_PIC_PAINTER               147\n', '#define TRAINER_PIC_PAINTER               147\n' + '\n'.join(add_const) + '\n', 1))
wr('src/data/graphics/trainers.h', gfx.rstrip('\n') + '\n' + '\n'.join(add_gfx) + '\n')
g = rd('include/graphics.h'); wr('include/graphics.h', g.replace('extern const u32 gTrainerFrontPic_Leaf[];', '\n'.join(add_ext) + '\nextern const u32 gTrainerFrontPic_Leaf[];', 1))
t = tables
# coords array
i = t.index('const struct MonCoords gTrainerFrontPicCoords[]'); j = t.index('};', i); t = t[:j] + '\n'.join(add_coord) + '\n' + t[j:]
i = t.index('const struct CompressedSpriteSheet gTrainerFrontPicTable[]'); j = t.index('};', i); t = t[:j] + '\n'.join(add_spr) + '\n' + t[j:]
i = t.index('const struct CompressedSpritePalette gTrainerFrontPicPaletteTable[]'); j = t.index('};', i); t = t[:j] + '\n'.join(add_pal) + '\n' + t[j:]
wr('src/data/trainer_graphics/front_pic_tables.h', t)
an = rd('src/data/trainer_graphics/front_pic_anims.h'); i = an.rindex('};'); wr('src/data/trainer_graphics/front_pic_anims.h', an[:i] + '\n'.join(add_anim) + '\n' + an[i:])

# --- trainer entries
tr = rd('src/data/trainers.h')
for n, c in cast.items():
    if not c['trainer']: continue
    m = re.search(r'(\[%s\] = \{.*?\n    \},)' % c['trainer'], tr, re.S); blk = m.group(1)
    nb = re.sub(r'\.trainerPic = \w+', '.trainerPic = ' + newc[n], blk)
    nb = re.sub(r'\.trainerName = _\("[^"]*"\)', '.trainerName = _("%s")' % n.upper(), nb)
    tr = tr.replace(blk, nb, 1)
wr('src/data/trainers.h', tr)

# --- names in dialogue (string literals only)
rep = [('PROF. OAK', 'MOULDER'), ('LT. SURGE', 'GILLIAM'), ('BROCK', 'SETH'), ('MISTY', 'MARISA'), ('ERIKA', 'VANESSA'), ('KOGA', 'COLM'), ('SABRINA', 'LUTE'),
       ('BLAINE', 'GARCIA'), ('GIOVANNI', 'VIGARDE'), ('LORELEI', 'SELENA'), ('BRUNO', 'BINKS'), ('AGATHA', 'SYRENE'), ('LANCE', 'VALTER'),
       ('OAK', 'MOULDER')]
def sub_names(line):
    for a, b in rep: line = re.sub(r'(?<![A-Za-z])' + re.escape(a) + r'(?![A-Za-z])', b, line)
    return line
count = 0
for root, _, fs in os.walk(D):
    if '/build' in root or '/.git' in root or 'tools' in root.split(os.sep)[-1:]: continue
    for f in fs:
        if not f.endswith(('.inc', '.h', '.c')): continue
        if not (root.startswith(os.path.join(D, 'data')) or root.startswith(os.path.join(D, 'src'))): continue
        p = os.path.join(root, f); s = open(p, errors='surrogateescape').read(); out = []
        for line in s.split('\n'):
            if '.string "' in line or ('_("' in line and not line.lstrip().startswith('//')):
                nl = sub_names(line)
                if nl != line: count += 1
                line = nl
            out.append(line)
        ns = '\n'.join(out)
        if ns != s: open(p, 'w', errors='surrogateescape').write(ns)
# item names have a 13 character limit
it = rd('src/data/items.h'); wr('src/data/items.h', it.replace("_(\"MOULDER'S PARCEL\")", '_("PARCEL")'))
print('new pics', len(newc), 'trainer slots, text lines changed', count)
