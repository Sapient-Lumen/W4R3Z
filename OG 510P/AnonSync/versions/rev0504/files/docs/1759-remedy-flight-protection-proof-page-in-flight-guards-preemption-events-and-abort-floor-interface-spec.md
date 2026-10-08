# Remedy-flight-protection proof page — in-flight guards, preemption events, and abort floor

## Purpose

This page is the durable proof object for why the product believed an in-flight cure was or was not protected strongly enough to finish.
It exists so later readers can verify whether the product honestly distinguished `started` from `finish-protected`.

## Proof body

The proof must record:

- case identifier
- source remedy-runway receipt identifier
- current remedy-flight-protection posture rung
- required cohort identifier
- promised finish window
- proof timestamp and time-authority basis
- active queue snapshot
- priority and preemption snapshot
- scheduler and pause snapshot
- current execution cohort snapshot
- source continuity floor
- hidden-task pressure summary
- watcher or rediscovery floor
- service-metadata integrity summary
- temporary-write continuity summary
- strongest honest sentence
- strongest blocked stronger sentence
- exact blocker summary

## Acceptable proof inputs

The proof may draw from:

- queue and priority state
- scheduler and pause state
- current start or transfer receipts
- source continuity attestations
- hidden-task warnings and resource-pressure signals
- watcher-health or rediscovery-risk signals
- `.sync` and service-state integrity checks
- restart, resume, or requeue traces

## Forbidden compressions

The proof must not compress these into one verdict:

- runway ready versus finish-protected
- started versus likely to finish unattended
- configured priority versus bounded preemption exposure
- source present now versus source continuity through finish
- visible progress versus stable finish guarantee
- warning absence versus low abort floor

## Stronger-sentence blockers

The proof must explicitly preserve blockers such as:

- higher-priority queue arrival risk
- queue rebuild churn
- scheduler closure before safe finish
- pause exposure
- hidden-task congestion
- watcher or rediscovery lag
- source disappearance risk
- ghost-file risk
- service-metadata corruption or `.sync` fragility
- restart or temporary-write fragility
- manual babysitting debt
