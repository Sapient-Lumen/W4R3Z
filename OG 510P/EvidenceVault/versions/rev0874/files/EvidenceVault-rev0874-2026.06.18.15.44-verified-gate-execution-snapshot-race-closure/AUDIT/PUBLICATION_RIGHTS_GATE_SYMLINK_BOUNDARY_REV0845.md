# Publication rights gate symlink-boundary audit — rev0845

This audit records rev0845 hardening of the fresh publication-rights scan around symlink boundaries and additional local rights-reference forms.

- Status: `publication_rights_gate_symlink_boundary_and_html_rst_forms_validated`
- Helper SHA-256: `abfab7a27c008d49f2157a70f66660cdf15ed3f39af5af3767afa85a1d86dd73`
- Validator: `scripts/validate_publication_rights_gate_symlink_boundary_rev0845.py`
- Validator return code: `0`

## Required behavior
- symlinked scan input under sources/ blocks a rights-ready ledger without reading through the link
- local LICENSE target that is itself a symlink blocks even when it resolves inside the archive
- HTML href, reStructuredText inline link, and reStructuredText reference definitions pointing at missing rights files are checked
- in-document #license anchors are ignored rather than misclassified as missing local files

## Validator output

```text
publication-rights-gate-symlink-boundary-rev0845: OK
```

## Limit

The scan still checks local rights-reference integrity only; it does not determine license compatibility or legal sufficiency.
