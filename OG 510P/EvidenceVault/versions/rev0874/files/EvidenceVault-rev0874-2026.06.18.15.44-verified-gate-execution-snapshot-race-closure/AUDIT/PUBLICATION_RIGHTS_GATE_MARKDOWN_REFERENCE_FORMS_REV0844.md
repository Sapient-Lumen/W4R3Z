# Publication rights gate Markdown reference-form audit — rev0844, refreshed in rev0845

This carried-forward audit was refreshed after rev0845 extended the same parser boundary and changed the shared rights-gate helper hash.

- Status: `publication_rights_gate_markdown_reference_forms_validated_refreshed_with_rev0845_parser_boundary`
- Helper SHA-256: `abfab7a27c008d49f2157a70f66660cdf15ed3f39af5af3767afa85a1d86dd73`
- Validator: `scripts/validate_publication_rights_gate_markdown_reference_forms_rev0844.py`
- Validator return code: `0`

## Required behavior
- inline Markdown [license](LICENSE "title") missing target blocks a rights-ready fixture
- angle-wrapped [NOTICE](<NOTICE.md> "title") missing target blocks
- reference-style [id]: COPYING "title" missing target blocks
- resolved reference-style local LICENSE target allows a rights-ready fixture
- CLI --json works with the extended parser and emits no Python bytecode

## Validator output

```text
publication-rights-gate-markdown-forms-rev0844: OK
```

## Limit

The scan remains intentionally narrow; it checks local rights-file reference integrity, not license compatibility or legal sufficiency.
