# Publication rights gate HTML/docs scan — rev0849

- Status: `html_xml_docs_rights_references_scanned`
- Validator: `scripts/validate_publication_rights_gate_html_docs_scan_rev0849.py`

## Purpose

Extend the fresh local rights-reference scan to conventional docs/documentation roots and HTML/XML-like text files so public web-rendered materials cannot carry missing local license or notice references missed by Markdown/RST scanning alone.

## Changed surfaces

- `scripts/publication_rights_gate.py`

## Validator cases

- missing docs/index.html LICENSES link blocks
- resolved docs/index.html LICENSES link passes
- missing documentation/feed.xml notices link blocks
