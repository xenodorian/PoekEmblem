# Grok B notes

## Turns
- Names IPS (uppercase) for species 1-12
- Free space doc (0x71A23C large region)
- Verified Cast_v2
- **New:** Gym Leaders IPS replacing BROCK/MISTY/ERIKA/KOGA/SABRINA/BLAINE/GIOVANNI with SETH/VANESSA/EIRIKA/COLM/NEIMI/GARCIA/LYON at their text offsets (~0x1B03xx)

## Encoding
Uppercase Gen3 map. Prefer merging with A’s lowercase Cast_v2 for consistency.

## Graphic target suggestion (for next)
- FE8 Eirika map sprite or portrait: typically in FE8 portrait table ~0x5Bxxxx range or via FEBuilder export. Insert into FireRed overworld sprite table or trainer sprite free space at 0x71A23C after conversion (16-color, LZ77).
- Blocked on full FEBuilder in sandbox; recommend local Windows run for PNG export then HMA import.

## Status
Incremental text progress. Art/story still requires external GUI tools.
