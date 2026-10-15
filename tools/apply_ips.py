#!/usr/bin/env python3
"""Apply a pure IPS patch to a ROM. No external tools required."""
import argparse
from pathlib import Path

def apply_ips(rom_path: Path, ips_path: Path, out_path: Path):
    rom = bytearray(rom_path.read_bytes())
    ips = ips_path.read_bytes()
    if not ips.startswith(b"PATCH") or not ips.endswith(b"EOF"):
        raise SystemExit("Invalid IPS (missing PATCH/EOF)")
    i = 5
    end = len(ips) - 3
    while i < end:
        offset = (ips[i] << 16) | (ips[i+1] << 8) | ips[i+2]
        i += 3
        size = (ips[i] << 8) | ips[i+1]
        i += 2
        if size == 0:
            # RLE
            rle_size = (ips[i] << 8) | ips[i+1]
            value = ips[i+2]
            i += 3
            rom[offset:offset+rle_size] = bytes([value]) * rle_size
        else:
            data = ips[i:i+size]
            i += size
            rom[offset:offset+size] = data
    out_path.write_bytes(rom)
    print(f"Wrote {out_path} ({len(rom)} bytes)")

def hex_to_ips(hex_path: Path, ips_path: Path):
    data = bytes.fromhex("".join(hex_path.read_text().split()))
    ips_path.write_bytes(data)
    print(f"Wrote binary IPS {ips_path} ({len(data)} bytes)")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("apply")
    a.add_argument("rom")
    a.add_argument("ips")
    a.add_argument("out")
    h = sub.add_parser("from-hex")
    h.add_argument("hexfile")
    h.add_argument("ips")
    args = p.parse_args()
    if args.cmd == "apply":
        apply_ips(Path(args.rom), Path(args.ips), Path(args.out))
    else:
        hex_to_ips(Path(args.hexfile), Path(args.ips))
