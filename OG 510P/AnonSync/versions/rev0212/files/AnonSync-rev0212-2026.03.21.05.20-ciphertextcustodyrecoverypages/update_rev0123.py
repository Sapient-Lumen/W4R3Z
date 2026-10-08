from pathlib import Path
import shutil

src_root = Path('/mnt/data/work_anonsync/anonsync_rev0123')
dst_parent = Path('/mnt/data/anonsync_export_rev0123')
dst_root = dst_parent / 'anonsync_rev0123'

if dst_parent.exists():
    shutil.rmtree(dst_parent)
dst_parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src_root, dst_root)

print('Prepared', dst_root)
print('Added docs:')
print('- 153-policy-editor-scope-pivot-and-baseline-effect-preview-interface-spec.md')
print('- 154-home-now-soon-quiet-and-review-rhythm-interface-spec.md')
print('- 155-draft-object-summary-outlier-split-and-apply-interface-spec.md')
print('- 156-projection-parity-and-surface-capability-contract-interface-spec.md')
