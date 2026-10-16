# Test harness (exact setup used in the session)
- Sources: `shot.c`, `shot_save.c`, `watch.c`. Prebuilt Linux binaries: `bin/shot`, `bin/shot_save`, `bin/watch` (need libmgba0.10).
- Usage: `bin/shot_save ROM script.txt`. Script commands are listed at the top of `shot_save.c` (run N, keys HEX N, shot FILE, r8/r16/r32 ADDR, w8/w16/w32, rununtil16). It writes a `.sav` next to the ROM, so delete the `.sav` for a clean boot.
- Test ROMs in `builds/test/`: `partner_battle_test_hook.gba` and `chapter3_test_hook.gba` start their scenes by themselves from the player's room (about frame 300, then press A repeatedly).
- `workdata/saves/`: the `.sav` files the runs produced. Memory addresses: look them up with `arm-none-eabi-nm` on a build of `decomp_full.tar.gz`.
- `decomp_full.tar.gz` (repo root): the complete working decomp tree (no build outputs, no ROMs). Unpack, run `make -j8`.
