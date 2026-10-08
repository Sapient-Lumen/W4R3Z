from pathlib import Path
import shutil

src_root = Path('/mnt/data/work_anonsync/anonsync_rev0125')
dst_parent = Path('/mnt/data/anonsync_export_rev0125')
dst_root = dst_parent / 'anonsync_rev0125'

if dst_parent.exists():
    shutil.rmtree(dst_parent)
dst_parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(src_root, dst_root)

print('Prepared', dst_root)
print('Added docs:')
print('- 161-offer-issuance-reissue-and-audit-surface-interface-spec.md')
print('- 162-portable-offer-inspection-browser-handoff-and-local-claim-continuity-interface-spec.md')
print('- 163-settings-layer-collapse-and-effective-truth-interface-spec.md')
print('- 164-future-arrival-defaults-placement-memory-and-device-wide-posture-boundary-interface-spec.md')
