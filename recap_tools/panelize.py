"""Turns scrolling screenshots of a vertical comic into clean, numbered panels.

Usage (from the WanGP folder):
    python recap_tools/panelize.py <screenshots folder> [--out <folder>]

The folder can hold normal screenshots, long scroll captures, or PDFs such as
an iPhone Safari "Full Page" screenshot (needs: pip install pypdfium2).

Steps:
  1. Loads the files in file name order (phone names are already in time order).
  2. Removes the phone status bar and app menus: rows that look identical in every
     screenshot are interface, not comic.
  3. Stitches the screenshots into one long strip, removing the parts that overlap.
  4. Splits the strip into panels at the empty gaps between them.

Writes <out>/strip.png (the whole episode) and <out>/panel_001.png, panel_002.png, ...
Take the screenshots with some overlap (a quarter of the screen or more) so no panel is lost.
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")
PDF_WIDTH = 1440        # pixel width PDF pages are rendered at
MAX_OVERLAP = 4000      # rows searched for an overlap, keeps long captures fast


def load_pdf(path):
    """All pages of a PDF rendered and joined top to bottom into one tall image."""
    try:
        import pypdfium2
    except ImportError:
        sys.exit("Reading PDFs needs pypdfium2: run  pip install pypdfium2")
    pdf = pypdfium2.PdfDocument(path)
    pages = []
    for page in pdf:
        if page.get_height() >= 14399:
            print(f"WARNING: {os.path.basename(path)} hits the PDF maximum page height, so the comic is probably "
                  "cut off at the end. Screenshot the rest, starting a little before where it stops.")
        scale = PDF_WIDTH / page.get_width()
        pages.append(np.asarray(page.render(scale=scale).to_pil().convert("RGB")))
    width = min(p.shape[1] for p in pages)
    return np.vstack([p[:, :width] for p in pages])


def load_screenshots(folder):
    names = sorted(f for f in os.listdir(folder) if f.lower().endswith(IMAGE_EXTS + (".pdf",)))
    if not names:
        sys.exit(f"No screenshots or PDFs found in {folder}")
    images = [load_pdf(os.path.join(folder, n)) if n.lower().endswith(".pdf")
              else np.asarray(Image.open(os.path.join(folder, n)).convert("RGB")) for n in names]
    width = images[0].shape[1]
    # Screenshots from the same phone share a width; rescale any odd one out.
    for i, img in enumerate(images):
        if img.shape[1] != width:
            h = round(img.shape[0] * width / img.shape[1])
            images[i] = np.asarray(Image.fromarray(img).resize((width, h), Image.LANCZOS))
    print(f"Loaded {len(images)} screenshots ({width}px wide)")
    return images


def interface_rows(images, tolerance=6.0):
    """Number of rows at the top and bottom that never change between screenshots."""
    # Only same-size screenshots line up; long captures and PDFs are left as they are.
    if len(images) < 3 or len({img.shape[0] for img in images}) > 1:
        return 0, 0
    height = min(img.shape[0] for img in images)
    stack = np.stack([img[:height].astype(np.float32).mean(axis=2) for img in images])
    changing = stack.std(axis=0).mean(axis=1) > tolerance
    rows = np.flatnonzero(changing)
    if len(rows) == 0:
        return 0, 0
    return int(rows[0]), int(height - 1 - rows[-1])


def row_signatures(img, columns=64):
    """Each row shrunk to a few averaged columns, for fast and noise tolerant matching."""
    gray = img.astype(np.float32).mean(axis=2)
    usable = gray.shape[1] - gray.shape[1] % columns
    return gray[:, :usable].reshape(gray.shape[0], columns, -1).mean(axis=2)


def find_overlap(prev, nxt, min_overlap=60, max_error=8.0, min_detail=3.0):
    """Row in prev where nxt starts, or None when the two screenshots do not overlap.

    Compares the whole overlapping area for every possible scroll position, ignoring
    positions where that area is plain background, since those would match anywhere.
    """
    a, b = row_signatures(prev), row_signatures(nxt)
    best, best_error = None, max_error
    for start in range(1, len(a) - min_overlap):
        rows = min(len(a) - start, len(b))
        error = np.abs(a[start:start + rows] - b[:rows]).mean()
        if error < best_error and b[:rows].std() >= min_detail:
            best, best_error = start, error
    return best


def stitch(images, top, bottom):
    pieces = [img[top:img.shape[0] - bottom] for img in images]
    strip = pieces[0]
    for no, piece in enumerate(pieces[1:], 2):
        window = min(piece.shape[0], MAX_OVERLAP)
        tail = strip[-window:]
        start = find_overlap(tail, piece[:window])
        if start is None:
            print(f"  screenshot {no}: no overlap found, appended as is (a few rows may be missing)")
            strip = np.vstack([strip, piece])
        else:
            strip = np.vstack([strip, piece[len(tail) - start:]])
    print(f"Stitched strip: {strip.shape[1]}x{strip.shape[0]}")
    return strip


def split_panels(strip, min_gap=20, min_panel=120, sliver=400, tolerance=10.0, max_color=8.0):
    """Cuts at the gutters between panels: runs of plain rows.

    Neutral gutters (white, black, gray fades) always cut. A plain run in a real color can
    also be a dark or misty stretch inside one panel, so it only cuts when both sides are
    full size panels rather than slivers.
    """
    pixels = strip.astype(np.float32)
    flat = pixels.mean(axis=2).std(axis=1) < tolerance
    color = (pixels.max(axis=2) - pixels.min(axis=2)).mean(axis=1)
    gutters, y = [], 0
    while y < len(flat):
        if not flat[y]:
            y += 1
            continue
        end = y
        while end < len(flat) and flat[end]:
            end += 1
        if end - y >= min_gap:
            gutters.append([y, end, color[y:end].mean() < max_color])
        y = end

    def pieces():
        bounds = [(0, 0)] + [(g0, g1) for g0, g1, _ in gutters] + [(len(flat), len(flat))]
        return [bounds[i + 1][0] - bounds[i][1] for i in range(len(bounds) - 1)]

    # Drop colored gutters next to slivers, one at a time, until none is left.
    while True:
        sizes = pieces()
        weak = [i for i, (_, _, neutral) in enumerate(gutters)
                if not neutral and min(sizes[i], sizes[i + 1]) < sliver]
        if not weak:
            break
        gutters.pop(min(weak, key=lambda i: min(sizes[i], sizes[i + 1])))

    panels, start = [], 0
    for g0, g1, _ in gutters + [[len(flat), len(flat), True]]:
        if g0 - start >= min_panel:
            panels.append((start, g0))
        start = g1
    return panels


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder", help="folder with the screenshots, in order")
    parser.add_argument("--out", help="output folder (default: <folder>_panels)")
    parser.add_argument("--top", type=int, help="rows to cut from the top of each screenshot (default: auto)")
    parser.add_argument("--bottom", type=int, help="rows to cut from the bottom of each screenshot (default: auto)")
    parser.add_argument("--margin", type=int, default=8, help="empty margin kept around each panel")
    args = parser.parse_args()

    images = load_screenshots(args.folder)
    top, bottom = interface_rows(images)
    top = args.top if args.top is not None else top
    bottom = args.bottom if args.bottom is not None else bottom
    print(f"Removing {top}px at the top and {bottom}px at the bottom of each screenshot")

    strip = stitch(images, top, bottom)
    out = args.out or args.folder.rstrip("/\\") + "_panels"
    os.makedirs(out, exist_ok=True)
    Image.fromarray(strip).save(os.path.join(out, "strip.png"))

    panels = split_panels(strip)
    for no, (y0, y1) in enumerate(panels, 1):
        y0, y1 = max(0, y0 - args.margin), min(len(strip), y1 + args.margin)
        Image.fromarray(strip[y0:y1]).save(os.path.join(out, f"panel_{no:03d}.png"))
    print(f"Saved {len(panels)} panels to {out}")


if __name__ == "__main__":
    main()
