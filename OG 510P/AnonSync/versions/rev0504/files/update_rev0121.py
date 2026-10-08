from pathlib import Path
import shutil

src_root = Path('/mnt/data/anonsync_work_rev0121/anonsync_rev0121')
dst_parent = Path('/mnt/data/anonsync_export_rev0121')
dst_root = dst_parent / 'anonsync_rev0121'

if dst_parent.exists():
    shutil.rmtree(dst_parent)
dst_parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src_root, dst_root)

print('Prepared', dst_root)
print('Added docs:')
print('- 147-baseline-exception-request-and-justification-review-interface-spec.md')
print('- 148-exception-expiry-renewal-promotion-and-baseline-rejoin-proof-interface-spec.md')
