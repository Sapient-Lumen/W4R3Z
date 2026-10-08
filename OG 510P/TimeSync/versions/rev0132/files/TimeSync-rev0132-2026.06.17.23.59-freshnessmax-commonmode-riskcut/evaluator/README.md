# TimeSync rev0132 evaluator notes

This directory contains evidence-class vocabulary, evaluator-facing examples, and the narrow adapter reference evaluator documentation.

Current operational notes:

- `MULTISOURCE-ADJUDICATOR-REV0132.md` — current-use composition with stalest-input freshness and common-mode carry-forward.
- `MULTISOURCE-ADJUDICATOR-REV0131.md` — retained background for initial multi-source composition without cherry-picking.
- `NTP-ADAPTER-EQUIVALENCE-REV0130.md` — shared bound arithmetic and cross-adapter equivalence guard.
- `NTPQ-REFERENCE-EVALUATOR-REV0129.md` — second-adapter ntpq readvar/peers replay evaluator.
- `CHRONY-AUTHPOSTURE-REV0128.md` — reported chrony authentication is retained but cannot strengthen TimeSync decisions.
- `CHRONY-CAPTURE-INSTANT-AGEGUARD-REV0127.md` — conservative tracking-command instant used for replay age growth.
- `CHRONY-LIVE-HARNESS-SOURCESTATS-REV0126.md` — fake-live harness and sourcestats diagnostic capture.
- `CHRONY-P1-POLICY-DECISION-REV0125.md` — machine-readable P1 lane policy and boundary acceptance.
- `CHRONY-INDEPENDENT-EVALUATOR-REV0124.md` — second evaluator over `chrony_observation` JSON.
- `CHRONY-CAPTURE-EVALUATOR-REV0123.md` — capture envelope and primary chrony evaluator background.
- `RFC9249-CROSSWALK-REV0124.md` — comparison guard against premature generic observation vocabulary.

Generated examples live in `chrony-p1-general-explanation.json` and `examples/evaluator/`; the multi-source current-use adjudicator lives in `tools/multisource_adjudicator.py`; the shared NTP bound engine lives in `tools/ntp_bound.py`; the shared P1 lane table currently lives in the legacy-named `p1-chrony-policy.json` with adapter-family policy IDs.

The evaluators are intentionally small. Chrony ingest consumes raw `chronyc tracking`/`sources`/`sourcestats`/`authdata`/`ntpdata` replay text or a validated `chrony_command_capture_v1` envelope. ntpq ingest consumes `ntpq -c rv` plus optional `ntpq -pn` replay text. Both derive conservative TimeState intervals through the same bound module, evaluate only `P1-general-computing`, and emit unsupported conditions explicitly. Sourcestats, authentication reports, ntpq peer details, and multi-source diversity summaries are adapter/evaluator evidence, not new core fields.

Existing signature/receipt/verifier fields are still primarily checked for schema and relational consistency. Do not infer cryptographic verification unless an implementation explicitly performs and reports it.
