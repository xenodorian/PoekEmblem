# Grok B notes

## Turn 1-2
- Confirmed ROMs: FireRed BPRE, FE8 BE8E (WiiU VC).
- Created uppercase-encoded names IPS for species 1-12 at 0x245EEB (Eirika..Myrrh).
- Files: patches/FireRed_SacredStones_Names.ips.b64 (and .hex earlier).
- IPS creator + poke_encode helpers in local tools/.

## Encoding note
Grok A used lowercase-capable Gen3 map (better). My first patch is uppercase-only. Prefer A's Import.ips for broader chars.

## Limitations for full objective
Full art (portraits, map sprites, battle anims) + story (scripts, chapters, dialogue) import requires:
- FEBuilderGBA or Emblem-Magic for FE8 asset dump
- HexManiacAdvance or unLZ + sprite tools for FireRed insertion
- Pointer-safe text/script editors
- Free space management (FireRed is tight)
These are mostly Windows GUI; sandbox is Linux CLI. Partial text is achievable; full rewrite is multi-week team project.

## Next suggested
- Merge name patches (prefer A encoding)
- Locate & patch rival / gym leader names
- LZ77 decompress sample FE8 portrait for PNG conversion
- Document free space in FireRed
