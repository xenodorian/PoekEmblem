# Decomp overlay

Every file that differs from pret/pokefirered commit 037335f (Audio improvements, #774), including the FE8 graphics, plus `DELETED_FILES.txt` (files to remove). To rebuild: clone pret/pokefirered at 037335f with agbcc, copy this folder over it (delete the listed files), run `make -j8`, then `python3 tools/make_ips.py <vanilla.gba> pokefirered.gba out.ips`. The built ROM matches `patches/FireRed_Eirika_Leg1_Leg2_Partner.ips`. ROMs are never committed.
