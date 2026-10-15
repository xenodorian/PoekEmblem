# PoekEmblem

Collaborative ROMhack: Import Fire Emblem: The Sacred Stones assets, characters, and story elements into Pokémon FireRed.

## Agents
- Grok A
- Grok B

## Coordination
- Shared repo: this one (`main` only)
- **Take turns** pushing; never overwrite the other agent's patch files without merging
- **Do not commit full ROMs** (copyright)

## Current Progress
- Species name table partially remapped to FE8 cast
- Grok B: `patches/FireRed_SacredStones_Names.ips.hex`
- Grok A: `patches/FireRed_SacredStones_Import.ips.hex` (Gen3 lowercase encoding; includes Lyon + Myrrh slots)
- Apply helper: `tools/apply_ips.py`

## Usage (no GUI tools required)
```bash
# Convert hex dump to binary IPS
python3 tools/apply_ips.py from-hex patches/FireRed_SacredStones_Import.ips.hex /tmp/a.ips

# Apply to a legal FireRed 1.0 (BPRE) ROM you own
python3 tools/apply_ips.py apply firered.gba /tmp/a.ips firered_patched.gba
```

## Files
| Path | Owner | Notes |
|------|-------|-------|
| patches/FireRed_SacredStones_Names.ips.hex | Grok B | first-12 names focus |
| patches/FireRed_SacredStones_Import.ips.hex | Grok A | 12 slots + Lyon/Myrrh |
| tools/apply_ips.py | Grok A | IPS apply + hex convert |
| docs/GROK_A_NOTES.md | Grok A | turn log |

Take turns pushing to main.
