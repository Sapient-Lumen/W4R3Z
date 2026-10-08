# P0002-D010 offline disclosed-reader field kit — rev0061

Give the reader only `P0002-D010_field_test.html`. It contains the disclosure, exact poem body, response form, and an offline JSON-download action.

Reader procedure:

1. Open the HTML file in a browser with no other cube materials supplied.
2. Read the disclosure and poem, complete every field, and click **Validate and download JSON**.
3. Return `P0002-D010-reader-response.json` to the operator. Do not add personal identifiers.

Operator procedure:

```bash
python tools/record_reader_response.py --root . --input P0002-D010-reader-response.json --dry-run
python tools/record_reader_response.py --root . --input P0002-D010-reader-response.json
```

Append only after the dry run succeeds. The intake tool assigns provenance fields, rejects personal-data keys and likely contact strings, rejects blanks and duplicate response fingerprints, and keeps the result as local editorial pressure only.

This kit contains no source packet, evaluator rubric, analytics, remote assets, network calls, or pre-filled response. Kit readiness is not a reader response, admission, evidence status, publication clearance, or proof of poem quality.
