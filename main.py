#!/usr/bin/env python3
"""Entrypoint for the news-image-20261121 entry.

Delivers the pre-rendered Saturday 21 November 2026 world-news summary
image: copies ``entry.png`` from this directory into the output directory
(``$MAKEFUN_OUTPUT_DIR`` when set, otherwise ``/output``).

The picture itself was drawn ahead of time by ``render.py``; this module
only moves the bytes, so it needs nothing beyond the standard library.
It runs in a bare interpreter with no Pillow and no fonts installed,
which is why the render step must NOT happen here.
Repeated runs are byte-identical.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "entry.png"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576  # 1 MiB cap on the delivered image
EXPECT_W, EXPECT_H = 1024, 1024


def png_dimensions(raw):
    """Read width/height from the IHDR chunk of a PNG byte string."""
    if raw[:8] != PNG_MAGIC:
        raise ValueError("entry.png does not start with the PNG signature")
    if raw[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk where expected")
    width = int.from_bytes(raw[16:20], "big")
    height = int.from_bytes(raw[20:24], "big")
    return width, height


def deliver(out_dir):
    """Copy entry.png into out_dir; return (dest, size, w, h, sha256).

    The copy is verified afterwards: the destination bytes are re-read
    and must hash identically to the source, so a truncated or partial
    copy fails loudly instead of shipping a corrupt image.
    """
    if not SOURCE.is_file():
        raise FileNotFoundError("entry.png is missing next to main.py")
    raw = SOURCE.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError(f"entry.png is {len(raw)} bytes, over the 1 MiB cap")
    width, height = png_dimensions(raw)
    if (width, height) != (EXPECT_W, EXPECT_H):
        raise ValueError(f"entry.png is {width}x{height}, expected 1024x1024")
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / "entry.png"
    shutil.copyfile(SOURCE, dest)
    copied = dest.read_bytes()
    if copied != raw:
        raise ValueError("copied entry.png does not match the source bytes")
    digest = hashlib.sha256(raw).hexdigest()
    return dest, len(raw), width, height, digest


def main(argv=None):
    target = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    try:
        dest, size, width, height, digest = deliver(target)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {dest} {width}x{height} {size} bytes sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
