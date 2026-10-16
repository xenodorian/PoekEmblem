#!/usr/bin/env python3
"""Rule driven indoor autotiler for FireRed, mixing FireRed interior blocks and FE8 backdrop tiles.

It is the indoor twin of the outdoor rules in Pokemon-War-and-Murder (lawn_rules.py, rock_rules.py,
edge_rules.py): the four cardinal neighbours pick edge blocks, diagonal-only neighbours pick convex
corner blocks, a table says which blocks may repeat, and validate() checks the result.
See docs/INDOOR_TILING.md for the rules.

Usage:
  indoor_tiling.py render OUT.png [LABELS.png]       offline render of the test room
  indoor_tiling.py emit DIR                          write secondary tileset + map.bin + collision list for the decomp
  indoor_tiling.py selftest
Env: POKEFIRERED (default /workspace/pokefirered), FE8_DECOMP (default /workspace/fireemblem8u)
Needs Python 3 and Pillow only."""
import os, sys, struct, json
from collections import deque
from PIL import Image, ImageDraw

PF = os.environ.get('POKEFIRERED', '/workspace/pokefirered')
FE8 = os.environ.get('FE8_DECOMP', '/workspace/fireemblem8u')
PRIM = 'building'            # FireRed primary tileset used for furniture, rugs, doors, cream wall panels
SEC0 = 0x280                 # first secondary metatile / tile id in FireRed (640)

# ======================================================================================
# 1. RULE TABLES (the indoor version of lawn_rules.EDGE / CONVEX)
# ======================================================================================
# Floor shading. A floor cell is split in 4 quadrants (TL, TR, BL, BR). The 4 cardinal neighbours that are
# not floor (wall, void) pick which quadrants use the dark palette. Key = (dark N, S, E, W).
EDGE = {(1, 0, 0, 0): (1, 1, 0, 0),    # dark north: top half
        (0, 1, 0, 0): (0, 0, 1, 1),    # dark south: bottom half
        (0, 0, 1, 0): (0, 1, 0, 1),    # dark east: right half
        (0, 0, 0, 1): (1, 0, 1, 0),    # dark west: left half
        # concave corners (dark on two sides): three quadrants
        (1, 0, 0, 1): (1, 1, 1, 0), (1, 0, 1, 0): (1, 1, 0, 1),
        (0, 1, 1, 0): (0, 1, 1, 1), (0, 1, 0, 1): (1, 0, 1, 1)}
# No cardinal neighbour but a diagonal one: convex corner, one quadrant. Key = (dx, dy) of the dark cell.
CONVEX = {(1, 1): (0, 0, 0, 1), (-1, 1): (0, 0, 1, 0), (1, -1): (0, 1, 0, 0), (-1, -1): (1, 0, 0, 0)}

# Rug (FireRed ids). Key = (N, S, E, W) neighbour is NOT rug.
RUG_EDGE = {(1, 0, 0, 0): 68, (0, 1, 0, 0): 92, (0, 0, 1, 0): 86, (0, 0, 0, 1): 83,
            (1, 0, 0, 1): 67, (1, 0, 1, 0): 70, (0, 1, 0, 1): 91, (0, 1, 1, 0): 94}
RUG_CENTER = 69
# FireRed has no inner (concave) rug corner block and no one cell wide rug: those layouts are rejected.

# Wall (FireRed cream panel) and void blocks
FR_CAP, FR_FACE, FR_VOID = 32, 40, 8
DOOR_ROW = (26, 27, 28)        # void row under the door, middle = door
DOOR_MAT = (18, 19, 20)        # mat on the last floor row, middle = warp trigger behaviour

# Wall mounted furniture (FireRed): (width, cap row ids, face row ids, floor row ids or None). Placed on the cream
# panel only, on the face row, never touching brick. Each object lists the blocks per column.
WALL_OBJ = {'w': (2, (33, 34), (41, 42), None),          # window
            's': (2, (43, 44), (51, 52), (59, 60)),      # green shelf
            'k': (2, (32, 32), (49, 50), (57, 58)),      # sink and stove
            'f': (1, (45,), (53,), (61,)),               # fridge
            'x': (2, (46, 47), (54, 55), (62, 63))}      # cabinet
# Floor standing furniture. Tall plant = top cell + pot cell (top is walkable, pot is solid).
PLANT = {'left': (87, 95), 'right': (71, 79)}            # leaves face the room centre
TABLE = ((76, 77), (84, 85)); CHAIR_L, CHAIR_R = 75, 78  # table and chairs sit on rug (their bottom layer is rug)
# Blocks whose bottom layer is plain parquet and can therefore be lifted onto another floor (checked in code)
PARQUET = {0x1003, 0x1004, 0x1013, 0x1014, 0x1005, 0x1006, 0x1015, 0x1016}
# Collision bit per FireRed block (from the vanilla house maps: 1 = solid)
SOLID_FR = {8, 26, 27, 28, 32, 40, 33, 34, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51, 52, 53, 54, 55,
            76, 77, 84, 85, 95, 79}

WALL_CH = set('#=') | set(WALL_OBJ)
FLOORISH = set('.cpTab')
# layout legend (see docs/INDOOR_TILING.md)
LEGEND = {' ': 'void', '#': 'FE8 brick wall (two rows: cap, face; a room uses # or =/objects, never both)', '=': 'FireRed cream wall panel', '.': 'slab floor',
          'c': 'rug', 'T': 'table (2x2, on rug)', 'a': 'chair facing east', 'b': 'chair facing west',
          'p': 'tall plant (pot cell, plant top is the cell above)', 'D': 'door in the bottom wall row',
          'w': 'window', 's': 'shelf', 'k': 'sink', 'f': 'fridge', 'x': 'cabinet'}

# ======================================================================================
# 2. TEST ROOM (15 x 16 metatiles). Row 0 is the wall cap row, row 1 the face row.
# ======================================================================================
ROOM = [
    " ============= ",
    " ==wwssxxf==== ",
    " ............. ",
    " .p........... ",
    " ............. ",
    " ......cccccc. ",
    " ......caTTbc. ",
    " ......caTTbc. ",
    " ......cccccc. ",
    " ............. ",
    " .....ccc..... ",
    " .....ccc..... ",
    " .....ccc..... ",
    " .....ccc...p. ",
    " ............. ",
    "         D     ",
]
# normalise: every row is 15 wide
ROOM = [r.ljust(15)[:15] for r in ROOM]

# ======================================================================================
# 3. TILESET: FireRed primary (read from the pokefirered tree) + generated secondary (FE8 tiles)
# ======================================================================================
def read_pal(path):
    L = open(path).read().split('\n')[3:19]
    return [tuple(int(v) for v in l.split()) for l in L if l.strip()]

class FRPrimary:
    def __init__(s, name=PRIM):
        d = PF + '/data/tilesets/primary/' + name + '/'
        s.tiles = open(d + 'tiles.4bpp', 'rb').read()
        s.pals = [read_pal(d + 'palettes/%02d.pal' % i) for i in range(7)]
        mb = open(d + 'metatiles.bin', 'rb').read(); ab = open(d + 'metatile_attributes.bin', 'rb').read()
        s.n = len(mb) // 16
        s.meta = [struct.unpack('<8H', mb[i * 16:i * 16 + 16]) for i in range(s.n)]
        s.attr = [struct.unpack('<I', ab[i * 4:i * 4 + 4])[0] for i in range(s.n)]
    def tile_pixels(s, i):
        buf = s.tiles[i * 32:i * 32 + 32]; px = []
        for b in buf: px += [b & 15, b >> 4]
        return px

def q5(c): return tuple((v >> 3) << 3 | (v >> 6) for v in c)       # 5 bit as the GBA shows it

def fe8_patch(bg, x, y, w=16, h=16):
    """w x h RGB patch from an FE8 background (graphics/bg/bg_<bg>.png of the FE8 decomp, the game's own art)"""
    im = Image.open('%s/graphics/bg/bg_%s.png' % (FE8, bg)).convert('RGB')
    return im.crop((x, y, x + w, y + h))

# FE8 pieces. All were found by a seam search (tools/indoor_tiling.py seam check in docs): the 16x16 patch repeats with
# no visible seam on both axes (floor) or on the horizontal axis (walls). No furniture is cropped.
FE8_PIECES = {'floorA': ('Castle_Interior', 79, 44), 'floorB': ('Castle_Interior', 58, 45),
              'brick': ('Grado_Chamber', 184, 140), 'course': ('Castle_Interior', 112, 120)}
WSHADE = 0.65                                 # dark wall palette (palette 10) for wall end corner blocks
SHADE = 0.8                                   # dark palette = floor palette * SHADE

class Registry:
    """Generated secondary tileset: 8x8 tiles, 6 palettes (absolute 7..12), metatiles."""
    def __init__(s):
        s.tiles = [[0] * 64]; s.tidx = {tuple([0] * 64): 0}
        s.metas = []; s.midx = {}; s.pal = {}
        s.src = {}                              # metatile id -> 'fe8' | 'fr' | 'mix'
        # quantise each FE8 colour group to 15 colours; floor group and wall group, plus a dark floor palette
        pf = [fe8_patch(*FE8_PIECES[k]) for k in ('floorA', 'floorB')]
        pw = [fe8_patch(*FE8_PIECES[k]) for k in ('brick', 'course')]
        s.pal_floor = s._quant(pf); s.pal_wall = s._quant(pw)
        s.pal_dark = [tuple(int(v * SHADE) for v in c) for c in s.pal_floor]
        s.pal_wdark = [tuple(int(v * WSHADE) for v in c) for c in s.pal_wall]
        s.quads = {}                            # name -> 4 tile ids (TL, TR, BL, BR)
        for k, g, pal in (('floorA', pf[0], s.pal_floor), ('floorB', pf[1], s.pal_floor),
                          ('brick', pw[0], s.pal_wall), ('course', pw[1], s.pal_wall)):
            s.quads[k] = [s._tile(g.crop((qx * 8, qy * 8, qx * 8 + 8, qy * 8 + 8)), pal) for qy in (0, 1) for qx in (0, 1)]
        # mirrored floor variants reuse the same 8x8 tiles through the flip bits (no new tile data)
        a = s.quads['floorA']; H_, V_ = 0x400, 0x800
        s.quads['floorAh'] = [a[1] ^ H_, a[0] ^ H_, a[3] ^ H_, a[2] ^ H_]
        s.quads['floorAv'] = [a[2] ^ V_, a[3] ^ V_, a[0] ^ V_, a[1] ^ V_]
        s.quads['floorAhv'] = [a[3] ^ (H_ | V_), a[2] ^ (H_ | V_), a[1] ^ (H_ | V_), a[0] ^ (H_ | V_)]
    def _quant(s, imgs):
        w = sum(i.width for i in imgs); big = Image.new('RGB', (w, imgs[0].height)); x = 0
        for i in imgs: big.paste(i, (x, 0)); x += i.width
        q = big.quantize(colors=15, method=Image.Quantize.MEDIANCUT)
        p = (q.getpalette() + [0] * 45)[:45]; cols = [q5(tuple(p[i * 3:i * 3 + 3])) for i in range(15)]
        return [(0, 0, 0)] + cols
    def _tile(s, im, pal):
        px = []
        for y in range(8):
            for x in range(8):
                c = im.getpixel((x, y)); px.append(min(range(1, 16), key=lambda i: sum((a - b) ** 2 for a, b in zip(pal[i], c))))
        k = tuple(px)
        if k not in s.tidx: s.tidx[k] = len(s.tiles); s.tiles.append(list(k))
        return s.tidx[k]
    @staticmethod
    def entry(tile, pal): return (SEC0 + (tile & 0x3ff)) | (tile & 0xc00) | (pal << 12)     # tile may carry flip bits (0x400 h, 0x800 v)
    def palette(s, absn):
        return {7: s.pal_floor, 8: s.pal_dark, 9: s.pal_wall, 10: s.pal_wdark}.get(absn, [(0, 0, 0)] * 16)
    def add(s, ents, attr, src):
        k = (tuple(ents), attr)
        if k not in s.midx:
            s.midx[k] = len(s.metas); s.metas.append(k); s.src[SEC0 + s.midx[k]] = src
        return SEC0 + s.midx[k]
    # ---- block factories
    def floor(s, variant, mask):
        ents = [s.entry(s.quads[variant][q], 8 if mask[q] else 7) for q in range(4)]
        return s.add(ents + [0] * 4, 0, 'fe8')
    def floor_entries(s, variant, mask):
        return [s.entry(s.quads[variant][q], 8 if mask[q] else 7) for q in range(4)]
    def wall(s, kind, west_end=False, east_end=False):
        """wall block; at a wall end (void beside it) the outer column of quadrants uses the dark wall palette: the corner block"""
        dk = (west_end, east_end, west_end, east_end)
        ents = [s.entry(t, 10 if dk[q] else 9) for q, t in enumerate(s.quads[kind])]
        return s.add(ents + [0] * 4, 0, 'fe8')
    def lift(s, fr, frid, variant, mask):
        """FireRed block `frid` with its parquet bottom quadrants replaced by our floor quadrants (clean: the
        object itself lives in the top layer or in non parquet bottom quadrants, which are kept)"""
        e = list(fr.meta[frid]); fl = s.floor_entries(variant, mask)
        for q in range(4):
            if e[q] in PARQUET: e[q] = fl[q]
        return s.add(e, fr.attr[frid], 'mix')

# ======================================================================================
# 4. THE AUTOTILER
# ======================================================================================
class RuleError(Exception): pass

def shade_mask(dark, x, y):
    """(TL,TR,BL,BR) dark flags for a floor cell, dark(x, y) -> bool. Same shape as lawn_rules.border_block."""
    k = (int(dark(x, y - 1)), int(dark(x, y + 1)), int(dark(x + 1, y)), int(dark(x - 1, y)))
    if k in EDGE: return EDGE[k]
    if any(k):    # three or four sided dead end: union of its cardinal edges
        card = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)); m = [0, 0, 0, 0]
        for i in range(4):
            if k[i]: m = [u | v for u, v in zip(m, EDGE[card[i]])]
        return tuple(m)
    m = [0, 0, 0, 0]
    for (a, b), q in CONVEX.items():
        if dark(x + a, y + b): m = [u | v for u, v in zip(m, q)]
    return tuple(m)

def rug_block(isrug, x, y):
    k = (int(not isrug(x, y - 1)), int(not isrug(x, y + 1)), int(not isrug(x + 1, y)), int(not isrug(x - 1, y)))
    if k in RUG_EDGE: return RUG_EDGE[k]
    if k == (0, 0, 0, 0):
        if any(not isrug(x + a, y + b) for a, b in CONVEX): raise RuleError('rug inner corner at %s: no FireRed block for it' % ((x, y),))
        return RUG_CENTER
    raise RuleError('rug too thin at %s (neighbours %s): rugs need to be at least 2x2' % ((x, y), k))

SEED = 0                      # per room seed for the floor pattern (set by autotile(seed=...))
_BCACHE = {}
def _h(x, y, salt=0):
    v = (x * 73856093 ^ y * 19349663 ^ (SEED + 1) * 83492791 ^ salt * 2654435761) & 0xffffffff
    v ^= v >> 13; v = (v * 0x5bd1e995) & 0xffffffff; v ^= v >> 15
    return v
def is_accent(x, y):
    """irregular accent placement: a hash picks about one cell in five, and a cell never becomes an accent if its west
    or north neighbour is one (so no two accents touch on either axis)"""
    k = (SEED, x, y)
    if k not in _BCACHE:
        _BCACHE[k] = _h(x, y) % 5 == 0 and not (x > 0 and is_accent(x - 1, y)) and not (y > 0 and is_accent(x, y - 1))
    return _BCACHE[k]
def accent_adjacent(x, y):
    return is_accent(x, y) and (is_accent(x + 1, y) or is_accent(x, y + 1))
def floor_variant(x, y):
    """floorB is an isolated accent (irregular, never touching another accent). All other cells use floorA or its mirrored
    forms, picked by a hash, so the pattern has no regular repeat"""
    if is_accent(x, y): return 'floorB'
    return ('floorA', 'floorAh', 'floorAv', 'floorAhv')[(_h(x, y, 7) >> 3) & 3]

def autotile(layout=ROOM, reg=None, fr=None, seed=0):
    global SEED
    SEED = seed
    reg = reg or Registry(); fr = fr or FRPrimary()
    H = len(layout); W = len(layout[0])
    ch = lambda x, y: layout[y][x] if 0 <= x < W and 0 <= y < H else ' '
    for y in range(H):
        if len(layout[y]) != W: raise RuleError('row %d has width %d, not %d' % (y, len(layout[y]), W))
    floorish = lambda x, y: ch(x, y) in FLOORISH
    dark = lambda x, y: not floorish(x, y)
    # rug region: rug cells plus the footprint of table and chairs, which sit on rug
    isrug = lambda x, y: ch(x, y) in 'cTab'
    ids = [[None] * W for _ in range(H)]; coll = [[0] * W for _ in range(H)]; src = [[''] * W for _ in range(H)]
    objs = []
    def put(x, y, bid, c, s=None):
        if ids[y][x] is not None: raise RuleError('cell %s tiled twice' % ((x, y),))
        ids[y][x] = bid; coll[y][x] = c; src[y][x] = s or reg.src.get(bid, 'fr')
    wall_end = lambda x, y: (ch(x - 1, y) == ' ', ch(x + 1, y) == ' ')     # void beside an FE8 wall cell = wall end
    # ---- pass 1: walls and void (neighbours below decide cap / face / void)
    wall_objects = []
    for y in range(H):
        x = 0
        while x < W:
            c = ch(x, y)
            if c == ' ': put(x, y, FR_VOID, 1, 'fr'); x += 1; continue
            if c in '#=' or c in WALL_OBJ:
                below = ch(x, y + 1)
                if c in WALL_OBJ:
                    w = WALL_OBJ[c][0]; run = 0
                    while ch(x + run, y) == c: run += 1
                    if run % w: raise RuleError('wall object %r at %s: run of %d is not a multiple of width %d' % (c, (x, y), run, w))
                    if not (floorish(x, y + 1)): raise RuleError('wall object %r at %s needs floor below it' % (c, (x, y)))
                    for i in range(0, run, w): wall_objects.append((c, x + i, y))
                    for i in range(run):
                        _, cap, face, flo = WALL_OBJ[c]; col = i % w
                        if ch(x + i, y - 1) != '=': raise RuleError('wall object %r at %s must sit under cream panel (=), not %r' % (c, (x + i, y), ch(x + i, y - 1)))
                        put(x + i, y - 1, cap[col], 1, 'fr') if ids[y - 1][x + i] is None else None
                        put(x + i, y, face[col], 1, 'fr')
                    x += run; continue
                if floorish(x, y + 1):   # face row: a wall cell always has floor below it (no wall over void)
                    if ch(x, y - 1) not in WALL_CH: raise RuleError('wall face at %s has no cap above it' % ((x, y),))
                    if c == '#': put(x, y, reg.wall('brick', *wall_end(x, y)), 1)
                    else: put(x, y, FR_FACE, 1, 'fr')
                elif ch(x, y + 1) in WALL_CH:               # cap row (its face is below). Objects under it set their own cap
                    below_obj = ch(x, y + 1) in WALL_OBJ
                    if not below_obj:
                        if c == '#': put(x, y, reg.wall('course', *wall_end(x, y)), 1)
                        else: put(x, y, FR_CAP, 1, 'fr')
                else: raise RuleError('dangling wall cell at %s' % ((x, y),))
            x += 1
    # cap cells under wall objects were filled by the object; fill their placeholders
    # ---- pass 2: floor cells
    for y in range(H):
        for x in range(W):
            if ids[y][x] is not None or ch(x, y) not in FLOORISH: continue
            c = ch(x, y); m = shade_mask(dark, x, y); v = floor_variant(x, y)
            if c == '.': put(x, y, reg.floor(v, m), 0)
            elif c == 'c':
                put(x, y, reg.lift(fr, rug_block(isrug, x, y), v, m), 0)
            elif c == 'p':
                top = ch(x, y - 1)
                if top != '.': raise RuleError('plant at %s needs a free floor cell above it' % ((x, y),))
                side = 'left' if x < W // 2 else 'right'
                put(x, y, reg.lift(fr, PLANT[side][1], v, m), 1)
            elif c == 'T':
                # 2x2 table: this must be the top-left cell
                if ch(x - 1, y) == 'T' or ch(x, y - 1) == 'T': continue
                if not (ch(x + 1, y) == ch(x, y + 1) == ch(x + 1, y + 1) == 'T'): raise RuleError('table at %s is not a 2x2 block' % ((x, y),))
                for dy in (0, 1):
                    for dx in (0, 1): put(x + dx, y + dy, TABLE[dy][dx], 1, 'fr')
            elif c == 'a':
                if ch(x + 1, y) != 'T': raise RuleError('chair a at %s must have a table to its east' % ((x, y),))
                put(x, y, CHAIR_L, 0, 'fr')
            elif c == 'b':
                if ch(x - 1, y) != 'T': raise RuleError('chair b at %s must have a table to its west' % ((x, y),))
                put(x, y, CHAIR_R, 0, 'fr')
    # plant tops placed above (the loop above may have visited the cell before the pot): fix those cells
    for y in range(H):
        for x in range(W):
            if ch(x, y) == 'p':
                side = 'left' if x < W // 2 else 'right'
                ids[y - 1][x] = None       # the plain floor cell above the pot becomes the plant top
                put(x, y - 1, reg.lift(fr, PLANT[side][0], floor_variant(x, y - 1), shade_mask(dark, x, y - 1)), 0)
    # ---- wall object floor rows (bottom part of shelf, sink, fridge, cabinet): clean lift onto the floor
    for (c, x, y) in wall_objects:
        w, cap, face, flo = WALL_OBJ[c]
        if flo:
            for col in range(w):
                xx = x + col
                if ids[y + 1][xx] is not None and ch(xx, y + 1) == '.':
                    ids[y + 1][xx] = None
                put(xx, y + 1, reg.lift(fr, flo[col], floor_variant(xx, y + 1), shade_mask(dark, xx, y + 1)), 0)
    # ---- door: D on the last row; 3 wide mat above it, void row flanks
    for y in range(H):
        for x in range(W):
            if ch(x, y) != 'D': continue
            if y != H - 1: raise RuleError('door at %s must be on the last row' % ((x, y),))
            for dx in (-1, 0, 1):
                if ch(x + dx, y - 1) != '.': raise RuleError('door mat cell %s must be plain floor' % ((x + dx, y - 1),))
                if dx and ch(x + dx, y) != ' ': raise RuleError('door flank %s must be void' % ((x + dx, y),))
                ids[y - 1][x + dx] = None
                put(x + dx, y - 1, reg.lift(fr, DOOR_MAT[dx + 1], floor_variant(x + dx, y - 1), shade_mask(dark, x + dx, y - 1)), 0)
                ids[y][x + dx] = None
                put(x + dx, y, DOOR_ROW[dx + 1], 1, 'fr')
    for y in range(H):
        for x in range(W):
            if ids[y][x] is None: raise RuleError('cell %s left untiled (char %r)' % ((x, y), ch(x, y)))
    res = dict(ids=ids, coll=coll, src=src, W=W, H=H, reg=reg, fr=fr, layout=layout)
    validate(res)
    return res

def validate(res):
    """edge rule style checks; raises RuleError listing the findings"""
    ids, coll, layout, W, H = res['ids'], res['coll'], res['layout'], res['W'], res['H']
    bad = []
    ch = lambda x, y: layout[y][x] if 0 <= x < W and 0 <= y < H else ' '
    # 1. floorB accent never touches floorB (the comb check: no block repeats along an axis it should not)
    for y in range(H):
        for x in range(W):
            if accent_adjacent(x, y): bad.append(('accent-adjacent', x, y))
    # 2. a wall face must have a cap above and a floor below; caps must sit over faces
    for y in range(H):
        for x in range(W):
            if ch(x, y) in WALL_CH:
                if ch(x, y + 1) not in WALL_CH and ch(x, y + 1) not in FLOORISH and ch(x, y - 1) not in WALL_CH: bad.append(('wall-end', x, y))
    # 3. every walkable cell is reachable from the door mat, and objects leave the cell in front of wall objects and the door free
    walk = lambda x, y: 0 <= x < W and 0 <= y < H and ch(x, y) in FLOORISH and not coll[y][x]
    start = None
    for x in range(W):
        if ch(x, H - 1) == 'D': start = (x, H - 2)
    if start is None: bad.append(('no-door', 0, 0))
    else:
        seen = {start}; q = deque([start])
        while q:
            x, y = q.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n not in seen and walk(*n): seen.add(n); q.append(n)
        for y in range(H):
            for x in range(W):
                if walk(x, y) and (x, y) not in seen: bad.append(('unreachable', x, y))
        sx, sy = start
        for dx in (-1, 0, 1):
            if coll[sy - 1][sx + dx]: bad.append(('door-blocked', sx + dx, sy - 1))
    for y in range(H):
        for x in range(W):
            if ch(x, y) in WALL_OBJ and ch(x, y + 2) in FLOORISH and coll[y + 2][x]: bad.append(('object-front-blocked', x, y + 2))
    # 4. only FireRed primary blocks (<640) and our generated blocks appear
    reg = res['reg']
    for y in range(H):
        for x in range(W):
            b = ids[y][x]
            if b >= SEC0 and b - SEC0 >= len(reg.metas): bad.append(('bad-id', x, y))
    # 5. everything FireRed that we lift uses primary tiles and palettes only (clean extraction, no secondary dependency)
    for (ents, attr) in reg.metas:
        for e in ents:
            if e and e < SEC0 and (e >> 12) > 6: bad.append(('palette-outside-primary', e, 0))
    # 6. ONE wall style per room, and wall width == floor width (no wall over void, no floor edge without wall)
    wall_cells = [(x, y) for y in range(H) for x in range(W) if ch(x, y) in WALL_CH]
    if any(ch(x, y) == '#' for x, y in wall_cells) and any(ch(x, y) != '#' for x, y in wall_cells): bad.append(('mixed-wall-styles', 0, 0))
    wrows = sorted({y for _, y in wall_cells})
    for y in wrows:
        for x in range(W):
            if ch(x, y) in WALL_CH:
                st = {'#': 'fe8'}.get(ch(x, y), 'fr')
                if not (res['src'][y][x] == st or (st == 'fe8' and res['src'][y][x] == 'fe8')): bad.append(('wall-style-mismatch', x, y))
    frows = [y for y in range(H) if any(ch(x, y) in FLOORISH for x in range(W))]
    fcols = {x for y in frows for x in range(W) if ch(x, y) in FLOORISH}
    if fcols and fcols != set(range(min(fcols), max(fcols) + 1)): bad.append(('floor-not-contiguous', 0, 0))
    for y in frows:
        r = {x for x in range(W) if ch(x, y) in FLOORISH}
        if r != fcols: bad.append(('floor-not-rectangle', min(r ^ fcols), y))
    if frows and frows != list(range(frows[0], frows[-1] + 1)): bad.append(('floor-rows-gap', 0, 0))
    for y in wrows:
        r = {x for x in range(W) if ch(x, y) in WALL_CH}
        if r != fcols: bad.append(('wall-width-mismatch', min(r ^ fcols), y))
    for x in range(W):
        for y in range(H):
            if ch(x, y) in FLOORISH and ch(x, y - 1) not in FLOORISH and ch(x, y - 1) not in WALL_CH: bad.append(('floor-edge-without-wall', x, y))
            if ch(x, y) in WALL_CH and ch(x, y + 1) not in WALL_CH and ch(x, y + 1) not in FLOORISH: bad.append(('wall-over-void', x, y))
    if bad: raise RuleError('%d rule violations, first: %s' % (len(bad), bad[:8]))
    return 0

# ======================================================================================
# 5. RENDER AND EMIT
# ======================================================================================
def render_entries(ents, fr, reg):
    out = Image.new('RGBA', (16, 16), (0, 0, 0, 255))
    for layer in (0, 1):
        for k in range(4):
            e = ents[layer * 4 + k]; t, pal, hf, vf = e & 0x3ff, (e >> 12) & 15, (e >> 10) & 1, (e >> 11) & 1
            if t < SEC0: px = fr.tile_pixels(t); P = fr.pals[pal] if pal < 7 else [(255, 0, 255)] * 16
            else: px = reg.tiles[t - SEC0]; P = reg.palette(pal)
            if layer == 1 and not any(px): continue
            tile = Image.new('RGBA', (8, 8))
            data = []
            for y in range(8):
                for x in range(8):
                    v = px[(7 - y if vf else y) * 8 + (7 - x if hf else x)]
                    data.append((0, 0, 0, 0) if v == 0 else q5(P[v]) + (255,))
            tile.putdata(data); out.alpha_composite(tile, ((k % 2) * 8, (k // 2) * 8))
    return out

def metatile_image(bid, fr, reg):
    if bid < SEC0: return render_entries(fr.meta[bid], fr, reg)
    return render_entries(reg.metas[bid - SEC0][0], fr, reg)

def render(res, scale=3):
    W, H, fr, reg = res['W'], res['H'], res['fr'], res['reg']
    im = Image.new('RGB', (W * 16, H * 16))
    for y in range(H):
        for x in range(W): im.paste(metatile_image(res['ids'][y][x], fr, reg).convert('RGB'), (x * 16, y * 16))
    return im.resize((W * 16 * scale, H * 16 * scale), Image.NEAREST)

def render_labels(res, scale=3):
    base = render(res, scale).convert('RGBA'); W, H = res['W'], res['H']; S = 16 * scale
    col = {'fr': (40, 110, 255, 70), 'fe8': (255, 130, 20, 55), 'mix': (200, 40, 230, 80)}
    ov = Image.new('RGBA', base.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(H):
        for x in range(W):
            s = res['src'][y][x]
            d.rectangle((x * S, y * S, x * S + S - 1, y * S + S - 1), fill=col[s], outline=col[s][:3] + (200,))
    out = Image.alpha_composite(base, ov)
    pad = 120; full = Image.new('RGB', (out.width, out.height + pad), (24, 24, 24)); full.paste(out.convert('RGB'), (0, pad))
    d = ImageDraw.Draw(full)
    items = [('fe8', 'FE8: stone floor (Castle Interior), wood panel wall face (Grado Chamber) and moss course cap (Castle Interior), dark shade is a palette swap'),
             ('fr', 'FireRed: void, cream wall panels, window, door row, table and chairs'),
             ('mix', 'Both: FireRed object (rug, plants, door mat, shelf, sink, fridge, cabinet floor row) lifted onto the FE8 stone floor')]
    for i, (k, t) in enumerate(items):
        c = col[k][:3]; d.rectangle((8, 10 + i * 30, 30, 32 + i * 30), fill=c); d.text((40, 16 + i * 30), t, fill=(255, 255, 255))
    return full

def count_sources(res):
    n = {}
    for r in res['src']:
        for s in r: n[s] = n.get(s, 0) + 1
    return n

def emit(res, outdir):
    """secondary tileset files for the decomp (same layout as tools/leg4_story_tilesets.py) plus map.bin"""
    reg = res['reg']; os.makedirs(outdir + '/palettes', exist_ok=True)
    nt = len(reg.tiles)
    if nt > 384 or len(reg.metas) > 384: raise RuleError('tileset too big: %d tiles, %d metatiles' % (nt, len(reg.metas)))
    rows = (nt + 15) // 16; sheet = Image.new('P', (128, rows * 8))
    data = []
    for ty in range(rows):
        for y in range(8):
            for tx in range(16):
                i = ty * 16 + tx
                data += reg.tiles[i][y * 8:y * 8 + 8] if i < nt else [0] * 8
    sheet.putdata(data)
    pal = reg.palette(7); sheet.putpalette([v for c in pal for v in c] + [0] * (768 - 48)); sheet.save(outdir + '/tiles.png')
    for k in range(16):
        p = reg.palette(k)
        if len(p) != 16: p = [(0, 0, 0)] * 16
        open('%s/palettes/%02d.pal' % (outdir, k), 'w').write('JASC-PAL\r\n0100\r\n16\r\n' + ''.join('%d %d %d\r\n' % c for c in p))
    open(outdir + '/metatiles.bin', 'wb').write(b''.join(struct.pack('<8H', *m[0]) for m in reg.metas))
    open(outdir + '/metatile_attributes.bin', 'wb').write(b''.join(struct.pack('<I', m[1]) for m in reg.metas))
    W, H = res['W'], res['H']
    mp = [res['ids'][y][x] | (res['coll'][y][x] << 10) | (3 << 12) for y in range(H) for x in range(W)]
    open(outdir + '/map.bin', 'wb').write(struct.pack('<%dH' % len(mp), *mp))
    open(outdir + '/border.bin', 'wb').write(struct.pack('<4H', *([FR_VOID] * 4)))   # void border
    door = [x for x in range(W) if res['layout'][H - 1][x] == 'D'][0]
    json.dump(dict(width=W, height=H, tiles=nt, metatiles=len(reg.metas), door=[door, H - 1], arrive=[door, H - 2]), open(outdir + '/room.json', 'w'))
    return nt, len(reg.metas)

def selftest():
    # shade table
    D = lambda s: (lambda x, y: (x, y) in s)
    assert shade_mask(D({(0, -1)}), 0, 0) == (1, 1, 0, 0)
    assert shade_mask(D({(0, -1), (-1, 0)}), 0, 0) == (1, 1, 1, 0)         # concave: three quadrants
    assert shade_mask(D({(1, 1)}), 0, 0) == (0, 0, 0, 1)                    # convex: one quadrant
    assert shade_mask(D(set()), 0, 0) == (0, 0, 0, 0)
    assert shade_mask(D({(0, -1), (0, 1), (1, 0)}), 0, 0) == (1, 1, 1, 1)   # dead end: union
    # rug
    rug = lambda s: (lambda x, y: (x, y) in s)
    R = {(x, y) for x in range(4) for y in range(3)}
    assert [rug_block(rug(R), x, 0) for x in range(4)] == [67, 68, 68, 70]
    assert [rug_block(rug(R), x, 2) for x in range(4)] == [91, 92, 92, 94] and rug_block(rug(R), 1, 1) == 69
    for bad in ({(0, 0), (1, 0), (2, 0)}, R - {(0, 0)}):
        try: rug_block(rug(bad), 1, 0 if bad != R - {(0, 0)} else 1); raise SystemExit('rug rule did not fire')
        except RuleError: pass
    # whole room tiles and validates
    res = autotile()
    assert res['H'] == 16 and res['W'] == 15
    # violations are caught
    L2 = list(ROOM); L2[2] = L2[2][:8] + 'T' + L2[2][9:]
    try: autotile(L2); raise SystemExit('table rule did not fire')
    except RuleError: pass
    L3 = list(ROOM); L3[14] = L3[14][:8] + 'p' + L3[14][9:]       # plant on the cell above the door mat... mat needs plain floor
    try: autotile(L3); raise SystemExit('door rule did not fire')
    except RuleError: pass
    # brick wall end corner: the outer quadrants of a wall cell beside void use palette 10, an inner cell does not
    BR = [" ########### ", " ########### "] + [" ........... "] * 3 + ["      D      "]
    r2 = autotile(BR); reg = r2['reg']; e0 = reg.metas[r2['ids'][0][1] - SEC0][0]; e1 = reg.metas[r2['ids'][0][3] - SEC0][0]
    assert (e0[0] >> 12) == 10 and (e0[1] >> 12) == 9 and (e1[0] >> 12) == 9, 'wall corner block'
    # wall rules: mixed styles, wall past the floor, floor L shape
    def must_fail(lay, why):
        try: autotile(lay); raise SystemExit(why + ' rule did not fire')
        except RuleError: pass
    good = [" ========= ", " ========= "] + [" ......... "] * 3 + ["    D      "[:11]]
    good[-1] = "     D     "
    autotile(good)
    mixed = list(good); mixed[0] = " ###======= "; mixed[1] = " ###======= "; must_fail(mixed, 'mixed wall')
    wide = list(good); wide[0] = "=========== "; wide[1] = "=========== "; must_fail(wide, 'wall past floor')
    narrow = list(good); narrow[0] = "  ======== "; narrow[1] = "  ======== "; must_fail(narrow, 'wall narrower than floor')
    ell = list(good); ell[3] = "     ..... "; ell[4] = "     ..... "; must_fail(ell, 'floor L shape')
    # irregular floor: accents never touch, and the old x + 2y = 0 mod 4 lattice is gone
    assert not any(accent_adjacent(x, y) for x in range(40) for y in range(40))
    assert any(is_accent(x, y) != ((x + 2 * y) % 4 == 0) for x in range(20) for y in range(20))
    assert len({floor_variant(x, y) for x in range(20) for y in range(20)}) == 5
    print('indoor_tiling selftest ok', count_sources(res))

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == 'selftest': selftest()
    elif a[0] == 'render':
        res = autotile(); render(res).save(a[1]); print('wrote', a[1], count_sources(res))
        if len(a) > 2: render_labels(res).save(a[2]); print('wrote', a[2])
    elif a[0] == 'emit':
        res = autotile(); print('tiles, metatiles:', emit(res, a[1]))
    else: print(__doc__)
