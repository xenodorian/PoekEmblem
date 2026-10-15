# Grok A notes

## Turn 3
- Missed wire ids 30-31 until user prompted (background poll logs only; does not wake agent between user turns).
- Responded to B gym leaders work: pushed patches/FireRed_SacredStones_GymLeaders_lc.ips.hex (lowercase Gen3 encoding of Seth/Vanessa/Eirika/Colm/Neimi/Garcia/Lyon at B's offsets).

## Monitoring constraint
Agent only runs when a chat turn is active. "Background" shell poll cannot interrupt to act. Fix: on every user message, fetch wire after=last immediately before other work.
