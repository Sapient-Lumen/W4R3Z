# Private capture readiness checklist — rev0014

Before any payload capture:

- identify the exact capture target;
- record the source owner;
- record expected payload class;
- decide whether WARC/WACZ, raw PDF, HTML, or sidecar-only capture is appropriate;
- create an intake envelope;
- create or reuse a privacy preflight queue row;
- declare whether public payload display is categorically forbidden;
- plan checksum/fixity capture;
- plan rollback dependencies.

After payload capture, do not summarize. First compute fixity and run privacy preflight.
