# ADR 0210: Account for actual-Tor target-circuit populations

Status: accepted bounded corpus accounting, 2026-08-28.

## Context

ADRs 0203 through 0209 retain seven independently verified two-IoTox actual-Tor proofs. Each proof
binds its successful exact Tox relay stream to a qualifying three-hop Tor application circuit, but
the roadmap still described path-population accounting as wholly open. Counting every circuit in a
Tor status dump would be wrong: Tor also builds unused application circuits and legitimate one-hop
directory circuits. Counting manifest path hashes alone would conceal whether distinct commitments
resolve to distinct relay identities.

The remaining distinction is equally important. A different last-hop identity in a verified target
circuit is observed path-population diversity. It is not, by itself, independently reviewed exit
operator, jurisdiction, network, anonymity, availability, or separated-time evidence.

## Decision

Add `tools/analyze-actual-tor-path-population.py` and retain its canonical report. The analyzer:

- first runs the complete compact Sandwurm verifier over every supplied proof;
- accepts only actual-Tor compact proofs and binds their compact/source manifests, exact target
  records, IoTox binaries, Tor binary, scenarios, and declared evidence files;
- resolves only path commitments already joined to exact target streams by role/phase evidence or
  exact before/after Ratox churn evidence;
- reparses raw Tor control/status paths, excludes explicit one-hop directory circuits, requires at
  least three canonical relay identities, and independently matches the declared raw path digest
  and purpose;
- normalizes relay fingerprints for diversity counting but emits only domain-separated SHA-256 set
  commitments, counts, proof identities, and pairwise reuse counts; and
- supports deterministic regeneration plus byte-exact `--verify-report` verification.

Name the endpoints `first_hop` and `last_hop` in the report. Do not name the last hop an
independently qualified exit. Keep `independent_exit_diversity_qualified=false`,
`time_window_count=0`, and `time_window_separation_evidenced=false` until separately designed gates
provide those claims.

## Qualification

The accepted report `artifacts/rev0045/actual-tor-path-population.json` initially reverified seven
compact proofs. ADR 0243 extends the same deterministic corpus to eight proofs spanning six
scenarios, three public Tox records, one Tor binary, and three IoTox binary identities. It resolves
30 exact-target circuit declarations into 24 distinct normalized three-hop paths, 20 first-hop
identities, 23 last-hop identities, and 24 first/last pairs. Twenty declarations are
`CONFLUX_LINKED`; ten are `GENERAL`. Of 28 cross-proof comparisons, none reuse a complete path or
last hop; one shares a first hop. The current report SHA-256 is
`3986dc9c0d4246afb8876269009cad9e3d136a70e289af54f0ec8bc2abf1f7da`.

## Consequences

- Explicit target-path population accounting is closed for the retained compact corpus.
- The result is evidence against an accidental single-path/single-last-hop corpus, not proof of
  independent exit operators or anonymity.
- Later repetitions can append proofs to the same deterministic analysis and will expose exact
  first/last/path reuse without publishing relay fingerprints.
- Independent time windows, reviewed exit/operator diversity, I2P, and voluntary infrastructure
  stewardship remain separate M8 gates.

See `docs/evidence/2026-08-28-actual-tor-path-population.md`.
