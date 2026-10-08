# 170. SLSA + in-toto provenance profile for election systems (North Star)

**Track:** C (North Star)

This doc maps the North Star “transparent manufacturing/provenance” idea into
a concrete, standards-aligned artifact profile.

Instead of inventing bespoke provenance formats, we piggyback on:
- **SLSA provenance** as a widely adopted predicate for software build provenance,
- **in-toto Attestation Framework** as the common wrapper format.

Authoritative sources:
- SLSA v1.1 spec (`xref: slsa_spec_v1_1_html`)
- SLSA Provenance v1 (`xref: slsa_provenance_v1_html`)
- NIST SP 800-204D (CI/CD supply-chain security strategies) (`source: nist_sp800_204d_pdf`)
- in-toto specifications index (`xref: intoto_specs_html`)
- in-toto Statement v1 (`source: intoto_statement_v1_md`)
- in-toto predicate: SLSA Provenance (`source: intoto_slsa_provenance_predicate_md`)

## 170.1 Why supply-chain transparency belongs in voting

If the adversary is “humans + institutions”, then the long-term compromise risk is:
- build pipeline capture,
- firmware signing key misuse,
- vendor/insider collusion,
- and unverifiable field updates.

A North Star ecosystem needs *more than attestations from devices* —
it needs attestable, auditable provenance of how those devices and their software were produced.

## 170.2 Artifact profile (normative outline)

### 170.2.1 Wrapper: in-toto Statement

Provenance artifacts MUST be carried in an in-toto Statement:
- `subject` identifies the artifact (binary, firmware image, configuration package)
- `predicateType` identifies SLSA provenance v1 (or another predicate)
- `predicate` carries the provenance details

### 170.2.2 Predicate: SLSA Provenance v1

For election artifacts, minimum fields SHOULD include:
- builder identity
- build type
- invocation parameters (redacted where necessary)
- source materials (repo commit, patches)
- dependencies (SBOM references where available)
- completeness flags
- reproducibility hints
- timestamps and environment identity

See `xref: slsa_provenance_v1_html`.

### 170.2.3 Distribution and binding

Provenance MUST be distributed alongside the artifact it describes
and MUST be content-bound (hash of subject).

See SLSA guidance on distributing provenance (`xref: slsa_spec_v1_1_html`).

## 170.3 Extending beyond software (manufacturing steps)

Software provenance is necessary but not sufficient.
For hardware manufacturing, we can reuse the same in-toto wrapper with domain-specific predicates, e.g.:
- lot/build step records
- component sourcing declarations
- measurement of ROM/bootloader
- secure element provisioning events

These should be anchored to endorsement transparency (`169-endorsement-and-reference-value-transparency.md`).

## 170.4 Proof obligations

This doc strengthens:
- PO-203 (manufacturing evidence pipeline)
- **new** PO-204 (software build provenance is auditable and bound to shipped artifacts)

See `157-manufacturing-evidence-pipeline.md` for the broader pipeline.
