# Publish dry-run side-effect boundary

`publishdryrun.py` is a no-network side-effect lane. It rejects the easy mistake where accepted component reports are treated as permission to write to the DHT or publish a public bridge record.

The dry-run binds:

- profile and service;
- scope and request;
- public payload digest;
- bridge-shadow report digest;
- audit-quorum report digest;
- egress report digest;
- action: refresh, withdraw, or repair;
- sequence and previous dry-run digest;
- family and path diversity.

The harsh rule is: a valid dry-run signature is not enough if the component digests drift, if egress did not accept, if one family supplies the whole dry-run, or if the sequence/previous link regresses.
