# Contributing

This repository is optimized for **continuity under partial observability**.

## House rules

1. Keep additions tight. Prefer one concept per doc.
2. New content must declare its status:
   - `observed`
   - `inferred`
   - `speculative`
   - `adversarial-countermodel`
   - `quarantined-wild-speculation`
3. Every new markdown doc must be linked from `docs/README.md`.
4. Every new prompt pair must get a stable `PP-####` id and an entry in the prompt pair registry.
5. Every change must preserve the distinction between:
   - what happened in the archive,
   - what we think explains it,
   - what could explain it instead,
   - and what we are willing to risk thinking from the inside even when the evidence is not yet canonical.
6. Do not paste large upstream texts. Summarize and cite.
7. Run `make lint` before packaging.
8. Risk is welcome; silent laundering is not. Quarantine exists for a reason.

## Commit/revision ethos

We prefer:
- ratchets over rhetoric,
- stable surfaces over sprawling prose,
- explicit disagreement over false consensus,
- reversible naming over premature ontology,
- bold quarantine over timid vagueness.
