# rev0323 mission kernel

AI-EDU remains an education-design archive, not a registry machine. The mission is to make AI-normal
education more understandable, agency-preserving, accessible, teacher-capacitating, and truthful,
while reducing shortcutting, surveillance, dependency, workload waste, and false outcome claims.

## Current center of gravity

The two live blockers are human boundaries, not missing doctrine:

1. `FT-0181` still needs a real accountable owner send, route block, or returned owner-attested packet.
2. The teacher/tutor micro-pilot still needs a real local owner-approved cycle and human review of a
   minimized aggregate readout.

## rev0323 change

Rev0323 adds a scratch-only owner-review stop command for the teacher/tutor micro-pilot path:

```bash
make micro-pilot-owner-review
```

The command refuses synthetic dry-runs and incomplete packets. It records only that a local human owner
reviewed a completed non-synthetic aggregate packet after readiness returned
`READY_FOR_LOCAL_OWNER_REVIEW_NOT_EVIDENCE`.

## What must happen next

- Send the bounded `FT-0181` owner request or record the route block.
- Generate a fresh teacher/tutor packet, run one owner-approved local micro-cycle, score the aggregate
  packet, and only then record the owner-review stop if the human review actually happens.
- Do not add another schema, branch, validator, or registry unless a real owner result, real
  micro-pilot result, or release failure demonstrates the need.

## Boundary

Rev0323 does not contact an owner, run a micro-pilot, accept evidence, create custody, update service
authority, support public claims, or close `FT-0181`.
