# Actual-Tor target-path population evidence

Date: 2026-08-28; expanded 2026-08-29

Status: accepted bounded content-free accounting over eight verified two-IoTox proofs

## Claim

The retained actual-Tor compact corpus no longer consists of unaccounted path commitments. A
deterministic analyzer first ran the strict Sandwurm verifier over all eight source-linked compact
proofs, then resolved only Tor paths already associated with successful exact-target streams or
verified Ratox before/after churn transitions. It independently matched each declared raw path
SHA-256 and circuit purpose against the inventoried Tor control/status evidence.

The corpus contains 30 target-circuit observations and 24 distinct normalized three-hop relay
identity paths. Those paths contain 20 distinct first-hop identities, 23 distinct last-hop
identities, and 24 distinct first/last pairs. Relay fingerprints are not present in the report; the
analyzer retains only counts and domain-separated set commitments.

| Measure | Result |
|---|---:|
| verified compact proofs | 8 |
| scenarios | 6 |
| public Tox target records | 3 |
| Tor binary identities | 1 |
| IoTox binary identities | 3 |
| inventoried Tor circuit/control files | 48 |
| parsed qualifying application-circuit lines | 1,427 |
| exact-target/churn circuit declarations | 30 |
| unique normalized target paths | 24 |
| unique first hops | 20 |
| unique last hops | 23 |
| unique first/last pairs | 24 |
| `CONFLUX_LINKED` declarations | 20 |
| `GENERAL` declarations | 10 |
| hop-count range | 3–3 |

All 28 cross-proof comparisons have zero complete-path reuse and zero last-hop reuse. Exactly one
comparison, `pair.2mycvy9n` against `pair.k8o54n2v`, shares one first hop while sharing neither a
last hop nor a complete path.

## Corpus

| Proof | Scenario | Declarations | Unique paths | First hops | Last hops |
|---|---|---:|---:|---:|---:|
| `pair.2mycvy9n` | private actual-Tor sync | 2 | 2 | 2 | 2 |
| `pair.2waqdpgk` | Ratox Tor-process loss | 3 | 3 | 2 | 3 |
| `pair.9cx0jels` | Ratox circuit churn, second relay | 6 | 4 | 3 | 4 |
| `pair.iompvehf` | sync Tor-process loss | 3 | 3 | 3 | 3 |
| `pair.k8o54n2v` | Ratox circuit churn | 6 | 4 | 4 | 3 |
| `pair.lzsyitvy` | exact-carrier sync payload | 2 | 2 | 2 | 2 |
| `pair.vx6z0csh` | adversarial local boundary | 2 | 2 | 2 | 2 |
| `pair.wbsef5tp` | Ratox circuit churn, later operator window | 6 | 4 | 3 | 4 |

The aggregate normalized path, first-hop, last-hop, and first/last-pair set commitments are:

```text
cb841c43d1481ae55f4047cbe3021fb7f9bb40df92ea5a24838d0a6989334b4d
1bcff1b119d4d8f0743c3e7ba1dd97258087c3687769f0dcc7bdb23b63238ecb
5d736c15834a60f87361e9fee80d31514c88d38e424df3289e0037db235c4ad3
dc0504f69c086c440064c488e43adeaafcbf95efad3e8acf6c3c80d2d1170690
```

## Reproduction

```sh
python3 tools/analyze-actual-tor-path-population.py \
  .sandwurm/exports/pairs/pair.2mycvy9n \
  .sandwurm/exports/pairs/pair.2waqdpgk \
  .sandwurm/exports/pairs/pair.9cx0jels \
  .sandwurm/exports/pairs/pair.iompvehf \
  .sandwurm/exports/pairs/pair.k8o54n2v \
  .sandwurm/exports/pairs/pair.lzsyitvy \
  .sandwurm/exports/pairs/pair.vx6z0csh \
  .sandwurm/exports/pairs/pair.wbsef5tp \
  --verify-report artifacts/rev0045/actual-tor-path-population.json
```

The command returns `actual-Tor path-population report verification: PASS`. Regeneration uses the
same proof list with `--output`. The canonical report is 18,761 bytes, declares
`contains_secrets=false`, and has SHA-256
`3986dc9c0d4246afb8876269009cad9e3d136a70e289af54f0ec8bc2abf1f7da`. The rev0045 checksum file
binds it alongside the existing local and operator-Tor receipts.

## Exact nonclaims and next gate

The 23 distinct last-hop identities establish observed target-path population diversity in this
bounded corpus. They do not establish 23 independent exit operators, exit-policy review,
jurisdiction or autonomous-system diversity, anonymity, unlinkability, availability, an SLA, or
resistance to a global observer. The retained evidence was produced on one host and date; the
report therefore deliberately records `independent_exit_diversity_qualified=false`,
`time_window_count=0`, and `time_window_separation_evidenced=false`.

The added `pair.wbsef5tp` operator run occurred on the following date and contributes four paths
with no first-hop, last-hop, or complete-path reuse against any prior proof. The compact schema does
not independently witness UTC, so the report correctly retains `time_window_count=0` and
`time_window_separation_evidenced=false`. M8 still requires a schema-bound later-window campaign
with reviewed current relay/exit-operator populations. Actual I2P construction and voluntary
bootstrap/relay stewardship remain separate gates.
