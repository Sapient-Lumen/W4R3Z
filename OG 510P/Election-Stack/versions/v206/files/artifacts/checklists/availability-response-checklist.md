# Availability incident response checklist (DDoS / partition / selective unreachability)

Use this when endpoints become unreachable, or different audiences see different availability.

## Evidence first
- Generate URPs (internal + RIPE Atlas if configured) and checkpoint them.
- Publish an OutageAttestation and anchor it in the availability transparency log.
- Run audience parity checks from multiple networks.

## Containment / recovery
- Activate failover per `DOC:docs/111-failover-trigger-policy.md`
- Rotate mirrors and update distribution manifests.

## Public accountability
- Publish a `hfv.public.notice` PublicNotice (notice_type: incident_advisory) that includes:
  - what endpoints were affected
  - time windows
  - canonical hashes of evidence objects

## After
- Run a censorship-and-partition drill postmortem.
