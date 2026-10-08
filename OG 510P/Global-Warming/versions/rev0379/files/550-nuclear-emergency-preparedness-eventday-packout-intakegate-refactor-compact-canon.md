# 550 — Nuclear emergency preparedness: event-day evidence packout, intake gates and loss-cap refactor

## Canonical correction

Rev0342 created a capture command board and a 60-packet minimum evidence cutline. Rev0343 turns that into an event-day packout that an evidence custodian can actually run under time pressure.

The failure mode being corrected is practical, not doctrinal: a required packet can be named in a CSV and still fail because the artifact label was not assigned, the offline form was not printed, the owner and backup did not know the custody step, the redacted surrogate was not created, the packet arrived late without a loss cap, or a public meeting statement was allowed to substitute for the raw record.

## Non-negotiable rule

A public notice, public meeting statement, preliminary finding, AAR paragraph, dashboard, PI page, MSEL event, extent-of-play statement, source ID, duplicate URL, redacted surrogate, folder skeleton, label, or complete-looking local packet may demand, cap, route, contradict, or reopen a claim. It cannot automatically close local emergency-readiness evidence.

## Operational route

`capture command board → artifact ID namespace → packet folder skeleton → offline capture form → chain-of-custody event → intake check-in gate → rapid quality gate → redaction/surrogate clock → loss-cap board → adjudication docket → CAP/retest/verifier → integrated claim kernel`

## New material in rev0343

Rev0343 adds:

- a 60-row event-day evidence packout catalog derived from the rev0342 cutline;
- a 60-packet field-kit folder skeleton with one README per packet;
- an artifact-ID namespace and label grammar so evidence does not arrive as loose PDFs, screenshots or unlabeled files;
- a chain-of-custody event template that works even if the network, printer or repository is unavailable;
- an intake check-in queue with missing/late/default-cap behavior;
- a rapid quality gate that rejects public-context closure attempts, missing hashes, missing owners, missing source clocks, unpaired redactions and self-attested closure;
- a redaction/surrogate SLA so sensitive annexes can be protected without losing public accountability;
- a validator and SQLite views for packout rejections, holds, candidate-not-closure rows, reopen signals, and public-context-to-local-closure leaks.

## Claim boundary

This file is a capture-control canon, not a readiness finding. REAL_BVPS_PUBLIC_ONLY remains public-context-only. The cube still makes no claim that Beaver Valley, Pennsylvania, West Virginia, Ohio, any county, any ORO, any alerting authority, any evaluator, any controller, any evidence custodian, or any facility is ready, unready, green, failed, passed, certified, sufficient, demonstrated, reasonable-assurance-ready, or closed.

## Why this is the priority

The June 2026 exercise window is close enough that evidence loss is now the primary preventable failure. Rev0343 is designed to move the package from “we know what is required” to “a custodian can label, collect, hash, check in, triage, cap and route what appears.”
