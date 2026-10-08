from pathlib import Path
import shutil

src_root = Path('/mnt/data/work_anonsync/anonsync_rev0124')
dst_parent = Path('/mnt/data/anonsync_export_rev0124')
dst_root = dst_parent / 'anonsync_rev0124'

if dst_parent.exists():
    shutil.rmtree(dst_parent)
dst_parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src_root, dst_root)

print('Prepared', dst_root)
print('Added docs:')
print('- 157-reviewed-mutation-commit-barrier-and-receipt-continuity-interface-spec.md')
print('- 158-adopt-rebind-reconnect-and-pre-existing-path-repair-interface-spec.md')
print('- 159-local-web-first-bringup-auth-and-empty-state-interface-spec.md')
print('- 160-narrow-width-proof-preservation-and-progressive-disclosure-interface-spec.md')
