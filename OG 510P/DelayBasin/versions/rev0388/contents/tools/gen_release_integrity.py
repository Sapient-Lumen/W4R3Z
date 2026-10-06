import pathlib

from release_integrity_lib import write_release_integrity

ROOT = pathlib.Path(__file__).resolve().parents[1]
write_release_integrity(ROOT, None, None)
print("wrote FILE-MANIFEST.json")
print("wrote CHECKSUMS.sha256")
print("wrote RELEASE-PROVENANCE.json")
