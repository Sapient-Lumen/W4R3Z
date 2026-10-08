# Disinformation response playbook (evidence artifact targeting)

Use this playbook when a disinformation campaign targets evidence artifacts, results packages, or mirrors.

## Actions
- Activate:
  - `CHECK:artifacts/checklists/results-disclosure-policy-checklist.md`
  - `CHECK:artifacts/checklists/incident-comms-proof-checklist.md`
- Publish a signed `hfv.public.notice` **PublicNotice** with `notice_type: rumor_control` (or `correction`) that includes:
  - canonical artifact hashes / checkpoint IDs
  - mirror list
  - offline verification steps
  - references to relevant evidence packets/envelopes by digest

## Evidence obligations
- Ensure a third-party can verify without privileged access (observer kit).
- Prefer reproducible commands + expected digests over screenshots.

See: `DOC:docs/186-incident-communications-as-evidence.md`.
