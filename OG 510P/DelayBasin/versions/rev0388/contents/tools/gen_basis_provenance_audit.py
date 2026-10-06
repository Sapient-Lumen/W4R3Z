import pathlib

from basis_provenance_audit_lib import write_basis_provenance_audit

ROOT = pathlib.Path(__file__).resolve().parents[1]
write_basis_provenance_audit(ROOT)
print('wrote BASIS-PROVENANCE-AUDIT.json')
print('wrote docs/00-meta/basis-provenance-audit.md')
