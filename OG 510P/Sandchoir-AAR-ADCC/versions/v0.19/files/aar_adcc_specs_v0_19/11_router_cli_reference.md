# 11 — Router CLI Reference (v0.19)

This is the control surface for humans and MetaLLM.

## State / views
- `state show --view=summary`
- `state show --agent=A2 --view=delta --since=CURSOR`
- `state show --agent=A2 --view=hot`
- `state show --id=C12`
- `state cursor`

## Working set management
- `ws pin --id=H0`
- `ws promote --id=C12`
- `ws compact --profile=default|emergency`
- `ws evict --id=...` (rare; never mandatory anchors)

## Modes / strictness
- `mode set recorder|gatekeeper|patchonly|freeze|jailer`
- `strictness set S0|S1|S2|S3`

## Leases
- `lease grant --scope=src/parser.py --owner=A2 --ttl=+200c --mode=soft`
- `lease revoke --scope=src/parser.py`
- `lease list`

## Voting ingestion
- `vote ingest --agent=A2 --cursor=128 --payload=@VOTE...`
- `vote tally --type=patch|floor|hot|ce_admit|checks`

## Patches / canonicalization
- `patch register --id=P7 --diff=path --touch=...`
- `patch select --id=P7`
- `patch apply --id=P7` (respects mode)
- `patch rollback --id=P7`

## Verifiers / evidence
- `verifier list`
- `verifier run --name=pytest_fast`
- `evidence add --id=E12 --from=verifier_run:xyz`

## Snapshots / rollback
- `snapshot create --name=...`
- `snapshot list`
- `snapshot restore --name=...`

## Capabilities
- `cap probe --agent=A2 --mode=fast`
- `cap show --agent=A2`

## Requests (REQ)
- `req add --to=A3 --type=test --targets=CE4 --deliverable="Run unit_fast" --deadline=+80c --priority=2`
- `req list --agent=A3`
- `req close --id=REQ12 --status=done|expired|rejected`

## Verifier registry
- `verifier register --name=unit_fast --kind=test --cost=cheap --cmd=...`
- `verifier show --name=unit_fast`
