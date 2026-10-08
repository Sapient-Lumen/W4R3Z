from pathlib import Path
import shutil

"""
Revision helper for rev0095.

This script mirrors the pattern used by earlier revisions:
- copy /mnt/data/anonsync_rev0094 to /mnt/data/anonsync_rev0095
- then overwrite the files that changed in rev0095 from the checked-out archive directory
"""

src = Path('/mnt/data/anonsync_rev0094')
dst = Path('/mnt/data/anonsync_rev0095')
here = Path(__file__).resolve().parent

changed = [
    'README.md',
    'docs/00-status.md',
    'docs/10-resilio-sync-evaluation.md',
    'docs/30-interface-spec.md',
    'docs/31-daemon-api-spec.md',
    'docs/32-interface-flows.md',
    'docs/38-operator-workbench-interface-spec.md',
    'docs/39-interface-pattern-language.md',
    'docs/40-architecture-decisions.md',
    'docs/50-roadmap.md',
    'docs/64-critical-open-questions.md',
    'docs/108-approval-memory-constellation-mutation-and-family-rebase-interface-spec.md',
]

if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

for rel in changed:
    src_file = here / rel
    dst_file = dst / rel
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_file)

print('rev0095 materialized at', dst)
