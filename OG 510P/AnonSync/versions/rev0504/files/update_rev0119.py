from pathlib import Path
import shutil

src_root = Path('/mnt/data/anonsync_work_rev0119/anonsync_rev0119')
dst_parent = Path('/mnt/data/anonsync_export_rev0119')
dst_root = dst_parent / 'anonsync_rev0119'

if dst_parent.exists():
    shutil.rmtree(dst_parent)
dst_parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src_root, dst_root)

print('Prepared', dst_root)
print('Added docs:')
print('- 143-incident-overlay-vs-standing-mutation-review-interface-spec.md')
print('- 144-temporary-override-lease-expiry-and-residue-attestation-interface-spec.md')
