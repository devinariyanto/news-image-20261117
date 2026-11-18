#!/usr/bin/env python3
"""Validate entry.png and copy it byte-for-byte to the output directory.

Contract (make.fun news-image-20261117, program/v1):
- Read entry.png next to this file.
- Accept PNG (magic 89 50 4E 47 0D 0A 1A 0A) or JPEG (magic FF D8 FF).
- PNG: check the CRC of every chunk; require IHDR + IDAT (inflate the
  image data to prove it is intact) + IEND; reject any bytes after IEND.
- JPEG: walk the markers to EOI; reject any bytes after EOI.
- Max size 1,048,576 bytes; max side 1024 px; dimensions must be > 0.
- On failure print the error to stderr and exit 1.
- On success copy the exact bytes to $MAKEFUN_OUTPUT_DIR/entry.png
  (default /output), creating the directory if needed.
- Two runs produce byte-identical output (a plain copy).
"""
import os
import struct
import sys
import zlib

MAX_BYTES = 1_048_576
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def fail(msg):
    print("error: %s" % msg, file=sys.stderr)
    sys.exit(1)


def validate_png(data):
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        fail("not a PNG file")
    pos = 8
    seen = set()
    idat = b""
    while True:
        if pos + 8 > len(data):
            fail("truncated PNG chunk header")
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        start = pos + 8
        end = start + length
        if end + 4 > len(data):
            fail("truncated PNG chunk %r" % ctype)
        stored_crc = struct.unpack(">I", data[end:end + 4])[0]
        actual_crc = zlib.crc32(ctype + data[start:end]) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            fail("bad CRC in PNG chunk %r" % ctype)
        if ctype == b"IHDR":
            if length != 13:
                fail("bad IHDR length")
            width, height = struct.unpack(">II", data[start:start + 8])
            if width <= 0 or height <= 0:
                fail("PNG dimensions must be > 0")
            if width > MAX_SIDE or height > MAX_SIDE:
                fail("PNG side exceeds %d px" % MAX_SIDE)
            seen.add("IHDR")
        elif ctype == b"IDAT":
            idat += data[start:end]
            seen.add("IDAT")
        elif ctype == b"IEND":
            if pos + 12 != len(data):
                fail("trailing bytes after PNG IEND")
            seen.add("IEND")
            break
        pos = end + 4
    if "IHDR" not in seen:
        fail("PNG missing IHDR")
    if "IDAT" not in seen:
        fail("PNG missing IDAT")
    if "IEND" not in seen:
        fail("PNG missing IEND")
    try:
        zlib.decompress(idat)
    except zlib.error as exc:
        fail("PNG IDAT does not inflate: %s" % exc)


def validate_jpeg(data):
    if len(data) < 3 or data[:3] != JPEG_MAGIC:
        fail("not a JPEG file")
    pos = 2
    saw_sof = False
    width = height = 0
    while True:
        if pos + 2 > len(data):
            fail("truncated JPEG marker")
        if data[pos] != 0xFF:
            fail("bad JPEG marker at offset %d" % pos)
        marker = data[pos + 1]
        pos += 2
        if marker == 0xD8:  # SOI (already consumed at start)
            continue
        if marker == 0xD9:  # EOI
            if pos != len(data):
                fail("trailing bytes after JPEG EOI")
            break
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            continue  # standalone markers, no length field
        if pos + 2 > len(data):
            fail("truncated JPEG segment length")
        seg_len = struct.unpack(">H", data[pos:pos + 2])[0]
        if seg_len < 2 or pos + seg_len > len(data):
            fail("bad JPEG segment length for marker 0x%02X" % marker)
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            if seg_len < 7:
                fail("short JPEG SOF segment")
            height, width = struct.unpack(">HH", data[pos + 3:pos + 7])
            saw_sof = True
        if marker == 0xDA:  # SOS: entropy data follows until next marker
            pos += seg_len
            # Scan entropy-coded data for the next 0xFF marker (not 0xFF00
            # stuffed bytes, and not restart markers which have no length).
            while pos + 1 < len(data):
                if data[pos] == 0xFF and data[pos + 1] != 0x00:
                    break
                pos += 1
            continue
        pos += seg_len
    if not saw_sof:
        fail("JPEG missing SOF (no dimensions found)")
    if width <= 0 or height <= 0:
        fail("JPEG dimensions must be > 0")
    if width > MAX_SIDE or height > MAX_SIDE:
        fail("JPEG side exceeds %d px" % MAX_SIDE)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    try:
        with open(src, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        fail("cannot read entry.png: %s" % exc)
    if len(data) > MAX_BYTES:
        fail("entry.png is %d bytes, over the %d byte limit"
             % (len(data), MAX_BYTES))
    if len(data) == 0:
        fail("entry.png is empty")
    if data[:8] == PNG_MAGIC:
        validate_png(data)
    elif data[:3] == JPEG_MAGIC:
        validate_jpeg(data)
    else:
        fail("entry.png is neither PNG nor JPEG")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
            fh.write(data)
    except OSError as exc:
        fail("cannot write output: %s" % exc)


if __name__ == "__main__":
    main()
