# Privacy preflight method — rev0013

Privacy preflight happens before content review.

Each target is classified by likely exposure rather than by whether the source is legally public. Legal documents can contain judges, attorneys, agency officials, officers, civilians, witnesses, family members, addresses, signatures, docket identifiers, and case narratives. Official news pages can also contain status language that looks final but is not docket proof.

## Minimum rule

No payload may be summarized, OCRed, quoted, entity-linked, or publicly displayed until it has:

1. a private capture or transport-failure sidecar;
2. a fixity sidecar or explicit no-hash failure reason;
3. a privacy risk class;
4. a human review count matched to risk;
5. a redaction/display decision;
6. a rollback trigger.

## Special restriction

Names in public documents are not entity records. Rev0013 preserves this ban for officers, civilians, witnesses, family members, judges, attorneys, public officials, and document signers.

