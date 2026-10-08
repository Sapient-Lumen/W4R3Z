from pathlib import Path
import shutil

src = Path('/mnt/data/AnonSync-rev0175-2026.03.20.19.52-surfaceparitysavebackpages')
dst = Path('/mnt/data/AnonSync-rev0176-2026.03.20.20.12-captureproofcleanuppages')
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

# This revision adds docs/23 and docs/313-316, refreshes README/status,
# and appends rev0176 addenda into the main evaluation, direction, workbench,
# pattern language, architecture, roadmap, and sources notes.
