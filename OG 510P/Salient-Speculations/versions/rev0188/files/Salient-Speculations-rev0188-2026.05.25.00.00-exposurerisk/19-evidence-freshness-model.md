
# Evidence Freshness Model

rev0184 performs the archive's first hard refactor: the **evidence-freshness family** is now treated as a reusable model rather than an ever-expanding set of separate dossiers.

## Why this refactor was necessary

Several strong dossiers were all naming adjacent versions of the same deeper mechanism:

- authority freshness;
- validation expiry;
- revalidation windows;
- VEX expiry;
- security-feed uptime;
- successor-map freshness;
- history-retention floors;
- renewal-history normalization;
- revocation propagation;
- stale-clearance fault classes;
- supported-version windows.

Each is still useful, but the cube was starting to treat every freshness clock as a new bottleneck. The better abstraction is:

> A proof object is not just true or false. It has a **freshness budget**: the interval, clock source, fallback rule, and disclosure obligation that determines when someone may rely on it.

This model separates the reusable mechanism from sectoral examples.

## The five clocks

Freshness failures become confusing because institutions often collapse several clocks into one timestamp. The archive should now distinguish at least five.

| Clock | Question it answers | Example fields |
|---|---|---|
| Assertion clock | When did the issuer make the claim? | `issued_at`, `signed_at`, `asserted_at` |
| Observation clock | When was the source system actually observed? | `source_observed_at`, `snapshot_at`, `last_seen_at` |
| Validation clock | When did a verifier check the assertion? | `validated_at`, `last_checked_at`, `next_check_due` |
| Reliance clock | When did a buyer, agency, insurer, platform, or court use it? | `relied_at`, `decision_at`, `packet_cutoff_at` |
| Correction clock | When did revocation, appeal, correction, or withdrawal become known? | `revoked_at`, `stayed_at`, `corrected_at`, `notice_received_at` |

A dossier is often weak if it says “fresh” without naming which clock governs the decision.

## Core freshness states

The following state vocabulary should replace vague uses of “valid,” “old,” “expired,” and “stale.”

| State | Meaning | Reliance implication |
|---|---|---|
| `live-current` | fresh lookup or recently validated state is within the required budget | ordinary reliance permitted |
| `valid-cached` | cached state remains inside explicit max-age | reliance permitted, but cache age should be visible |
| `stale-permitted` | state is older than normal budget but expressly usable for a bounded purpose | reliance permitted only under stated conditions |
| `stale-if-error` | stale state may be used because the source is unavailable or failing | reliance permitted with fallback disclosure and retry obligation |
| `grace` | expiration or refresh deadline has passed but a rule extends temporary use | reliance permitted only inside grace window |
| `revalidation-due` | evidence remains usable but must be refreshed before next higher-risk reliance | limited or warning-state reliance |
| `expired` | ordinary validity has ended | no new reliance unless override or grace applies |
| `suspended` | authority has paused the artifact without final withdrawal | reliance controlled by stay/suspension rules |
| `revoked` | authority has withdrawn validity | reliance normally prohibited; past reliance needs afterlife rule |
| `superseded` | a newer artifact governs prospectively or retroactively | reliance shifts to successor or version policy |
| `archive-only` | retained for history but not current reliance | admissible as history, not as current proof |
| `unverifiable` | source, resolver, witness, or validation path cannot be reached | fallback, escalation, or non-reliance rule required |
| `contested` | state is under appeal, dispute, or correction review | stay label or interim reliance rule required |

## Freshness budgets

A useful freshness policy has at least these components:

1. **scope** — what decision the freshness budget governs;
2. **clock source** — which system's time and observation event count;
3. **max age** — how old the evidence may be;
4. **lag budget** — how long a propagation delay is tolerated;
5. **grace rule** — whether temporary reliance survives expiry;
6. **stale-if-error rule** — whether fallback reliance is permitted during outage;
7. **revocation rule** — how quickly withdrawal must propagate;
8. **revalidation trigger** — event, time, version, risk, or dispute condition requiring refresh;
9. **disclosure rule** — whether the relying party sees the age and fallback state;
10. **liability rule** — who bears loss when reliance occurs on too-old evidence.

The model's strongest practical output is a contract clause or API schema that says not merely “this is valid,” but “this was observed at X, validated at Y, can be cached until Z, may be used in stale-if-error mode for N hours, and becomes non-reliance after event E.”

## Refactored dossier family

rev0184 tags the following dossiers with `refactor_cluster: evidence-freshness` and adds a more specific `freshness_role`.

| Family role | Dossiers |
|---|---|
| authority-state currentness | `authority-freshness-guarantees-become-compliance-metrics`, `delegate-freshness-proofs-become-a-service-metric` |
| expiry and revalidation | `validation-expiry-dates-become-procurement-terms`, `revalidation-windows-become-a-standing-operational-burden`, `gate-expiry-disputes-become-a-service-layer`, `vex-expiry-governance-becomes-a-procurement-term` |
| fallback and stale-use rules | `stale-clearances-split-into-distinct-fault-classes`, `graceful-degradation-becomes-a-constitutional-design-problem`, `security-feed-uptime-obligations-become-supplier-grade-commitments` |
| historical admissibility | `history-retention-floors-become-procurement-terms`, `renewal-history-normalization-services-become-a-quiet-broker-market` |
| successor and support clocks | `successor-map-freshness-guarantees-become-a-service-metric`, `supported-version-windows-become-quiet-exclusion-regimes` |
| validation artifacts | `portable-validation-reports-become-a-quiet-mutual-recognition-surface`, `post-waiver-validation-certificates-become-a-service-tier`, `validator-services-become-outsourced-certifiers` |

## New admission rule

A future freshness dossier should be standalone only if it adds a new clock, enforcement surface, abuse mode, or fallback constitution. If it merely says “this proof needs an expiry date,” it belongs inside this model rather than as a new dossier.

## Adversarial implications

Freshness creates its own fraud surface.

- An actor can present a favorable stale snapshot while suppressing a live correction.
- A broker can hide cache age while claiming live validation.
- A supplier can exploit grace periods as hidden extensions.
- A resolver can continue serving a superseded object.
- A platform can selectively refresh disfavored parties more slowly.
- A buyer can reject small suppliers by demanding live proof where stale-but-safe proof would suffice.

This is why freshness belongs in the same family as appealability, privacy proofs, and anti-legibility. A freshness rule is never merely technical. It allocates advantage during uncertainty.

## Falsifiers

The model weakens if:

- contracts and regulators continue to accept undifferentiated “valid/invalid” evidence;
- cache age and last-validation time remain invisible to relying parties;
- stale use during outages remains informal rather than typed;
- revocation and correction events rarely produce disputes about past reliance;
- vendors absorb renewal and revalidation internally without buyers, insurers, or auditors asking for proof.

## Research signals

HTTP caching already has explicit freshness, stale, and revalidation semantics [S1534][S1535]. Verifiable credential work exposes validity periods and proof expiry fields [S1536][S1537]. NVD guidance tells API users to maintain local repositories with last-modified update windows and rate-limited synchronization [S1532]. CA/Browser Forum baseline requirements now put public TLS certificates and validation-data reuse on sharply shortening validity schedules, culminating in 47-day certificate validity and 10-day domain/IP validation reuse by 2029 [S1538][S1539]. These are not one sector's quirks; they are examples of a general governance pattern.
