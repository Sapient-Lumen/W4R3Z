from pathlib import Path
import shutil

src_root = Path('/mnt/data/work_anonsync/anonsync_rev0122')
dst_parent = Path('/mnt/data/anonsync_export_rev0122')
dst_root = dst_parent / 'anonsync_rev0122'

if dst_parent.exists():
    shutil.rmtree(dst_parent)
dst_parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src_root, dst_root)

print('Prepared', dst_root)
print('Added docs:')
print('- 149-interface-shell-navigation-and-persistent-context-spec.md')
print('- 150-subject-workspace-and-review-stack-interface-spec.md')
print('- 151-inherited-versus-excepted-value-explanation-interface-spec.md')
print('- 152-command-palette-bulk-review-and-apply-boundary-interface-spec.md')
