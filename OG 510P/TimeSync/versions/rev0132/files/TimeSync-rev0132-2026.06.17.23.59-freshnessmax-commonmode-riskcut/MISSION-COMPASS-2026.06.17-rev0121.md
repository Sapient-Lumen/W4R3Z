# TimeSync mission compass — rev0121 — 2026-06-17

## Executive judgment

The heart of TimeSync is not time transfer. It is **time-use admission control**: given a bounded time claim, local observations, and a consumer profile, decide what the consumer may safely do with that time *now* without silently upgrading precision, authenticity, freshness, traceability, or operational health into one another.

The durable design is the narrow waist:

1. `interval` — the bounded claim, not a point estimate disguised as certainty;
2. `timescale` — what the numbers mean;
3. `freshness` — whether the assessment is current enough for this use;
4. `regime` — the clock/system operating condition;
5. `source_posture` — what is known about the source relationship;
6. `applicability` — the consumer-facing use boundary.

Equally important is the split between a **wire claim** and a **local assessed state**. A source can claim a time and present identity/authentication material. Only the receiver, under its own policy and observations, can decide whether that claim is fit for a particular use. That separation is the project’s clearest contribution.

A useful one-sentence mission is:

> TimeSync turns imperfect timing evidence into a conservative, explainable, profile-scoped decision about safe use.

## What the archive actually is

The archive is currently a specification corpus, fixture corpus, and consistency checker. It is not yet a reference time evaluator. It can validate a TimeSync-shaped object with considerable depth, but it does not ingest a real NTP/PTP implementation’s state and derive that object end to end.

That distinction should remain explicit in every release. “Validator” is accurate. “Evaluator” is presently aspirational except for semantic checks over already-authored assessment objects.

## What is unusually strong

- The model refuses the common category errors `authenticated = correct`, `precise = traceable`, `fresh = actionable`, and `source claim = receiver conclusion`.
- The bounded interval is a safer primitive than a naked timestamp or quality score.
- Applicability is consumer- and profile-relative rather than a global “good clock” label.
- The no-silent-upgrade posture is well represented in negative fixtures.
- The archive preserves explanations and non-provenance boundaries instead of allowing metadata to mutate TimeState implicitly.

## What is missing

### 1. The conversion boundary

There is no executable path from raw observations to TimeState. The critical missing function is conceptually:

```text
evaluate(observation, profile, policy, evaluated_at)
  -> LocalAssessedState + explanation + unsupported_conditions
```

Until this exists, the project proves internal consistency more than practical usefulness.

### 2. One real adapter

The six transport adapters are abstract carriage patterns. None parses chrony, ntpd, NTP YANG, linuxptp/pmc, PTP management data, Windows Time, or a hardware clock. A single real adapter with captured input is more valuable now than another family of authority/receipt schemas.

### 3. Conservative uncertainty arithmetic

The archive represents an interval but does not provide a reference algorithm for deriving or growing it from offset, delay, dispersion, frequency error, holdover age, and observation latency. Freshness is modeled; uncertainty evolution is not yet demonstrated.

### 4. A monotonic observation anchor

Wall-clock timestamps alone are circular evidence when the clock itself is under assessment. A practical evaluator needs a monotonic collection anchor, elapsed-time handling, and a rule for widening uncertainty between collection and decision.

### 5. Explicit leap/smear/timescale behavior

The schema admits RFC 3339 timestamps, while real timing systems can encounter leap seconds, leap indicators, smear policies, TAI/UTC conversion, and implementation-specific behavior. rev0121 now fails closed on leap-second arithmetic, but the project still needs a declared policy and test corpus.

### 6. Executed acceptance tests

`tests/acceptance-tests.yaml` contains 124 scenario records. The current validator checks their shape and duplicate IDs; it does not execute their `given/when/then` meaning. Executed semantic vectors are real tests. The scenario file is a requirements catalog until a runner binds each scenario to fixtures and assertions.

### 7. Assurance levels that match execution

Many objects contain signature, digest, verifier, receipt, and transparency concepts. Most validation is structural and relational, not cryptographic. The project needs explicit assurance labels such as:

- structural only;
- digest recomputed;
- signature cryptographically verified;
- source identity policy verified;
- cross-source coherence assessed;
- operational capture independently reproduced.

A field named `signature` must not imply the higher levels by itself.

### 8. Adoption and release basics

The incoming archive had no license, contribution policy, security policy, CI definition, package metadata, or fully pinned dependency lock. Those are not cosmetic: without a license, reuse rights are unclear; without reproducible build instructions and provenance, a manifest only detects drift against itself.

## Where the incoming rev0120 had gone severely wrong

### Exact timestamp ordering was false beyond microseconds

The schemas accept RFC 3339 fractional seconds, but `datetime.fromisoformat()` truncates digits beyond Python’s microsecond resolution. Consequently, `...000000002Z` and `...000000001Z` compared equal, and an inverted nanosecond interval could pass. rev0121 replaces this with exact rational arithmetic and adds `TV-N343` / `DF-0121-001`.

This is not a cosmetic edge case. PTP explicitly targets submicrosecond operation and supports better-than-nanosecond regimes, so a precision-oriented semantic layer cannot silently collapse those digits.

### The release chain certified the wrong revision

The rev0120 archive’s receipt still declared rev0119 and the validator did not reject it. Revision identity was duplicated across scripts and documents. rev0121 makes the receipt the source of truth, checks immediate baseline, filename, timestamp/name alignment, manifest identity, and current validation output.

### Generated bytecode was shipped and deliberately invisible

The incoming ZIP contained 31 `.pyc` files, roughly 571 KB, despite a prior changelog entry saying generated caches had been removed. The manifest/validator explicitly ignored them. rev0121 removes them, rejects generated caches in release source, and supplies a deterministic builder.

### Assurance volume outran external evidence

The incoming archive had 361 semantic vectors and 277 negative example files, but no real timing capture and no end-to-end evaluator. Approximately 4.14 MB sat in `examples/`, while a selected five-file core (`00-charter`, `01-model`, `02-timestate`, and the TimeState/WireClaim schemas) was about 9.3 KB. The exact ratio depends on selection, but the direction is unmistakable: the periphery dwarfs the mission-bearing core.

### The project drifted toward a custom assurance bureaucracy

Specs 33–49 add challenge receipts, replay portability, transparency receipts, witness cohorts, trust-policy lifecycle, authority rotation/compromise/recovery, aggregate correction lineage, and related rollups. Some may be useful, but together they risk turning TimeSync into the very registry/certificate/transparency/governance system its non-goals disclaim.

The test for every peripheral concept should be: **does a real adapter/evaluator need this to make a safe time-use decision?** If not, move it to an optional extension, external integration note, or separate project.

### Revision activity became an internal optimization loop

FT-0090 generated valuable decomposition and mutation pressure, but it remained open across many revisions while the same missing external proof remained untouched. The process optimized the consistency of a closed world. rev0121 closes FT-0090 without claiming all cleanup is complete and opens FT-0121 around real evidence.

## Waste that can be corrected over time

1. **Rendered negative fixture duplication.** Keep a small reviewable set rendered; generate the rest from positive bases plus patches during validation. The derivation manifest already proves the direction.
2. **Repeated schema subtrees.** Introduce source definitions or `$defs` generation while continuing to publish standalone schemas. Measure semantic equivalence before deleting anything.
3. **Audit-note accretion.** Preserve immutable release receipts and concise epoch summaries; stop copying the same frontier narrative into every document.
4. **Full-only distribution.** Publish a slim conformance/evaluator bundle and a separate full research/history bundle.
5. **Hard-coded revision prose.** Generate current headings and validation snippets from receipt/build metadata where practical.
6. **Duplicated semantic logic.** Define a machine-readable rule inventory that points to schema constraints, semantic functions, vectors, and explanation codes. Do not create another ontology; use it as a coverage index.

## What should change now

### Freeze ontology growth

For the next proof cycle, add no new core or assurance concepts unless a real adapter reveals an irreducible gap. The burden of proof shifts from “we can describe it” to “a consumer needs it to decide.”

### Build one vertical slice

Use chrony first:

```text
chronyc tracking + sources + sourcestats
    -> parsed ChronyObservation
    -> conservative uncertainty calculation
    -> TimeState
    -> P1/P2 profile assessment
    -> explanation + unsupported conditions
```

Chrony is attractive because its reports expose reference time, system correction, RMS/last offset, root delay, root dispersion, frequency/skew, source reachability, and leap status. RFC 9249’s NTP YANG operational state then offers a standards-based comparison surface.

### Make claims proportional to tests

Rename the 124 YAML records “acceptance scenarios” until executable, or implement a runner. Keep separate counts for:

- schemas checked;
- fixtures schema-validated;
- semantic vectors executed;
- mutation probes executed;
- documentary scenarios checked for shape;
- cryptographic verifications executed;
- real captures replayed.

### Separate local explanation from global governance

Keep a local, deterministic explanation receipt: inputs, rule IDs, policy/profile digest, decision, unsupported conditions. Avoid building a global transparency/witness/authority infrastructure inside the core. Integrate with external attestation systems when a deployment needs that assurance.

### Establish two release products

- **TimeSync Core/Conformance:** current specs, schemas, profiles, evaluator, adapters, golden tests, and release metadata.
- **TimeSync Research Archive:** historical audits, migrations, exploratory schemas, and the full negative corpus.

## External research and why it matters

As of 2026-06-17:

- The active NTPv5 draft defines the on-wire protocol and explicitly leaves source selection, filtering, and clock discipline out of scope. That creates a legitimate space for a protocol-neutral local assessment layer, but TimeSync must prove it with implementations rather than merely occupying the conceptual gap.  
  https://datatracker.ietf.org/doc/html/draft-ietf-ntp-ntpv5-08
- Roughtime focuses on secure rough-time bootstrapping and detecting/reporting inconsistent servers. It is complementary evidence, not a substitute for local applicability policy.  
  https://datatracker.ietf.org/doc/draft-ietf-ntp-roughtime/
- NIST IR 8323 Rev. 2 is an initial public draft (published 2026-05-06; comments due 2026-07-06) framing PNT use as risk management across source identification, manipulation detection, response, and recovery. TimeSync aligns best when it remains an operational decision/explanation layer rather than claiming compliance by itself.  
  https://csrc.nist.gov/pubs/ir/8323/r2/ipd
- RFC 9249 exposes NTP configuration, current state, statistics, and association state through YANG. It is a practical standards-based adapter target after chrony.  
  https://www.rfc-editor.org/rfc/rfc9249.html
- Chrony’s operational reports expose enough material for a first conservative evaluator, including root delay/dispersion and estimator/source state. Chrony defines root distance as half delay plus dispersion.  
  https://chrony-project.org/examples.html  
  https://chrony-project.org/faq.html
- IEEE 1588 targets heterogeneous precision-clock systems, including submicrosecond and better-than-nanosecond regimes. That supports exact fractional ordering and argues against a microsecond-limited parser.  
  https://standards.ieee.org/standard/1588-2019.html
- Python documents that extra fractional digits accepted by `fromisoformat()` are truncated beyond six digits. JSON Schema’s `date-time` is RFC 3339-based, where fractional seconds are not limited to six digits.  
  https://docs.python.org/3/library/datetime.html  
  https://json-schema.org/understanding-json-schema/reference/type  
  https://www.rfc-editor.org/info/rfc3339/
- Reproducible-build guidance warns that archive timestamps, order, users/groups, and permissions can encode build-environment variation. SLSA provenance is a useful later model for binding builder, build definition, and artifacts; rev0121 only establishes deterministic local packaging, not signed provenance.  
  https://reproducible-builds.org/docs/archives/  
  https://slsa.dev/spec/v1.2/build-provenance

## Speculation, clearly labeled

### Best-case identity

TimeSync could become a small “time firewall” or “use-admission API” between timing implementations and applications. NTP, PTP, GNSS, hardware clocks, and rough-time services provide observations; TimeSync returns a bounded state and use decision with reasons. That is a narrower and more adoptable identity than a universal time-trust ecosystem.

### Likely failure mode

Without the freeze, the archive may continue adding evidence/governance nouns faster than independent implementations can understand them. It would become internally rigorous but externally non-interoperable—a semantic tarpit.

### A promising architectural split

Keep the six-field core and profile evaluation stable. Put protocol ingestion, uncertainty algorithms, cryptographic verification, and organizational policy in replaceable modules. Emit a compact explanation record. Let existing attestation and transparency systems carry that record when stronger provenance is required.

## Decision for rev0121

Keep and grow the narrow waist, wire/local split, bounded interval, profile-specific applicability, and no-silent-upgrade rules. Freeze the assurance ontology. Prove one real vertical slice. Measure success by independently replayable decisions, not by schema count.
