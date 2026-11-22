#!/usr/bin/env python3
"""make.fun news-image-20261122 entry program.

The poster (entry.png, rendered by build_poster.py and committed next
to this file) is copied into the output directory as entry.png.
Python 3 standard library only; deterministic - the same bytes on
every run. The output directory is MAKEFUN_OUTPUT_DIR when set, else
OUTPUT_DIR, else /output, matching the program/v1 harness contract.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def main():
    if not os.path.isfile(SOURCE):
        print(f"error: poster not found: {SOURCE}", file=sys.stderr)
        return 1
    with open(SOURCE, "rb") as fh:
        if fh.read(8) != PNG_MAGIC:
            print("error: entry.png is not a PNG file", file=sys.stderr)
            return 1
    out_dir = (os.environ.get("MAKEFUN_OUTPUT_DIR")
               or os.environ.get("OUTPUT_DIR") or "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    if os.path.getsize(dest) != os.path.getsize(SOURCE):
        print("error: copied poster size mismatch", file=sys.stderr)
        return 1
    print(f"entry.png -> {dest} ({os.path.getsize(dest)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
