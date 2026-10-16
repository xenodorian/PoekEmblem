"""Furniture props for the six story maps: crops of the FE8 backdrop (src x0,y0,x1,y1 in the 240x160 art) pasted into the
deeper floor area of the extended map image (dest x,y in px, multiples of 16), optional mirror. Used by leg4_story_tilesets.py
(pixels) and leg5_story_map_objects.py (collision cells)."""
PROPS_OLD = {  # retired by owner rule: no props cropped from FE8 backdrops

 'bg_Renais_Chamber':      [((16, 48, 48, 128), (32, 160), False), ((192, 48, 224, 128), (176, 160), False)],
 'bg_Castle_Interior':     [((16, 48, 48, 128), (48, 160), False), ((16, 48, 48, 128), (160, 160), True)],
 'bg_White_Chamber':       [((32, 64, 64, 128), (32, 176), False), ((176, 64, 208, 128), (176, 176), False)],
 'bg_Fort':                [((112, 48, 144, 96), (48, 176), False), ((144, 48, 176, 96), (32, 208), False)],
 'bg_Throne_Normal':       [((48, 64, 80, 112), (32, 176), False), ((48, 64, 80, 112), (176, 176), True)],
 'bg_Black_Temple_Inside': [((176, 48, 208, 112), (48, 176), False), ((48, 48, 80, 112), (160, 192), False)],
}
PROPS = {}
def block_cells(bg):
    """metatile cells (x, y) covered by the lower half of each prop, blocked for walking"""
    out = []
    for (x0, y0, x1, y1), (dx, dy), _m in PROPS.get(bg, []):
        w = (x1 - x0) // 16; h = (y1 - y0) // 16
        for cy in range(h // 2, h):
            for cx in range(w):
                out.append((dx // 16 + cx, dy // 16 + cy))
    return out
