# Start here — rev0900

Bundle: `Anonymity-rev0900-2026.06.18.11.54-obschannel-counterexamples-modelbinding-validatorcut.zip`

This revision publishes nothing. The central repair is that a scalar observation probability does not define an erasure channel. Equal per-secret reveal rates can coexist with one full bit of leakage, so channel identity must be explicit and source-bound before arithmetic can support a privacy claim.

Read these first:

1. `series/bossfight_series/paperA_bossfight_budgets/paper.tex` — theorem root, cyclic-reveal counterexample, valid common-mixture wrapper, and composition boundary.
2. `series/bossfight_series/paperB_anondht_dial_sheet/paper.tex` — rewritten dial sheet that separates telemetry from channel evidence.
3. `series/bossfight_series/paperB_addendum_evidence_tables/paper.tex` — independence-sensitive contact and target-erasure tables.
4. `series/bossfight_series/paperC_proof_carrying_budgets/paper.tex` — model-binding gate and `VALID-UNDER-MODEL(d_M)` verdict.
5. `series/synthesis/paper11_observation_attenuation/paper.tex` and `paper15_tiered_observation_vectors/paper.tex` — exact wrapper conditions and joint-tier synergy.
6. `series/evaluation_series/paper2_advantage_contracts_stealth_audits/paper.tex` and `series/synthesis/paper17_worked_example_receipt_interlock/paper.tex` — repaired active consumers.
7. `publishing/check_hostile_review_vectors.py` and `release_queue/HOSTILE_REVIEW_VECTORS.json` — seven executable Boss Fight attacks plus the earlier State/MUCC/MC-EQ/CPPC/endpoint vectors.
8. `release_queue/EXTERNAL_HOSTILE_REVIEW_PACKET.md` — 19-task outside-review handoff over 35 required surfaces; packet readiness is not countersignature.
9. `REVISION_RECEIPT.json`, `CONTEXT_PACK.json`, and `PATCH_NOTES.md` — revision identity, exact changes, and remaining blockers.

Mechanical core:

```text
three-secret cyclic reveal
Pr[reveal | i] = 1/2 for every secret i
actual maximal leakage = 1 bit
actual exact guess      = 2/3
scalar-erasure bits     = log2(1.25) = 0.321928094887
scalar exact guess      = 5/12

m=10, rho=0.1
independent any-hit     = 1-(1-rho)^m = 0.6513215599
equal-marginal range   = [rho, min(1,m rho)] = [0.1,1]

one-time-pad tier control
I(S;X)=0, I(S;Y)=0, I(S;X,Y)=1 bit
```

No deployment Boss Fight certificate is claimed. The four affected papers are on Hold. External hostile-review countersignature and the `.package.dsse.json` signature envelope remain missing.
