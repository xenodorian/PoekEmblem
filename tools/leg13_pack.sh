#!/bin/bash
# Usage: leg13_pack.sh TREE N ROMNAME IPSNAME   (never overwrites: refuses if a target exists)
set -e
T=$1; N=$2; ROM="builds/Pokemon FireRed Eirika $3.gba"; IPS="patches/$4.ips"; TAR="decomp_full_v$N.tar.gz"
cd /workspace/PoekEmblem
for f in "$ROM" "$IPS" "$TAR"; do [ -e "$f" ] && { echo "exists: $f"; exit 1; }; done
cp "$T/pokefirered.gba" "$ROM"
python3 tools/make_ips.py "Pokemon - FireRed Version (USA).gba" "$ROM" "$IPS"
tar czf "$TAR" -C "$(dirname $T)" --transform "s#^$(basename $T)#pf_eirika_work#" --exclude="$(basename $T)/build" --exclude='*.gba' --exclude='*.elf' "$(basename $T)"
ls -la "$ROM" "$IPS" "$TAR"
