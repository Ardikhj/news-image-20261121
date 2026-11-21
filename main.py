#!/usr/bin/env python3
"""Entry point for news-image-20261121.

Renders the Saturday 21 November 2026 world-news summary image and writes
it to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png when set).

The render is fully deterministic: fixed story list, fixed palette, fixed
fonts, no clock, no randomness, no network. Running twice produces
byte-identical output, as the harness requires.
"""

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from render import build_image

MAX_BYTES = 1_048_576  # harness gate: at most 1 MiB
EXPECT_W, EXPECT_H = 1024, 1024


def output_path() -> str:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    return os.path.join(out_dir, "entry.png")


def main() -> int:
    path = output_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image = build_image()
    image.save(path, format="PNG", optimize=True)

    with open(path, "rb") as fh:
        blob = fh.read()
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        print("FAIL: output is not a PNG", file=sys.stderr)
        return 1
    if len(blob) > MAX_BYTES:
        print(f"FAIL: {len(blob)} bytes exceeds the 1 MiB cap", file=sys.stderr)
        return 1
    if image.size != (EXPECT_W, EXPECT_H):
        print(f"FAIL: size {image.size} is not 1024x1024", file=sys.stderr)
        return 1
    digest = hashlib.sha256(blob).hexdigest()
    print(f"WROTE {path} {image.size[0]}x{image.size[1]} "
          f"{len(blob)} bytes sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
