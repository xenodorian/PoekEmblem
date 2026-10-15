# Grok A notes

## Turn 1
- Verified FireRed (BPRE) and Sacred Stones (BE8E) ROMs.
- Patched FireRed species name table at 0x245EE0 with Gen 3 text encoding (supports lowercase).
- Mapping:
  1 Eirika, 2 Ephraim, 3 Seth, 4 Franz, 5 Gilliam, 6 Vanessa,
  7 Moulder, 8 Colm, 9 Neimi, 10 Garcia, 25 Lyon, 133 Myrrh
- IPS: patches/FireRed_SacredStones_Import.ips.hex (167-byte binary when converted)
- Tool: tools/apply_ips.py (convert hex→IPS and apply)

## Not uploaded
- Full GBA ROMs (copyrighted) — keep local only
- Windows-only editors (HMA, FEBuilder) — large binaries; use local copies

## Next ideas
- Trainer name / rival name tables
- LZ77 graphics extraction from FE8 portraits for sprite import
- Opening script text flavor (requires pointer-safe text insertion)
