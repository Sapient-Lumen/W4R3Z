# Python surface — rev0011

New or expanded files:

```text
src/i2p_dht_lab/providerpoison.py
src/i2p_dht_lab/provider_poison.py
src/i2p_dht_lab/gardenrefusal.py
src/i2p_dht_lab/garden_churn.py
src/i2p_dht_lab/churnforge.py
```

New tests:

```text
tests/test_rev0011_providerpoison_gardenrefusal.py
tests/test_rev0011_provider_garden_churn.py
tests/test_rev0011_churnforge.py
```

## providerpoison.py

```text
ProviderProbeKind
ProviderProbeChallenge
ProviderProbeReceipt
ProviderPoisonDecisionKind
ProviderPoisonPolicy
ProviderPressureObservation
ProviderPoisonAnalysis
ProviderProbePlan
make_provider_probe_plan
analyze_provider_poisoning
```

## provider_poison.py

```text
ProviderProbeOutcome
ProviderProbeReceipt
ProviderRecordAssessmentKind
ProviderProbeAssessmentKind
ProviderPoisonBook
ProviderNodeMemory
select_provider_records
```

## gardenrefusal.py

```text
GardenWorkKind
GardenAdmissionKind
GardenRefusalReason
GardenWorkRequest
GardenLoadState
GardenAdmissionPolicy
UsefulRefusalReceipt
GardenAdmissionBatch
admit_garden_work
```

## garden_churn.py

```text
GardenRefusalReceipt
GardenRefusalBook
ChurnGarden
ChurnBehavior
ChurnLookupEngine
ChurnLookupReport
```

## churnforge.py

```text
ChurnState
ChurnContact
ChurnFrontier
ChurnDecisionKind
select_churn_frontier
assess_churn_frontier
make_churn_transcript
```
