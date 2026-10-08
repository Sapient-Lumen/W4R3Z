# Session review — rev0869

## Substance delivered

- Restored two exact canonical source files as the two-byte JSON value `[]`:
  `sources/ocf_llm/examples/refused_set_empty_v1.json` and
  `sources/pact/PACT_workdir/eval_real_registry_semantic_scan/out/violations.json`. Each matches its indexed size and SHA-256
  `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- Raised exact at-path coverage to **103 / 4,586 files** and exact source
  coverage to **16 / 3,476**. With 16 historical recovery objects, **119 files /
  4,973,444 bytes** are rehydratable; **4,467 files / 101,448,546 bytes** remain
  unavailable.
- Reproduced a severe rev0868 validation bypass: a safe central-directory path
  plus a local-header-only Unicode Path extra field carrying `../escape.txt`
  was approved. The validator now rejects all alternate/unsupported extra-field
  semantics and requires exact local/central flags and extraction versions.
- Rebuilt deterministic packaging around a captured source-tree digest and
  per-file identity/hash checks. The source is recaptured after writing and
  after temporary archive validation, and the final output must still be the
  validated temporary inode with the validated SHA-256.

## Audit/refactor result

The regression suite preserves the full rev0868 duplicate/traversal/alias/
symlink/header/prefix/suffix/no-clobber coverage and adds the demonstrated
`0x7075` local-only pathname split plus same-size mutation, late-file addition,
and symlink-swap attacks against the source snapshot. All mutation cases must
leave no published artifact.

## Still at highest risk

Rights closure remains human-blocked: there is no owner-approved root license or
notice. All 17 selected StreamFold payloads remain absent, and canonical
`README.md` is still the sole unresolved present-path mismatch. The strict ZIP
profile and source snapshot improve local integrity; they are not a signed
provenance attestation or a hermetic build guarantee.
