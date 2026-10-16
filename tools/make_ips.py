#!/usr/bin/env python3
"""Create an IPS patch by byte-diffing a base ROM against a modified ROM of the same size."""
import sys
from pathlib import Path

def make_ips(base: bytes, mod: bytes) -> bytes:
    assert len(base) == len(mod)
    out = bytearray(b"PATCH")
    n = len(base)
    i = 0
    while i < n:
        if base[i] == mod[i]:
            i += 1
            continue
        start = i
        # extend while differing, merging gaps of up to 8 equal bytes
        last_diff = i
        j = i
        while j < n and j - last_diff <= 8 and j - start < 0xFFFF:
            if base[j] != mod[j]:
                last_diff = j
            j += 1
        end = last_diff + 1
        # offset 0x454F46 would read as the EOF marker; start one byte earlier
        if start == 0x454F46:
            start -= 1
        chunk = mod[start:end]
        out += start.to_bytes(3, "big") + len(chunk).to_bytes(2, "big") + chunk
        i = end
    out += b"EOF"
    return bytes(out)

if __name__ == "__main__":
    base, mod, dst = map(Path, sys.argv[1:4])
    ips = make_ips(base.read_bytes(), mod.read_bytes())
    dst.write_bytes(ips)
    print(f"Wrote {dst} ({len(ips)} bytes)")
