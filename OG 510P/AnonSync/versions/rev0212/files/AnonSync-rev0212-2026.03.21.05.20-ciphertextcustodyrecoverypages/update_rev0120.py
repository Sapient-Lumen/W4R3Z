from pathlib import Path
import shutil

src_root = Path('/mnt/data/anonsync_work_rev0120/anonsync_rev0120')
dst_parent = Path('/mnt/data/anonsync_export_rev0120')
dst_root = dst_parent / 'anonsync_rev0120'

if dst_parent.exists():
    shutil.rmtree(dst_parent)
dst_parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src_root, dst_root)

print('Prepared', dst_root)
print('Added docs:')
print('- 145-standing-baseline-rollout-and-target-cohort-delta-review-interface-spec.md')
print('- 146-baseline-drift-audit-and-rollback-proof-interface-spec.md')
