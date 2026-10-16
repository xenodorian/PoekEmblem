# Working data (session scratch, uploaded 2026-10-16)

- `banim/`, `portraits_all/`, `playable_allies/`, `back_sprites/`, `eirika_*`, `innes_pieces/`: FE8 art and animation frames used by tools/. Python helpers (`fe8_portrait.py` etc.) sit in this folder.
- `harness/`: mGBA headless driver sources (`shot.c`, `shot_save.c`, `watch.c`; build with libmgba, see top of `shot_save.c`) and sample input scripts.
- `leg1_tests/`, `leg3_tests/`: input scripts and notes used for the partner battle and 23-chapter tests, plus `chapters.json` extractor output.
- `em/`: pokeemerald sources the partner battle was ported from (reference only).
- `cast/`: cast list JSON.
Hardcoded paths in the scripts point at the old scratch directory; edit them first.
