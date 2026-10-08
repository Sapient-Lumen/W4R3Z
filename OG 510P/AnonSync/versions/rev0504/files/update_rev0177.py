from pathlib import Path
import shutil

src = Path('/mnt/data/AnonSync-rev0176-2026.03.20.20.12-captureproofcleanuppages')
dst = Path('/mnt/data/AnonSync-rev0177-2026.03.20.19.27-principalauthorityrepairpages')
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

# This revision adds docs/24 and docs/317-320, refreshes README/status,
# and appends rev0177 addenda into the main evaluation, interface grammar,
# workbench, product direction, architecture, roadmap, and sources notes.
