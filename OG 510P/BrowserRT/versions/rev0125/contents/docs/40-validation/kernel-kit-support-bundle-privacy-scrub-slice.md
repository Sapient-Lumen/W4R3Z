# Kernel Kit Support Bundle Privacy Scrub Slice — rev0107

## Purpose

This slice makes the support-bundle handoff privacy boundary executable instead of relying on reviewer discipline. A Kernel Kit support bundle can carry useful proof structure, but it also naturally contains local OPFS prefixes, handoff digests, exact command text, possible URLs, lock names, and other scalars that should not be casually copied into future notes or public debugging transcripts.

The new privacy scrub produces a compact, proof-preserving handoff summary. It redacts sensitive scalars/objects into deterministic local `fnv32:` digests plus type/length metadata, keeps proof booleans and section names visible, and replaces exact command text with command identity digests.

## Executable proof

Run:

```bash
node tools/run_tests.mjs --tier release --id demo:kernel-kit-support-bundle-privacy-scrub-proof --jobs 1
```

The proof builds the normal Kernel Kit support bundle, validates its embedded scrub report, regenerates a scrub report from the bundle, and asserts that the scrubbed output does not contain raw `sha256:`, `browserrt/rev`, `BrowserRT.KernelKitDemo.handoff`, `http://`, or `https://` tokens.

## Boundary

This is a privacy scrub checkpoint, not a production privacy claim.

Non-claims include:

- No production support-bundle privacy claim.
- No anonymization, differential-privacy, or irreversible de-identification claim.
- No side-channel, fingerprinting, or telemetry-ingestion mitigation claim.
- No support-bundle authenticity, signing, or trust validation claim.
- No automated security review or data-loss-prevention claim.

## Risk reduced

Before this slice, the support bundle was useful but too easy to treat as a safe handoff object. After this slice, the bundle carries an embedded `privacyScrub` report, the browser demo exposes a scrub button/API, and release/browser probes assert the scrub path directly.

This checkpoint is not side-channel mitigation and must not be presented as telemetry-ingestion privacy hardening.
