# Recap Tools

## panelize.py: screenshots to clean panels

1. Scroll through the episode and take screenshots, overlapping each one with the previous by about a quarter of the screen.
2. Put them in one folder, in order. Phone screenshot names are already in time order.
3. From the WanGP folder run:

       python recap_tools/panelize.py path\to\screenshots

It removes the phone status bar and app menus, stitches everything into one strip without the overlaps,
and splits it into panels at the gaps between them. The results go into `<screenshots>_panels`:
`strip.png` (the whole episode) and `panel_001.png`, `panel_002.png`, ...

Options:
- `--out <folder>`: choose the output folder
- `--top N` / `--bottom N`: cut exactly N pixels from the top or bottom of each screenshot,
  if the automatic interface removal leaves a menu bar or cuts into the comic
  (it needs at least 3 screenshots to detect the bars by itself)
