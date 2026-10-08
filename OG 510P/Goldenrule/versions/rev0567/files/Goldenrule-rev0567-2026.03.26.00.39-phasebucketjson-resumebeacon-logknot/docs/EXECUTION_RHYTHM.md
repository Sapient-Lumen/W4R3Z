# Execution Rhythm

Concord execution cadence should keep fast feedback and strict release posture separate.

## Daily

1. `make test-quick`
2. implement one narrow concern
3. regenerate impacted reports
4. `make gate` before integration-ready claims

## Weekly

1. dependency/security tranche checks
2. robustness sweep trend run
3. spec ledger review and assumption retirement sweep
4. timing baseline drift review

## Release Candidate

1. `make gate-strict`
2. release manifest + checksum checks
3. reproducibility bundle verification
4. claim-class audit (`CC-*` mapping complete)
