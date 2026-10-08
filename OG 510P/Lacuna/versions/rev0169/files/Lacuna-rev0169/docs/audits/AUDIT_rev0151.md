# Audit — rev0151

## Scope

This audit examined whether Lacuna’s delayed-commitment architecture can make a verifiable fair-play promise without leaking hidden state, conflating cryptographic continuity with truth, granting secret custody to a narrator model, or creating an unaudited parallel projection. It also reviewed the runtime/schema operation registry, dormant particle-update code, migration integrity, perspective noninterference, receipt stability, parser/schema parity, and deterministic rebuild.

## A-0151-01 — plastic hidden worlds had no verifiable counterweight

**Severity:** high narrative integrity

**Before:** Lacuna could mark an assignment hard and record its authored basis, but a skeptical player had no cryptographic evidence that a selected secret existed before later investigation.

**Risk:** a host could retrospectively choose a culprit or continuity answer, then describe it as preplanned. The event ledger would faithfully record the later assertion without proving earlier commitment.

**Repair:** add domain-separated salted SHA-256 fair-play seals. Only the digest and public metadata enter the cube before reveal; the opening can later be verified exactly.

**Evidence:** domain-binding, secret-absence, wrong-opening refusal, exact-reveal, receipt, CLI, replay, and migration tests.

## A-0151-02 — policy commitment could be mistaken for cryptographic commitment

**Severity:** high semantic clarity

**Before:** the word `precommitment` appeared in design doctrine as a possible hard-assignment basis, while the threat model correctly noted that this was only a policy label.

**Risk:** documentation or integrators could overclaim that a hard assignment proved prior authorship or byte continuity.

**Repair:** introduce a separate `fair_play_seals` record kind and explicitly preserve the distinction among assignment commitment, anchored assertion, and cryptographic opening. Reveal does not create truth or canon automatically.

**Evidence:** protocol, glossary, threat-model, context-contract, and receipt nonclaims.

## A-0151-03 — unsalted low-entropy secrets would be enumerable

**Severity:** high confidentiality

**Before:** a straightforward hash of a culprit ID or one-of-five answer could be brute-forced by anyone holding the digest.

**Risk:** publishing a commitment would disclose the secret by enumeration.

**Repair:** require a fresh 256-bit nonce in every opening and keep it outside the cube until reveal. Validate exact lowercase-hex length and use operating-system cryptographic randomness by default.

**Evidence:** opening construction and nonce-validation tests; research comparison with RFC 9901’s 128-bit recommended minimum.

## A-0151-04 — structured commitment bytes were underspecified

**Severity:** high interoperability and integrity

**Before:** “hash the JSON” would leave whitespace, key ordering, number serialization, Unicode, and runtime differences unresolved.

**Risk:** equivalent-looking openings could hash differently, or different implementations could accept incompatible commitment bytes.

**Repair:** define and test a deliberately narrow portable JSON profile: sorted compact JSON, UTF-8, no floats, safe integers only, bounded nesting/items/bytes, and no Unicode normalization. Name the scheme explicitly and refuse to claim JCS conformance.

**Evidence:** float and unsafe-integer refusal, schema validation, opening self-check, and protocol formula.

## A-0151-05 — commit and reveal in one transaction would be vacuous

**Severity:** high protocol integrity

**Before:** a naïve multi-operation implementation could insert the digest and its opening atomically, allowing the host to claim “precommitment” at the moment of disclosure.

**Risk:** the primitive would provide no temporal ordering even within Lacuna’s own ledger.

**Repair:** reveal and void require an origin seal whose event already belongs to a committed earlier change-set. A same-change reveal or void refuses the entire transaction.

**Evidence:** atomic same-change refusal leaves event count, head, and projections untouched.

## A-0151-06 — secret material could leak into event, receipt, or context before reveal

**Severity:** critical confidentiality

**Before:** a convenient implementation might store the opening file as source metadata, echo it in a receipt, or include it in planner/audience context.

**Risk:** the “hidden” answer would be present in the cube, backups, model context, or logs before intended disclosure.

**Repair:** `seal create` parses the external opening but writes only scheme, digest, label, purpose, visibility, audience, and optional provenance source ID. Pre-reveal events, projection, list output, receipt, render output, and context contain no nonce or payload.

**Evidence:** serialized ledger/receipt secret-absence tests and CLI output assertions.

## A-0151-07 — even a director model was overprivileged for secret custody

**Severity:** critical authority separation

**Before:** the director grant was defined as all runtime operations, which would automatically have included newly added seal operations.

**Risk:** prompt injection, model overadaptation, or accidental output could create, reveal, or void the secret commitment. A model could invent a solution and “precommit” it in the same reasoning loop.

**Repair:** define host-custody operations explicitly and subtract them from `DIRECTOR_TURN_OPERATIONS`. The direct change-set/CLI host entrance remains capable; ordinary turn proposals are refused before mutation.

**Evidence:** grant enumeration/schema parity and illicit-director-operation refusal test.

## A-0151-08 — a restricted receipt could leak hidden provenance topology

**Severity:** high confidentiality

**Before:** the seal projection may cite a privileged source containing author notes. Generic projection or explanation logic could expose the source ID even while withholding its body.

**Risk:** identifiers and dependency edges can reveal hidden ontology, authoring structure, or the existence of a private document.

**Repair:** perspective seal views and receipts omit `source_id`; perspective explanations scrub the source dependency completely. Planner explanations retain full custody.

**Evidence:** player/outsider context and explanation noninterference test.

## A-0151-09 — the first receipt core changed after reveal

**Severity:** critical receipt integrity

**Before during rev0151 development:** the initial receipt core reused a live seal view containing `status`, `revealed_seq`, and `voided_seq`.

**Risk:** an externally anchored `receipt_sha256` would change at the moment of reveal, defeating its purpose as evidence of the earlier commitment.

**Repair:** split immutable origin fields from lifecycle fields. `receipt_core` contains only origin seal metadata and event envelope. Current status, opening, resolution, and head remain outside the core.

**Evidence:** tests assert complete core and digest equality before and after reveal and recompute the digest independently.

## A-0151-10 — receipt claims could outrun local trust

**Severity:** high trust-model accuracy

**Before:** an origin event timestamp and hash chain could be rhetorically mistaken for a trusted timestamp or globally unique history.

**Risk:** a hostile host could fork the cube, backdate local metadata, or reveal only one of many prepared seals while presenting a locally valid receipt as external proof.

**Repair:** every receipt states that it proves only byte-stable opening continuity; it explicitly denies truth, completeness, authorship, uniqueness, external timestamping, signatures, and non-equivocation. The creation command instructs the verifier to retain or externally anchor the stable receipt digest.

**Evidence:** receipt output, threat model, protocol, and Sigstore/RFC 9162 research notes.

## A-0151-11 — reveal projection needed event-exact verification

**Severity:** high replay integrity

**Before:** adding a projection table without event-payload comparison would allow coordinated edits to nonce, payload, reason, or sequence while preserving local table shape.

**Risk:** a corrupted projection could show a different opening than the immutable reveal event.

**Repair:** full verification checks origin event, terminal event, lifecycle exclusivity, field equality, phase separation, digest recomputation, sequence binding, missing projections, and audience shape. Deterministic rebuild restores event-derived state.

**Evidence:** projection tamper produces both reveal-projection mismatch and reveal-digest errors; rebuild restores the opening without changing head.

## A-0151-12 — opening parser and JSON Schema could accept different envelopes

**Severity:** medium exchange integrity

**Before during rev0151 development:** the JSON Schema required `event` and `custody_warning`, but the runtime parser treated them as optional and did not validate the event constant.

**Risk:** a document rejected by tooling could be accepted by the executable, weakening the custody warning and protocol identity boundary.

**Repair:** runtime parsing now requires the exact field set, event constant, schema, scheme, non-empty custody warning, digest form, nonce, payload, and self-consistency.

**Evidence:** malformed-envelope refusal tests and Draft 2020-12 schema validation.

## A-0151-13 — current receipt lifecycle needed an exchange schema

**Severity:** medium integration reliability

**Before:** the new receipt was structured but undocumented as a machine-checkable exchange contract.

**Risk:** hosts could silently drop the stable core, confuse current state with anchorable state, or accept impossible lifecycle combinations.

**Repair:** add `seal-receipt.v1.schema.json` with strict fields, portable payload profile, sealed/revealed/voided lifecycle shapes, and opening/resolution consistency.

**Evidence:** meta-schema validation and concrete lifecycle-shape test.

## A-0151-14 — runtime registries advertised an unimplemented particle mutation

**Severity:** high API honesty

**Before during audit:** `update_particle_bank` and `particle.updated` remained in public operation/event registries even though no preparation or projection handler implemented them.

**Risk:** exchange schemas and director grants could promise an operation that always failed in an assertion path, and future callers might infer a supported probabilistic state transition that did not exist.

**Repair:** remove the ghost operation and event from runtime registries and turn schemas. Delete the now-unreferenced experimental `particles.py` implementation rather than shipping policy code disguised as a kernel feature.

**Evidence:** runtime/schema parity tests and repository search show no public particle operation.

## A-0151-15 — dormant particle tables were outside rebuild custody

**Severity:** high projection hygiene

**Before during audit:** schema-compatibility tables `particle_updates` and `particle_update_members` were not included in `PROJECTION_TABLES`, even though no event protocol owned them.

**Risk:** private or legacy rows could survive a rebuild and masquerade as replayed kernel state.

**Repair:** retain the tables only for database-shape compatibility, flag any rows as `unsupported-particle-projection`, and clear them during deterministic rebuild before replaying event-owned projections.

**Evidence:** injected unsupported row is detected; rebuild removes it and preserves the ledger head.

## A-0151-16 — database schema evolution needed ordered custody

**Severity:** high operational integrity

**Before:** the new seal table could not be assumed present in schema-5 cubes, and automatic mutation on open would violate Lacuna’s migration doctrine.

**Risk:** old cubes could fail ambiguously or acquire unrecorded schema state.

**Repair:** raise the database schema to 6, add a digest-identified 5→6 migration, require explicit `lacuna migrate`, preserve the event head, and retain ordered migration from coherent schema 1/2/3/4/5 histories.

**Evidence:** schema-5 downgrade fixture refuses normal open, migrates explicitly, preserves head, records migration custody, and passes verification.

## A-0151-17 — seal visibility was not enough without context/render integration

**Severity:** medium usability and confidentiality

**Before:** a projection accessible only through low-level SQL or planner-only methods would invite hosts to construct ad hoc views, while generic context inclusion could leak restricted records.

**Risk:** inconsistent player displays and parallel authorization policy.

**Repair:** add planner and perspective seal context paths, visibility-aware list/receipt/verify APIs, status rendering, status counts, snapshot inclusion, and explanation support under the existing context firewall.

**Evidence:** context, render, perspective, status, explanation, and CLI tests.

## A-0151-18 — documentation overstated director authority after the new boundary

**Severity:** medium operational safety

**Before:** the turn protocol said a director could use all kernel operations.

**Risk:** host implementers could treat model privilege as administrative privilege and route secret openings through model proposals.

**Repair:** update the turn contract and interaction-surface documentation to name the explicit host-only seal exception.

**Evidence:** documentation link audit and schema/grant tests.

## A-0151-19 — malformed Unicode escaped the structured refusal boundary

**Severity:** medium protocol portability

**Before during audit:** Python payload strings could contain lone UTF-16 surrogate code points. Canonicalization reached UTF-8 encoding and raised a raw `UnicodeEncodeError`.

**Risk:** malformed openings would fail differently across runtimes and bypass Lacuna’s stable error contract.

**Repair:** validate every payload string and object key as Unicode scalar values before canonicalization; mirror the restriction in opening and receipt schemas.

**Evidence:** value/key surrogate regression tests, schema meta-validation, and the 109-test acceptance run.

## A-0151-20 — the executable inherited arbitrary ambient Python state

**Severity:** high runtime-boundary hygiene

**Before during audit:** the Python shebang launcher initialized normal `site`, permitting machine-specific site packages and `sitecustomize` hooks to execute before Lacuna. On the acceptance host, a no-op Python process consumed roughly 286 MB and repeated CLI tests became pathologically slow.

**Risk:** hidden runtime dependencies, supply-chain expansion, nondeterministic startup behavior, and denial-of-service through unrelated host configuration.

**Repair:** replace the launcher with a POSIX wrapper that sets the local `src/` path and executes `python3 -S -m lacuna.cli`. The kernel remains standard-library-only.

**Evidence:** launcher smoke fell to roughly 32 MB on the audit host; all six subprocess CLI tests complete together and the full 109-test suite passes.

## Residual risks

Rev0151 intentionally does not solve:

- externally trusted time or signatures;
- fork detection when no verifier retains a receipt;
- proof that only one seal was prepared;
- proof that a sealed resolution was fair, coherent, or deducible;
- clue-graph commitment or chronology;
- selective disclosure of leaves inside one payload;
- threshold/multi-party opening custody;
- semantic binding from a revealed payload to claims or world assignments;
- protection from an authorized hostile host or director leaking other hidden state in prose;
- cryptographic erasure of opening files, shell history, backups, or model-provider logs.

These limits are explicit so the primitive can remain useful without becoming a story-shaped security claim.
