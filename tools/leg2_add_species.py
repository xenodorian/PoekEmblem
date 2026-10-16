#!/usr/bin/env python3
"""Leg 2: add the 8 friendly NPCs as Pokemon species to a pokefirered decomp tree (Eirika must already be added).

usage: leg2_add_species.py DECOMP_DIR ART_DIR
  ART_DIR has one folder per character with back.png (64x64 indexed) and normal.pal/shiny.pal. FE8 art is not in this repo.
Each ally takes an unused old "?" species slot (252 onward), copies a base species' stats, TM/HM and tutor compatibility, gets its FE8 portrait as
front and back picture, a portrait icon, the base species' cry and footprint, and a learnset: the base species' moves plus the character's signature moves.
"""
import re, sys, os, shutil
import numpy as np
from PIL import Image
D, ART = sys.argv[1], sys.argv[2]
def rd(p): return open(os.path.join(D, p)).read()
def wr(p, s): open(os.path.join(D, p), 'w').write(s)
def sub1(p, old, new):
    s = rd(p); assert old in s, (p, old); wr(p, s.replace(old, new, 1))

# (constant, slot letter, display name, art folder, base species, gender, signature moves)
A = [
    ('INNES',    'B', 'INNES',     'Innes',     'FEAROW',    'MALE',   ['DRILL_PECK', 'FURY_ATTACK', 'FOCUS_ENERGY', 'AGILITY']),
    ('TANA',     'C', 'TANA',      'Tana',      'PIDGEOT',   'FEMALE', ['WING_ATTACK', 'GUST', 'QUICK_ATTACK', 'AGILITY']),
    ('LARACHEL', 'D', "L'ARACHEL", 'L_Arachel', 'CLEFABLE',  'FEMALE', ['SING', 'DOUBLE_SLAP', 'HEAL_BELL', 'MOONLIGHT']),
    ('DOZLA',    'E', 'DOZLA',     'Dozla',     'MACHAMP',   'MALE',   ['THUNDER_PUNCH', 'KARATE_CHOP', 'SUBMISSION', 'FOCUS_ENERGY']),
    ('JOSHUA',   'F', 'JOSHUA',    'Joshua',    'SCYTHER',   'MALE',   ['SLASH', 'WING_ATTACK', 'QUICK_ATTACK', 'SWORDS_DANCE']),
    ('DUESSEL',  'G', 'DUESSEL',   'Duessel',   'GOLEM',     'MALE',   ['ROCK_THROW', 'EARTHQUAKE', 'HARDEN', 'BODY_SLAM']),
    ('CORMAG',   'H', 'CORMAG',    'Cormag',    'DRAGONITE', 'MALE',   ['WING_ATTACK', 'SLASH', 'FLY', 'DRAGON_CLAW']),
    ('MYRRH',    'I', 'MYRRH',     'Myrrh',     'DRAGONAIR', 'FEMALE', ['DRAGON_RAGE', 'WRAP', 'AGILITY', 'THUNDER_WAVE']),
]
CRY_BASE = {a[0]: a[4] for a in A}

# species constants
s = rd('include/constants/species.h')
for c, slot, *_ in A:
    s = s.replace('#define SPECIES_OLD_UNOWN_%s ' % slot, '#define SPECIES_%s SPECIES_OLD_UNOWN_%s\n#define SPECIES_OLD_UNOWN_%s ' % (c, slot, slot), 1) if False else s
for c, slot, *_ in A:
    m = re.search(r'#define SPECIES_OLD_UNOWN_%s (\d+)\n' % slot, s)
    s = s.replace(m.group(0), m.group(0) + '#define SPECIES_%s SPECIES_OLD_UNOWN_%s\n' % (c, slot), 1)
wr('include/constants/species.h', s)

# icons: quantize the portraits into two shared icon palettes (4 icons each)
def portrait(folder):
    im = Image.open(os.path.join(ART, folder, 'back.png')); pal = np.array(im.getpalette()[:48], np.uint8).reshape(16, 3)
    idx = np.array(im); return pal[idx], idx != 0
def small(folder):
    rgb, mask = portrait(folder)
    sm = Image.fromarray(rgb).resize((32, 32), Image.LANCZOS); ms = Image.fromarray((mask * 255).astype(np.uint8)).resize((32, 32), Image.BOX)
    return np.array(sm), np.array(ms) > 127
smalls = {a[3]: small(a[3]) for a in A}
def hue(folder):
    rgb, m = smalls[folder]; px = rgb[m].astype(float); return np.arctan2(*(px.mean(0)[[1, 0]] - 0)) if len(px) else 0
order = sorted(A, key=lambda a: (smalls[a[3]][0][smalls[a[3]][1]].mean(0)[0] - smalls[a[3]][0][smalls[a[3]][1]].mean(0)[2]))
groups = [order[:4], order[4:]]
icon_pal_idx = {}
for gi, grp in enumerate(groups):
    sheet = Image.new('RGB', (32 * len(grp), 32)); maskall = []
    for k, a in enumerate(grp):
        rgb, m = smalls[a[3]]; sheet.paste(Image.fromarray(rgb), (32 * k, 0)); maskall.append(m)
    q = sheet.quantize(colors=15, method=Image.MEDIANCUT, dither=Image.NONE)
    qp = np.array(q.getpalette()[:45], np.uint8).reshape(15, 3); qi = np.array(q) + 1
    pal = [(255, 0, 255)] + [tuple(int(v) for v in c) for c in qp]
    n = 4 + gi
    open(os.path.join(D, f'graphics/pokemon/icon_palettes/icon_palette_{n}.pal'), 'w').write('JASC-PAL\n0100\n16\n' + '\n'.join('%d %d %d' % c for c in pal) + '\n')
    for k, a in enumerate(grp):
        idx = np.where(maskall[k], qi[:, 32 * k:32 * k + 32], 0).astype(np.uint8)
        f2 = np.zeros_like(idx); f2[1:] = idx[:-1]
        im = Image.fromarray(np.vstack([idx, f2]), 'P'); p = [v for c in pal for v in c]; im.putpalette(p + [0] * (768 - len(p)))
        os.makedirs(os.path.join(D, f'graphics/pokemon/{a[3].lower()}'), exist_ok=True); im.save(os.path.join(D, f'graphics/pokemon/{a[3].lower()}/icon.png'))
        icon_pal_idx[a[0]] = n
sub1('src/pokemon_icon.c', '    INCBIN_U16("graphics/pokemon/icon_palettes/icon_palette_3.gbapal")\n',
     '    INCBIN_U16("graphics/pokemon/icon_palettes/icon_palette_3.gbapal"),\n    INCBIN_U16("graphics/pokemon/icon_palettes/icon_palette_4.gbapal"),\n    INCBIN_U16("graphics/pokemon/icon_palettes/icon_palette_5.gbapal")\n')

# species info blocks, tm/hm, tutor, learnsets
info = rd('src/data/pokemon/species_info.h'); tm = rd('src/data/pokemon/tmhm_learnsets.h'); tut = rd('src/data/pokemon/tutor_learnsets.h')
ptrs = rd('src/data/pokemon/level_up_learnset_pointers.h'); lus = rd('src/data/pokemon/level_up_learnsets.h')
new_learnsets = ''
for c, slot, disp, folder, base, gender, sig in A:
    sl = 'SPECIES_OLD_UNOWN_' + slot
    blk = re.search(r'    \[SPECIES_%s\] =\n    \{.*?\n    \},\n' % base, info, re.S).group(0)
    nb = blk.replace('[SPECIES_%s]' % base, '[SPECIES_%s]' % c)
    nb = re.sub(r'\.genderRatio = [^,]+,', '.genderRatio = MON_%s,' % gender, nb)
    info = info.replace('    [%s] = OLD_UNOWN_SPECIES_INFO,\n' % sl, nb, 1)
    b = re.search(r'    \[SPECIES_%s\]\s*= TMHM_LEARNSET\(.*?\),\n' % base, tm, re.S).group(0)
    tm = tm.replace('    [%s] = TMHM_LEARNSET(0),\n' % sl, re.sub(r'\[SPECIES_%s\]\s*=' % base, '[SPECIES_%s] =' % c, b), 1)
    mt = re.search(r'    \[SPECIES_%s\] = TUTOR.*?,\n' % base, tut, re.S)
    if mt: tut = tut.replace('    [SPECIES_CHIMECHO] =', mt.group(0).replace('SPECIES_%s' % base, 'SPECIES_%s' % c) + '\n    [SPECIES_CHIMECHO] =', 1)
    sym = re.search(r'\[SPECIES_%s\] = (\w+)' % base, ptrs).group(1)
    body = re.search(r'static const u16 %s\[\] = \{(.*?)\n\};' % sym, lus, re.S).group(1)
    ents = [(int(l), m) for l, m in re.findall(r'LEVEL_UP_MOVE\(\s*(\d+),\s*MOVE_(\w+)\)', body)]
    ents = [e for e in ents if e[1] not in sig]
    lv = [1, 1, 8, 16]
    ents += [(lv[i], sig[i]) for i in range(4)]
    ents.sort(key=lambda e: e[0])
    name = 'Ally' + c.capitalize()
    new_learnsets += 'static const u16 s%sLevelUpLearnset[] = {\n' % name + ''.join('    LEVEL_UP_MOVE(%2d, MOVE_%s),\n' % e for e in ents) + '    LEVEL_UP_END\n};\n\n'
    ptrs = ptrs.replace('[%s] = sSpecies%dLevelUpLearnset' % (sl, 252 + 'BCDEFGHI'.index(slot)), '[%s] = s%sLevelUpLearnset' % (sl, name))
wr('src/data/pokemon/species_info.h', info); wr('src/data/pokemon/tmhm_learnsets.h', tm); wr('src/data/pokemon/tutor_learnsets.h', tut)
wr('src/data/pokemon/level_up_learnset_pointers.h', ptrs)
i = lus.index('static const u16 sEirikaLevelUpLearnset[]'); wr('src/data/pokemon/level_up_learnsets.h', lus[:i] + new_learnsets + lus[i:])

# graphics: pictures, tables, coordinates, names, icons, cry
gfx_decl = gfx_ext = ''
for c, slot, disp, folder, base, gender, sig in A:
    sl = 'SPECIES_OLD_UNOWN_' + slot; cn = folder.replace('_', '').capitalize() if folder != 'L_Arachel' else 'Larachel'
    low = folder.lower(); d = os.path.join(D, 'graphics/pokemon', low); os.makedirs(d, exist_ok=True)
    for f in ('back.png',): shutil.copy(os.path.join(ART, folder, f), os.path.join(d, 'back.png')); shutil.copy(os.path.join(ART, folder, f), os.path.join(d, 'front.png'))
    for f in ('normal.pal', 'shiny.pal'): shutil.copy(os.path.join(ART, folder, f), os.path.join(d, f))
    shutil.copy(os.path.join(D, 'graphics/pokemon/%s/footprint.png' % base.lower()), os.path.join(d, 'footprint.png'))
    gfx_decl += (f'const u32 gMonFrontPic_{cn}[] = INCBIN_U32("graphics/pokemon/{low}/front.4bpp.lz");\nconst u32 gMonPalette_{cn}[] = INCBIN_U32("graphics/pokemon/{low}/normal.gbapal.lz");\n'
                 f'const u32 gMonBackPic_{cn}[] = INCBIN_U32("graphics/pokemon/{low}/back.4bpp.lz");\nconst u32 gMonShinyPalette_{cn}[] = INCBIN_U32("graphics/pokemon/{low}/shiny.gbapal.lz");\n'
                 f'const u8 gMonIcon_{cn}[] = INCBIN_U8("graphics/pokemon/{low}/icon.4bpp");\nconst u8 gMonFootprint_{cn}[] = INCBIN_U8("graphics/pokemon/{low}/footprint.1bpp");\n')
    gfx_ext += (f'extern const u32 gMonFrontPic_{cn}[];\nextern const u32 gMonPalette_{cn}[];\nextern const u32 gMonBackPic_{cn}[];\nextern const u32 gMonShinyPalette_{cn}[];\nextern const u8 gMonIcon_{cn}[];\nextern const u8 gMonFootprint_{cn}[];\n')
    sub1('src/data/pokemon_graphics/front_pic_table.h', f'SPECIES_SPRITE(OLD_UNOWN_{slot}, gMonFrontPic_DoubleQuestionMark)', f'SPECIES_SPRITE(OLD_UNOWN_{slot}, gMonFrontPic_{cn})')
    sub1('src/data/pokemon_graphics/back_pic_table.h', f'SPECIES_SPRITE(OLD_UNOWN_{slot}, gMonBackPic_DoubleQuestionMark)', f'SPECIES_SPRITE(OLD_UNOWN_{slot}, gMonBackPic_{cn})')
    sub1('src/data/pokemon_graphics/palette_table.h', f'SPECIES_PAL(OLD_UNOWN_{slot}, gMonPalette_DoubleQuestionMark)', f'SPECIES_PAL(OLD_UNOWN_{slot}, gMonPalette_{cn})')
    sub1('src/data/pokemon_graphics/shiny_palette_table.h', f'SPECIES_SHINY_PAL(OLD_UNOWN_{slot}, gMonShinyPalette_DoubleQuestionMark)', f'SPECIES_SHINY_PAL(OLD_UNOWN_{slot}, gMonShinyPalette_{cn})')
    sub1('src/data/pokemon_graphics/footprint_table.h', f'[SPECIES_OLD_UNOWN_{slot}] = gMonFootprint_QuestionMark', f'[SPECIES_OLD_UNOWN_{slot}] = gMonFootprint_{cn}')
    sub1('src/data/text/species_names.h', f'[SPECIES_OLD_UNOWN_{slot}] = _("?")', f'[SPECIES_OLD_UNOWN_{slot}] = _("{disp}")')
    sub1('src/pokemon_icon.c', f'[SPECIES_OLD_UNOWN_{slot}] = gMonIcon_QuestionMark', f'[SPECIES_OLD_UNOWN_{slot}] = gMonIcon_{cn}')
    sub1('src/pokemon_icon.c', f'[SPECIES_OLD_UNOWN_{slot}] = 0,', f'[SPECIES_OLD_UNOWN_{slot}] = {icon_pal_idx[c]},')
    for fn in ('front', 'back'):
        p = f'src/data/pokemon_graphics/{fn}_pic_coordinates.h'; t = rd(p)
        t = re.sub(r'(\[SPECIES_OLD_UNOWN_%s\] =\n    \{\n        \.size = MON_COORDS_SIZE\(64, 64\),\n        \.y_offset = )\d+' % slot, r'\g<1>0', t); wr(p, t)
g = rd('src/data/graphics/pokemon.h'); wr('src/data/graphics/pokemon.h', g.replace('const u32 gMonFrontPic_Scizor[]', gfx_decl + 'const u32 gMonFrontPic_Scizor[]', 1))
h = rd('include/graphics.h'); wr('include/graphics.h', h.replace('extern const u32 gMonFrontPic_Scizor[];', gfx_ext + 'extern const u32 gMonFrontPic_Scizor[];', 1))
# cries
cry = ''.join('    if (species == SPECIES_%s)\n        return SPECIES_%s - 1;\n' % (c, CRY_BASE[c]) for c, *_ in A)
sub1('src/pokemon.c', '    if (species == SPECIES_EIRIKA)', cry + '    if (species == SPECIES_EIRIKA)')
print('added', len(A), 'species; icon palettes', icon_pal_idx)
