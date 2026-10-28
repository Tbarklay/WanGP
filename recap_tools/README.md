# Recap Tools

## panelize.py: screenshots to clean panels

It accepts any of these, in one folder:
- **Normal screenshots**, each overlapping the previous by about a quarter of the screen.
- **Long scroll captures** (Samsung "Capture more", Pixel "Capture more"). Overlap them a little if you take several.
- **PDFs**, such as an iPhone Safari "Full Page" screenshot. Needs a one-time `pip install pypdfium2`.

1. Put the files in one folder, in reading order. Phone names are already in time order.
3. From the WanGP folder run:

       python recap_tools/panelize.py path\to\screenshots

It removes the phone status bar and app menus, stitches everything into one strip without the overlaps,
and splits it into panels at the gaps between them. The results go into `<screenshots>_panels`:
`strip.png` (the whole episode) and `panel_001.png`, `panel_002.png`, ...

Options:
- `--out <folder>`: choose the output folder
- `--top N` / `--bottom N`: cut exactly N pixels from the top or bottom of each screenshot,
  if the automatic interface removal leaves a menu bar or cuts into the comic
  (it needs at least 3 same-size screenshots to detect the bars by itself; long captures and PDFs are kept whole)

A website PDF also contains the page around the comic (site header, buttons, comments). Those come out as extra
panels at the start and end: delete them.
