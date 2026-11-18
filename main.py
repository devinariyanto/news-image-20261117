"""news-image-20261117 entry program.

Reads the bundled image ``entry.png`` that sits next to this file,
checks it against the competition gates (PNG or JPEG by magic bytes,
at most 1 MiB, at most 1024x1024 pixels, structurally whole), then
writes the exact same bytes to ``$MAKEFUN_OUTPUT_DIR/entry.png``
(default ``/output``).

Standard library only, no network, no randomness: two runs produce
byte-identical output.
"""

import os
import struct
import sys
import zlib

SOURCE_NAME = "entry.png"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


class GateError(Exception):
    """Raised when the bundled image fails a competition gate."""


def die(message):
    raise GateError(message)


def png_dimensions_and_integrity(data):
    """Return (width, height) after checking every PNG chunk CRC.

    Also inflates the concatenated IDAT payload so a truncated or
    corrupt image stream is caught instead of copied blindly.
    """
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        die("not a PNG file")
    pos = 8
    width = height = None
    idat = bytearray()
    saw_iend = False
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        kind = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4
        if end > len(data):
            die("truncated PNG chunk: " + kind.decode("latin-1"))
        body = data[pos + 8:pos + 8 + length]
        stored_crc = struct.unpack(">I", data[pos + 8 + length:end])[0]
        actual_crc = zlib.crc32(kind + body) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            die("PNG chunk CRC mismatch: " + kind.decode("latin-1"))
        if kind == b"IHDR":
            if length != 13:
                die("bad PNG IHDR length")
            width, height = struct.unpack(">II", body[:8])
        elif kind == b"IDAT":
            idat += body
        elif kind == b"IEND":
            saw_iend = True
            if end != len(data):
                die("trailing bytes after PNG IEND")
            break
        pos = end
    if width is None or height is None:
        die("PNG has no IHDR chunk")
    if not saw_iend:
        die("PNG has no IEND chunk")
    if not idat:
        die("PNG has no IDAT data")
    try:
        zlib.decompress(bytes(idat))
    except zlib.error as exc:
        die("PNG image data does not decompress: " + str(exc))
    return width, height


def jpeg_dimensions_and_integrity(data):
    """Return (width, height) after walking JPEG markers to the EOI.

    The EOI marker must be the last two bytes of the file: any data
    after it means the file is not a whole, unappended JPEG.
    """
    if len(data) < 2 or data[:2] != b"\xff\xd8":
        die("not a JPEG file")
    pos = 2
    width = height = None
    saw_eoi = False
    while pos + 1 < len(data):
        if data[pos] != 0xFF:
            die("bad JPEG marker at offset %d" % pos)
        marker = data[pos + 1]
        pos += 2
        if marker == 0xD8:  # SOI, no payload
            continue
        if marker == 0xD9:  # EOI
            if pos != len(data):
                die("trailing bytes after JPEG EOI")
            saw_eoi = True
            break
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            continue  # standalone markers
        if pos + 2 > len(data):
            die("truncated JPEG segment")
        seg_len = struct.unpack(">H", data[pos:pos + 2])[0]
        if seg_len < 2 or pos + seg_len > len(data):
            die("truncated JPEG segment")
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            if seg_len < 7:
                die("bad JPEG frame segment")
            height, width = struct.unpack(">HH", data[pos + 3:pos + 7])
        if marker == 0xDA:  # SOS: entropy data follows; scan for EOI
            rest = data[pos + seg_len:]
            idx = rest.find(b"\xff\xd9")
            if idx < 0:
                die("JPEG has no EOI marker")
            if idx + 2 != len(rest):
                die("trailing bytes after JPEG EOI")
            saw_eoi = True
            break
        pos += seg_len
    if width is None or height is None:
        die("JPEG has no frame header")
    if not saw_eoi:
        die("JPEG has no EOI marker")
    return width, height


def validate(data):
    """Check size, format, dimensions and wholeness; return dimensions."""
    if len(data) > MAX_BYTES:
        die("image is %d bytes, over the 1048576 limit" % len(data))
    if data[:8] == PNG_MAGIC:
        width, height = png_dimensions_and_integrity(data)
        kind = "PNG"
    elif data[:3] == JPEG_MAGIC:
        width, height = jpeg_dimensions_and_integrity(data)
        kind = "JPEG"
    else:
        die("image is neither PNG nor JPEG (magic bytes)")
    if width > MAX_SIDE or height > MAX_SIDE:
        die("image is %dx%d, over the 1024x1024 limit" % (width, height))
    if width <= 0 or height <= 0:
        die("image has a zero dimension")
    return kind, width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    try:
        with open(source, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        print("error: cannot read %s: %s" % (source, exc), file=sys.stderr)
        return 1
    try:
        kind, width, height = validate(data)
    except GateError as exc:
        print("error: gate failed: %s" % exc, file=sys.stderr)
        return 1
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, SOURCE_NAME)
    with open(target, "wb") as handle:
        handle.write(data)
    print("wrote %s (%s %dx%d, %d bytes)" % (target, kind, width, height,
                                             len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
